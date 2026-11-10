# Sources and contributions

## What I used

- **The brief:** "Job-Search Agent 2 — The Loop, the Tools, and the Diff", INFO 7375 Fall 2026
  (`assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` on `main`, and Canvas).
- **My JS1** (`fall-2026/ashwin-t/js1-contract-and-watch/`, commit `d95f05e`): `rule.py`, `text.py`,
  `persona.py` and the fictional résumé were copied unchanged (each file says so in its first line).
  `state.py` was adapted (per-board keys).
- **Lectern's `ATS.md`** (`fall-2026/nik-bear-brown/lectern/ATS.md` on `main`), read for which public
  endpoints Greenhouse, Ashby and Lever expose. No Lectern code was copied.
- **Data:** public, keyless board listings, fetched 2026-11-08 (probe, one GET each) and 2026-11-09 (the live
  run): Greenhouse `klaviyo`, `hubspotjobs`; Ashby `notion`, `supabase`; Lever `palantir`; and the
  nonexistent Greenhouse board `klaviyo-nonexistent-js2`. Postings are those companies' text, saved
  unchanged in `runs/*/raw/` as evidence.
- **Tools:** Python 3 standard library; Claude Code (desktop app) with Claude Opus 5.5 (`claude-opus-5-5`);
  Codex for review; git.
- **Persona:** Supriya Sharma is invented (from JS1). No real résumé is used.

## Decisions and requests recorded for Ashwin

- Approved the gate on 2026-11-09; Claude Code changed its Status line before commit `c9ff312`.
- Kept the gate's state rule, including no state update after the deliberate failure.
- Sent the patch request and accepted the scoped patch on 2026-11-10, as recorded in the review packet.
- Final submission sign-off remains pending. Successful post-patch checks recorded in the packet
  were run by Claude Code; personal command attempts failed because of the working directory.

## What Claude Code contributed

- The board probe (2026-11-08) and `drafting/GATE-QUESTIONS.md` (questions only).
- All code in `jobloop/` except the copied JS1 files, `independent_check.py`, `wrong_versions/`,
  `seeded/finished-wrong-answer/build.py`, and every test file except the review-packet test.
- The live run and the seeded demo runs, and the independent checks of them.
- The boundary-case list (inputs only) and the Actual column, filled from test output.
- Finding and reproducing the interrupted-request defect (`review-packet/reproduce_interrupt.py`).
- Drafts of `README.md`, `finished-wrong-answer/README.md`, the facts sections of
  `review-packet/REVIEW-PACKET.md`, the facts table and driver's-seat draft in `SIGNOFF.md`, this file, and
  the "What happened" / "Evidence" lines of `FRICTIONAL.md`.
- Its own bug, found and fixed: the misleading seeded state line (`a11a167`).

## What Codex contributed

- 2026-11-09: drafted GATE.md from Claude Code's questions and the assignment brief, including
  proposed budgets, exits, permissions, and review choices. Approval was a separate step.
- 2026-11-09: filled all 18 initial Predicted and Why cells in policy/BOUNDARY-TABLE.md from the gate,
  without running boundary tests. Later reviewed the saved table for completeness. The initial
  wording was assisted drafting, not independently written student text.
- 2026-11-10: drafted and saved tests/test_review_interrupt.py using the existing reproduction and
  test helpers; ran it before the patch and saved its three failures (exit 1). Claude Code committed
  the test separately at 279c10f.
- 2026-11-10: drafted the fix request sent to Claude Code and reviewed the resulting loop.py diff.
- 2026-11-10: drafted the remaining review analysis, sign-off fields, driver's-seat revisions, and
  evidence-based FRICTIONAL entries; updated this contribution record. Personal feelings, successful
  personal checks, and a final signature have not been inferred from automated results.

Earlier labels calling the initial gate or boundary predictions solely Ashwin's writing are
superseded by this contribution record. Historical commits are preserved.
