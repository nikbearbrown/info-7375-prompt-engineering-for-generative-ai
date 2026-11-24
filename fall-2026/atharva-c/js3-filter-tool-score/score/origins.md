# Where every number comes from

Every number used in README.md, FILTER.md and the reports has a row here.

- **Kind** says what the number is:
  - **measured**: counted by a program over saved data, reproducible with the command given;
  - **hand-set**: a value I chose, not learned or tuned by any search;
  - **hand-judged**: a count of my own labels or judgments;
  - **sample estimate**: an inference from a sample, not a rate for all postings;
  - **reported**: a value printed by a tool I did not write.
- **Commands** run from `js3-filter-tool-score/`.

## Data

| Number | Kind | Origin |
|---|---|---|
| 400 postings: robinhood 162, affirm 218, wealthfront 20 | measured | `evidence/run-20261123-185425Z/report.json`; recount with `python3 -m agent.postings` |
| 3 GET requests, 1.8 s, exit `finished` | measured | same `report.json` (`budget.used`, `exit`) |
| 0 postings missing title, location, department or text | measured | `python3 -m agent.postings` |
| Budget 5 boards / 15 requests / 60 s | hand-set (in JS2) | `budget.json`, from JS2 `GATE.md` |
| 173 postings share a board and title with another (82 groups); 91 extra copies | measured | `python3 -m score.recount`. FILTER.md v1.0 and my Nov 23 FRICTIONAL entry say "91 … share", which is wrong; corrected in FILTER.md v1.3 |
| 149 of 199 engineering-ish titles have a seniority or intern word | measured | `python3 -m score.recount` (strata A1 50, A2 149, B 201) |
| 23 `Engineer II` titles: 16 at 1.5+, 2 at 2+, 2 at 3+, 2 "no fixed minimum", 1 with none | measured | `python3 -m score.recount`; FILTER.md v1.1 changelog |

## Labels

| Number | Kind | Origin |
|---|---|---|
| 90 labeled postings, seed 2026, 45 dev / 45 held-out | hand-set design | `agent/label_sheet.py` (v2 sampler), commit `215f29a` |
| dev 6 keep / 39 reject; held-out 5 keep / 40 reject | hand-judged | `labels/dev.csv`, `labels/heldout.csv` (`215f29a`) |

## Filter rules (all hand-set, none tuned by search)

| Number | Kind | Origin |
|---|---|---|
| Threshold 0.50 | hand-set | FILTER.md v1.0 §1 (`0041401`); unchanged since |
| R1 +0.50, R3 +0.20, R4 +0.10 | hand-set | FILTER.md v1.0 §1 |
| R2: +0.30 if N ≤ 2; −0.40 if N ≥ 3 | hand-set; **N = 3 changed once** | v1.0 gave 0 at N = 3. v1.2 (`6dc9c6a`) was chosen after the dev comparison and the audit, and was not searched over other values |
| 60-character window around "experience" | hand-set | FILTER.md v1.0 §1 R2 |
| "2+ or more claims insufficient → abstain" | hand-set | FILTER.md v1.0 §2 |

## Filter results

| Number | Kind | Origin |
|---|---|---|
| v1.0 kept 22 of 400; G1 fired 295, G2 5, G3 148 | measured | `evidence/filter-v1.0/summary.txt` |
| v1.2 kept 15 of 400; 7 postings changed, all at N = 3 | measured | `evidence/filter-v1.2/summary-dev.txt`; diff of the two `decisions.jsonl` files |
| dev v1.0: tp 6, fp 6, fn 0, tn 33 | measured against hand labels | `python3 -m agent.evaluate evidence/filter-v1.0/decisions.jsonl labels/dev.csv` |
| dev v1.2: tp 6, fp 0, fn 0, tn 39 | measured against hand labels | same command with `filter-v1.2` |
| held-out v1.0: tp 5, fp 5, fn 0, tn 35; v1.2: tp 5, fp 4, fn 0, tn 36 | measured against hand labels, **run once** (Nov 24, 05:54 UTC) | `evidence/heldout/v1.0-vs-v1.2.txt` (`bdf8998`) |

## Reject audit (filter v1.0)

| Number | Kind | Origin |
|---|---|---|
| 30 rejects drawn at random from 378, seed 2026 | hand-set design | `python3 -m agent.audit_sheet evidence/filter-v1.0/decisions.jsonl` |
| 0 of 30 should have been kept | hand-judged | `audit/filter-v1.0/rejects.csv` (`c87c9b6`) |
| 95% interval 0% to 11.4%, about 0 to 43 of 378 rejects | **sample estimate** (Wilson score interval, z = 1.96) | computed from 0/30; for this run only, not for postings in general |
| 11 of 22 kept should be kept (precision 50%) | hand-judged, **all** kept postings (not a sample) | `audit/filter-v1.0/kept.csv` (`cd6bfe8`) |
| 7 of the 11 wrong keeps ask for exactly 3 years | measured | `years` column of `kept.csv` |
| 9 close calls: 8 kept, of which I judged 1 right and 7 wrong (all 7 ask for 3 years); 1 rejected (`affirm:7815952003`), which I also reject, so 0 missed keeps | hand-judged | `audit/filter-v1.0/close_calls.csv`. `affirm:7815952003` was first recorded as keep (`cd6bfe8`, a misclick) and corrected to reject on Nov 24 |
| 20 cited "N+ yrs" in reject reasons, all found in the text | measured | check run on Nov 24 (not saved) |

## Shortlist

| Number | Kind | Origin |
|---|---|---|
| 15 kept → 10 ranked, 1 "I cannot tell", 4 contradicted | measured | `python3 -m agent.shortlist` → `shortlist/shortlist.json` |

## MCP server

| Number | Kind | Origin |
|---|---|---|
| 4 tools, 0 that write | measured | `tools/list` in `evidence/mcp/scripted-transcript.jsonl` |
| Real session: 12 turns, 10 tool calls, $0.33 | **reported** by Claude Code | `evidence/mcp/claude-code-transcript.jsonl` (`result` row) |
| Server log: 13 rows for that session | measured | `evidence/mcp/claude-code-server-log.jsonl` |
| "Software Engineer I" search matches 31 titles (8 SWE I, 22 SWE II, 1 intern) | measured | `python3 -m score.recount`. The client's own answer said 23 SWE II, which is wrong |
| 50 `judge_posting` calls in 26 ms | measured once, this machine | probe on Nov 24; its log is in `out/` (not committed) |

## Tests

| Number | Kind | Origin |
|---|---|---|
| 57 tests (filter 29, shortlist 13, MCP 15), all pass | measured | `python3 -m unittest discover -s tests -t .` |
| W1–W5 each make their test class fail | measured | `python3 -m tests.wrong_versions` |
