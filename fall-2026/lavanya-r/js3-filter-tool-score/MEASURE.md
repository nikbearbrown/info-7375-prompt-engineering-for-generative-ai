# MEASURE.md — what moves the score (Chapter 9)

My scorer has two parts:
- **The filter score** (FILTER.md v1.1): hard rejects, then points, then a threshold.
- **A Claude judge** (`score/claude_score.py`): asked whether a posting is worth Priya's time, given a prompt and a context.

This file covers three things: where every number came from, what changed when exactly one object changed, and what persistence does not prove.

## 1. Where every number came from

| Number | Value | Where it came from |
|---|---|---|
| S1 points for a role word in the title | 3 | **hand-set**: Claude proposed the 3/1/1 structure, and I accepted it from options (FILTER.md §1b). Not fitted. |
| S2 points per topic word, and its cap | 1 each, max 3 | **hand-set**, same way |
| S3 points per résumé skill, and its cap | 1 each, max 3 | **hand-set**. The skill list is **inherited** from my JS1 rule (`agent/rule.py`), which got it from the fictional résumé. |
| Threshold | 5 | **hand-set**: I chose it from 4/5/6 after seeing how many postings each kept (236/115/48). After the audit, 4 was measured on my audit labels and **rejected** (X1, AUDIT.md §4). The audit informed the choice, but no value was fitted. |
| R5 years of experience | reject at ≥ 3 (`max_years_asked` 2) | **hand-set**, chosen from options after seeing the counts |
| R5 cap on N | ignore N ≥ 20 | **hand-set by Claude** to skip "founded 25 years ago". Not something I chose; recorded here. |
| "Cannot tell" text length | 200 characters | **hand-set by Claude** (FILTER.md §1c / §2 E1, accepted by me) |
| Seniority, role, topic words and the US city list | FILTER.md §1 | **hand-set**. The seniority words are **inherited** from JS1 (plus "Head of"). The city list was hand-set by Claude from the cities seen in this corpus. |
| R4 sponsorship phrases (10) | — | **inherited** from JS1 |
| Claude judge prompt | `score/prompts/score-v1.md`, `score-v2.md` | **hand-written by Claude** for this measurement. Not tuned on any labels. |
| Claude judge context | `score/context/persona-summary.md` | **hand-written by Claude** from the fictional résumé |
| Model | `sonnet` (reported as `claude-sonnet-5-5`) | **a setting**: the alias Claude Code resolves |
| Text sent to Claude | first 6,000 characters | **hand-set by Claude**, to bound cost |

**Nothing in the scorer was fitted to labels.** The only measurements that shaped it are the four one-change comparisons in AUDIT.md §4, made on my audit labels (groups A–C).

## 2. One change at a time, on held-out labels

**Labels:** group H, which `audit/draw.py` drew before any verdict. It is 15 postings kept by v1.0 and 15 below the threshold. I judged 21 of the 30 (9 have no verdict), and these were never used to choose a rule. All 21 are y/n (14 y, 7 n).

**Setup:**
- Every experiment changes exactly one object from its baseline. All five Claude experiments were defined in `score/experiments.json` and committed (`0b7f903`) before any call.
- Claude was called through `claude -p` (Claude Code 2.1.312) on 2026-11-24, from a temporary folder outside this repo, with tools disabled (`--tools ""`) and no saved session.
- Every raw reply is in `score/runs/<experiment>/`: 105 calls, 0 unparseable. The CLI reported `total_cost_usd` 1.46 in total, on my NEU login; I did not check what is actually billed.

### 2a. The filter file (FILTER.md v1.0 → v1.1), scored by the filter alone

`python3 -B audit/measure.py --heldout` → `logs/js3-04-measure-heldout.txt`

| Filter | Wrong of 21 | kept but I said n | rejected but I said y |
|---|---|---|---|
| v1.0 | 9 | 3 | 6 |
| v1.1 (X4, the Canada fix) | 9 | 3 | 6 |

**Changing the filter file from v1.0 to v1.1 moved nothing on the held-out labels.** That is expected: the change fixes a wrong reason that touched no verdict.

The same log also scores the variants I had **rejected** on the audit labels. **X3** (R5 uses the largest years asked) would have been wrong on **7 of 21** instead of 9 here. I chose on the audit labels, where X3 changed nothing (AUDIT.md §4). One caveat: Claude had already seen v1.0's held-out mistakes when it recommended rejecting X3 (AUDIT.md §4, Disclosure). Adopting X3 now would mean choosing on the held-out labels, and then they would no longer be held out. So I did not change v1.1. X3 is the first thing to re-test on a fresh held-out set.

### 2b. The Claude judge: prompt, context and setting, one at a time

`python3 -B score/claude_score.py --report` → `logs/js3-05-claude-report.txt`

| Exp | The one change (vs E0a) | Agree with me | Disagree | cannot_tell | Verdicts changed vs E0a |
|---|---|---|---|---|---|
| E0a | baseline: prompt v1, persona summary, `sonnet` | 8 | 13 | 0 | — |
| E0b | **nothing** (same inputs, new session): the noise floor | 7 | 13 | 1 | **1** |
| E1 | the **prompt**: v1 → v2 (an explicit decision order, with "cannot_tell" when the posting doesn't say) | 10 | 7 | 4 | **6** |
| E2 | the **context**: persona summary → the full fictional résumé JSON | 8 | 12 | 1 | **1** |
| E3 | a **setting**: model `sonnet` → `haiku` (reported `claude-haiku-5-5`) | 7 | 14 | 0 | **1** |

**What moved the score:**
- **Only the prompt moved it beyond the noise floor.** Re-running the same inputs changed 1 verdict out of 21. The context and model changes also changed 1 each, the same as doing nothing. The prompt change moved 6.
- **The Claude judge is much stricter than I am.** In E0a it said "no" to **13 of the 14** postings I marked y, and "no" to all 7 I marked n. Its reasons (`score/runs/E0a/`) fall into three groups:
  - **seniority or "significant experience" wording**;
  - **skills Priya hasn't shipped**: Kotlin, kernel security, chip design;
  - **eligibility rules that neither my filter nor the short summaries I judged from showed me**: a required US security clearance; internships for current students; and a fellowship restricted to graduates of French Grandes Écoles (sheet item 7, which I marked y).

  So a "disagreement" does not always mean Claude is wrong. Some of my y verdicts were made without facts that the full posting states. The prompt v2 change moved it toward "cannot_tell" (4) and "yes" (3).
- **What 21 labels can and can't show.** A difference of 1–2 verdicts out of 21 is not distinguishable from the noise floor. "E1 agrees more (10 vs 8)" fits a real improvement, and it also fits luck plus the 4 abstentions. I am not claiming the prompt v2 judge is better, only that the prompt moved the score and the other two changes did not.
- **The tool list was not changed.** Every call had tools disabled. Giving the judge my `search_postings` tool is an untested fifth object.

## 3. What persistence is not proof of

- **Repeating isn't learning.** E0a and E0b ran in separate, unsaved sessions and gave the same verdict on 20 of 21 postings. That is the same inputs going to the same model, not memory, and not anything learned from E0a.
- **A change that stays isn't training.** If prompt v2's behaviour shows up again in a new session tomorrow, it's because `score/prompts/score-v2.md` is sent on every call. No weights changed: each reply reports the same model name, and nothing in this folder can train a model.
- **Files can carry behaviour between sessions, and that still isn't training.** A behaviour can "persist" across sessions through files the tool loads by itself. Run inside this repo, `claude -p` would load the repo's `CLAUDE.md` / `AGENTS.md` as context. That is a hidden context change that looks like the model "remembering" a rule. I avoided it by calling Claude from a folder outside the repo. I did not run the comparison inside the repo, so its effect is **not measured**.
- **This report doesn't measure stability over time.** The model behind the `sonnet` alias can change upstream. A different result next month would not mean my experiments trained anything, and the same result would not mean nothing changed.
