# Changes to this held-out kit

## 2026-11-22: cards rebuilt, before any verdict

The audit (`js3/audit/2026-11-21T044414Z/AFTER-REVEAL.md`) found that the filter's sentence splitter cuts a line at
"U.S.", which hid "U.S. Person Required" from audit card 17. `tools/audit_kit.py` now keeps "U.S.", "e.g." and "i.e."
inside their lines on cards and shows every line R5's phrases match. CARDS.md here was rebuilt with the same seed: the
sample, the card order and `sealed/answers.json` are byte for byte the same (SHA-256 in README.md, which the rebuild
also reproduces unchanged). Six cards changed, all in their status lines: card 11 had shown none and now shows its
U.S.-citizen requirement; cards 03, 07, 10, 22 and 29 now show whole sentences where the old cards had cut them at
"U.S.". No verdict existed yet: VERDICTS.md was still blank.

## 2026-11-22: verdicts entered

Aravind judged the 30 rebuilt cards in chat on 2026-11-22 (compact cards: every fact line, with the description cut to its first 32 words; the full cards stayed in CARDS.md) and sent his verdicts in one message, recorded at 2:48 AM ET. Claude Code entered them in VERDICTS.md with his verdict letters unchanged; his reasons were already one line each. His message is kept word for word outside the repo. `sealed/answers.json` was not opened, and it stays sealed until the list of v1.1 changes is fixed from the audit alone, so that this set measures those changes once (chapter 9).

## 2026-11-22: answers opened for the pre-registered experiments

`tools/heldout_experiments.py` opened `sealed/answers.json` at 2026-11-22T083619Z (UTC), after the list of changes was committed (`1c9a37e`), and measured each run once (`js3/score/EXPERIMENTS.md`). If a result here leads to adopting a change, this set is development data from then on, and a later claim about a change needs a new held-out set.

## 2026-11-22: this set is development data from now on

After seeing the measurement, Aravind made three calls for FILTER.md v1.1 (cutoff 50, an export-control line costs 10 points, "build systems" dropped; `5dff01f`). Since those choices used this set's results, the set has guided a change: any later claim about a change needs a new held-out set.
