# Job-Search Agent 3: The Filter, the Tool, and the Score

**Omkar Salian (omkar-s) · INFO 7375 Fall 2026 · Chapters 7–9**

My JS2 agent collected from several boards. This layer decides **what reaches the (fictional) candidate Aarav Patel, and why**. It has three parts:

- **a filter you can read:** `FILTER.md`, versioned, written before any code, with every later rule measured;
- **the agent offered to Claude as a tool:** an MCP server written from scratch;
- **a score whose numbers are accounted for:** every number's origin, plus one change at a time measured on held-out labels.

On 2026-11-17 the agent collected **1,142 postings from 7 boards on 3 applicant-tracking systems**. Filter v1.6 keeps **7**. Every claim in their justifications is labelled supported / contradicted / insufficient against the posting text, and only **2** are *worth reading*.

> **Status (2026-11-25):** The code, runs and docs were built and run by **Claude Code** on 2026-11-17. **Omkar's parts are done.** He ran the tests and mutants himself on 2026-11-18. He labelled all 49 audit cards by hand (2026-11-18 to 2026-11-25), hand-checked 15 claims, and made the FILTER.md §6 and SCORE.md §4 decisions. He wrote the sign-off, the driver's-seat "why" column and FRICTIONAL Part 1. Answers he typed in chat were entered by Claude Code and are marked as his. The Canvas due date shown on 2026-11-25 was "Wednesday by 23:59" (2026-11-25).

**Started from:** my JS2 (`../js2-loop-tools-diff/`). Its `ats.py`, `transport.py`, `policy.py`, `rule.py` and `persona.py` are byte-identical copies in `js3/js2/`. Also my JS1 (the persona and my 20 hand labels), the **Reallocation Engine**'s greenhouse-watch scoring scheme (inherited weights), and the instructor's **Lectern** (the filter-as-a-document idea and the two-part reject audit, read as a reference; no code copied). Details: `SOURCES.md`.

## Toolchain

| | |
|---|---|
| Language | **Python 3**, standard library only. No `pip install`. Tested on **3.14.2** (python.org build, macOS); written for ≥ 3.10 |
| Claude | Claude Code CLI **2.1.292** (`claude -p`, signed in), model **claude-sonnet-5-5**, one fresh session per call. Needed only for the second rater, the experiments and the MCP-client sessions. Every result is cached, so tests and reports run without it |
| Network | HTTPS GET to `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co` only (JS2 allow-list, unchanged). No login, no keys, no POST |
| OS | macOS 15 (Darwin 24.6) |

## Commands (from a fresh clone, starting at the repository root)

```bash
cd fall-2026/omkar-s/js3-filter-tool-score   # locally: ~/Desktop/info7375-week01-video/course/fall-2026/omkar-s/js3-filter-tool-score

# tests (offline, no Claude, ~0.2 s) and the wrong versions (a control run must pass first; each mutant must be KILLED)
python3 -m unittest discover -s tests -t . -v
python3 tests/run_mutants.py

# the pipeline on the saved corpus (offline)
python3 -m js3.run_filter                 # filter in force (filter/CURRENT = v1.6) → runs/<corpus>/filter-v1.6/summary.md
python3 -m js3.shortlist                  # → shortlist/shortlist-v1.6.md + claims-v1.6.csv
python3 -m js3.audit report               # → audit/AUDIT-RESULTS.md
python3 -m js3.experiments report         # → experiments/SCORE-RESULTS.md (cached Claude answers; no new calls)

# the tool server
python3 -m js3.mcp_client probe-mine      # handshake + 15 probes, transcript in transcripts/
python3 -m js3.mcp_client probe-claude    # the other server (claude mcp serve): initialize + list only

# live (network): a new collection, then the same pipeline on it
python3 -m js3.collect                    # exit 0 complete · 3 incomplete (greenhouse:webflow is empty on purpose)

# [Omkar] the hand parts
python3 -m js3.audit label                # 49 blind cards, interactive: k / r / c / o / q
python3 -m js3.audit show                 # or one card at a time: show the next card ...
python3 -m js3.audit label --card N --verdict reject --note "why"   # ... and save one verdict
python3 -m js3.experiments fit-threshold  # after labelling: dev-only threshold fit, reported, not adopted
```

## What is in this folder

| Path | What |
|---|---|
| `FILTER.md` | **The gate.** The filter (gates, points, threshold, each with one line of reasoning and its origin), the evidence rules, the abstention rule, the expected sources, 7 wrong versions, and the change log of every rule added, cut or rejected after measuring. v1.0 frozen in `evidence/` |
| `AUDIT.md` | The reject audit: sample design, what 30 random rejects can honestly show, the second rater, 5 named false friends |
| `SHORTLIST.md` | The source-grounded shortlist explained: relevance ≠ entailment, the abstention rule, 4 counterexamples |
| `TOOL-SERVER.md` | The MCP server, real transcripts in both directions, both evaluations, both trust decisions |
| `SCORE.md` | The origin of every number, the one-change-at-a-time experiments, what persistence is not proof of |
| `js3/` | `collect` (JS2 loop rules), `textutil` + `scorer` (FILTER.md as code), `run_filter`, `shortlist`, `audit`, `mcp_server`, `mcp_client`, `experiments`, `store` (the write boundary), `redact`, and `js2/` (JS2 copies) |
| `tests/` | 72 tests; `run_mutants.py` + `mutants/wrong_versions.py` (8 mutants for WV1–WV7) |
| `filter/` | `filter-v1.0.json` … `filter-v1.6.json`; `CURRENT` names the one in force |
| `data/` | `raw/` (the exact bytes from each board, gzip, sha256 in `runs/…/sources.json`), `corpus/` (normalized postings) |
| `runs/<corpus>/filter-v*/` | `summary.md` (the measurement behind each change-log row) and `records.jsonl.gz` per version |
| `audit/` | `cards.md` (blind), `sample-key.json`, `claude-second-rater.jsonl`, `AUDIT-RESULTS.md` (generated), and **[Omkar]** `omkar-verdicts.csv` |
| `shortlist/` | the generated shortlists v1.2–v1.6 and their claim CSVs |
| `mcp/js3.mcp.json` | Claude Code config for the server |
| `transcripts/` | every tool-server session, both directions; `e5/` (20 experiment sessions); `REDACTIONS.md` |
| `prompts/judge-P1.txt`, `experiments/` | the Claude prompt; `lock.json`, `lock-2.json`, `variants/`, `runs/` (cached answers), `SCORE-RESULTS.md` |
| `labels/heldout-js1/` | Omkar's 20 JS1 hand labels, copied unchanged: the held-out set |
| `evidence/` | `FILTER-v1.0-frozen.md`, `TIMELINE.md` (order of work), `test-runs/` (saved end-to-end runs) |
| `persona/` | the fictional persona (byte-identical to JS1/JS2) |
| `SOURCES.md`, `FRICTIONAL.md` | credits and AI use; the honest log |

## What ran

All on **2026-11-17**, by **Claude Code**, from this folder. Times UTC. "Live" means the network or Claude was really called; nothing here is simulated. Constructed test fixtures are labelled CONSTRUCTED in `tests/helpers.py`.

| When | What | Result | Evidence |
|---|---|---|---|
| 06:15:27 | FILTER.md v1.0 written and frozen; no code yet | — | `evidence/TIMELINE.md` (file list), `evidence/FILTER-v1.0-frozen.md` |
| 06:16:31 | **live collection**, 8 sources | 1,142 postings; 7 ok, `greenhouse:webflow` empty → "I cannot tell"; 8 requests, 3.3 s | `data/runs/2026-11-17T06-16-31Z/sources.json` |
| 06:16–06:38 | filter v1.0 → v1.6, each measured on all 1,142 | keep 9 → 9 → 9 → 9 → 9 → 8 → 7 | `runs/…/filter-v1.*/summary.md`, FILTER.md §5 |
| 06:23:44 | audit sample drawn (v1.2, seed 7375003) | 49 blind cards: R 30, C 6, G 8, K 9 | `audit/sample-key.json` |
| 06:24:05–06:24:41 | **live** Claude second rater, 49 calls | 49 valid; agrees with the filter on 30/30 random rejects and 5/9 kept | `audit/claude-second-rater.jsonl` |
| 06:27:05 | my probe client vs my server | 15 probes as designed (traversal, unknown tool, extra args → refused) | `transcripts/client-mine-…` |
| 06:27:16 | **live Claude Code as MCP client** | tool called once, result correct; Claude's summary upgraded `kept_cannot_tell` to "Yes, it should reach Aarav" | `transcripts/claude-client-…`, `server-…-44135.jsonl` |
| 06:27:46 | **live** Claude client, injected posting | injection flagged and ignored (one trial) | `transcripts/claude-client-injection-…` |
| 06:28:01 | `claude mcp serve` probed | 28 tools, 0 with annotations; no tool called | `transcripts/client-claude-mcp-serve-…` |
| 06:33:35 | experiment batch 1 locked | — | `experiments/lock.json` |
| 06:33–06:35 | **live** batch 1: 100 Claude calls | C0b vs C0: 0 changes; E1, E2: +1 correct; E3: 3 abstentions; E4, E5: 0 changes; 0 invalid; $2.57 | `experiments/runs/`, `experiments/SCORE-RESULTS.md` |
| 06:38:27 | batch 2 locked and run (filter only) | E6, E7: 0 held-out changes; F0 under the new code identical | `experiments/lock-2.json`, `experiments/runs/filters-2.jsonl` |
| 06:45 / 06:46:23 | **end-to-end check** on a fresh copy: tests, mutants, offline pipeline vs saved outputs, MCP probe, **live** collection, **live** Claude client, edge cases | first run: 22/22 PASS, but a traceback showed `redact.py` crashing on `transcripts/e5/` while its check passed. Fixed redact and the check; second run 22/22 PASS | `evidence/test-runs/2026-11-17T06-46-23Z-…` |
| 06:47–~11:28 | **independent TA-style review** by a fresh subagent (read-only) | estimated ~61 now / ~90–93 once the [Omkar] parts are done. It found that the v1.1 count was wrong (133 → **120**), AWS 40 → 42, the test count, a stale lock line, and one overstatement. All fixed (FRICTIONAL) | FRICTIONAL Part 2 |
| 17:31:55 | **end-to-end check after the fixes** | **22/22 PASS**, 71 tests OK, 8/8 mutants KILLED, live collection 1,142 postings, Claude client called the tool | `evidence/test-runs/2026-11-17T17-31-55Z-…` |
| 2026-11-25 22:21:59 | end-to-end check after Omkar's parts were added | 21/22: the one FAIL was the live Claude step, because the `claude` CLI login had expired ("OAuth session expired"). Not a code fault | `evidence/test-runs/2026-11-25T22-21-59Z-…` |
| 2026-11-25 22:23:22 | **same check, after Omkar signed in again** | **22/22 PASS**. The fresh live collection showed Toast posting 8334794 (used since 17 Nov) is **gone from the board**. Claude, calling the tool, was told the id is not in the latest corpus, and reported that instead of guessing | `evidence/test-runs/2026-11-25T22-23-22Z-…` |

## Sign-off — Job-Search Agent 3

**[Omkar]** Written by Omkar on 2026-11-25, from a list of facts Claude Code drafted from the record, paraphrased in his own words and pasted in chat. Claude Code copied it here unchanged.

```text
Sign-off — Job-Search Agent 3
Checked:      * On 18 November, at around 15:22 EST, I ran all 71 tests. Every test passed.
              * I ran the mutation check: the control passed, and all 8 deliberately incorrect
                versions were caught.
              * I manually labelled all 49 audit cards—card 1 in the terminal and cards 2–49 in chat.
              * I found no incorrect rejections among the 30 randomly sampled rejects. Of the 9
                postings the filter kept, I would reject 5.
              * I reviewed 15 claims across the 2 strongest postings, agreeing with 13 and
                disagreeing with 2.
              * I chose to retain the 5.0 threshold, adopt neither E1 nor E2, and leave the existing
                labels unchanged.
How:          * I personally ran the test and mutation commands.
              * I assessed the cards and claims manually by reading each posting summary.
              * Claude produced the code, tests, and documentation, and entered my chat responses
                into the files.
              * I did not review the code line by line.
Not checked:  * Roughly 1,100 rejected postings beyond the 30 sampled; as many as approximately 131
                suitable jobs could still be hidden among them.
              * The individual postings affected by the v1.5/v1.6 years-rule changes; I checked
                counts only.
              * The filter's treatment of "open to picking up Python" as a requirement, which I
                disagreed with.
              * The behaviour of the other MCP server, `claude mcp serve`; I assessed only its tool list.
              * Results across other collection dates or Claude models; this covered only
                17 November's collection and one model.
              * The code itself.
Not claiming: A "keep" means a posting passed the filter and its text supports the claims made about
              it. It does not establish that the job is good or that Aarav should apply. The agent
              never submits applications, sends emails, or logs in.
Signed or withheld: Signed — Omkar Salian, 25 November 2026
```

## Driver's seat

The "What Claude should do", "What I should do" and "Evidence" columns were written by Claude Code from the record. The "Why that part stays mine" column is Omkar's own words (2026-11-25, paraphrased by him from a draft list and pasted in chat).

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **The filter** | propose rules, measure every candidate on the whole corpus, report flips, write the change-log row | confirm or change each rule (FILTER.md §6); decide E1/E2 | This is my job search, so I choose the rules. | FILTER.md §5–6 |
| **The reject audit** | draw a seeded, blind sample; compute the interval; give a second reading, kept apart | judge all 49 cards myself; say what the misses have in common | I am the person who can judge whether a rejected posting was something I wanted. | `audit/` |
| **The shortlist's claims** | label every claim against the posting and quote it; abstain when the text does not say | hand-check the claims on the postings I would act on | Before trusting a claim marked "supported," I need to read the posting myself. | SHORTLIST.md §5 |
| **The tool server** | write it, probe it, say what it declares versus does | decide whether I trust it and with what conditions; never give it a tool that acts | I set the limits on what tools can access and do. They must never act on my behalf. | TOOL-SERVER.md |
| **The score** | trace every number; change one thing at a time; report effects at noise level honestly | decide what to adopt, and whether my held-out labels need re-labelling | Adjusting a weight changes which jobs I see, so that decision belongs to me. | SCORE.md §4 |
| **Whether a posting is worth my time** | nothing beyond the evidence: even the Claude client said "Yes, it should reach Aarav" when the tool said "I cannot tell" | read the posting and decide | Claude answered "yes" when the tool said "I cannot tell." That makes my own final judgment essential. | TOOL-SERVER.md §2 |
