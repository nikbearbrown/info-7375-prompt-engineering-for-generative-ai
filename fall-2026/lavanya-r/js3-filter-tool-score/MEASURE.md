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

**Labels:** group H, which `audit/draw.py` drew before any verdict. It is 15 postings kept by v1.0 and 15 below the threshold. I judged 21 of the 30 (9 have no verdict), and these were never used to choose a rule. Of the 21, 20 are y/n and 1 is "?".

RESULTS_PLACEHOLDER
