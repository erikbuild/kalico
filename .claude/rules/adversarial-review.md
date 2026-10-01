# adversarial review

every non-trivial change gets reviewed by somebody who did not write it, before it is
reported done. the author is the worst available reviewer of their own diff: they review
the code they *meant* to write, and the bug is always in the gap between that and the code
that is actually there.

this is a gate, not a courtesy. "i re-read it and it looks right" is not a review.

this repository is microcontroller firmware (kalico or katapult) plus its python host code
and build scripts. a defect here can brick a board, corrupt flash, or move a motor or heater
the wrong way, so the review standard is the same as for security-sensitive code.

## every claim carries a proof and a test

a claim with no evidence is a note, and a note is not a finding. this binds both sides of the
review, and it is the rule the rest of this file is built on.

- **the author.** "it builds", "the clock is 144 MHz", "the page is erased", "nothing else
  reads this" - every one of those is a claim. each ships with the observation that produced
  it (the command, its output, the build log, the register value from the reference manual
  digest) **and** the test that keeps it true, where a host-side test can exist. register-level
  firmware behaviour that only silicon can show is a claim for the hardware acceptance list,
  and must be named as such rather than reported as verified
- **the reviewer.** a finding names the defect, the concrete input or state that triggers it,
  and what goes wrong as a result. "this could overflow" is a note. "with a 256 KiB part an
  erase at offset 0x20000 selects bank 1 page 16, which does not exist, so the erase fails and
  the flash write returns -3" is a finding. a note may be raised as a question, never counted
  as a finding
- **the fix.** lands with a test that **fails before it and passes after**, in the same commit,
  wherever a host-side test can exercise it. mutation-check it: undo the fix, watch the test
  fail with the message you expect, restore. a test never seen red proves nothing
- **a claim you cannot test** is either not true yet or not a claim. say which, and say what it
  would take to test it. "verified by reading" and "should work" are the phrases to catch
  yourself on

nothing is reported done on the strength of a note.

## when it is required

| situation | review |
|---|---|
| new mcu family, driver, kconfig option, host module, script | required |
| flash writes, option bytes, read protection, bootloader entry, watchdog, interrupt handlers | required, and the reviewer is told which of those it touches |
| a fix to a bug that a test did not catch | required - the missing test is part of the finding |
| refactor that moves behaviour between files | required |
| typo, log line, comment, formatting, vendor header import | skip |

## the reviewer must be unbiased

unbiased means **structurally** unable to inherit the author's belief, not "asked to be
objective":

- a **different vendor**, not just a fresh context. the house judge is the codex reviewer
  (the `codex-reviewer` agent, or `bash scripts/codex-review.sh`), which runs the strongest
  model the codex cli lists at `high` reasoning effort
- **a broken review blocks; a missing reviewer downgrades, loudly.** if codex is simply not
  installed here (`scripts/codex-review.sh` exits 3) a same-vendor claude reviewer stands in
  and says so in the first line of its report. every other failure blocks: a bad ref, an
  empty scope or a crashed run is a broken review, not a missing one
- give it **the diff and the requirement**. do NOT give it the plan, the reasoning, the
  commit body, or "here is why this is correct"
- ask it to **find what is wrong and propose the fix**, ranked by consequence
- it judges **quality**, not only correctness: is this the right shape, does it duplicate an
  invariant that already exists somewhere, will the next person to touch it understand it

## the six dimensions

| dimension | asks |
|---|---|
| security | what can this do to the hardware or the machine that it must not - writes outside the application flash area, option-byte or read-protection changes, bootloader entry that can lock a user out, memory safety (bounds, alignment, access width on memory-mapped areas), interrupt races and shared state touched outside `irq_save`, untrusted host or bus input reaching a register or buffer |
| design | is this the right shape - does it belong in the family file or the shared driver, does it duplicate a table or invariant that already has a home, does it copy code between kalico and katapult that will drift, will the next family port be cheap or expensive |
| usability | the person building and flashing a board - are the kconfig menus offering only options this chip has, are defaults safe, does a failure say what to do next, are the docs enough to flash a blank chip and recover a bad one |
| logic / flow | trace one real boot end to end: reset state, a bootloader handing over without a reset, clock switching order, flash wait states before frequency, erase then program, the second write to the same page, a retransmitted block, the interrupt that arrives mid-sequence, the state nobody designed for |
| best practice + standards | does it match this codebase's conventions (family `#if` branches, `DECL_*` macros, kconfig patterns, the neighbouring family files) and the reference manual's required sequences, or did it invent a competing pattern |
| sanity check | step back. does it actually do what was asked, is it obviously too much or too little code for the job, and would a colleague reading it cold understand why it exists |

on a large change, give each lens its own reviewer rather than several identical skeptics.

## the questions that find real defects

1. **is the control real?** treat a confident comment as a claim to test, especially one
   explaining why something is safe. grep for the reader of every value that is written: a
   register field set and never consumed by the hardware path enforces nothing
2. **is the gate watched rejecting something?** a test that never saw a violation refused is
   not a gate. mutation-check it
3. **which other path reaches this same hardware, and at what bar?** one fixed driver beside
   another family's unfixed copy, or kalico fixed and katapult not, is not a fix
4. **what does the test not cover?** zero, the last page, the last bank, the largest
   transfer, a reset mid-write, a bootloader that left a peripheral running, the other clock
   source, the other part number
5. **does this duplicate a rule that already lives somewhere?** one invariant written twice
   drifts, and the copy nobody remembers is the one that is wrong
6. **is it the right altitude?** would a smaller change have done it, and does this introduce
   a competing pattern beside an existing one
7. **does it reach every place its concept already has?** a new mcu that builds in one config
   but is missing from the kconfig menus, the test configs, the host scripts or the docs is a
   port nobody can use

## running the review

- **the reviewer must not fan out.** one reviewer, one context, its own tool calls
- **a review arrives all at once.** budget for the whole run; an interrupted review has
  produced nothing, and its progress log is the only record of how far it got
- **more than one lens beats more reviewers of the same kind.**

## acting on findings

- **verify before you pay.** check the consequence against the code and the reference manual
  digest. a finding can state a real gap with an inflated consequence
- a finding you disagree with gets an argued answer, not silence
- a real finding that the suite could not have caught means **the gate was missing**, so the
  fix ships with the test that would have caught it, or with a hardware acceptance item when
  only silicon can catch it
- findings that are real but out of scope go to `plans/` follow-ups with an owner, never to
  "we will fix it later"

## reporting

when the change is reported done, say who reviewed it, **which of the six dimensions were
covered**, what each found, and what was fixed versus recorded. every claim that survives into
that report carries its proof and the test pinning it.
