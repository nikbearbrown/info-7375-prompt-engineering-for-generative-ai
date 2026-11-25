# SOURCES - JS2

## What I used
- Public job-board APIs, read-only, no login, one request per board per run:
  Ashby `api.ashbyhq.com/posting-api/job-board/commure`;
  Greenhouse `boards-api.greenhouse.io/v1/boards/{stripe,figma,gleanwork,databricks,doordashusa,twitch,roblox}/jobs?content=true`;
  Lever `api.lever.co/v0/postings/palantir?mode=json`.
- My JS1 agent (`../js1-contract-and-watch/`): `rule.py`, `validate.py`, `resume.py` copied unchanged, and the JS1 rule/validator/resume tests (`tests/test_js1_carryover.py`).
- Fictional persona `data/resume/rohan-desai.example.json` (from JS1).
- The 2026-10-14 and 2026-10-23 responses from my pitch-film probe (same bytes as JS1's `data/raw/`).
- Python 3.13.3 standard library.

## What I decided or wrote (Vrajesh)
- Every GATE.md item marked *(chosen 10-31)*: the 9 boards (I added Glean, Databricks, DoorDash, Twitch, Roblox to Claude's list), the budget and the later raise to 12/15/180, the error policy, the approval target, the bad-name failure. My acceptance of the rest of GATE.md.
- The choice of review defect (first the years regex, then the Greenhouse location bug once the first did not reproduce).
- Review packet steps 5 and 6, FRICTIONAL.md, and the signature (or withholding) on the sign-off.

## What Claude (Claude Code, Opus 5.5, 2026-10-31 to 2026-11-01 session) contributed
- Probed the ATS APIs live: 404 behavior for bad names on all three, which ATS each company uses, posting counts.
- Searched 288 real SWE postings for the years-regex defect and found it does not reproduce (0 of 72).
- Drafted the GATE.md sections marked *(proposed by Claude)*.
- Wrote all code in `earlybird/` (except the three files copied from JS1), all tests, `tests/wrong_versions.py` and `experiments/finished_wrong.py`.
- Ran run1, run2-live, the two demos and the after-fix replays; mutation-tested three policies.
- Reproduced the R3 defect, wrote `tests/test_review_r3.py` before the patch, wrote the patch, audited 740 location strings, and drafted review steps 1-4 and 7.
- Drafted README.md (including the sign-off draft and the driver's-seat table) and this file.
