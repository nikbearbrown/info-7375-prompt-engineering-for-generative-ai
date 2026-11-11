# SOURCES

## What I used

- **My Job-Search Agent 1 code.** `agent/rule.py` and `agent/resume.py` were copied into `agent2/`, along with the persona `data/resume_jack_spencer.json`.
- **Public job-board APIs** (read-only, no login):
  - Greenhouse: `boards-api.greenhouse.io/v1/boards/figma/jobs`
  - Lever: `api.lever.co/v0/postings/spotify`
  - Ashby: `api.ashbyhq.com/posting-api/job-board/snowflake`
- **Python 3.12.10**, standard library only.
- **Claude Code in VS Code** (`claude-opus-5-5`) as my coding assistant on 2026-11-10.

## What I wrote or decided

- **Every decision in GATE.md.** Claude proposed seven numbered suggestions and I accepted all seven unchanged (the provenance line is in GATE.md). I also approved the dated budget-enforcement entry after the review.
- **My review of the 15 boundary predictions** before the first run.
- **The review packet:**
  - the choice of defect (A);
  - the spec for its test;
  - running the tests before and after the patch, the `git diff`, and the live check (`review/`);
  - the decision to accept, and the reasoning in my own words.
- **The signature on the sign-off**, and my reflections in FRICTIONAL.md.

## What Claude Code contributed

- **All code:** `agent2/`, `scripts/`, and `tests/`, including the two wrong versions in `tests/wrong_versions.py`.
- **The wording of GATE.md**, the 15 boundary predictions (derived from GATE.md), and the two review-packet defect candidates, which it found by reading v1 against GATE.md.
- **The review-packet test**, drafted from my spec, and the patch.
- **The SEEDED demo design.**
- **Drafts** of README.md (including the sign-off wording and the driver's-seat "why" column), POLICY_TESTS.md, REVIEW_PACKET.md (except my decision and reasoning), this file, and the factual log in FRICTIONAL.md.
- **The first runs of the loop and wrong-version tests** during development, the two live runs at 19:43 and 19:44, and the SEEDED demo. I ran the full test suite and the post-patch live check myself.

## What Claude did not contribute

- Any posting or result. Every board response is real and saved in `out/evidence/`, except the one SEEDED empty figma response in `out/demo_finished_wrong/`, which is labeled as seeded. Test responses are marked CONSTRUCTED.
