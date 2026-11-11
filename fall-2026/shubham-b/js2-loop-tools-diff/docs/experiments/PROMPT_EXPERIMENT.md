# Chapter 2: Prompt experiment

**Question.** How often does Claude's first reply under the prompt contract agree with my hand labels, and does changing exactly one section of the prompt (`label_definition`, v1 → v2) change that?

**Procedure.** [`experiments/prompt/PROCEDURE.md`](../../experiments/prompt/PROCEDURE.md). Pre-registered v2 candidates, my choice and why: [`prompts/CHANGELOG.md`](../../prompts/CHANGELOG.md). Prompts: [`prompts/judge.v1.md`](../../prompts/judge.v1.md), [`prompts/judge.v2.md`](../../prompts/judge.v2.md).

**Order, each step committed before the next (git is the timeline).**

| Step | Commit | When (ET) |
|---|---|---|
| Select 20 postings (seed 20261029): 10 dev, 10 held-out | `af4777c` | 2026-10-29 22:22 |
| My 20 hand labels and `SEAL.json`, before any model call | `14e51f9` | 2026-10-31 14:21 |
| v1 on dev | `f1717e2` | 2026-10-31 14:22 |
| My v2 choice, `judge.v2.md`, `FREEZE.json`, before any v2 call | `c2e5599` | 2026-10-31 14:31 |
| v2 on dev, v1 on held-out, v2 on held-out | `27be4a3`, `a7f1852`, `d066c76` | 2026-10-31 |
| Score (strata revealed) | `ed2c64c` | 2026-10-31 |

```bash
uv run jsa exp prompt select
uv run jsa exp prompt seal
uv run jsa exp prompt run --prompt v1 --set dev
uv run jsa exp prompt freeze
uv run jsa exp prompt run --prompt v2 --set dev
uv run jsa exp prompt run --prompt v1 --set heldout
uv run jsa exp prompt run --prompt v2 --set heldout
uv run jsa exp prompt score
```

**Labels.** [`experiments/prompt/labels/dev.labels.json`](../../experiments/prompt/labels/dev.labels.json), [`heldout.labels.json`](../../experiments/prompt/labels/heldout.labels.json). I personally decided each of the 20 labels by applying the `CONTRACT.md` §6 criteria (§16) to the postings. Claude did not choose, generate, or adjudicate any label; it only formatted my already-made decisions and notes as JSON. See `SOURCES.md`.

**Raw evidence.** Every call's argv, raw stdout, session ID, cost and validation result: `data/experiments/prompt/results/<cell>/calls/<posting>/attempt-1.json`. Seal: `data/experiments/prompt/SEAL.json`. Freeze: `data/experiments/prompt/FREEZE.json`. Metrics: `data/experiments/prompt/metrics.json`. Generated tables: `data/experiments/prompt/PROMPT_EXPERIMENT.tables.md` (re-running `score` regenerates that file without my sections; this document keeps them).

## Results

Changed section (v1 to v2): `label_definition`. First reply only; no retries. Format acceptance is the validator pass rate, not accuracy. Brackets are Wilson 95% intervals.

| Cell | Format acceptance | Agreement (invalid = disagree) | Agreement among valid | Evidence entries valid | Replies with a bad path |
|---|---|---|---|---|---|
| v1-dev | 10/10 [0.72, 1.00] | 7/10 [0.40, 0.89] | 7/10 [0.40, 0.89] | 49/49 | 0 |
| v2-dev | 10/10 [0.72, 1.00] | 10/10 [0.72, 1.00] | 10/10 [0.72, 1.00] | 41/41 | 0 |
| v1-heldout | 10/10 [0.72, 1.00] | 6/10 [0.31, 0.83] | 6/10 [0.31, 0.83] | 45/45 | 0 |
| v2-heldout | 10/10 [0.72, 1.00] | 10/10 [0.72, 1.00] | 10/10 [0.72, 1.00] | 47/47 | 0 |

## Confusion matrices (rows: hand label; columns: Claude)

### v1-dev

| hand \ Claude | MATCH | NO_MATCH | INVALID |
|---|---|---|---|
| MATCH | 1 | 3 | 0 |
| NO_MATCH | 0 | 6 | 0 |

### v2-dev

| hand \ Claude | MATCH | NO_MATCH | INVALID |
|---|---|---|---|
| MATCH | 4 | 0 | 0 |
| NO_MATCH | 0 | 6 | 0 |

### v1-heldout

| hand \ Claude | MATCH | NO_MATCH | INVALID |
|---|---|---|---|
| MATCH | 0 | 4 | 0 |
| NO_MATCH | 0 | 6 | 0 |

### v2-heldout

| hand \ Claude | MATCH | NO_MATCH | INVALID |
|---|---|---|---|
| MATCH | 4 | 0 | 0 |
| NO_MATCH | 0 | 6 | 0 |

## v1 vs v2 discordant postings

- dev: 8197135 (M; v1 NO_MATCH, v2 MATCH), 8197891 (M; v1 NO_MATCH, v2 MATCH), 8198280 (M; v1 NO_MATCH, v2 MATCH)
- heldout: 8039548 (M; v1 NO_MATCH, v2 MATCH), 8206731 (M; v1 NO_MATCH, v2 MATCH), 8267736 (M; v1 NO_MATCH, v2 MATCH), 8332676 (M; v1 NO_MATCH, v2 MATCH)

## Rule vs hand audit

- dev: none
- heldout: none

## Limits

- n = 10 per cell: one posting moves a rate by 10 points.
- One call per cell ignores the sampling variance measured in the sampling report.
- Both sets come from one board on one day.
- The stratified mix is not the board's base rate.
- **Held-out exposure in the pre-freeze v2 draft:** My initial v2 draft contained examples drawn from held-out postings. Claude flagged this during the pre-freeze review, and at my direction those examples were replaced with the full `CONTRACT.md` §6 lists before `FREEZE.json` and before any v2 calls. The frozen v2 prompt therefore did not retain those examples, but the earlier draft exposure remains a limitation of the experiment process: held-out material had already informed the draft before the correction. The corrected freeze does not erase that exposure.

## Rule-vs-hand decisions (labeling slip or rule bug)

No decisions were needed: my hand labels and the coded rule agreed on all 20 postings (`10/10` on `dev`, `10/10` on `heldout`), with zero labeling slips or rule bugs to adjudicate.

## Conclusion

### Pass rates and what changed from `v1` to `v2`
- **First-reply format acceptance (validator pass rate):** All 40 first replies across the four cells passed the §8 validator (`10/10 [0.72, 1.00]` in `v1-dev`, `v2-dev`, `v1-heldout`, and `v2-heldout`), with zero retries and zero invalid JSON paths.
- **Agreement with hand labels:**
  - On `dev`, agreement rose from **`7/10 [0.40, 0.89]`** under `v1` to **`10/10 [0.72, 1.00]`** under `v2`.
  - On `heldout` (touched once after `FREEZE.json`), agreement rose from **`6/10 [0.31, 0.83]`** under `v1` to **`10/10 [0.72, 1.00]`** under `v2`.
- **Pattern of discordance:** Every single `v1` miss across the entire study—3 on `dev` (`8197135`, `8197891`, `8198280`) and all 4 `MATCH` postings on `heldout` (`8206731`, `8332676`, `8039548`, `8267736`)—was a Stratum `M` (`MATCH`) posting that `v1` rejected as `NOT_RELEVANT` (`v1` called 0 of the 10 held-out postings `RELEVANT`). Replacing `label_definition` with the four-gate rule in `v2` flipped all 7 `MATCH` postings from `NO_MATCH` to `MATCH` without introducing any false positives on the 12 `NO_MATCH` postings.

### What `10/10` under `v2` actually means (and the two-judge tradeoff)
1. **Turning Claude into a second copy of the rule removes independent judgment:** Achieving `10/10` on both sets shows that `claude-sonnet-5-5` can follow the written four-gate specification when it is spelled out in `label_definition`. However, doing so turns the model into a slower, ~$0.02/call duplicate of the deterministic Python rule rather than an independent second judge. `CONTRACT.md` ("What this agent does" and §2) explicitly notes that the title filter misses unmarked senior roles and keeps the rule verdict separate from Claude's qualitative opinion for that exact reason. Under `v1`, rejecting roles that demand 5+ or 6+ years of experience (`8197135`, `8197891`, `8198280`, `8206731`), native Mandarin fluency (`8039548`), or shipped Go/Terraform/Ansible (`8267736`) was arguably the more useful substantive judgment for an early-career candidate like Kiran—which is why the production pipeline keeps `judge.v1` as its separate opinion while the deterministic rule handles the literal four-gate filter.
2. **Hand labels were my decisions, not AI decisions:** I decided each of the 20 labels myself by applying the `CONTRACT.md §6` criteria to each posting before the model calls. Claude only formatted those decisions and notes as JSON; it did not label the postings. The `20/20` rule-vs-hand audit therefore shows that my application of the written criteria matched the coded rule (`CONTRACT.md §16`). It does not establish agreement with an independent recruiter's judgment of job fit.

### How little `n = 10` cases per cell can show
- **10 percentage points per posting and overlapping 95% Wilson intervals:** With `n = 10` per cell, a single posting shifts a pass rate by 10 percentage points. Even a `10/10` result has a 95% Wilson score interval of **`[0.72, 1.00]`**, which still overlaps `v1-dev`'s `7/10 [0.40, 0.89]` and `v1-heldout`'s `6/10 [0.31, 0.83]`. Observing `10/10` on 10 postings cannot rule out a true disagreement rate of up to ~28%.
- **One call per cell ignores sampling variance:** Each cell makes only one first-reply call per posting. Chapter 1 showed that boundary postings can split across fresh sessions (`8234357` split `3/1`) and that `19/20` calls cited different evidence-path sets, so a single draw per cell leaves run-to-run variance unmeasured.
- **Pre-freeze held-out exposure in the v2 draft:** The initial v2 draft included examples from held-out postings. Claude identified the issue before freeze; at my direction, the examples were replaced with the complete `CONTRACT.md` §6 lists before `FREEZE.json` and before v2 calls. This correction reduced exposure in the frozen prompt but cannot undo the fact that held-out examples had appeared in the earlier draft.
- **Stratified quotas (`40%` `MATCH`) vs. board base rate (~`2.2%` `MATCH`):** Both sets were stratified to include 4 `M` postings out of 10 (`40%`). On the full 734-posting Stripe board from October 29, 2026, only ~16 postings are `MATCH` (~`2.2%`). Because `v1` only disagreed with the rule on `M` postings, a 40%-`MATCH` sample magnifies the `v1`-vs-`v2` gap roughly 18-fold compared to unstratified board traffic (such as our Day-2 live run, where all 21 new postings were `NO_MATCH` and `v1` agreed `21/21` times).
