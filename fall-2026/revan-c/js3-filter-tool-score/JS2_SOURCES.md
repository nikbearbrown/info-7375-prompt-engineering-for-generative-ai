# Sources and AI assistance — Job-Search Agent 2

## What I started from

- My Job-Search Agent 1 in this repository: the fictional résumé, `jsagent/resume.py`, `jsagent/rule.py`, and CONTRACT.md, reused unchanged.
- Lectern's `ATS.md` (instructor's collector), read for how Greenhouse, Ashby, and Lever endpoints behave, and for the warning that an empty board can mean a wrong slug. No Lectern or Reallocation Engine code was used.
- Greenhouse Job Board API and Lever Postings API documentation, cited in GATE.md.

## What Claude Code (Claude Opus 5.5, in the Claude desktop app) contributed

| Contribution | Commit | What I did with it |
|---|---|---|
| Probed live endpoints on 2026-11-09 and 2026-11-10 (Greenhouse, Ashby, Lever; bad slugs; Webflow's empty Greenhouse board). Responses not saved | — | Chose my own boards in GATE.md (Duolingo, Patch My PC), which differ from Claude's suggestions |
| Reviewed my GATE.md draft. Pointed out: the approval flag blocked every observation-only run; the time limit let a request start at second 40; no look-alike host case; an empty board was now caught by policy, so Webflow no longer fit the review packet | — | Revised GATE.md myself (observation-only default, 10-second rule, B03a, B16) and committed it in `f3072e5` |
| Wrote the JS2 tests from GATE.md, before the implementation | `e7493d7` | I ran the full suite (110 passed) and compared BOUNDARY_TESTS.md's named results from Claude's `-v` run with my predictions; I did not read every assertion closely. |
| Wrote `jsloop/`, `tools/independent_check.py`, `tools/check_wrong_versions_js2.py`, and tightened three tests after the code existed (listed in the commit message) | `ac2827a` | I checked the loop through the saved live and seeded traces, the independent checker, the full suite, and the 17 mutants; I did not audit every line of `jsloop/`. |
| Found, while writing the mutation checker, that its own state write passed `approve_state_write=True` hard-coded, and changed it to pass the real flag | `ac2827a` | I accepted the fix after the approval boundary tests and my 17-of-17 mutant run; I did not treat the original green test as proof of the write path. |
| Rebuilt `.venv` on Python 3.12.14 after Python 3.14 turned out to be uninstalled | — | I accepted the rebuilt environment and ran the full suite on it after the review patch: 110 passed. |
| Renamed JS1's README, SOURCES, and FRICTIONAL to `JS1_*`; wrote the seeded empty fixture and its provenance; drafted README, BOUNDARY_TESTS, the REVIEW_PACKET skeleton, this file, and the SIGNOFF draft | `6fbefdb` | I kept the JS1 renames and labeled fixture, rewrote FRICTIONAL.md and REVIEW_PACKET.md, filled the README “What ran” table, and updated BOUNDARY_TESTS.md with my results; SIGNOFF.md: I checked every line and signed it |
| Pointed out the Lever remote-location defect used in the review packet | — | I reproduced both saved postings with the pre-patch code in a worktree at `bfbc822`, committed a failing remote-versus-onsite test, and accepted `06e9257` after reviewing its behavior and scope. |
| Patched Lever normalization to carry `workplaceType: "remote"` into the rule's location input | `06e9257` | I read the one-file diff, ran the two-case test, full suite, and 17 mutants, then accepted the patch while recording the synthesized-location and country-restriction limits in REVIEW_PACKET.md. |
| Saved my pasted terminal log as `review_evidence/post_patch_commands.txt` (header added, email removed) and added two evidence sentences in REVIEW_PACKET.md §1 and §5 | `9ec1695` | I ran every command in that log and checked both sentences against it before committing. |
| Checked my documents against the commits and files and pointed out inaccurate wording | — | I rewrote the flagged sentences, including FRICTIONAL.md §2, §5, and §7, after checking who did each action. |

## Not from Claude

- GATE.md: every decision and its wording.
- The review packet's content in §§1–7, except two evidence sentences Claude added in §1 and §5 at my request; Claude also drafted the earlier skeleton.
- FRICTIONAL.md.
- The signature.
