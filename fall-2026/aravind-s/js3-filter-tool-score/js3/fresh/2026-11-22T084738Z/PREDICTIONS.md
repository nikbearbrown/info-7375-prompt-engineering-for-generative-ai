# Predictions and how each outcome is read (written before any verdict)

Written by Claude Code on 2026-11-24 with the kit, before Aravind judged any card. `tools/score_fresh.py` checks the predictions with the same numbers (they are constants in `tools/fresh_kit.py`). A "?" is counted on its own, never as a mistake, as in every other set.

## A, the cutoff of 50 (12 cards)

v1.1 recommends every A posting and v1.0 recommends none. A Keep is a card where v1.1's recommendation agrees with Aravind and v1.0's does not; a Reject is the reverse. The cutoff call holds on this set if his Keeps outnumber his Rejects. The bound reported is the exact one-sided 95% upper bound on v1.1's disagreements among the A cards he judged.

Prediction: Keep on at least 9 of the 12 A cards (in the audit and the held-out set he kept every kept posting he judged). Held: at least that many. Partly: more Keeps than Rejects, but fewer. Not held: no more Keeps than Rejects.

## B, the export-control penalty (3 cards)

v1.1 holds every B posting back from the shortlist; without the penalty they would be recommended. A Keep disagrees with the penalty. A Reject agrees with holding it back (and disagrees with the filter's keep). A ? says the card does not settle it, which is what a caution is for: the posting stays kept for a person to check, not recommended outright.

Prediction: ? on at least 2 of the 3 B cards (he marked all three export-control cards of the held-out set ?). Held: at least 2. Partly: one. Not held: none.

## C and D, the controls (3 and 2 cards)

Both versions agree on these. A Reject on a C card or a Keep on a D card is a disagreement both versions share; it says nothing for or against v1.1's calls. Prediction: Keep on every C card and Reject on every D card. Held: all of them. Partly: all but one. Not held: more than one off.

## "build systems"

No card tests this call (README.md says why).

## After the result

If a result here leads to a change of FILTER.md, this set becomes development data from that date, and that is written in a CHANGES.md here. Anything Aravind says about a card after the answers are opened goes in AFTER-REVEAL.md and is reported beside the frozen result, never in place of it.
