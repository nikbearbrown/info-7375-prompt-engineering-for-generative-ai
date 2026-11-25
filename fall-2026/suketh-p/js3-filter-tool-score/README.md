# Job-Search Agent 3 — The Filter, the Tool, and the Score

INFO 7375 · Fall 2026 · Suketh Produtoor (`suketh-p`) · branch `js3-filter-tool-score`

JS3 has five parts:
- **The filter.** The student's written filter, FILTER.md, is turned into code and run on every posting the JS2 loop collected on 2026-11-24: 1,551 postings from Anthropic, Databricks and Linear.
- **The reject audit.** The filter is audited against **the student's own 80 hand verdicts**.
- **One change.** One rule is changed and measured **once** on 30 labels held out before any tuning.
- **The shortlist.** The top 8 postings are written up as quote-backed claims, which the student labels.
- **The tool.** The filter is offered to Claude as a **Model Context Protocol tool server written from scratch**. That server is evaluated beside the course's own teaching server.

- **The specification is the student's [FILTER.md](FILTER.md)**, committed before any code (`03485318`, 17:35 EST). Its later additions record each choice the student made and when.
- **Started from JS2:** `jobwatch/` was copied unchanged from `9c1db18` (`ef0e7057`, 37 files, blob-identical) and then extended.
- **The applicant is fictional:** Alex Morgan ([persona/alex_morgan.json](persona/alex_morgan.json)). No real résumé, contact or tracker is in this folder.

Claude Code (Claude Opus 5.5) drafted this README from the commit record. [SOURCES.md](SOURCES.md) says who wrote what.

## Status on 2026-11-25, 08:45 EST

| Part | State |
| --- | --- |
| FILTER.md v0.1, code and tests | done; 295 tests pass |
| Reject audit (the student's 80 verdicts) | done: [reports/REJECT-AUDIT.md](reports/REJECT-AUDIT.md) |
| One change, measured on held-out labels | done, once: [reports/ONE-CHANGE.md](reports/ONE-CHANGE.md). v0.2 matches 24 of 26 scored held-out rows, but the student's bar is **not met** (P53) |
| Where every number came from | [reports/NUMBERS.md](reports/NUMBERS.md) |
| Shortlist claims | done: [reports/SHORTLIST.md](reports/SHORTLIST.md). The student labelled all 64 (48 supported, 16 insufficient). Claude's challenge proposed 5 changes, and the student's decisions moved 10 labels (final 40 supported, 24 insufficient, 0 contradicted). The report includes the relevance-versus-entailment case (R4-C4) and the abstention rule with two counterexamples |
| Tool server and two evaluations | done. The student's decisions: **allow** this folder's server for one saved posting at a time in a controlled local session; **deny** the course's server as a dependency for the JS3 workflow ([evaluations/](evaluations/)) |
| Frictional entries 2–4 | done, the student's ([FRICTIONAL.md](FRICTIONAL.md)) |
| The sign-off | written by the student and **withheld** (below) |

## Language, toolchain, and what a TA needs

| | |
| --- | --- |
| Language | Python 3, standard library only (no `pip install`). Ran on Python 3.12.7 (Anaconda), macOS |
| Tests | `unittest`, **279 tests**, offline, about 7 s. 164 came over unchanged from JS2: Claude Code wrote 160 there, and the student wrote `tests/test_review_empty_board.py` (4). Claude Code wrote the 115 new JS3 tests. The cases in `StudentsWrongVersionsTest` and the exact-quote case in `test_evidence.py` are the student's own words from FILTER.md |
| Network | The agent's only requests were the corpus run's HTTPS GETs to the three boards in [jobwatch/boards.py](jobwatch/boards.py), JS2's allow-list. The `claude -p` calls in the next row went through Claude Code. Everything else reads the saved run |
| Model | `claude-opus-5-5` through the student's Claude Code login (`claude -p`, no API key), in four places: the shortlist claims, the challenge to the student's claim labels, the discrepancy leads, and the real tool-server session. Each call is saved with its date. The filter itself calls no model |

Run every command from this folder (`fall-2026/suketh-p/js3-filter-tool-score/`).

**1. The tests** (offline):

```bash
python3 -W error -m unittest -v
```

**2. Check that the saved raw bodies are byte for byte what the boards sent**, and recount them without the agent's code:

```bash
python3 -m jobwatch verify runs/2026-11-24-js3-corpus
```

```bash
python3 -I checks/independent_check.py runs/2026-11-24-js3-corpus --state-before evidence/state/before-2026-11-24-js3-corpus.json --state-after evidence/state/after-2026-11-24-js3-corpus.json
```

**3. The corpus against the student's expected sources:**

```bash
python3 -m jobwatch.js3 inventory runs/2026-11-24-js3-corpus --out corpus/INVENTORY.md
```

**4. FILTER.md v0.1 and v0.2 on every posting.** These print counts and write `audit.jsonl`, `AUDIT-VIEW.md` and `SUMMARY.md`:

```bash
python3 -m jobwatch.js3 screen runs/2026-11-24-js3-corpus --out audit/v0.1
```

```bash
python3 -m jobwatch.js3 screen runs/2026-11-24-js3-corpus --variant variants/v0.2-experience-minimum.json --out audit/v0.2
```

**5. The filter against the student's 50 development labels** (never the 30 held out):

```bash
python3 -m jobwatch.js3 audit-dev --audit audit/v0.1/audit.jsonl --sample labels/v0.1-sample.json --labels labels/hand-labels.json --out audit/v0.1
```

```bash
python3 -m jobwatch.js3 dev-effect runs/2026-11-24-js3-corpus --sample labels/v0.1-sample.json --labels labels/hand-labels.json variants/v0.2-experience-minimum.json variants/candidates/*.json
```

**6. The held-out comparison.** It ran once, at 19:43 EST. Run again into the same folder, it refuses (exit 1), because the held-out set is measured once. To re-derive the numbers, point `--out` at a new folder. That reruns the same comparison and does not choose anything:

```bash
python3 -m jobwatch.js3 held-out runs/2026-11-24-js3-corpus --sample labels/v0.1-sample.json --labels labels/hand-labels.json --variant variants/v0.2-experience-minimum.json --out /tmp/js3-held-out-check
```

**7. The shortlist's labels and evidence table** (offline). These read the student's pasted labels and apply the student's decisions on Claude's challenge:

```bash
python3 -m jobwatch.js3 claims-final shortlist/v0.1
```

**8. The tool server.** It speaks MCP over stdio. Under the scripted harness, with the audit hook that reports every file, socket and process event:

```bash
python3 -m jobwatch.mcp_client --script transcripts/scripts/jobwatch-harness.json --log transcripts/my-harness-run.jsonl -- python3 -m jobwatch.mcp_server
```

The real Claude Code session, the harness run against the course's server, and their exact commands are in [transcripts/README.md](transcripts/README.md).

**9. Live commands** (not needed to check anything; each one uses the student's Claude Code login or the network):
- `python3 -m jobwatch run --run-id <new-id>` collects a new corpus. It never writes `state/` without an approval.
- `python3 -m jobwatch.js3 draft-claims ...` asks Claude for claims, and `python3 -m jobwatch.js3 flip ...` asks Claude to challenge the labels (it refuses a folder that already has results).
- `python3 -m jobwatch.host_session ...` runs a new host session.

The exact lines are in the evidence files below.

## What ran

Times are EST, on 2026-11-24 unless marked, and each step is in the commit named.

| When | What | Who | Record |
| --- | --- | --- | --- |
| 17:35 | FILTER.md v0.1 and Frictional entry 1, then the student's answers on expected totals, the U.S. test and shortlist size | the student | `03485318`, `8dc8e89c` |
| 17:36 | **Live corpus run** with the unchanged JS2 loop: 631 / 890 / 30 postings, against the student's expected 635 / 895 / 32. It ended `incomplete` by design, with no state approval | Claude Code ran it | [evidence/terminal/2026-11-24-js3-corpus.txt](evidence/terminal/2026-11-24-js3-corpus.txt); `verify` OK and the independent check PASS in [evidence/terminal/2026-11-24-js3-corpus-checks.txt](evidence/terminal/2026-11-24-js3-corpus-checks.txt) |
| 17:41–17:43 | Tests from FILTER.md first (RED), then the filter (GREEN) | Claude Code | [evidence/test-runs/](evidence/test-runs/) 01–02 |
| 17:51 | v0.1 on all 1,551 postings: 41 kept, 1 review, 1,509 rejected | Claude Code | `ee7cf9e9`, [audit/v0.1/SUMMARY.md](audit/v0.1/SUMMARY.md) |
| 17:54 | 80-posting sample drawn (seed 20261124), and the blind labelling page | Claude Code | `5de6a6bf` |
| 17:56–17:57 | **8 live Claude calls**: 64 claims for the top 8 | Claude, through `claude -p` | `9dd1ef76`, [evidence/terminal/2026-11-24-draft-claims.txt](evidence/terminal/2026-11-24-draft-claims.txt) |
| 17:59–18:09 | Tool server, tap, harness, a **real Claude Code host session**, Claude's discrepancy leads, server 0.1.1 test-first, both evaluations | Claude Code; Claude in the session and the leads | `cc80e659` → `519e4b69` |
| ~19:13 | **The student's 80 verdicts and reasons**, pasted in chat (the page's own download at 18:51 held none) | the student | `1589c6ee`, [labels/hand-labels-as-pasted.tsv](labels/hand-labels-as-pasted.tsv) |
| ~19:30 | After the development audit, the student chose v0.2's one change, the held-out scoring, and both false friends | the student | `4fec7d70` |
| 19:39–19:42 | v0.2's experience rule and the held-out scoring, test-first | Claude Code | `92cecb57` (RED), `d9f5a96e` (GREEN), [evidence/test-runs/](evidence/test-runs/) 07–08 |
| 19:43 | v0.2 on everything (27 / 1 / 1,523), then **the one held-out run** | Claude Code ran the commands | `845c8783`, `65c132b7`, [evidence/terminal/2026-11-24-held-out.txt](evidence/terminal/2026-11-24-held-out.txt) |
| 11-25, by 08:02 | **The student's 64 claim labels**, pasted in chat: 48 supported, 16 insufficient, 0 contradicted | the student | `abca3125` |
| 11-25, 08:06–08:08 | **8 live Claude calls**: the challenge to each claim label. 5 proposed changes | Claude, through `claude -p` | `602cfa61`, [evidence/terminal/2026-11-25-flip.txt](evidence/terminal/2026-11-25-flip.txt) |
| 11-25, 08:09–08:20 | The student's decisions on the 5 proposals: 10 labels moved (final 40 / 24 / 0) | the student | `f4a08d28`, [EVIDENCE.md](shortlist/v0.1/EVIDENCE.md) |

## FILTER.md → code → test

| FILTER.md says | Code | Tests |
| --- | --- | --- |
| Role, Level, Topic in title, Topic in description, cutoff 2, ranking | [jobwatch/screen.py](jobwatch/screen.py) | [tests/test_screen.py](tests/test_screen.py); every word list and number must appear in FILTER.md ([tests/test_filter_doc.py](tests/test_filter_doc.py)) |
| U.S. location: country or state | [jobwatch/location.py](jobwatch/location.py), countries from tzdata 2026e `iso3166.tab` (copied unchanged) | `LocationTest` |
| Evidence labels; an exact quote is not enough | [jobwatch/evidence.py](jobwatch/evidence.py) | [tests/test_evidence.py](tests/test_evidence.py) |
| v0.2: "Reject when the description sets a minimum of 3+ years that is not marked preferred." | [jobwatch/experience.py](jobwatch/experience.py), switched on by [variants/v0.2-experience-minimum.json](variants/v0.2-experience-minimum.json) | [tests/test_experience.py](tests/test_experience.py), including all 1,551 v0.1 records reproduced with the rule off |
| Wrong versions: the student's WV1–WV4, Claude Code's C1–C12 | [tests/js3_wrong_versions.py](tests/js3_wrong_versions.py) | [tests/test_js3_wrong_versions_caught.py](tests/test_js3_wrong_versions_caught.py): each wrong version swapped in makes its named tests fail; **16 of 16 caught** |
| Held-out scoring, as the student chose it | [jobwatch/held_out.py](jobwatch/held_out.py) | [tests/test_held_out.py](tests/test_held_out.py) |

## The reject audit, in one paragraph

- **Random rejects:** 0 of the 30 were wrong. The exact 95% interval for the pool of 1,494 rejects is 0% to 11.6%, so that is a sample, not a rate.
- **The kept sample:** 0 of 10 were Yes. Five of the six No answers name an experience minimum stated in the description, which v0.1 never reads.
- **False friends:** both are named, "machine learning" in descriptions and "ai" in Applied AI titles.

Full report: [reports/REJECT-AUDIT.md](reports/REJECT-AUDIT.md).

## The one change, in one paragraph

- **The change:** v0.2 adds the experience-minimum rule and nothing else.
- **On held-out rows:** it removes 6 of v0.1's 8 wrong keeps, and 24 of 26 scored rows match (92%).
- **The bar is not met.** P53 states its minimum as "5+ YOE", which the rule does not read as years.
- **Nothing changed after the run.** A fix would need new held-out labels.

Full report: [reports/ONE-CHANGE.md](reports/ONE-CHANGE.md).

## The shortlist

- **The claims.** v0.1's top 8 are all Anthropic postings. Claude wrote 64 claims with exact quotes; all 49 quotes are in their postings word for word.
- **The labels.** The student labelled every claim. Claude was then asked for the sentence that would change each label. It named five, and the student changed R3-C3, R4-C4 and all eight location claims, and kept all eight work-authorization abstentions.
- **Relevance is not entailment.** R4-C4 quotes the posting exactly but drops "Former technical founders are also encouraged to apply." The student labelled it insufficient.
- **The abstention rule.** It abstains on silence. No posting is silent about sponsorship, yet sponsorship for this role stays unresolved. A phrase check would also miss "We sponsor H-1B visas for this role." (CONSTRUCTED).
- **The hand labels.** None of the five shortlisted postings that are also hand-labelled is a Yes.

Full report: [reports/SHORTLIST.md](reports/SHORTLIST.md).

## The tool server

`score_posting` is one read-only tool over the saved run (no network, no writes), in [jobwatch/mcp_server.py](jobwatch/mcp_server.py), version 0.1.1:
- **The real session.** Claude Code 2.1.291 was the host. Every message in both directions is recorded, and the answer's numbers match the served record.
- **The capability check.** The audit hook saw 49 file reads and no writes, sockets or processes.
- **The course's server.** The course's teaching server was evaluated the same way, against the same MCP 2025-11-25 pages.

[evaluations/JOBWATCH-SERVER.md](evaluations/JOBWATCH-SERVER.md) and [evaluations/COURSE-REFERENCE-SERVER.md](evaluations/COURSE-REFERENCE-SERVER.md) hold both evaluations. The allow / deny / pending decision at the end of each is the student's, and both are still blank.

## Calls Claude Code made where FILTER.md was silent

- **Scoring.**
  - "Add 2 points for … or data infrastructure" is one award per rule, not one per term (C5).
  - Board and key compare as text when ranking.
  - Review postings are ranked and can reach the shortlist.
- **Location.**
  - A blank location is unresolved, and the description is not scanned for one.
  - DC counts as a state.
  - Two-letter country codes are not read as countries, so "Toronto, CA" reads as California. That is the risk in the option the student chose.
  - U.S. territories are left out of "other countries".
- **Measuring.** "Reaches Alex" means kept or review. Can’t tell is never scored.
- **Claims.** At most 3 qualification claims per posting. Claude drafts the claims, as the film's approved plan had it.
- **v0.2's reading of a description.** This covers blocks and headings, the preferred markers, what makes a mention of years not a requirement, ranges at their lower end, and that a singular "year" never counts. It is listed in [jobwatch/experience.py](jobwatch/experience.py) and pinned by tests.
- **Held-out scoring.** The mechanical reading of "clears an unmet requirement" for the filter is in [jobwatch/held_out.py](jobwatch/held_out.py), fixed before the run.

## Known limits

- **One snapshot, one labeller.** One day of three boards, labelled by one person in one sitting. No interval here is a rate for other days or other boards.
- **v0.2 misses some minimums.** It does not read "YOE" or similar abbreviations, "up to N years", or alternatives inside one sentence. A block that calls something else preferred marks its years preferred too.
- **Topics are matched as words.** The description topic matches a phrase wherever it sits, including a nice-to-have list (the first false friend, still in v0.2).
- **Level is read only from titles,** by the student's design. A "Staff level" stated in a description is not seen (P53).
- **The page's download was empty.** The labelling page's own download at 18:51 held no labels. The student typed their verdicts outside the page, and the pasted table is the record.
- **The hook can't see everything.** The audit hook reports what these runs did on these inputs. Code can avoid audit events.

## Driver's seat

A draft by Claude Code, from the record, for the student to revise. The brief asks for "what Claude should do, what you should do, and why the judgment that a posting is worth your time stays yours."

| Part | What Claude did here, and should do | What the student did here, and should do | Why it stays the student's | Record |
| --- | --- | --- | --- | --- |
| **The filter's rules** | Asked about the gaps in v0.1, in questions; turned FILTER.md into code and tests | Wrote FILTER.md v0.1 and its four wrong versions before any code; answered the expected totals in their own words; chose the U.S. test, shortlist size and held-out design | The rules say what is worth Alex's time. "It cannot write the expected-source list without defeating it" (Ch. 7) | `03485318`, `8dc8e89c` |
| **The hand verdicts** | Drew the sample with a fixed seed; built a page that hides score, fate and group; read the pasted table without changing a word | Judged all 80 and wrote every reason | Whether a posting deserves Alex's time is the judgment being audited, so it can't come from the thing being audited | `1589c6ee` |
| **The reject audit and false friends** | Compared the filter with the development labels; found the candidate false friends and the gap; drafted the report | Named both false friends | Naming a false friend says which matches the student counts as wrong | [REJECT-AUDIT.md](reports/REJECT-AUDIT.md) |
| **The one change** | Wrote the options with their development effects; coded the chosen rule test-first; ran the held-out comparison once and reported it as it came out | Chose the change, how Can’t tell counts, and that "unmet requirement" covers both the filter and the claims | The objective and the stop rule are written first, by the person who owns the result (Ch. 9) | `4fec7d70`, `65c132b7` |
| **The shortlist claims** | Drafted the 64 claims and quotes; checked that each quote exists; looked for the sentence that would flip each label (5 found); Claude Code checked that two of those sentences are in all eight postings | Labelled all 64; decided each of the 5 proposals and applied two of them to all eight ranks; kept the eight abstentions | A quote can be exact and still not support the claim. Only a reader who has read the passage can say | `9dd1ef76` |
| **The tool server** | Wrote and tested it; recorded a real session and the harness runs; drafted both evaluations and checked Claude's leads against the spec | Decided, in their own words: allow this folder's server for one saved posting at a time in a controlled local session; deny the course's server as a dependency | Trusting a server means deciding what it may touch on the student's behalf | [evaluations/](evaluations/) |
| **The sign-off** | Listed the facts below; ran the student's three named checks again to compare results (Claude Code's run) | Wrote it and **withheld** it; then ran the three checks in their own Terminal (60 tests OK, three hashes OK, PASS) | Their name goes on it | below |

## Sign-off (the student's): withheld

**Withheld by the student on 2026-11-25.** It was pasted in chat (arrived by 08:41 EST) and is reproduced verbatim:

```text
Sign-off · Job-Search Agent 3
Checked:      My runs matched all three saved response hashes, independently recounted 1,551 postings, confirmed unchanged state, and passed 60 targeted tests.
How:          I used the recorded outputs and made the four decisions on the claim challenge. I drafted FILTER.md and the initial posting and claim labels myself. My own Terminal rerun is pending.
Not checked:  A fresh independently labeled benchmark, a corpus from a different day, or a live host session using jobwatch-js3 0.1.1.
Not claiming: Corpus-wide accuracy, MCP conformance, or that v0.2 met my stop rule. P53 still reached the shortlist.
Signed or withheld: Withheld · Suketh Reddy Produtoor · 2026-11-25
```

The student's reason, in Frictional entry 4: "I’m withholding sign-off while I reproduce the Terminal checks and document my work in SOURCES.md."

### The three checks the student names

The student wrote: "I ran these from the JS3 project folder. Use the same commands for my own Terminal record." Their commands and reported results:

| Check | Command | The student's reported result |
| --- | --- | --- |
| Targeted tests | `python3 -B -W error -m unittest -v tests.test_filter_doc tests.test_experience tests.test_evidence tests.test_claim_labels tests.test_mcp_server` | "60 passed" |
| Saved response integrity | `python3 -B -m jobwatch verify runs/2026-11-24-js3-corpus` | "All three SHA-256 hashes matched the trace" |
| Independent recount and state check | `python3 -I -B checks/independent_check.py runs/2026-11-24-js3-corpus --state-before evidence/state/before-2026-11-24-js3-corpus.json --state-after evidence/state/after-2026-11-24-js3-corpus.json` | "631 Anthropic, 890 Databricks, 30 Linear. The state snapshots matched byte for byte." |

The third command was pasted on three lines without line-continuation backslashes. It is shown here on one line, which is how it runs.

- **Claude Code's run, not the student's.** Claude Code ran the same three commands on `7e4ae241` (2026-11-25, 13:43Z) and got the results the student reports: 60 tests OK, three hashes OK, and PASS with 631 / 890 / 30 jobs and "state file unchanged between the two copies" ([evidence/terminal/2026-11-25-the-students-three-checks-run-by-claude-code.txt](evidence/terminal/2026-11-25-the-students-three-checks-run-by-claude-code.txt)).
- **The student's own run (added later, 2026-11-25, about 08:51 EST).** The student ran the three commands in their own Terminal, from this folder, and pasted the output: 60 tests OK, three hashes OK, and PASS with 631 / 890 / 30 and the state unchanged ([evidence/terminal/2026-11-25-the-students-three-checks-run-by-student.txt](evidence/terminal/2026-11-25-the-students-three-checks-run-by-student.txt)).
- **Their first attempt failed.** It was run from the home folder and found none of the modules ([the first attempt](evidence/terminal/2026-11-25-the-students-three-checks-first-attempt-from-home-folder.txt)).
- **The sign-off above predates that run.** It was written before the run and is unchanged until the student revises it.


### The facts Claude Code listed for it

- **The student's own checks so far:** the 80 verdicts, the 64 claim labels, the four decisions on Claude's challenge, their choices in FILTER.md, naming the false friends, the two trust decisions, and the three Terminal checks above, run in their own Terminal (output committed).
- **Claude Code's tests and checks:**
  - 279 tests, offline.
  - 16 wrong versions swapped in and caught.
  - `verify` and the independent check on the corpus run.
  - v0.1's 1,551 records reproduced with the rule off.
  - The held-out comparison, run once.
  - The audit hook on both servers.
  - Claude's 24 leads checked against source and the MCP pages.
- **Not checked (candidates):**
  - The student's labels against a second labeller.
  - Postings on other days or boards.
  - "YOE" and other abbreviations of years.
  - Whether a Can’t tell posting should reach Alex.
  - A second reviewer challenging a supported claim (Chapter 7 suggests one).
  - Repeat runs of the claims and challenge prompts.
  - A tool server under a client other than Claude Code 2.1.291 and the harness.
  - Python versions other than 3.12.7.
- **Not claiming (candidates):**
  - That 0 of 30 is a rate for all rejects.
  - That 24 of 26 is a rate for all postings.
  - That v0.2 meets the student's bar (it does not).
  - That "no write was seen" means a server cannot write.
  - That any behaviour that persists across sessions shows that anything was trained.

```text
Sign-off — Job-Search Agent 3
Checked:      which properties, by which of my own tests (name them)
How:          by hand / by a test I wrote before reading Claude's code /
              by recomputation / with Claude's help (say which parts)
Not checked:  at least three real items
Not claiming: what this agent does not show
Signed or withheld: ____________ (name, date)
```
