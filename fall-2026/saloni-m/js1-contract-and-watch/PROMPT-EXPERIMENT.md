# Prompt experiment (Chapter 2)

## Setup, in the order it happened (2026-11-01)

1. **Postings.** `scripts/pick_postings.py` (seed 7375) took 20 real postings from the run-1 raw
   response: 10 the rule calls relevant and 10 "engineer" titles the rule calls not_relevant.
   A second seeded shuffle split them 10 dev / 10 held-out. List: `labels/experiment_set.json`.
2. **Labeling rule, written first.** `labels/LABELING-RULE.md`, drafted with Claude and committed
   in JS1-4, before any label existed.
3. **Hand labels.** Saloni labelled all 20 with `scripts/label.py` (14:22:30–14:24:59 local,
   in `labels/hand_labels.csv`) before any Claude verdict existed. 15 were labelled relevant,
   5 not_relevant.
4. **Baseline on dev.** `prompts/v1_baseline.md`, 1 fresh call per posting.
5. **One change.** After reading the dev results, `prompts/v2_years_soft.md` was written. It is v1
   plus one paragraph: *treat a stated years-of-experience number as a soft preference, not a
   cutoff (up to about 5 years for a non-senior role).* Committed in JS1-6 (`eef1786`) before
   any held-out call.
6. **v2 on dev, then v1 and v2 on held-out**, once each, with no further changes.

A rejected or errored call counts as a miss. There were none (0/40).

## Results (recompute: `python3 scripts/score.py experiment`)

| split | judge | agrees with hand label |
|---|---|---|
| dev | rule (record) | 7/10 |
| dev | Claude v1 baseline (judgment) | 4/10 |
| dev | Claude v2 years-soft (judgment) | 5/10 |
| held-out | rule (record) | 8/10 |
| held-out | Claude v1 baseline (judgment) | 2/10 |
| held-out | Claude v2 years-soft (judgment) | 3/10 |

What v2 changed: on dev it flipped one posting ("Applied AI Engineer, Startups", which asks for 4+
years) to relevant. On held-out it flipped one ("Applied AI Engineer, Enterprise", also 4+ years)
to relevant. Both flips were in the direction of the hand label. Every other verdict was the same
under both prompts. Per-posting verdicts are in `results/experiment/scores.md`.

## Why the judges disagree: the labels, not only the prompt

Claude's misses are not random. All 14 v1 misses were the same kind: Claude said not_relevant, the
hand label said relevant. In every one, Claude's stated reason maps to a criterion that
`labels/LABELING-RULE.md` itself names as disqualifying. (This mapping was done by reading the
14 reasons in `results/experiment/calls.jsonl`; it is a reading, not a computed result.)

- **Customer-facing or pre-sales** (rule point 1): all 5 "Applied AI Architect" postings, plus
  Startups and Lab Automation.
- **IT or security operations** (rule point 1): IT Operations, IT Systems (macOS), Security
  Engineer – Threat Intel.
- **Research, or a stack she lacks** (points 1–2): Research Engineer – Pretraining (JAX/TPU
  pretraining), Security Data Engineer (hardware chain-of-custody data systems).
- **Far more years than "roughly 3"** (point 2): Software Engineer – Labs (8+), Applied AI
  Engineer – Enterprise (4+), and most of the Architects (5+).

The hand labels look closer to "relevant unless the title is senior/staff", which is roughly what
the code rule computes. That would explain why the title-only rule scores 7/10 and 8/10. The
labels took about 7.5 seconds each on average (timestamps in the CSV), probably too fast to read
the requirements sections. So these numbers mostly measure **agreement with a fast,
title-driven label**, not whether the prompt finds jobs worth Priya's time. I did not relabel after
seeing Claude's answers. Doing that would make the held-out set no longer held out.

## Honest limits

- **Ten cases per split.** One posting is 10 points. v2's +1 on dev and +1 on held-out is one
  posting each time. An exact (Clopper–Pearson) 95% interval on 3/10 is about 7%–65%. This does not show v2 is
  better. It shows the years-of-experience instruction can flip a borderline 4+-year posting.
- **One call per posting per prompt.** The sampling report suggests verdicts are stable for this
  prompt, but only on 5 postings, and none of them were held-out ones.
- **The held-out set was not perfectly blind.** Its titles were printed in the build session
  when the set was picked. Its hand labels and rule scores were also printed (by `score.py`)
  before v2 was written. No *Claude* output on held-out existed until v2 was frozen, but the
  person and model writing v2 could have seen which held-out postings were labelled relevant.
- The 20 postings are stratified (half rule-relevant), not representative of the board, where
  56/674 titles are rule-relevant.
