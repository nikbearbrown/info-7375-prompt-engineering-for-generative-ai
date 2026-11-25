# How the postings to label were drawn

*Written by Claude Code on 2026-11-25, and committed with `labels/sample.json` BEFORE Shreyash typed any
verdict. The draw is `python3 -m js3 draw` (`js3/audit.py`, seed 7375); running it again on the same
`results/filter-v1/records.jsonl` gives the same file.*

Filter v1 on all 789 collected postings: **5 kept, 0 "I cannot tell", 784 rejected, 44 closest calls**
(rejects that fail exactly one rule and pass the other five).

Two sets, drawn in this order, that never overlap:

| Set | What | Why |
|---|---|---|
| **H, held-out (24)** | 3 of the 5 kept; 3 of the 6 Klaviyo closest calls that fail only experience; 8 of the 35 Palantir closest calls that fail only location; 10 rejects that are not closest calls | Used only to measure the one-change-at-a-time experiments (SCORE.md). No rule change or prompt change is designed from these labels. |
| **A1, random rejects (30)** | a uniform random sample of the 763 rejects not in H | The only part that supports a rate. |
| **A2, closest calls (15)** | the 6 closest calls outside Palantir that are not in H, and 9 of the 27 Palantir location-only ones not in H | Where misses are most likely; not random, so no rate. |
| **A3, kept (2)** | the 2 kept postings not in H | A check of what reaches Alex. |

One posting is in both A1 and A2, so Shreyash labels **70** postings, in one shuffled order. The label
tool (`python3 -m js3 label`) never shows the filter's verdict or which set a posting is in.

The other **18** Palantir closest calls are counted, not labeled: like the 17 that are labeled, they
are full-time Software Engineer postings in New York, Washington DC, Denver, Palo Alto or Seattle that
fail only the location rule, and they differ only in title and city.

What a label means: Shreyash's own answer to "Should this job reach Alex?" (yes / no / I cannot tell
from the posting), read from the posting, with an optional note.
