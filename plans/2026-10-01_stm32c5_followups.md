# STM32C5 support: follow-ups

Items found while executing `plans/2026-10-01_stm32c5.md` that are real but outside its scope. Each has an owner.

| Item | Where | Owner |
|---|---|---|
| Codex fallback reviewer switches a `--base`/`--commit` review to the working tree; it should keep the requested target, its validation and the plans/ exclusion | `.claude/agents/codex-reviewer.md` (source: HART-CETEC-Admin-Tool kit) | Erik |
| `codex-review.sh` treats an unreadable `codex doctor` result as "not set up" (exit 3), which licenses a same-vendor fallback for a broken tool; unknown auth status should block | `scripts/codex-review.sh` lines ~99-107 (source: HART-CETEC-Admin-Tool kit) | Erik |
| `codex-review.sh` creates temp files with `mktemp` before normalizing `TMPDIR`; with `TMPDIR` inside the repo the temp file enters the review scope | `scripts/codex-review.sh` lines ~124-125 (source: HART-CETEC-Admin-Tool kit) | Erik |
| Pre-existing GCC warnings (18) in the ar100 test build from src/ar100/util.{c,h}; present before this branch | src/ar100 | Erik |
