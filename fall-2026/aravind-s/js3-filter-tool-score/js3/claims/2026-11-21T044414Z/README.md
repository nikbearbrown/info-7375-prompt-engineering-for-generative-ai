# The shortlist's claims, filter run 2026-11-21T044414Z

Made by `tools/claims_kit.py` (Claude Code, at Aravind's request) from `js3/filter-run/2026-11-21T044414Z/`, before any human label existed. The rules for the claims, the passages and the checker are written in the tool's docstring.

- **The postings:** the 10 on the run's shortlist, shown in LABELS.md in an order shuffled with seed **2026112102**, so a posting's number says nothing about its rank or score. The sheet shows no score; the topic rows are the reason's own claims, so how many there are is visible by design.
- **The claims:** FILTER.md Section 5's list, one small statement each (Section 2: a claim with "and" in it is split in two).
- **The passages:** word for word from each posting as saved on 2026-11-20 (the board's saved answer, checked against the SHA-256 the filter run recorded): the board's own field for claims 1 to 4, every sentence that bears on claims 5 to 7 (or "none found"), and the sentence that earned the points for claim 8.
- **The checker:** a rule-based first opinion on every claim, by FILTER.md Section 2's labels. Its labels are in `sealed/checker-labels.json`, SHA-256 `c464b7a96222c0b4304f3dae8a2c2715c095b3c937e38e6244b95ad1d856bc2d`, committed with this kit before any human label. Only Aravind may mark a claim supported (Section 2); the checker's labels are a second opinion, never the answer.

| Claim | Rule | Claims |
|---|---|---:|
| 1. The posting is full time. | R1 | 10 |
| 2. It is in one of Jane's areas, or US remote. | R2 | 10 |
| 3. Its title has no level word. | R3 | 10 |
| 4. Its title names a software engineering role. | R4 | 10 |
| 5. It states no U.S.-person, clearance or no-sponsorship requirement. | R5 | 10 |
| 6. It requires no start before May 2027. | R6 | 10 |
| 7. It asks for 3 years or fewer, or makes more years optional. | R7 | 10 |
| 8. It describes work in a topic group (one claim per group that earned points). | topic words | 35 |
| total | | 105 |

## The order of the steps

1. This kit, with the sealed checker labels, is committed before any human label exists.
2. Aravind labels every claim in LABELS.md himself, first (chapter 7: label each row yourself first), and commits the sheet.
3. Only then is `sealed/checker-labels.json` opened. Its SHA-256 must still be the one above. Claude Code computes the agreement between the checker and Aravind, by claim type.
4. For each row where they disagree, Claude is asked for the sentence that would change Aravind's label, and whether it did is recorded (chapter 7).
