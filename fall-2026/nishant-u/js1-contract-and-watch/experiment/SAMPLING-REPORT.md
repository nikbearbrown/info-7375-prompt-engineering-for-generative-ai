# Sampling report (Chapter 1): baseline prompt, 5 dev postings × 4 fresh calls

- **Prompt:** `prompts/baseline.md`, unchanged.
- **Postings:** 5 from the development set only, picked by `experiment/claude_dev.py` with seed
  **20261030**: up to 2 postings I labeled relevant, the rest from my not_relevant ones. The dev set has
  only one posting I labeled relevant, so the pick is 1 relevant and 4 not_relevant. No held-out posting
  was sent; the script refuses any id outside `dev_ids.json`.
- **Calls:** 4 per posting, each a separate `claude -p --output-format json --tools ""` process
  (a fresh conversation, no `--resume` or `--continue`), run 2026-10-29 between 20:38 and 20:40 UTC on my
  Claude Code login (CLI 2.1.312), with no API key. 20 calls, 20 distinct session_ids. Every prompt and raw reply,
  with its date, session_id and model, is under `experiment/sampling/<posting_id>/call-<n>/`;
  `experiment/sampling/results.json` holds the parsed rows.
- **Columns, kept separate:** *valid* = the validator in `agent/validator.py` accepted the shape
  (with the 2026-10-29 empty-quote amendment). *Citations supported* = each quote is a substring of the
  posting field it names; it says nothing about whether the quote is the right evidence. *Pass* =
  valid AND the verdict equals my hand label.

## Every call

| posting_id | call | date (UTC) | session_id | model | my label | Claude verdict | valid? | citations supported | pass |
|---|---|---|---|---|---|---|---|---|---|
| 8660923002 | 1 | 2026-10-29T20:38:04+00:00 | `bcb74760-2ec2-49fd-81c6-08297ca25166` | claude-opus-5-5 | relevant | relevant | valid | 2/2 | yes |
| 8660923002 | 2 | 2026-10-29T20:38:12+00:00 | `77ee1bfc-259a-475c-9ab2-6c4de93af637` | claude-opus-5-5 | relevant | relevant | valid | 2/2 | yes |
| 8660923002 | 3 | 2026-10-29T20:38:21+00:00 | `1ca0f507-c408-4bd1-be69-ec10b5df3509` | claude-opus-5-5 | relevant | relevant | valid | 3/3 | yes |
| 8660923002 | 4 | 2026-10-29T20:38:27+00:00 | `6d500988-3ad3-4446-b898-8e21c20f974c` | claude-opus-5-5 | relevant | relevant | valid | 3/3 | yes |
| 8820806002 | 1 | 2026-10-29T20:38:34+00:00 | `19ab3834-f4d5-4c27-bc4a-348d397eabfc` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8820806002 | 2 | 2026-10-29T20:38:39+00:00 | `c9ff6c89-2b42-473d-83b3-4127bafe5191` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8820806002 | 3 | 2026-10-29T20:38:43+00:00 | `01474157-ebbf-4036-963a-3497d47c46fb` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8820806002 | 4 | 2026-10-29T20:38:48+00:00 | `82700e44-4434-46a5-9c1b-5b5002b798d1` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8832899002 | 1 | 2026-10-29T20:38:53+00:00 | `9e1aa179-450e-43a0-ae2d-b501bf753f04` | claude-opus-5-5 | not_relevant | not_relevant | valid | 4/4 | yes |
| 8832899002 | 2 | 2026-10-29T20:39:00+00:00 | `aed56ac4-cdf6-438b-8798-bd9f961069ad` | claude-opus-5-5 | not_relevant | not_relevant | valid | 4/4 | yes |
| 8832899002 | 3 | 2026-10-29T20:39:07+00:00 | `decf40e7-81e7-4934-8c0b-709a191acc5b` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8832899002 | 4 | 2026-10-29T20:39:14+00:00 | `5ab551b3-7428-4673-8b86-8e7490cfe67b` | claude-opus-5-5 | not_relevant | not_relevant | valid | 4/4 | yes |
| 8870975002 | 1 | 2026-10-29T20:39:21+00:00 | `9a42704b-fe14-4552-8953-219c1a1bb94a` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8870975002 | 2 | 2026-10-29T20:39:28+00:00 | `a2c3ae02-09f1-492c-8f61-1d3016fbcc5c` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8870975002 | 3 | 2026-10-29T20:39:33+00:00 | `8b84b303-c788-4939-a308-7fd9ad664055` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8870975002 | 4 | 2026-10-29T20:39:40+00:00 | `533545bb-6097-4c03-81a2-413d8702faf5` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8899853002 | 1 | 2026-10-29T20:39:44+00:00 | `6f055790-8735-4ea0-975b-83950a599742` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8899853002 | 2 | 2026-10-29T20:39:48+00:00 | `573f273e-f2ed-416b-a8b9-8327de06b304` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8899853002 | 3 | 2026-10-29T20:39:53+00:00 | `1decbd99-2ef6-46e8-bd29-2da4c1d0e098` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8899853002 | 4 | 2026-10-29T20:39:58+00:00 | `e73c1b94-2698-422c-99ca-a2e8960cf764` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |

## Spread per posting

| posting_id | my label | verdicts (4 calls) | valid | all citations supported | agrees with my label |
|---|---|---|---|---|---|
| 8660923002 | relevant | relevant 4/4 | 4/4 | 4/4 | 4/4 |
| 8820806002 | not_relevant | not_relevant 4/4 | 4/4 | 4/4 | 4/4 |
| 8832899002 | not_relevant | not_relevant 4/4 | 4/4 | 4/4 | 4/4 |
| 8870975002 | not_relevant | not_relevant 4/4 | 4/4 | 4/4 | 4/4 |
| 8899853002 | not_relevant | not_relevant 4/4 | 4/4 | 4/4 | 4/4 |

No unsupported citations.

## What we can and can't conclude (draft for Nishant to edit)

**Observed.**
- **Verdicts:** every posting got the same verdict in 4 of 4 calls, and all 20 calls agreed with my hand
  label.
- **Shape and quotes:** all 20 replies were valid, and every quote appeared in the field it named.
- **Citations varied:** the number of citations changed between calls of the same posting (8820806002: 1 or 2;
  8870975002: 1 or 3), and so did the `resume_field` attached to the same quote. For example, the title
  of 8820806002 was cited twice under `experience.0.title` and twice under `skills.languages`.

**We can conclude:** on these 5 postings, at this prompt, model and date, the baseline's verdict was
repeatable and so was its format.

**We can't conclude:**
- **Repeatability isn't correctness.** Four identical answers show the sampling spread is small here,
  not that the answer is right. That they match my labels is a separate check, and it only covers
  5 postings, picked to include just one relevant posting.
- **4 runs is a tiny sample.** 4/4 doesn't rule out a different answer on a fifth call. It is weak
  evidence that the disagreement rate is low on these postings, not a measured rate.
- **The 5 postings are easy.** Of the four not_relevant postings, three fail on the title (R1 or R2) and one fails R4 with no shipped skill.
  None is a borderline case such as a skill appearing only inside another word, or a multi-city
  location.
- **"Supported" is weaker than it sounds.** The support check confirms a quote exists, not that it
  is the evidence for the verdict. The schema doesn't ask which check failed, so a not_relevant reply
  can't be compared with my failed check. For an R4 failure, Claude has no way to cite an absence:
  quotes must be non-empty text from the field. In 8832899002 it cited "Strong programming skills"
  and an ML-methods sentence under `skills.backend_automation`; neither is the reason for its verdict.
- **The model can change.** These results are for `claude-opus-5-5` on 2026-10-29 only. A later model
  or CLI version may behave differently.
