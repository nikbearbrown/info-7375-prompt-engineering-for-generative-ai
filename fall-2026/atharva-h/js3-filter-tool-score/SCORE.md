# SCORE — what moves the score

**Status: Claude's draft from `measure.py` and `measure_changes.py` output. Waiting for my review. The decisions in "What I change" are mine, not yet made.**

## Where every number comes from
Each number below is produced by a script and saved in a file, or was set by hand and says so. Nothing in this table is estimated.

| Number | Value | Origin |
|---|---|---|
| Postings in the corpus | 4,240 (4,102 v1.0 + 138 supplement) | `python3 corpus.py`, reading `runs/2026-11-20T131355Z_corpus` and `runs/2026-11-25T175647Z_supplement_v1_1` |
| Boards | 12 + 2 | The v1.0 rule over a 116-board probe (`probe/2026-11-18_board_probe.json`); the v1.1 rule over a 196-board probe (`probe/2026-11-25_board_probe_v1_1.json`) |
| Threshold | 4 | **Set by hand** in FILTER.md v1.0, from my interview answers. Never tuned. |
| Weights: role phrase +4, bare "analyst" +1, each skill +1 | as stated | **Set by hand** in FILTER.md v1.0, so that a role phrase alone reaches 4 |
| R2's cut-off: reject when the lowest stated years ≥ 3 | 3 | Riley's `max_required_years: 2` (JS1 `persona/resume.json`) |
| Kept by v1.0 | 12 of 4,240 | `python3 filter.py run` → `state/filter/verdicts_v1.0.json` |
| Labels | 114 (92 v1.0 + 22 supplement); 112 "no", 2 "yes" | Claude drafted each; I reviewed every one (`reviewed` column, 2026-11-25). `state/labels/labels*.csv` |
| Split | 77 tuning, 37 held-out | `labels.py`, seed 20261120, each stratum split 2:1 (`state/labels/split*.json`) |
| Held-out precision and recall of v1.0 | 2/2 and 2/2 | `python3 measure.py` → `state/measure/v1.0_labels.txt` |
| Every change's numbers below | as shown | `python3 measure_changes.py` → `state/measure/changes.txt` and `changes.json`. The run before F5 was added is kept as `changes_before_F5.*`. |
| Claim counts, quotes found, coverage | as shown | `python3 claims.py check VARIANT` → `state/claims/VARIANT_checked.csv` and `_answers.json`. The claims are written by `claude -p` (Claude Code 2.1.331; the recorded model is `claude-opus-5-5`). |
| Audit error rates: kept 10/10 wrong, random rejects 0/30, near threshold 0/10 | as stated | My verdicts in `state/audit/audit_v1.0.csv` (judged by me, 2026-11-25); `python3 audit.py report` → `state/audit/report_v1.0.txt` |
| Collection budget: 15 boards, 35 requests, 180 s; 5 MB write approval | as stated | FILTER.md v1.0; the 5 MB is JS2's GATE.md, carried over |

## How to read the measurements
- **One change at a time:** each row below changes one thing against the same baseline, v1.0 with the base prompt. Changes are never stacked.
- **Held-out decides. Tuning is shown, marked, and never used to choose.**
- **The held-out set is small:** 37 labels with only 2 "yes", both from FanDuel. A held-out difference smaller than one posting can't be seen. "No change on held-out" means the held-out labels can't tell, not that the change does nothing.
- **Claude is not deterministic.** The base prompt was run twice with nothing changed (C0 and C0'). A Claude change whose effect is no bigger than the difference between those two runs is not shown to do anything.

## Filter changes
Precision and recall of "keep", with the counts behind them.

| Change | Held-out precision | Held-out recall | Tuning precision (not used) | Verdicts changed, whole corpus | Which postings flip |
|---|---|---|---|---|---|
| F0 v1.0 baseline | 2/2 | 2/2 | 0/7 | — | — |
| F1 a filter word: R4 also matches "does not provide sponsorship" | 2/2 | 2/2 | 0/6 | 1 | Veeva ADP data analyst, now rejected |
| F2 the threshold: 4 → 5 | 2/2 | 2/2 | 0/5 | 3 | FP&A Analyst R&D; both FanDuel Product Analysts, now rejected |
| F3 a rule boundary: R2 rejects at 2+ years | 1/1 | **1/2** | 0/4 | 7 | Includes **FanDuel "Analyst", a held-out "yes"**, now rejected because its "2+ years ... preferred" counts |
| F4 a rule reading: R2 reads the highest of the stated requirements | 2/2 | 2/2 | 0/7 | 1 | Zoox Financial Analyst ("6+ years ... 2+ years"), now rejected |
| F5 a filter word: "reporting" doesn't count before "to" | 2/2 | 2/2 | 0/7 | 1 | Datadog FP&A Analyst R&D ("Reporting to the Senior Manager"), now rejected. This is the false friend from my audit (#27). |

**What the held-out labels show:**
- **F3 is the only change they can see, and it lowers recall.**
- **F1, F2, F4, and F5 make no held-out difference.**
- **Tuning favours F2 and F3, which fix the most false keeps.** On held-out, F3 loses a real match. That is the over-fitting the held-out split exists to catch.

## Claude changes
The filter stays v1.0, so these act only on the 12 kept postings.
- **Coverage** is answered ÷ kept, where an answer is "keep" rather than "I cannot tell". **Accuracy** is on the answered postings only.
- Held-out has 2 kept postings, both "yes".

| Change | Held-out coverage | Held-out accuracy | Tuning coverage (not used) | Tuning accuracy (not used) | Quotes found by the checker |
|---|---|---|---|---|---|
| C0 base prompt | 0/2 | undefined | 3/7 | 0/3 | 46/48 |
| C0' the base prompt again, no change | 0/2 | undefined | 3/7 | 0/3 | 45/46 |
| C1 wording: "copy the quote exactly" removed | 1/2 | 1/1 | 3/7 | 0/3 | 44/48 |
| C2 context: title and locations only | 0/2 | undefined | 2/7 | 0/2 | 20/20 |
| C3 wording: "never include the field names in a quote" added | 0/2 | undefined | 4/7 | 0/4 | 46/46 |
| A1 abstention rule: abstain on role or location only, not seniority (base claims) | 1/2 | 1/1 | 6/7 | **0/6** | 46/48 |

**What these show:**
- **C1's held-out gain is noise, not the wording.** It comes from one posting, FanDuel "Analyst":
  - **In C0,** its location quote began with "Locations:" and the checker refused it, so the agent said "I cannot tell".
  - **In C1,** the location quote happened to be clean, and seniority was "contradicted", which doesn't force an abstention.
  - **In C0', the same prompt as C0,** the location was clean but seniority came back "insufficient", so the agent abstained again.

  The same prompt gives different answers, and the "gain" is that variation.
- **C3 fixed what it targeted:** all 46 quotes were found, against 46/48 in C0. In C0, two location quotes began with "Locations:", the prompt's own field name, so the checker correctly refused them. It didn't change held-out coverage.
- **C2, the title-only context,** produced 20 quoted claims instead of 48. The rest became "insufficient", so it answers less.
- **A1 shows what the seniority clause is doing.** Dropping it answers 6 of 7 tuning postings, and all 6 answers are wrong. The claims don't cover why those postings are a "no": a graduation date, part-time work, a 2-year minimum, a sponsorship line R4 doesn't know. Fewer abstentions would mean more confident wrong answers.

## Persistence is not training
- **What is saved:** labels, verdicts, claims, and transcripts are saved to disk (`state/`). FILTER.md keeps every version.
- **What that does not do:** none of it changes Claude. The model that wrote the C0 claims is the same model that wrote C0'. Saving their output taught it nothing, and the difference between the two runs is ordinary variation.
- **Where every improvement on this page comes from:** a rule, a number, or a prompt sentence that I wrote and versioned, measured against labels that I made.
- **What "the agent learned" would mean here:** a FILTER.md version changed. It does not mean a model was trained.

## What I change (my decisions, not yet made)
Claude's recommendation, for me to accept or reject:
- **F1, adopt.** Veeva's line is a stated refusal to sponsor, which is exactly what R4 exists for. Held-out can't see it, but the reason is the rule's own, not a score.
- **F4, adopt.** It fixes a misreading of R2 in the v1.0 code, not a new rule. FILTER.md's reason talks about one range ("1-3 years" passes). It never meant that a second, lower requirement cancels a higher one.
- **F5, adopt.** It is the false friend FILTER.md predicted and my audit found (#27). The fix is narrow: one word, before "to".
- **F2 and F3, reject.** F3 is shown to lose a held-out match. F2 has only tuning evidence.
- **A1, reject.** It trades abstentions for confident wrong answers on tuning.
- **C1 and C2, reject.**
- **C3, adopt as the prompt for v1.2.** It removes a checker failure caused by the prompt itself.
