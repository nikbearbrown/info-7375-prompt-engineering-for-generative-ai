# SOURCES

## Used
- Greenhouse Job Board API docs: https://developers.greenhouse.io/job-board.html
- Python 3.15.0, pip 26.2.2, anthropic 2.3.0, jsonschema 4.26.0, pytest 9.2.0 (pinned in requirements.txt)
- Claude Code CLI 2.1.314 (`claude -p`), as the judge backend `claude-cli`, on my subscription

## Written by me
- The rule, wrong versions and failure sentence: my decisions, drafted with Claude in chat on
  2026-10-29, then reviewed, edited and adopted by me; edited for clarity by Claude Code in session
  on 2026-10-29.
- Acceptance cases 9, 10, 13: cases and expected verdicts drafted with Claude (chat), hand-checked
  and adopted by me on 2026-10-29; test code typed by Claude Code from my answers.
- CONTRACT.md report.json shape, run_id, manifest fields, state file, prompt file format and Order
  step 2b; the citable posting document and the report counts' definitions; the persona's targets;
  the Wrong versions' demo lines; the widened case 10: drafted with
  Claude in chat on 2026-10-29, reviewed and adopted by me; written into CONTRACT.md,
  examples/persona_resume.json and ACCEPTANCE_CASES.md by Claude Code in session on 2026-10-29.

## Contributed by Claude
- Claude (claude.ai chat, 2026-10-27): planning checklist; folder scaffold and report templates;
  CLAUDE.md working rules; fictional persona résumé; scripts/presubmit_check.sh;
  first drafts of CONTRACT.md In / Out / Refuses.
- Claude (claude.ai chat, 2026-10-29): revised In / Out / Refuses and added Order of
  operations, Run labels and Interfaces, answering Claude Code's planning questions; acceptance cases 16 and 17;
  the whole-word matching definition used in The rule; tests/conftest.py (test fakes
  that fix the seam's duck types).
- Claude Code (2026-10-29/30): tests/spec/, written from my ACCEPTANCE_CASES.md before any implementation.
- Claude Code (2026-10-29): implemented jobwatch/, schema/resume.schema.json, tests/unit/; wrote tests/spec/ from my case list before the implementation; the contract amendments A1–A6 were my decisions.
- The judge under test: claude-sonnet-5-5 through the Claude Code CLI 2.1.314 (`--judge claude-cli`), 82 calls: 81 on 2026-10-30 (1 smoke, 20 sampling, 20 development, 20 held-out, 20 in run 2) and 1 on 2026-10-31 (run 3); every request and raw response is saved under evidence/, with each validator result in the run's report.json or the call's validation.json.
- Claude (claude.ai chat, 2026-10-30): first drafts of prompts/v1.md and labels/LABELING_RULE.md; edited and adopted by me. The 20 hand labels are mine.
- FRICTIONAL.md: Drafted by Claude Code from the session record on 2026-10-30, at my request, because I ran out of time.
- Claude Code (2026-10-30): implemented `replay`, `sample`, `experiment`, labels/make_split.py and the claude-cli judge backend, with their unit tests; listed the selection candidates by title only, drew the seeded 8 and wrote private/to_label.md; wrote scripts/exclusion_agreement.py; proposed the two candidate v2 changes (I picked one). Amendments A7–A15 were my decisions.
- Reports, README and sign-off drafted by Claude Code from saved results on 2026-10-30; conclusions drafted by Claude Code from saved results; not edited by me.
