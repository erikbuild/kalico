#!/usr/bin/env bash
# ABOUTME: Runs an adversarial code review through the codex cli for a working tree, branch or commit.
# ABOUTME: Builds the brief from .claude/rules/adversarial-review.md; exit 3 means codex is not set up.
# runs the kit's adversarial review through the codex cli. resolves the
# strongest listed model at run time, applies high reasoning effort, and feeds
# the six dimensions from .claude/rules/adversarial-review.md as the brief.
#
# usage:  bash scripts/codex-review.sh [--uncommitted | --base <ref> | --commit <sha>] [focus text...]
#
# env:    CODEX_REVIEW_MODEL   slug override; the catalog is still read, to validate effort
#         CODEX_REVIEW_EFFORT  reasoning effort override (default: high; max and ultra exist)
#
# exit codes:
#   0    the review ran
#   3    codex is not set up on this machine (absent, or no credentials).
#        the ONLY code that licenses a caller to fall back to another reviewer
#   130  interrupted
#   *    the review failed for a reason a different reviewer would not fix -
#        a bad ref, an empty scope, a missing brief, codex itself erroring.
#        these block, because falling back would hide a broken review
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)

# everything below reads git output, which is relative to cwd: from a
# subdirectory `plans/` reads as `../plans/` and slips past the filter that
# withholds it. anchoring here also makes codex's workdir the repo root
cd "$ROOT"

RULE_REL=".claude/rules/adversarial-review.md"
RULE="$ROOT/$RULE_REL"
# high, not max: measured on a 9-file change, max ran past ten minutes without
# returning a verdict while high finished and found real defects. max and ultra
# are one env var away when a change earns them
EFFORT="${CODEX_REVIEW_EFFORT:-high}"

target_kind=uncommitted
target_ref=""
target_set=""
focus=()

# last-flag-wins would report a successful review of a scope nobody asked for.
# a function, not a `;;&` fallthrough: stock macos ships bash 3.2, which has no
# fallthrough and fails to parse the file at all
claim_target() {
  if [ -n "$target_set" ] && [ "$target_set" != "$1" ]; then
    echo "FAIL: $target_set and $1 are both review targets - name one target"
    exit 1
  fi
  target_set="$1"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --uncommitted) claim_target "$1"; target_kind=uncommitted; target_ref=""; shift ;;
    --base)
      [ "$#" -ge 2 ] || { echo "FAIL: --base needs a ref"; exit 1; }
      claim_target "$1"; target_kind=base; target_ref="$2"; shift 2 ;;
    --commit)
      [ "$#" -ge 2 ] || { echo "FAIL: --commit needs a sha"; exit 1; }
      claim_target "$1"; target_kind=commit; target_ref="$2"; shift 2 ;;
    -h|--help)
      awk 'NR>1 && /^#/ { sub(/^# ?/, ""); print; next } NR>1 { exit }' "$0"
      exit 0 ;;
    *) focus+=("$1"); shift ;;
  esac
done

# ── preconditions ──────────────────────────────────────────────

if ! command -v codex >/dev/null 2>&1; then
  echo "FAIL: codex cli not found on PATH"
  echo "fix: npm i -g @openai/codex && codex login"
  exit 3
fi

# codex decides what counts as authentication - a stored file, an api key in
# the environment, or a source this script has never heard of. a stored
# auth.json is the fast path; anything else is settled by `codex doctor`, which
# takes 2s and exits 1 exactly when there are no credentials. enumerating auth
# env vars here would just be a second list to keep in sync with codex's.
# without any precheck an unauthenticated run retries five times and dies on a
# raw 401
CODEX_STATE="${CODEX_HOME:-$HOME/.codex}"
if [ ! -s "$CODEX_STATE/auth.json" ]; then
  doctor_rc=0
  doctor_json=$(codex doctor --json 2>/dev/null) || doctor_rc=$?
  # doctor aggregates auth, network, config and runtime, so its exit code says
  # "something is wrong", not "you are logged out". a ci box with a failed
  # reachability check is still authenticated, and answering that with
  # "codex login" blocks a mandatory review on the wrong remedy
  auth_status=$(printf '%s' "$doctor_json" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin)["checks"]["auth.credentials"]["status"])
except Exception:
    pass
' 2>/dev/null)
  if [ -n "$auth_status" ]; then
    blocked=$([ "$auth_status" = "ok" ] && echo 0 || echo 1)
  else
    blocked=$([ "$doctor_rc" -eq 0 ] && echo 0 || echo 1)
  fi
  if [ "$blocked" -eq 1 ]; then
    echo "FAIL: codex has no credentials"
    echo "fix: codex login, or supply an api key through a supported env var"
    exit 3
  fi
fi

if [ ! -f "$RULE" ]; then
  echo "FAIL: review brief missing: $RULE_REL"
  echo "fix: restore it from the kit - it is the only source of the six dimensions"
  exit 1
fi

# ── scope ──────────────────────────────────────────────────────
# codex refuses a target flag alongside a custom prompt: it is either its own
# targeting or our brief, never both. left to scope itself it runs
# `git diff --name-only HEAD`, which lists tracked changes only - a change made
# entirely of new files reviews as if it were empty. so the scope is computed
# here and stated in the brief.

GITERR=$(mktemp)
trap 'rm -f "$GITERR"' EXIT

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FAIL: not inside a git repository - the review scope comes from git"
  echo "fix: run this from the repo you want reviewed"
  exit 1
fi

# an option-shaped ref quotes cleanly but git still reads it as an option:
# `--commit --all` would make `git show` report paths from every commit, and
# the run would look like a successful review of the wrong scope
if [ -n "$target_ref" ]; then
  case "$target_ref" in
    -*)
      echo "FAIL: $target_ref looks like an option, not a ref"
      echo "fix: pass a branch, tag or sha"
      exit 1 ;;
  esac
  if ! git rev-parse --verify --quiet "$target_ref^{commit}" >/dev/null; then
    echo "FAIL: could not resolve $target_ref to a commit"
    echo "fix: pass a ref that exists in this repository"
    exit 1
  fi
fi

case "$target_kind" in
  uncommitted)
    scope_desc="the working tree: staged, unstaged and untracked changes"
    scope_cmd="git status --short --untracked-files=all"
    scope_out=$(git status --short --untracked-files=all) || scope_out="" ;;
  base)
    scope_desc="the changes on this branch against $target_ref"
    scope_cmd="git diff --name-status $target_ref...HEAD"
    # git's own error is the useful one here: a base with no merge base is a
    # different problem from an empty diff, and reporting it as "nothing to
    # review" sends the user off to make a change that already exists
    if ! scope_out=$(git diff --name-status "$target_ref...HEAD" 2>"$GITERR"); then
      echo "FAIL: could not diff $target_ref...HEAD"
      sed 's/^/  /' "$GITERR"
      echo "fix: name a base that shares history with HEAD"
      exit 1
    fi ;;
  commit)
    scope_desc="the changes introduced by commit $target_ref"
    # --first-parent because the default combined diff for a merge omits every
    # file that matches either parent, so an ordinary merge scopes to nothing
    scope_cmd="git show --first-parent --name-status --pretty=format: $target_ref"
    if ! scope_out=$(git show --first-parent --name-status --pretty=format: "$target_ref" 2>"$GITERR"); then
      echo "FAIL: could not read commit $target_ref"
      sed 's/^/  /' "$GITERR"
      exit 1
    fi ;;
esac

# the author's plan is withheld on purpose. adversarial-review.md: the reviewer
# gets the change and the standard, never the reasoning that produced it -
# handing over the conclusion is how a review becomes a rubber stamp.
#
# the decision is made on the destination path, because a rename record names
# two: `R  plans/a.md -> docs/a.md` is a change to docs/a.md and stays in scope
scope_out=$(printf '%s\n' "$scope_out" | python3 -c '
import sys

kept = []
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if "\t" in line:
        dest = line.split("\t")[-1]          # M<tab>path, R100<tab>old<tab>new
    else:
        dest = line[3:] if len(line) > 3 else line   # XY path
        if " -> " in dest:
            dest = dest.split(" -> ")[-1]
    if dest.strip().strip(chr(34)).startswith("plans/"):
        continue
    kept.append(line)
sys.stdout.write("\n".join(kept))
')

if [ -z "$scope_out" ]; then
  echo "FAIL: nothing to review in $scope_desc"
  echo "fix: make a change first, or name another target with --base <ref> or --commit <sha>"
  exit 1
fi

# ── model + effort resolution ──────────────────────────────────
# the catalog is the live list for this account, so "strongest" tracks new
# releases without a slug pinned anywhere in the kit. codex ships hidden
# entries (codex-auto-review) that outrank the listed models on priority and
# must never be selected, which is what the visibility filter is for.

CATALOG=$(mktemp)
trap 'rm -f "$GITERR" "$CATALOG"' EXIT
codex debug models > "$CATALOG" 2>/dev/null || true

rc=0
parsed=$(python3 - "$CATALOG" "${CODEX_REVIEW_MODEL:-}" <<'PY'
import json, sys

path, override = sys.argv[1], (sys.argv[2] or None)

try:
    with open(path) as fh:
        models = json.load(fh)["models"]
except Exception:
    models = None

if models is None:
    # no catalog: an explicit slug is the only way to know what to ask for
    if not override:
        sys.exit(2)
    print(override + "\t")
    sys.exit(0)

if override:
    entry = next((m for m in models if m.get("slug") == override), None)
    slug = override
else:
    listed = [m for m in models if m.get("visibility") == "list"]
    if not listed:
        sys.exit(3)
    entry = min(listed, key=lambda m: m.get("priority", 1 << 30))
    slug = entry.get("slug")

# an unknown override slug yields no levels, so validation is skipped rather
# than guessed at - codex rejects a bad slug itself
levels = [lv.get("effort") for lv in ((entry or {}).get("supported_reasoning_levels") or [])]
print((slug or "") + "\t" + ",".join(x for x in levels if x))
PY
) || rc=$?

if [ "$rc" -eq 2 ]; then
  echo "FAIL: could not read the codex model catalog (\`codex debug models\`)"
  echo "fix: set CODEX_REVIEW_MODEL to a slug, e.g. CODEX_REVIEW_MODEL=gpt-5.6-sol"
  exit 1
elif [ "$rc" -ne 0 ]; then
  echo "FAIL: the codex model catalog lists no selectable model"
  echo "fix: set CODEX_REVIEW_MODEL to a slug, or run \`codex doctor\`"
  exit 1
fi

MODEL="${parsed%%$'\t'*}"
LEVELS="${parsed#*$'\t'}"

if [ -z "$MODEL" ]; then
  echo "FAIL: could not resolve a review model"
  echo "fix: set CODEX_REVIEW_MODEL to a slug, or run \`codex doctor\`"
  exit 1
fi

# models disagree on the top of the range: luna stops at max, sol and terra
# reach ultra. failing here beats a remote error after the upload
if [ -n "$LEVELS" ] && ! grep -qx "$EFFORT" <<<"${LEVELS//,/$'\n'}"; then
  echo "FAIL: $MODEL does not support reasoning effort '$EFFORT'"
  echo "supported: ${LEVELS//,/, }"
  echo "fix: set CODEX_REVIEW_EFFORT to one of the above"
  exit 1
fi

# ── the brief ──────────────────────────────────────────────────
# the rule file is read, never copied. it is the single source of the six
# dimensions, so editing the rule changes what the reviewer is told.

PROMPT="you are reviewing this change as an unbiased reviewer who did not write it.
you were given the change and the standard below, and deliberately not the author's
plan or reasoning - do not ask for them.

## scope

review $scope_desc.

\`\`\`
\$ $scope_cmd
$scope_out
\`\`\`

every path listed above is in scope, including untracked ones - a new file is part of
this change. read the diff for a modified path and the whole file for a new one. do not
re-scope this yourself with \`git diff HEAD\`: it lists tracked changes only and would
skip every new file.

report findings ranked by consequence. every finding names the defect, the concrete
input or state that triggers it, what goes wrong as a result, and the fix you propose.
a concern you cannot ground that way is a question, not a finding - label it as one.

this is review only. do not edit, patch, or stage anything.

close with a coverage line: name which of the six dimensions below you actually
examined and what you looked at for each. it is the record the caller reports, so
do not claim a dimension you did not exercise, and give the line even when you
found nothing.

the standard you are reviewing against follows.

$(cat "$RULE")"

if [ "${#focus[@]}" -gt 0 ]; then
  PROMPT="$PROMPT

the reviewer requesting this run asked you to focus on: ${focus[*]}"
fi

# codex streams its progress to stderr, echoing back every file it reads.
# measured against this repo it ran 65-114x the size of the findings, ~71k
# tokens on one run, and a caller that captures both pays for all of it. the
# findings go to stdout, the stream goes to a log. the log lives outside the
# repo on purpose: a file written inside would show up in
# `git status --untracked-files=all` and land in the next review's scope
# `TMPDIR=$PWD` is a setting people really have, and a file written inside the
# repo lands in the next review's scope and grows every round. both sides are
# resolved physically before comparing: on macos /tmp is a symlink to
# /private/tmp and $TMPDIR sits under /private/var
tmpdir=$(cd "${TMPDIR:-/tmp}" 2>/dev/null && pwd -P) || tmpdir=""
root_real=$(cd "$ROOT" && pwd -P)
case "${tmpdir:-/tmp}/" in
  "$root_real"/*) tmpdir="" ;;
esac
[ -n "$tmpdir" ] || tmpdir=/tmp

BRIEF=$(mktemp "$tmpdir/codex-brief.XXXXXX")
trap 'rm -f "$GITERR" "$CATALOG" "$BRIEF"' EXIT

LOG=""
if [ -z "${CODEX_REVIEW_VERBOSE:-}" ]; then
  LOG=$(mktemp "$tmpdir/codex-review.XXXXXX")
  # ctrl-c on a long review should still say where the transcript is, even
  # before codex has been launched
  trap 'echo "interrupted. any interim findings are in the progress log: $LOG" >&2; exit 130' INT TERM
fi

echo "codex review: model $MODEL, effort $EFFORT, scope: $scope_desc" >&2
printf '%s\n' "$scope_out" | sed 's/^/  /' >&2
if [ -n "$LOG" ]; then
  # advertised before the run rather than after it. a review at high effort
  # runs for minutes and at max for longer than a foreground shell will wait,
  # so the path is only useful while there is still something to watch
  echo "progress log: $LOG" >&2
  printf 'watch it live: tail -f %q\n' "$LOG" >&2
fi

# `-` reads the brief from stdin. as a single argv entry, the scope listing
# plus the rule text is unbounded and a large working tree fails execve with
# E2BIG before codex ever starts
codex_args=(exec review
  -m "$MODEL"
  -c "model_reasoning_effort=\"$EFFORT\""
  --strict-config
  -)

printf '%s' "$PROMPT" > "$BRIEF"

# codex is a tracked background child, not the right half of a pipeline. bash
# defers a trap until its foreground command returns, so a wrapper that cannot
# forward the signal leaves a multi-minute review burning budget after the
# caller has already given up on it
if [ -n "${CODEX_REVIEW_VERBOSE:-}" ]; then
  # a human watching a multi-minute review wants the progress, live
  codex "${codex_args[@]}" < "$BRIEF" &
else
  codex "${codex_args[@]}" < "$BRIEF" 2>"$LOG" &
fi
codex_pid=$!
trap 'kill -TERM "$codex_pid" 2>/dev/null; echo "interrupted${LOG:+. any interim findings are in the progress log: $LOG}" >&2; exit 130' INT TERM

rc=0
wait "$codex_pid" || rc=$?

if [ -z "${CODEX_REVIEW_VERBOSE:-}" ]; then
  # the 401s and the retry storm live in that stream, so a failure still has to
  # say why rather than exiting non-zero in silence
  if [ "$rc" -ne 0 ]; then
    total=$(wc -l < "$LOG" | tr -d ' ')
    echo "codex exited $rc. $total lines of progress." >&2
    # a fixed tail can push the one actionable line off the top: codex emits
    # `ERROR: Reconnecting... 5/5` storms, and the message naming the fix comes
    # before them. so the error lines are pulled out first, then the tail
    matches=$(grep -inE 'error|unauthorized|denied|no prompt|not found|refused|fatal' "$LOG" | head -10 || true)
    if [ -n "$matches" ]; then
      echo "  error lines:" >&2
      printf '%s\n' "$matches" | sed 's/^/    /' >&2
    fi
    echo "  last 20 of $total lines:" >&2
    tail -20 "$LOG" | sed 's/^/    /' >&2
    echo "full log: $LOG" >&2
  fi
fi

exit $rc
