# What moves the score (Chapter 9)

## 1. Where every number came from

None of these numbers was **fitted** on labels. No labels existed when they were set.

| Number | Value | Where | Origin |
|---|---|---|---|
| role-word weight (R1) | +3 | FILTER.md §1 | **hand-set** by Claude Code, so a title match alone reaches the threshold |
| topic weight (R3) | +1 each | FILTER.md §1 | hand-set |
| topic cap (R3) | +2 | FILTER.md §1 | hand-set, so topic words alone can never keep (2 < 3) |
| years penalty (R4) | −3 at ≥ 5 years | FILTER.md §1 | hand-set; "roughly 3 years" is **inherited** from Saloni's JS1 labeling rule |
| R4 window | 60 chars before "experience" | `js3/filter.py` | hand-set |
| PhD penalty (R5) | −2 | FILTER.md §1 | hand-set; "no PhD" inherited from the JS1 rule |
| threshold (R6) | 3 | FILTER.md §1 | hand-set |
| short-text cutoff (R7) | 300 chars | FILTER.md §1 | hand-set |
| role words, seniority words | lists | FILTER.md §1 | **inherited** from JS1 `CONTRACT.md` / persona `search` block, plus 4 hand-set additions |
| abstain rule: "half or more insufficient" | 0.5 | FILTER.md §3 | hand-set |
| posting text sent to Claude | first 12,000 chars | `js3/claude.py` | **inherited** from JS1 `claude_judge.py` |
| Claude model | `claude-sonnet-5-5` | `js3/claude.py` | inherited from JS1 |
| Claude prompts | `prompts/judge_v1.md`, `justify_v1.md` | | hand-written by Claude Code on 2026-11-26; `judge_v2_criteria.md` copies Saloni's JS1 labeling rule |
| sample sizes 35 / 12 / 10 / 30 | | `scripts/make_samples.py` | hand-set (assignment minimum 30 random rejects, plus 5) |
| seed | 7375 | | hand-set (the course number) |

## 2. One change to one object at a time

The held-out set is 30 postings: 15 random v1.0 keeps and 15 random v1.0 rejects, disjoint from
the dev audit. It is **stratified**, so agreement on it is not a rate for the whole board.

**Claude variants** (real calls on 2026-11-26, 16:34:50–16:37:21 UTC, through the Claude Code
CLI 2.0.20, model `claude-sonnet-5-5`, one call per posting per variant, 120 calls in all, every
reply parsed. Raw replies are in `out/experiments/J*.jsonl`):

| Variant | Object changed | Change | worth / not / cannot tell | verdicts different from J0 |
|---|---|---|---|---|
| J0 | — | baseline: `judge_v1.md`, full posting, no tools | 3 / 25 / 2 | — |
| J1 | **prompt** | `judge_v2_criteria.md`: adds the three labeling criteria | 3 / 25 / 2 | 3 of 30 |
| J2 | **context** | title only, no posting text | 0 / 4 / 26 | 24 of 30 |
| J3 | **tool list** | my MCP server available (score_posting, search_postings) | 3 / 25 / 2 | 3 of 30 |

What each change did (measured, before any hand label):

- **Context moved Claude most.** With the title only, Claude said "cannot tell" on 26 of 30,
  including all 15 filter keeps. It answered "not worth time" only for 4 rejects whose titles
  say enough on their own. Taking away the text took away the evidence, and Claude abstained
  instead of guessing.
- **Prompt barely moved it.** Writing Saloni's three criteria into the prompt changed 3 of 30
  verdicts, and the totals came out identical (3 / 25 / 2), just on different postings. J0
  already rejected 25 of 30, so the criteria mostly restated what it was already doing.
- **The tool list changed behaviour, and that shows in the transcripts.** In J3 Claude called
  `score_posting` in **15 of 30** sessions (15 calls) and `search_postings` once (server
  transcripts in `out/mcp/transcripts/`). Three verdicts changed. In two of them Claude moved
  toward the filter's decision: one filter reject J0 called worth time became "not worth time",
  and one filter keep J0 could not decide became "worth time". In the third, a keep J0 rejected
  became "cannot tell". Agreement with the filter went from 16 of 30 (J0) to 18 of 30 (J3).
  That is the anchoring risk of giving Claude the scorer: it can lean on the filter instead of
  reading the posting. Three postings is too few to call it a pattern.

**Filter variants** (no model, `scripts/experiments.py measure`):

| Variant | Object changed | Change |
|---|---|---|
| F0 | — | FILTER.md v1.0 |
| F1 | **setting** | threshold 3 → 4 |
| F2 | **filter file** | C1: cut `training` |
| F3 | **filter file** | C2: veto `architect`, `recruiter` |
| F4 | **filter file** | C3: R4 without "experience" |

## 3. Measured against Saloni's held-out labels

> Filled by `python3 scripts/finish.py` after both sheets are labelled. It runs
> `python3 scripts/experiments.py measure` once on the held-out set, after C1–C3 were decided on
> dev labels.

<!-- finish.py:heldout -->
_Not computed yet: the held-out sheet is unlabelled._
<!-- /finish.py:heldout -->

## 4. What persistence is not proof of

If the agent behaves differently tomorrow, that does not mean anything was trained. Nothing in
JS3 changes a model's weights. Every Claude call here is a fresh `claude -p` conversation from
an empty folder, with no memory and no project files. A change that persists across sessions
lives in one of the objects above: FILTER.md, a prompt file, the snapshot that context is drawn
from, the tool list, or a setting. Or it lives on Anthropic's side (a model update under the
same name), which I cannot see. The J0 → J3 shift came from adding a tool, with nothing
trained. In session B Claude described its own tool use wrongly (TOOL-SERVER.md §2), so a
model's report of what changed is not evidence either. Repeated identical behaviour shows only
that the inputs and the model were the same. It does not show that the model learned.

## 5. Not checked

- Run-to-run variation: each Claude variant ran once. Some of the 3 changed verdicts in J1 and
  J3 could be noise; a J0 re-run would show how much.
- Whether the J3 change follows from the tool's answer in each session. I counted calls, but I
  did not match each changed verdict to that session's transcript.
- Any fitted number: the threshold could be fitted on dev labels after they exist. It was not.
