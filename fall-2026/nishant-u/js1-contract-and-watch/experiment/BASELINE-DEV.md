# Baseline prompt on the 10 dev postings

- **Prompt:** `prompts/baseline.md`, unchanged. No revised prompt has been written.
- **Postings:** all 10 in `experiment/dev_ids.json`, 1 fresh `claude -p` call each, run 2026-10-29
  between 20:38 and 20:39 UTC on my Claude Code login (CLI 2.1.312), with no API key. Run by
  `python3 experiment/claude_dev.py baseline-dev`. Prompts, raw replies and meta (date, session_id,
  model) are in `experiment/runs/baseline-dev/`, and the parsed rows in `results.json`. **No held-out
  posting was sent.**
- **Pass** = valid (the validator accepts the shape) AND the verdict equals my hand label. The
  "citations supported" column is reported separately and is not part of pass.

## Every call

| posting_id | date (UTC) | session_id | model | my label | Claude verdict | valid? | citations supported | pass |
|---|---|---|---|---|---|---|---|---|
| 8612874002 | 2026-10-29T20:38:04+00:00 | `2d980005-c22c-4b08-8c0d-fbb6a580014c` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8618151002 | 2026-10-29T20:38:08+00:00 | `bb069394-98ea-48c5-84df-dd6dc5e759ac` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8660923002 | 2026-10-29T20:38:14+00:00 | `30a4fc27-4f5c-426d-ab6c-da98e7203cfa` | claude-opus-5-5 | relevant | relevant | valid | 1/1 | yes |
| 8818059002 | 2026-10-29T20:38:20+00:00 | `20847fab-7296-4479-a559-be6a7c45cd7f` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8820806002 | 2026-10-29T20:38:24+00:00 | `b3e3098a-d8f9-452c-8071-a1869613f3ed` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8821336002 | 2026-10-29T20:38:30+00:00 | `a8baa6d5-e98a-4499-97b6-f265ccbc0445` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8832899002 | 2026-10-29T20:38:35+00:00 | `d3ddd70d-c734-43ee-96c6-1a9881fc027b` | claude-opus-5-5 | not_relevant | not_relevant | valid | 4/4 | yes |
| 8870975002 | 2026-10-29T20:38:42+00:00 | `7dc982f3-16ba-4a7f-afe6-df1b8b965d35` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8872721002 | 2026-10-29T20:38:49+00:00 | `c973d0aa-4a8e-45dc-929d-58e6ca86d7e0` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8899853002 | 2026-10-29T20:38:56+00:00 | `747c08ea-682e-44a9-aa8e-72341812f367` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |

**Dev pass rate: 10/10** (pass = valid AND verdict equals my label).
Valid: 10/10. All citations supported: 10/10.

No unsupported citations.

## Failures

None: all 10 dev calls passed. There is no failing case to point a single change at.

## Passes that the pass rule doesn't look at (for choosing the one change)

These aren't failures under the contract's pass rule. They are what the pass rule can't see:

1. **No failed check.** The schema has no field for the check that failed, so the 9 not_relevant
   verdicts can't be compared with my `my_failed_check`. They could be right for the wrong reason
   without the validator noticing.
2. **`resume_field` is decorative.** It only has to exist. Titles were cited under
   `skills.languages` (8612874002, 8818059002, 8870975002, 8872721002, 8899853002) and
   `experience.0.title` (8820806002, 8821336002), and locations under `personal.location`. These are
   valid and supported, but they don't say why.
3. **No way to cite an absence.** For 8832899002 (my R4 fail) Claude cited "Strong programming skills"
   and an ML-methods sentence under `skills.backend_automation`. Neither is evidence that no shipped
   skill appears. For 8612874002 it cited "You can use SQL or Excel…", which a reader could take as R4
   evidence, though by the rule this posting fails on its title.
4. **Thin coverage.** Only 1 of the 10 dev postings is relevant by my labels, so the prompt's
   relevant path was tested once.

The pass rate is 10/10 on easy cases. It can't separate this prompt from a better one; choosing the
one change, and whether to change the pass rule or the prompt, is Nishant's decision.
