# Job-Search Agent 3 — The Filter, the Tool, and the Score

**Lavanya R** · INFO 7375 · Fall 2026 · Chapters 7–9.

**What it does.** My agent already collects postings from several boards (JS1, JS2). JS3 adds three things:
- **a filter you can read:** FILTER.md, versioned, with a reason for every rule;
- **a source-grounded shortlist:** every claim is labelled against the posting's own text;
- **the agent as a tool for Claude:** an MCP tool server written from scratch.

It also measures what moves the score, one change at a time.

**Persona.** The agent uses the fictional persona Priya Nair (`persona/priya-nair.resume.json`), not a real résumé. It never applies, emails, messages or logs in.

**What I started from:**
- my own **JS2 folder** (`../js2-loop-tools-diff`), copied unchanged in `6f14d20`: the loop, policy, providers, independent check and tests;
- **my JS1 rule** (`agent/rule.py`), whose words, matcher, skill list and sponsorship phrases FILTER.md builds on;
- the JS2 board endpoints, which came from the instructor's **Lectern** `sources.json`.

I did not use the Reallocation Engine's scorer, or Lectern's filter or code.

**Read in this order:**
1. [FILTER.md](FILTER.md): the gate, v1.0 written before the filter code, then v1.1.
2. [AUDIT.md](AUDIT.md): the reject audit.
3. [SHORTLIST.md](SHORTLIST.md).
4. [TOOLSERVER.md](TOOLSERVER.md).
5. [MEASURE.md](MEASURE.md).
6. The sign-off and driver's seat below.
7. [SOURCES.md](SOURCES.md) and [FRICTIONAL.md](FRICTIONAL.md).

## Language and toolchain

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.11.5, **standard library only** (no `pip install`) | everything |
| git | 2.50.1 | the commit history these documents cite |
| Network | `boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com` (https GET only, JS2's allow-list) | the live collection only; the tests and everything else are offline |
| Claude Code CLI | 2.1.312 (NEU login) | only to re-run the Claude calls (`score/`, `agent/shortlist.py`) and the `claude mcp serve` probe. Their saved replies are committed, so the reports re-compute without it. |
| OS | macOS 26.5 | — |

## Commands (from a fresh clone)

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/lavanya-r/js3-filter-tool-score
```

Run every command from this folder.

**1. Tests: 150, offline, and nothing in the folder changes**
```bash
python3 -B -m unittest discover -s tests -t . -v
```

**2. The corpus is the one the reports used**
```bash
shasum -a 256 -c CORPUS.sha256
```

**3. Run the filter (FILTER.md v1.1) on all 3,117 postings.** It rewrites `out/filter/v1.1/`.
```bash
python3 -B -m agent.run_filter
```

**4. The audit: re-measure the variants on my hand verdicts, then print every verdict**
```bash
python3 -B audit/measure.py
```
```bash
python3 -B audit/measure.py --heldout
```
```bash
python3 -B audit/tables.py
```

**5. The shortlist: re-check every saved Claude label against the posting text (no Claude call)**
```bash
python3 -B -m agent.shortlist --table
```

**6. What moves the score: the report from the saved replies (no Claude call)**
```bash
python3 -B score/claude_score.py --report
```

**7. The tool server: my client against my server.** It writes a transcript into `transcripts/`.
```bash
python3 -B mcp/client.py --out transcripts/01-scripted-client-own-server.jsonl
```

**8. Claude Code as the client** (needs the Claude Code CLI)
```bash
claude -p "Use the search_postings tool to find postings mentioning MLflow on greenhouse/databricks, limit 5, and list their titles." --mcp-config mcp/claude-mcp-config.json --strict-mcp-config --allowedTools mcp__js3-postings__search_postings
```

**9. A live collection.** This uses the network and adds a folder under `runs/`. It is the JS2 loop, with JS3's six boards in `config/boards.json`.
```bash
python3 -B -m agent.loop
```

## What ran (all real, 2026-11-24, ET)

| When | What | Result | Evidence |
|---|---|---|---|
| 17:04 | **Live collection 1**: the JS2 loop on 6 boards | 3,117 postings, but Greenhouse sent **no job text** | `runs/2026-11-24T220407Z-live/` |
| 17:04 | Greenhouse URL given `?content=true`; **live collection 2** = the corpus | 3,117 postings, all with text except 1 (Zoox). `check.py` 9/9. Hashes frozen. | `runs/2026-11-24T220432Z-live/`, `CORPUS.sha256`, `8d0122c` |
| 17:08 | My MCP server: my scripted client, then a **Claude Code 2.1.312 session** as client | handshake, tools/list, calls; Claude's answer matched the tool result | `transcripts/01`, `02`, `309c996` |
| ~22:59 | **FILTER.md v1.0**, before any filter code | — | `75b2de8` |
| 23:00–23:01 | Filter tests (26), then the filter code. **First run** | 115 kept, 3,002 rejected, 0 cannot tell. Tests unchanged. | `a40e9bb`, `2c1b967`, `out/filter/v1.0/` |
| 23:02 | Seed committed, **then** the draw: 30 random rejects, 10 closest calls, 10 kept, 30 held out | blind sheet of 80 | `450e2f0`, `efe0296` |
| 23:05–23:14 | **My hand verdicts**, in 8 batches | 71 of 80 (9 held-out items not judged) | `audit/hand_verdicts.jsonl` |
| 23:20 | Audit measured; **FILTER.md v1.1** (X4 adopted; X1–X3 rejected) | random rejects 0 of 29 wrong; closest calls 4 of 10; kept 2 of 10 | `AUDIT.md`, `logs/js3-01`, `b5230a4` |
| 23:21–23:25 | **Claude Code's own MCP server** (`claude mcp serve`) probed: tools/list and 2 Read calls | 29 tools, no annotations; Read left the folder | `transcripts/03`, `04` |
| 23:25 | Adversarial probes against my server | all refused or handled | `transcripts/05` |
| 23:37–23:39 | **105 Claude scoring calls**: 5 one-change experiments × 21 held-out postings | only the prompt moved the score beyond the noise floor | `score/runs/`, `logs/js3-05`, `MEASURE.md` |
| 23:38–23:39 | **10 Claude labelling calls**, 113 claims, then the quote check | 72 supported, 3 contradicted, 38 insufficient (after fixing the checker's prefix bug) | `out/shortlist/`, `logs/js3-06`, `SHORTLIST.md` |

**Seeded vs live.**
- **Live:** both collections, and every Claude call (saved verbatim with its start time).
- **Constructed:** every posting in `tests/` is constructed for its test and labelled as such in the file.
- **Simulations:** there are none.

**Estimates, not rates.** Any rate in AUDIT.md is a sample estimate with its interval. It is not a measured rate for all postings.

## Sign-off — Job-Search Agent 3

**Checked:**
- **The filter does what FILTER.md says:** `tests/test_filter.py` (27). This includes the config-equals-FILTER.md checks, every hard rule, the score parts and threshold, "cannot tell", the real Sales-Platform posting rejected by R5 only, and the Canada false friend.
- **The wrong versions are caught:**
  - W1–W4 and W6 in `test_filter.TestWrongVersions`;
  - W5 in `test_evidence.test_w5_word_present_but_no_quote_is_not_supported`.
- **The reject audit:** 30 random rejects judged by me, blind to the filter, drawn with a seed committed before the draw. 0 of 29 wrong, with an honest interval of 0–11.7% (AUDIT.md §2). Also 4 of 10 closest calls and 2 of 10 kept were wrong.
- **The false friends:**
  - "Ontario, CA" read as California (found in the audit, fixed in v1.1, test `test_r3_canada_ca_is_not_california`);
  - the Databricks footer, which gives every Databricks posting "agents", "Databricks" and "Unity Catalog" (found in the shortlist, measured, recorded but not fixed).
- **Every shortlist claim is labelled,** and every quote is found verbatim in its posting: `agent/evidence.py` plus 11 tests. I hand-checked 3 labels: I agreed with 2 and disagreed with 1 (SHORTLIST.md §4).
- **My tool server does what it declares:** `tests/test_mcp_server.py` (13), my adversarial probes (`transcripts/05`), and a real Claude Code session (`transcripts/02`).
- **What moves the score:** five one-change experiments on 21 held-out labels, with a measured noise floor (MEASURE.md §2).

**How:**
- **By hand:**
  - all 71 hand verdicts, blind to the filter;
  - the choice of every FILTER.md rule and reason, picked from options Claude offered;
  - the decisions on X1–X4 and on the footer, following Claude's recommendations;
  - both trust decisions;
  - the 3 label checks.
- **By a test written before the code it tests:** `tests/test_filter.py` (`a40e9bb`, before `agent/filter.py`) and `tests/test_evidence.py` (`873ccd3`, before `agent/evidence.py`). **Claude wrote both test files, not me.** They came before Claude's code, but I didn't write them.
- **By recomputation:**
  - `audit/measure.py` and `audit/tables.py` recompute the audit from committed files;
  - `agent/shortlist.py --table` re-checks every saved label;
  - `score/claude_score.py --report` recomputes the experiments from saved replies;
  - JS2's `check.py` independently recounted the corpus (9/9).
- **With Claude's help:** Claude Code wrote all of the code, tests and first drafts of every document. It ran every command, made every Claude call, proposed every option and recommendation I chose from, and found both false friends.

**Not checked:**
1. **The Databricks footer is not fixed.** Every Databricks posting gets free points from its "About Databricks" paragraph. Removing it changes 6 verdicts in the corpus, none of them in my hand verdicts, so its effect on accuracy is unmeasured. Recorded for the next version.
2. **Rejected variant X3 looked better on the held-out labels** (7 vs 9 wrong of 21). I didn't adopt it, because choosing on the held-out labels would use them up. It needs a fresh held-out set.
3. **Only 3 of 113 claim labels were checked by hand.** For the other 110, only the quote's presence was checked, not whether the quote really says the claim.
4. **My own verdicts were made from short summaries.** Claude wrote one-line summaries of each posting's requirement lines, and I judged from those. Some of my y verdicts missed eligibility facts in the full posting: sheet item 7 is a fellowship only for French Grandes Écoles graduates; item 47 is an internship for current students. I didn't re-judge any item, and no second person judged.
5. **9 of the 30 held-out postings have no verdict,** so the Chapter 9 measurement rests on 21 labels. Differences of 1–2 are within the noise floor.
6. **Claude Code's dangerous tools were never called** (Bash, Write, Edit, …). So I don't know whether `claude mcp serve` asks permission before them.
7. **The `CLAUDE.md` context effect is not measured.** I argue that `CLAUDE.md` loaded inside the repo would be a hidden context change, but I didn't run that comparison.
8. **Board terms of use.** As in JS2, I relied on the public, documented job-board endpoints, at one request per board per run. I did not read each site's terms of use.

**Not claiming:**
- That the filter finds the best jobs for Priya. It reduces 3,117 postings to 115, and its errors are concentrated at the threshold.
- That 0 of 29 means the filter never rejects a good posting.
- That the prompt v2 judge is better. It moved the score; the 21 labels can't show it is better.
- That my tool server is safe against a hostile client, or against a client that ignores its read-only hint. It is read-only by construction, and the hint is only a hint.
- That anything here was trained. No weights changed.

**Signed** Lavanya R, 2026-11-24

## Driver's seat

| Part | What Claude should do | What I should do | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter rules | count words in the corpus, show real titles, offer options, implement exactly, test before code | choose each rule and its reason; decide what to add, cut or reject after measuring | what counts as "relevant" is a statement about **my** job search, not a property of the postings | FILTER.md §1 and Changes; `75b2de8` before `2c1b967` |
| The hand verdicts | draw the sample with a committed seed; hide the filter's answer; summarize each posting | judge each posting y / n / ? myself | the audit measures the filter against **my** judgment; if Claude judged, it would measure Claude against itself | `450e2f0` → `efe0296` → `audit/hand_verdicts.jsonl` |
| Claim labels | label every claim with a quote; check every quote mechanically | check a sample; disagree where my judgment differs | a quote can be real and still not say the claim; only a reader can tell | SHORTLIST.md §4 (my 1 disagreement is kept) |
| Trusting a tool server | probe it; report declared vs actual | decide whether my agent may use it | trusting a server grants it access to my machine and data; that's my decision, not the server's or Claude's | TOOLSERVER.md T1, T2 |
| **Whether a posting is worth my time** | rank, filter, label evidence, say "I cannot tell" | decide | Claude's judge said "no" to 13 of the 14 held-out postings I marked y (MEASURE.md §2b). Some of its reasons were right (an eligibility rule I hadn't seen), and some were stricter than I'd be. The trade-off between a long shot and a wasted application depends on my time, my visa clock and my risk tolerance. Those aren't in any posting, so the call stays mine. | MEASURE.md §2b; SHORTLIST.md §3 |

**Where I didn't keep the driver's seat:**
- I chose the FILTER.md rules and reasons from Claude's options rather than writing them in my own words first. That is what my JS1 feedback asked me to do differently.
- I followed Claude's recommendations on X1–X4 and on the footer.
- Claude wrote the tests that came before the code.

These are recorded in FRICTIONAL.md.

## Files

- **Documents:** `FILTER.md`, `AUDIT.md`, `SHORTLIST.md`, `TOOLSERVER.md`, `MEASURE.md`, `SOURCES.md`, `FRICTIONAL.md`; `GATE.md` is JS2's, copied unchanged.
- **New JS3 code:**
  - `agent/corpus.py`, `filter.py`, `run_filter.py`, `evidence.py`, `shortlist.py`;
  - `audit/draw.py`, `measure.py`, `tables.py`;
  - `score/claude_score.py`, plus `score/prompts/` and `score/context/`;
  - `mcp/server.py`, `tap.py`, `client.py`.
  - The JS2 code is unchanged except `agent/providers.py` (Greenhouse `?content=true`) and `config/boards.json`.
- **Config:**
  - `config/filter.json` is FILTER.md v1.1; `config/filter-v1.0.json` is v1.0;
  - `config/budgets.json` and `config/boards.json`.
- **Tests (150, offline):**
  - JS3: `test_filter` (27), `test_evidence` (11), `test_mcp_server` (13);
  - JS2's 99, unchanged.
- **Evidence:**
  - `runs/` (the two live collections, raw bytes) and `CORPUS.sha256`;
  - `out/filter/`, `out/shortlist/` (raw Claude replies), `score/runs/` (raw Claude replies);
  - `audit/` (seed, draw, sheet, my verdicts);
  - `transcripts/`, `logs/`.
