# What moves the score: origin of every number, and one change measured on held-out labels

Written 2026-11-25 with Claude's help (SOURCES.md). The measured results and counts are recomputable from the files named.
The wording is a draft for Vrajesh to rewrite.

## 1. Where every number in the scorer came from

There are no fitted weights and nothing was trained. The scorer is a filter of rules, a claim labeler, and a prompt.

| Number or object | Where it is | Origin |
|---|---|---|
| 3 years (R2 and `early_career`) | `rule.py`, `claims.py` | **Inherited** from JS1 CONTRACT R2 (new-grad target); hand-set, never tuned |
| Seniority words (senior, sr, staff, principal, lead, manager, head, director) | `rule.py` | **Inherited** from JS1/JS2, hand-set |
| R1 role phrases | `rule.py` | Vrajesh's list (2026-11-25) plus JS2's words; `/ API` added after audit item 60 (**hand-set, then changed after measuring**) |
| ML exclusion, AI engineer kept | `rule.py` | **Hand-set** decision, Vrajesh 2026-11-25 |
| R4 sponsorship wording | `rule.py` | JS1 wording **inherited**; widened after the audit (items 6, 15), measured on all 3,068 postings: 0 matches before, 14 after |
| R5 clearance wording | `rule.py` | **Hand-set** (Vrajesh's rule); widened after the audit (item 18), moves 1 posting |
| `cannot_tell` conditions (no location, no description) | `rule.py` | **Hand-set** decision, Vrajesh 2026-11-25 |
| Spelled-out numbers one..ten, context windows (60 and 25 characters) | `claims.py` | **Hand-set**, never tuned |
| `stack_fit` counts only technologies from the persona's shipped project | `claims.py` | **Fitted by hand on Vrajesh's labels** (claim-check items 5, 18, 22, 23, 24); the 24 items are not independent evidence it works |
| Seeds 7375, 7376, 7377; sample sizes 35 + 12 + 15, 24, 20 | `scripts/` | **Hand-set**; sizes chosen for the effort of hand labelling, not for statistical power |
| 95% Wilson intervals (z = 1.96) | this report | The textbook convention |
| Claude model `claude-sonnet-5-5`, `--max-turns 4`, no temperature set | `scripts/onechange.py` | **Setting**; model **inherited** from JS1 |
| The prompt in `onechange.py` | `scripts/onechange.py` | **Hand-written**, drafted with Claude |

## 2. The one change

- **Object changed:** the tool result Claude reads (one of the five objects: filter file, prompt, context, tool list, setting).
- **Change:** add each claim's `statement` (what the claim asserts) next to its label and quote. Variant A is the result as Claude Code
  first read it; variant B adds `statement`. Nothing else differs: same filter, labeler, model, prompt, and a fresh `claude -p`
  process for every call, so no session carries memory into the next.
- **Why this change:** Claude, reading a real result on 2026-11-25, said the `early_career` quote "seems to cut against the
  label" because the result never said what the claim was (EVAL-earlybird-score.md, defect 5).
- **Held out:** 20 (posting, claim) pairs drawn with seed 7377 from the 55 shortlisted postings that were in none of the earlier
  samples (audit sheet, claim-check sheet), and drawn and committed (`55a0bae`) before any Claude output existed. The filter and
  labeler were not tuned on them.
- **Ran:** 40 calls on 2026-11-25, 0 errors, 3 at a time, A and B interleaved. Outputs: `results/onechange-outputs.json`.
- **Judged:** Vrajesh labelled each sentence accurate or misleading with the variant hidden (`review/onechange-labels.csv`,
  committed `a116952` before the key was opened).

## 3. Result

| | misleading | accurate | 95% interval for misleading |
|---|---|---|---|
| A (no statement) | 3 of 20 | 17 | 5% to 36% |
| B (with statement) | 0 of 20 | 20 | 0% to 16% |

Paired: 17 pairs both accurate; 3 pairs A misleading and B accurate (pairs 2, 6, 15); no pair where B was worse. All three were on claims
the labeler had marked **supported**; on the 14 **insufficient** pairs both variants were always accurate. The two-sided sign test on
3 against 0 gives p = 0.25.

**What this shows:** in this sample, adding the statement never hurt and the three differences all went its way. **What it does not
show:** that B is better in general. Twenty pairs and three differences cannot separate a real effect from luck (p = 0.25). The
intervals overlap. This is a sample estimate, not a rate for all postings.

## 4. What weakens it
- **No repeat run.** Each variant ran once per pair. I did not run A against A, so Claude's own run-to-run variation is unmeasured.
  Some of the three differences could be that.
- **Imperfect blinding.** B's sentences sometimes repeat the claim's wording, which can reveal the variant to the judge.
- **One judge**, and the notes name the same distinctions the rule uses, so agreement is partly shared framing.
- **Narrow claims:** all three differences came from `early_career` (2) and `stack_fit` (1). The sample has few `ai_focus` and
  `us_location` pairs.

## 5. What a changed behaviour across sessions is not proof of
Claude answered differently in A and B across separate sessions. That does **not** mean anything was trained, learned or
remembered. Each call was a new process with no memory; the only difference between the two sets of calls is the text in the tool
result. A behaviour that "persists" across sessions because the same text is supplied each time is the text, not a changed model. Equally,
a behaviour that does *not* persist is not evidence that nothing is stored anywhere: I did not inspect the model.

## 6. Decision on the change
**Decision (Vrajesh, 2026-11-25): make variant B the default.** The server now includes each claim's statement unless
`EARLYBIRD_INCLUDE_STATEMENT=0` (variant A). The evidence for B is weak (3 differences against 0, p = 0.25, section 3); the switch
is kept so the measurement can be repeated. Vrajesh's reasons, in his words: "I chose B because including the claim statement makes the label easier to interpret. All three observed differences favored B, but the small sample and p = 0.25 make this a provisional choice based on clearer wording, not proof of better performance."
