# The changes to measure on the held-out set, fixed before its answers were opened

Written by Claude Code on 2026-11-22 (about 4 AM ET), before `js3/heldout/2026-11-21T044414Z/sealed/answers.json` was
opened, from the audit (development data), the claim labels and FILTER-CHANGES-PENDING.md alone. Each change is one
change to one object, measured once against Aravind's 30 frozen held-out verdicts (commit `1e2b1e1`). The predictions
are written now, so the results can prove them wrong. One held-out record was already seen: while checking the cards
for hidden status lines, Claude Code saw that held-out card 11's posting fails R5 ("U.S. citizen").

## What is measured in each run

1. **Fate agreement**, as the held-out kit fixed it: the run's kept against his Keep, rejected against Reject, on the
   27 cards he did not mark "?", for each pool on its own (15 drawn from the run's kept postings, 15 from its rejects),
   with the exact one-sided 95% bound on the disagreements.
2. **Cutoff agreement** (secondary): a posting counts as recommended when the run keeps it and it scores at or above the
   cutoff; recommended is compared with his Keep.
3. Which cards change against v1.0, and the same changes over the whole run of 1,509 postings (development data, for
   scale only).

Every run is kept, including runs that change nothing. Cost: no model is called, so every run costs $0 at API prices.

## The runs

| Run | Object | The change | Why (development evidence) | Prediction | Whose call to adopt it |
|---|---|---|---|---|---|
| R0 | none | FILTER.md v1.0 as committed | the baseline | none | |
| R0b | none | v1.0 again, the same input | shows the noise | identical to R0, card for card: the filter has no randomness and calls no model | |
| X1 | the filter file (Section 6, item 1) | the splitter keeps "U.S.", "e.g." and "i.e." inside a sentence | audit card 17: the cut hid "U.S. Person Required" from its card, and R5's quote fell back to the bare phrase | no fate changes: R5 reads the whole text; only sentence-based rules (R6, R7, topics) could move, and rarely | Claude Code's (an implementation choice) |
| X2 | the filter file (Section 6, item 3) | drop growth, revenue and customers from R7's company words | 77 fires on the whole run, every one a real requirement; audit card 34 | no fate changes: every posting where these words fired was already rejected by another rule; R7 becomes a failed rule on some of them | Claude Code's (an implementation choice) |
| X3 | the filter file (Section 1, topic words) | drop "build systems" from the Developer tools group | claim 09.8c: "build systems that consume ... signals" is a verb and a noun, and gave a kept posting 5 points | no fate changes (topic words only score); a few scores fall by 5, which can move a posting below the cutoff | Aravind's (Section 1 is his) |
| X4 | a setting (the ranking) | an export-control caution costs 10 points | audit cards 31 and 35: both kept at 55, and both "?" in his verdicts over that line | no fate changes (a penalty only scores); kept postings with the caution lose 10 points, so fewer are recommended | Aravind's (R5 is his) |
| X5 | a setting (the ranking) | shortlist cutoff 55 instead of 60 | audit: he kept every kept posting he judged, at 50, 55 and 60 alike (`ORIGINS.md`) | no fate changes; more of his Keeps are recommended, so cutoff agreement rises | Aravind's (the cutoff is his) |
| X6 | a setting (the ranking) | shortlist cutoff 50, so every kept posting qualifies and the score only orders | the same audit evidence | no fate changes; cutoff agreement rises further, to the fate agreement | Aravind's |

## Not measured, and why

- FILTER-CHANGES-PENDING.md items 2 (a season wholly before the earliest start rejects) and 4 (any US location that says
  remote is US remote): neither fired on any of the 1,509 postings, so no run on this data can show an effect. They go
  into v1.1 as fixes to the written rules, checked by unit tests.
- Items 3, 5 and 6 (`years_max` as a person fact, where dates come from, a posting with no id and the order of the
  rules) change wording, not behavior.
- The shortlist's wording for claims 5 to 7 ("the posting does not say", `ABSTENTION.md`) changes what a reason claims,
  not any fate or score.
- A prompt, context or tool-list change: the v1.0 score calls no model. A tool-list change through the MCP server would
  need live Claude Code calls on Aravind's seat; it is left out of this round.
