# Sign-off - Job-Search Agent 3

## Checked: which properties, by which of my own tests (named)
Everything runs with `python -m unittest discover -s tests` (51 tests: 4 + 27 + 20).

| Property | Test or evidence |
|---|---|
| The filter does what FILTER.md v2 says on 27 constructed postings (role words, ML excluded, Senior/Staff, 3+ years, clearance, sponsorship, non-US, `cannot_tell`) | `tests/test_filter.py` `RealFilter.test_every_case`, cases in `tests/cases.py` |
| Each plausible-but-wrong filter fails the tests: W1 no seniority rule, W2 "training" as a topic word, W3 clearance ignored | `WrongFiltersAreCaught` (two tests), `tests/wrong_filters.py` |
| Claims are labelled supported / contradicted / insufficient with a quote, silence is never support, false friends do not match ("go-to-market", "executive sponsorship", "JavaScript" is not Java) | `tests/test_claims.py`: `EarlyCareer`, `Sponsorship`, `Clearance`, `Location`, `StackFit`, `AiFocus`, `EveryClaimHasEvidenceOrAReason` |
| The MCP server answers the handshake, lists exactly one read-only tool, refuses bad input, path traversal and extra arguments, returns the same verdicts as the filter run, logs both directions, and refuses `connect`, `connect_ex` and `create_connection` | `tests/test_mcp.py`: `Handshake`, `ToolList`, `CallTool`, `Protocol`, `Log`, `NetworkGuard`, `ResultVariant` |
| The reject audit numbers (0 of 35 random rejects wrong; 1 of 12 close calls; 3 of 15 kept wrong, 2 unsure) | `python scripts/audit_summary.py` against my labels (`review/audit-labels.csv`); `review/AUDIT.md` |
| The claim labeler agrees with my labels on 21 of 24 items, 23 of 24 after one fix | `review/claim-check-labels.csv`, `review/claim-check-key.json` |
| Adding the claim statement to the tool result: 3 misleading of 20 without, 0 of 20 with (p = 0.25) | `REPORT-one-change.md`, `review/onechange-labels.csv` |
| The official fetch server's guards (private addresses, allowlist, robots.txt, redirects) work as declared; the prompt skips robots.txt | `evaluations/EVAL-fetch-server.md`, `evaluations/fetch-server/` |

## How
"Claude wrote the implementation, tests and drafts and ran the commands; I reviewed the outputs, made the decisions, and wrote the labels."

- **By hand (my words):** "I also judged the postings and wrote all three label files: audit-labels.csv, claim-check-labels.csv, and onechange-labels.csv. The claim-check and one-change labels were saved before their keys were opened." The decisions on the role list, ML, abstention, `stack_fit`, option lists and variant B are also mine.
- **By recomputation:** the audit numbers, claim-label counts and filter counts are recomputed by scripts (`scripts/audit_summary.py`, `run_filter.py`, `make_shortlist.py`); Claude ran them and I reviewed the outputs.
- **With Claude's help:** all code and tests, the blind sheets and keys, the numbers, both server evaluations, the experiment runs (40 Claude calls), and the drafts of every document. See SOURCES.md.
- **By a test I wrote before reading Claude's code:** none: Claude wrote the tests, before the code each time (red outputs `review/1-` ... `19-`).

## Not checked
1. `cannot_tell` never fired on a real posting; it is tested on constructed postings only.
2. The v2 filter changes were tuned on the audit sample and have no held-out measurement; 12 of the 14 postings that R4 v2 moved are unlabelled.
3. R3's country inference for Greenhouse postings and R5 rejects were barely sampled (2 and 0 in the random reject sample).
4. The fetch server's default `npm install` path was read in source and never run; its 47 dependencies, most of `server.py`, and packet-level traffic were not examined.
5. No A-against-A repeat of the one-change experiment, so Claude's run-to-run variation is unknown; only 20 pairs.
6. The claim labeler still counts "At least 1 year of university education" as support for "fewer than 3 years of experience".
7. "U.S. Person Required" (3 Palantir postings) is not handled by R4 or R5; "clearance is a plus" is still rejected.
8. JS2's loop, policy and fetch code is in the folder but untested in JS3; no live board and no real resume were used.
9. A valid but very large request to my MCP server, and many requests in a row: the server has no input-size limit or rate limit, and only a malformed 5 MB line was tried (`evaluations/EVAL-earlybird-score.md`, defect 3).

## Not claiming
"This does not demonstrate reliable job eligibility, guaranteed sponsorship, accurate labels for every posting, secure handling of real resumes, or a general improvement from B. It also does not demonstrate model training or learning: the experiment changed the tool-result text."

## Why I sign
"I read the blind sheets, judged and saved 24 claim labels and 40 sentence judgments, and verified all three label files had complete rows and valid labels. I kept both keys unopened and checked the source posting for pair 11’s missing quotation."

"I would not sign without reviewing the final diff, the 51-test run, and the documented limitations, with approval explicitly limited to the fictional persona and local snapshot.

The “Not checked” item that worries me most is a valid, very large request. The server has no input-size limit, so a client could exhaust memory. Passing ordinary requests and malformed-input tests does not establish that it handles this case safely."

## Driver's seat (draft table, for Vrajesh to edit)
| Claude should | I should | Why the judgment that a posting is worth my time stays mine |
|---|---|---|
| read postings, apply the written filter, quote the text behind every claim, and say "I cannot tell" when the text is silent | decide the filter: which roles, what counts as senior, what blocks me (sponsorship, clearance, "U.S. Person") | what counts as worth my time depends on my goals, visa situation and risk tolerance, which are not in any posting |
| write the code and tests, show the red and green runs, and report limits and failures plainly | choose what to change (R4/R5/R1, `stack_fit`, variant B), read the evidence, and reject suggestions that do not fit | the numbers describe samples, not all postings; deciding that a sample is enough is a judgment, not a measurement |
| build blind sheets and compute counts and intervals | label the samples and say when my own labels are inconsistent | the labels are the reference the rest is measured against, so they must be mine |
| run the tool server and evaluate it, including its own mistakes | decide whether to trust a server (mine and the fetch server) and with which settings | trust depends on what I am willing to risk with my data, and I own that |
| list unresolved items (clearance wording, "U.S. Person", the weak p-value) | decide whether they block a posting or the submission | Claude cannot know my tolerance for a missed or a wasted application |

## Signed or withheld
**Signed or withheld:** (Vrajesh Mathurbhai Nasit, 11/25/2026)
