# SCORE.md: what moves the score (Chapter 9)

## 1. Where every number came from

"Hand-set" = someone chose it; "fitted" = computed from my labels; "inherited" = carried over from earlier work or a
default. **No number the agent uses was fitted on labels.** The threshold was *checked* by a fit (§4), and the fitted
value was not adopted. One choice (adopting v1.1) was *selected* from candidates
by looking at dev labels; that is selection, not fitting, and it was done on dev only.

| Number / object | Value | Origin | Who |
|---|---|---|---|
| ROLE weight | +4, once | hand-set | Claude drafted; I accepted (chat, 2026-11-24) |
| JOB-TYPE weight | +1, once | hand-set | same |
| SKILL weight, cap | +1 each, max 4 | hand-set | same |
| TOPIC weight, cap | +1 each, max 2 | hand-set | same |
| Threshold | 6 (of 11) | hand-set, reasoned as "= the JS2 bar: title word + 2 skills"; **fit check (§4) gave 8, not adopted** | same |
| ROLE word list | 12 words | **inherited** from my JS1 rule's title words, + "Applied AI" | JS1 me; Claude added "Applied AI" |
| SKILL list | 8 skills | **inherited** from the persona's shipped skills, minus Databricks/Unity Catalog (JS1 amendment 1) | JS1 |
| TOPIC list | 8 words (7 in v1.1) | hand-set | Claude drafted; I accepted; I cut `agents` in v1.1 |
| Gates G1–G4 word lists | — | **inherited** from JS2 amendments 1–4 | JS1/JS2 me |
| G5 (ROLE word required) | on | hand-set, before any code | I chose it after Claude showed the W3 hole |
| G6 max smallest years | 3 (v1.1) | hand-set (my C4 rule); **selected** on dev labels | me |
| Early-career years limit (C4) | 3 | hand-set | me ("min years > 3") |
| A1 minimum text | 300 characters | hand-set | Claude drafted; I accepted |
| "experience" within 80 characters after "N years"; ignore N > 20 | 80, 20 | hand-set **by Claude in code; I never reviewed it** | Claude |
| US city list (v1.1) | 18 cities | hand-set | Claude drafted; I accepted |
| Sample sizes and seed | 32/10/10/6/20, seed 7375 | hand-set | Claude drafted; I kept 78 rather than 52 |
| Claude prompt v1 / v2 | `prompts/score-v1.md`, `score-v2.md` | hand-written | Claude; v2's rules restate my FILTER.md; committed `d470281` before my labels existed |
| Text shown to Claude | first 6,000 characters | hand-set | Claude |
| Model | CLI default `claude-opus-5-5` | **inherited** setting (from each saved response's `modelUsage`) | default |
| Claude Code CLI | 2.1.331 | inherited | — |

## 2. One change at a time, measured on held-out labels

Baselines: **filter v1** for filter-file changes, **Claude B1** (prompt v1, full text + persona, no tools, default model)
for the rest. Every row changes **one** object. Held-out = 20 postings that I labeled blind, frozen before any
measurement (`tests/test_heldout.py`). The filter changes were chosen on the 58 dev labels first. Full table:
`out/score-table.md`. Raw responses: `runs/claude/<label>/`.

| Object changed | Change | Held-out, blind labels | Held-out, corrected labels | Dev, corrected (58) |
|---|---|---|---|---|
| — | always say "not" (trivial baseline) | **16/20** | 19/20 | 55/58 |
| filter file | v1 (baseline) | 10/20 | 13/20 | 41/58 |
| filter file | c1: add G6 years gate | 14/20 | 19/20 | 47/58 |
| filter file | c2: years pattern | 10/20 | 13/20 | 41/58 |
| filter file | c3: US city names | 11/20 | 14/20 | 45/58 |
| filter file | c4: cut `agents` | 10/20 | 13/20 | 43/58 |
| filter file | v1.1 = c1+c2+c3+c4 | 15/20 | 20/20 | 52/58 |
| — | Claude B1 baseline | 15/20 | 20/20 | 56/58 |
| — | Claude B2: B1 again, fresh session | 15/20 (same 20 verdicts) | 20/20 | — |
| prompt | E2: prompt v2 (explicit rules + "cannot_tell" rule) | 14/20 | 16/20 | — |
| context | E3: title + location only, no text | 10/20 | 13/20 | — |
| tool list | E4: offer `score_posting` | 15/20 | 20/20 | — |
| setting | E5: model `haiku` | 15/20 | 19/20 | — |

### What I can and cannot say from this

- **The base rate dominates.** On my blind held-out labels, "always say not" (16/20) beats every scorer. That
  includes v1.1 (15/20) and Claude (15/20). Three of my blind held-out labels were Show. v1.1 and Claude each showed
  one posting (#35), which wasn't one of those three. All three (#26, #48, #75) are ones I later corrected to Not, and I corrected #35 to Show. **With 20 labels and 3 positives, agreement can't show that any
  scorer finds good jobs.** It shows they reject bad ones.
- **The blind Shows may be inflated too.** I admitted that a couple of times while labeling I thought about picking
  Show so that "always not" wouldn't beat the filter (`AUDIT.md` §2). So neither column is clean. Blind has my
  worry in it, and corrected has Claude's questions in it.
- **The corrected column is contaminated.** 5 of the 20 held-out labels (#16, #26, #35, #48, #75) were corrected in
  chat after I had seen the filter's verdicts and Claude's questions. The 20/20 for v1.1 and Claude is partly the
  corrections agreeing with the scorers. I report it, but the blind column is the honest one.
- **The one change I'd defend is G6 (c1).** It is the only single change that moved held-out agreement on both label
  sets (blind 10 → 14, corrected 13 → 19), and it matches what the audit found: kept postings fail on years.
  Intervals overlap (v1 blind 0.30–0.70, c1 0.48–0.85), so even this is suggestive, not shown.
- **Context mattered most for Claude.** Hiding the posting text (E3) dropped Claude from 15 to 10. It then showed 5
  postings and called 3 "cannot_tell" from the title alone.
- **The prompt change made it worse.** v2 added an explicit "cannot_tell" rule, and Claude used it on 4 postings it
  had decided before (15 → 14 blind, 20 → 16 corrected).
- **Offering the tool changed nothing.** With `score_posting` available, Claude called it on only 3 of 20 postings
  (`num_turns` = 2 in the saved responses) and gave the same 20 verdicts as B1.
- **The smaller model changed one verdict.** Haiku said "cannot_tell" on #35 instead of "show". It cost about
  $0.03 for 20 postings against about $0.83 for the default model (`total_cost_usd` in the saved responses).

## 3. What persistence is not proof of

B1 and B2 ran in separate, fresh `claude -p` sessions and gave **identical** verdicts on all 20 postings. That
persistence does **not** mean anything was learned or trained. Nothing about the model changed between or after the
sessions. Both runs got the same prompt file, the same posting text and the same default model, and the same inputs
gave the same outputs.

The same goes for v1.1. Its better numbers will show up every time it runs, because the change is in
`filters/filter-v1.1.json` (see `git diff` against `filter-v1.json`), not in any model. Every behavior change in this
folder can be traced to an edit in a file: the filter, the prompt, the context code, the tool config, a CLI flag.
If a future session behaves differently, look for the file that changed before believing anything learned.

## 4. A fitted check of the threshold (`tools/fit_threshold.py`, `out/fit-threshold.json`)

I ran filter v1.1 with **only the threshold changed** (3 to 11) on the 58 dev labels and picked the one with the most
agreement (ties go to 6, then to the lower value). The held-out 20 were scored afterwards and did not choose.

| Threshold | Dev agree (blind) | Dev agree (corrected) | Kept on dev | My blind dev Shows it keeps (of 7) | Held-out agree (blind) |
|---|---|---|---|---|---|
| 3 | 49 | 48 | 11 | **5** | 15 |
| 4 | 49 | 48 | 10 | 5 | 15 |
| 5 | 48 | 49 | 7 | 3 | 14 |
| **6 (mine)** | 48 | 52 | 5 | 2 | 15 |
| 7 | 49 | 54 | 2 | 2 | 15 |
| **8 (fitted)** | **50** | **55** | **0** | **0** | 15 |
| 9–11 | 50 | 55 | 0 | 0 | 16 |

**The fit picks 8, and 8 keeps nothing.** Agreement is highest when the filter rejects everything, because most of my
labels are Not. Fitting on agreement just rediscovers "always say not". v1.1 still uses the hand-set 6 (Riya's decision on this: see below). The fit is evidence
*against* trusting agreement as the thing to optimize, not evidence for 8.

The other direction is the real trade-off. Threshold 3 keeps 11 dev postings and catches 5 of my 7 blind dev Shows;
6 catches 2. Caring more about not missing a good job than about reading fewer postings would mean lowering the threshold, not
raising it. That is a choice for Riya, and agreement can't make it. **Decision:** _pending Riya_. A better target than agreement (for example, Shows caught per posting read) is not measured here.
