# Prompt experiment (Chapter 2)

**Question.** Does one change to the prompt contract make Claude's answers better on postings it was not tuned on?

## Setup, fixed before prompt v2 made any call

| | |
|---|---|
| Postings | 20 real postings from the run-1 baseline, chosen by `experiments/select_postings.py` (seed 20261028, commit `846c35a`) before any label existed. Stratified by rule outcome to include near-misses, so **not a random sample of the board**. 10 development, 10 held-out ([selection.json](../experiments/selection.json)). |
| Labels | The 20 labels the student supplied in chat ([hand_labels.csv](../labels/hand_labels.csv), `0f312fb`, 09:05), applying the student's [labeling rule](../labels/LABELING-RULE.md) (`7752e69`). Committed before any experiment call (the first came at 09:06), but **not independent of the rule's output** (README, "The labels are not independent"). They equal the rule records on 20/20 ([hand-vs-rule.md](../experiments/hand-vs-rule.md)). |
| Baseline | [prompts/judge_v1.md](../prompts/judge_v1.md), the prompt the agent uses |
| Revision | [prompts/judge_v2.md](../prompts/judge_v2.md) = v1 plus **one inserted paragraph**, nothing else (diff below) |
| Calls | every prompt × every posting × 3 fresh `claude -p` conversations; `claude-opus-5-5`, tools, settings, MCP and saved sessions off; at most 3 at once |
| Order | 1. v1 on development (ran 2026-10-31 09:06–09:07). 2. v2 on development. 3. v1 and v2 on held-out, once each, with `--final`. The script refuses held-out unless both prompt files are committed unchanged. Nobody looked at Claude's output on the held-out postings before step 3. |

**The one change**, chosen by the student on 2026-10-31. The student's reason, verbatim:

> A. I want the justification to name the exact résumé and posting fields because I should be able to trace the explanation back to the inputs without piecing it together from the evidence arrays.

```diff
@@ prompts/judge_v1.md -> prompts/judge_v2.md (inserted before "Evidence rules:")
+In "justification", name the exact field paths behind each condition, so the explanation can be traced to the inputs on its own: resume.preferences.title_word, resume.preferences.focus_terms and posting.title (engineering role); resume.preferences.excluded_title_words and posting.title (title seniority); resume.preferences.location_terms and posting.location.name (location); resume.skills and posting.content (skills).
```

**Measures, fixed before v2 ran:**

1. **Pass rate (primary).** A call passes only if the validator accepted the reply **and** its verdict equals the student's label. A rejected reply is a failure, never a `not_relevant`.
2. **Traceability (secondary).** Among valid replies, the share whose `justification` text names **all 8** field paths the rule reads (`scoring.traceability`). Also reported: the share naming the 3 posting paths.

**What would count as "v2 is better":** traceability goes up on both sets while the pass rate does not go down. **Known ceiling:** v1 already passed 30/30 on development, so the primary measure cannot rise there; at most it can stay level or fall.

## Results

All four runs took place on 2026-10-31. Calls, replies, and scores are in [experiments/prompt-experiment/](../experiments/prompt-experiment/), and the terminal output is in [evidence/terminal/](../evidence/terminal/).

| Prompt | Set | When (EDT) | Valid replies | **Pass rate** | Postings passing all 3 calls | **Justification names all 8 paths** | Names the 3 posting paths |
|---|---|---|---|---|---|---|---|
| v1 | development | 09:06–09:07 | 30/30 | **30/30** | 10/10 | **0/30** | 0/30 |
| v2 | development | 09:16–09:17 | 30/30 | **30/30** | 10/10 | **30/30** | 30/30 |
| v1 | held-out | 09:17 | 30/30 | **30/30** | 10/10 | **0/30** | 0/30 |
| v2 | held-out | 09:17–09:18 | 29/30 | **29/30** | 9/10 | **29/29** | 29/29 |

**The one failure.** On held-out posting 5436684008 ("Staff + Sr. Software Engineer, Cloud Inference"), v2's third call produced a reply with a stray `]` right after the justification string (`…resume.skills)."], "resume_evidence"…`). The validator rejected it as "not exactly one JSON object". As the contract requires, it counted as a failure, not as `not_relevant`. In the agent, it would have stopped the run without advancing the state. The other two v2 calls on that posting were valid and correct.

**Against the measures fixed in advance:**
- **Traceability rose on both sets**, from 0/30 to 30/30 (development) and from 0/30 to 29/29 valid (held-out). This is the student's goal, met on every valid v2 reply.
- **The pass rate held on development** (30/30 → 30/30) but **fell by one call on held-out** (30/30 → 29/30).
- So **v2 did not strictly meet the "pass rate does not go down" condition**. It made justifications traceable, and one of its 30 held-out replies broke the output format.

**Exploratory, not fixed in advance:**

| Prompt | Set | Median justification (words) | Median output tokens | Cost reported by `claude -p` |
|---|---|---|---|---|
| v1 | development | 37 | 394.5 | $0.55 |
| v2 | development | 43.5 | 519 | $0.66 |
| v1 | held-out | 34 | 438.5 | $0.58 |
| v2 | held-out | 43 | 538 | $0.66 |

v2's replies were longer (about 100–125 more output tokens each) and cost about 15–20% more.

**Was the broken reply caused by v2?** This data can't say. Across every v1 call made today (run 2: 27; the seeded demo: 1; sampling: 20; this experiment: 60), **0 of 108** v1 replies were malformed, against **1 of 60** v2 replies. If both prompts had the same error rate, a single error would land in the v2 group about 60/168 ≈ 36% of the time by chance. One event is not evidence of a difference. Longer justifications are a plausible cause, untested.

## What ten cases can and cannot show

- **The verdict task was at ceiling.** Both prompts got every verdict right on all 20 postings, except one reply that wasn't a verdict at all. With 10 postings × 3 calls per set, even a real difference of a few percentage points in accuracy could not have been detected. "Equal pass rates" here means "both near-perfect on these postings", not "equally good in general".
- **The traceability effect is large and consistent** (0% → 100% of valid replies, on both sets), so it is real for these postings. But it was measured by whether the path strings appear. **Not checked:** whether each named path is used correctly. A justification could name `posting.content` and still say something wrong about it.
- **Held-out guards against tuning to specific postings, not against change.** Both sets come from the same board, the same day, and the same strata. And the strata over-sample near-misses, so this is not a random sample of the board: 6 of the 20 are relevant, against 8 of 681 on the board.
- **The labels equal the rule (20/20), and they were made after the rule's output had been shown.** So the pass rate measures agreement with the rule, that is, whether Claude applied the student's rule. It is not an independent measure of correctness, and it says nothing about whether the rule picks good jobs. The student's Frictional note lists two postings where it doesn't: 4616971008 and 5418610008.
- **Everything ran on one model, one route, and one morning.** `claude -p` ran at its default effort, while the chat surface used "Max". The `api` route was never run.
- **The held-out set was run once per prompt.** Nothing was changed after seeing it.

**The agent still uses v1** (`jobwatch.judge.DEFAULT_PROMPT`). Whether to switch is the student's decision; see the README.
