# Job-Search Agent 3: the filter, the tool, and the score

**Mayank Bhadrasen (mayank-b)** · INFO 7375 · Fall 2026 · Chapters 7–9 · 2026-11-25

## Executive summary

**What this is.** My JS2 agent collects every posting from three public job boards. This layer decides what reaches Priya (a fictional early-career AI/ML engineer) and why:
- a **filter written as a document first** (`FILTER.md`), with a reason for every rule;
- a **reject audit** I judged by hand;
- a **source-grounded shortlist**, where every claim Claude makes is labelled against the posting's own text;
- the filter offered to Claude as a **tool server** that speaks the Model Context Protocol, evaluated alongside a second server;
- **one change, measured** on labels I held out blind.

**What ran (2026-11-25, Eastern):**
- **One fetch, 4 GETs.** Anthropic returned 635 postings, HubSpot 141 and Notion 174, all with posting text. The deliberate bad board returned 404 and was recorded as an error, not 0 postings. My dated predictions: Anthropic was inside the range; **HubSpot and Notion came in above it**.
- **Filter v0.1 on all 950 postings:** 76 kept, 874 rejected, 0 cannot-tell, 42 close calls. **Notion and HubSpot keep nothing.** On Notion, 85 rejects come from the inherited location rule alone: Notion writes "San Francisco, California" where the rule expects "San Francisco, CA". "agents" appears in 174 of 174 Notion postings (boilerplate).
- **The shortlist:** 10 postings, with justifications from Claude Haiku 5.5 (real responses via the Claude Code CLI; the JS1 API key returned 401, and that failed run is kept). One claim shows relevance without entailment (S01 C3).
- **The tool server** (`score_posting`, read-only, offline) matched all 22 predicted protocol steps. Claude Code connected to it as a real client. Chapter 8's teaching server also matched 22/22 predictions, and its known gaps were confirmed by running it.
- **Tests and the planted wrong versions.** 74 tests pass. The filter's planted wrong versions WF1–WF4 are each caught (`scripts/wrong_versions.py`), and so is the tool server's WF6. Every saved record equals a recomputation from the raw files.
- **The reject audit (my verdicts):** 1 of 30 random rejects was wrong (R08, rejected by the exclude word "Lead"); 0 of 15 close calls; 0 of 10 kept. For this snapshot's 874 rejects, the one-sided 95 % upper bound on the wrongly-rejected share is **14.9 %**, a statement about this pool only.
- **The shortlist:** all 40 claims labelled by me: 33 supported, 2 contradicted (S05 C3, S09 C3), 3 insufficient (S01, S06, S08 C3). The level claim C3 is where relevance and entailment come apart.
- **One change (v0.2: "Lead" cut), measured once on my 30 blind held-out labels:** agreement 19/30 before and after, no change. The held-out set's 9 false rejects are the real weakness (`SCORE.md`).

**Started from:** my JS2 loop and JS1 rule, plus the instructor's Lectern filter as the model for FILTER.md (`SOURCES.md`).

## Language, toolchain, commands

- **Python 3, standard library only**, no install. Run with Python 3.9.6 (macOS). The course validator rejects `.js`/`.ts` outside `learning-artifacts/`.
- `claude` (Claude Code 2.1.323) is used only for the shortlist justifications and the real-client transcript B.

```bash
cd fall-2026/mayank-b/js3-filter-tool-score
python3 -I -m unittest discover -s tests          # 74 tests, offline
python3 -I scripts/wrong_versions.py               # WF1–WF4: 4/4 caught
python3 -I scripts/wrong_versions_mcp.py           # WF6 (tool server)

# the pipeline (what ran, in order)
python3 agent.py run --label content                                            # the fetch (network: 2 allow-listed hosts)
python3 jsa3.py filter --corpus runs/2026-11-26T02-20-27Z-content               # v0.1 on everything
python3 jsa3.py draw --filter-run runs/2026-11-26T02-20-53Z-filter-v0.1         # blind held-out sheet + audit draw
python3 jsa3.py audit-sheet --filter-run runs/2026-11-26T02-20-53Z-filter-v0.1  # blank audit sheet
python3 jsa3.py boilerplate --filter-run runs/2026-11-26T02-20-53Z-filter-v0.1
python3 jsa3.py shortlist --filter-run runs/2026-11-26T02-20-53Z-filter-v0.1 --n 10 --via claude-cli --rerun 3
python3 jsa3.py audit-summary --filter-run runs/2026-11-26T02-20-53Z-filter-v0.1   # reads my verdicts
python3 jsa3.py filter --corpus runs/2026-11-26T02-20-27Z-content --config config/filter-v0.2.json
python3 jsa3.py measure --heldout labels/heldout-sheet.md --before runs/2026-11-26T02-20-53Z-filter-v0.1 --after runs/2026-11-26T04-26-02Z-filter-v0.2 --write

# the tool server
python3 -I src/jsa3/mcp_server.py --corpus runs/2026-11-26T02-20-27Z-content      # stdio JSON-RPC
python3 -I scripts/mcp_record.py --corpus runs/2026-11-26T02-20-27Z-content       # transcript A
bash review/run-review-commands.sh                                               # what I ran myself
```

## Where each part of the brief is

| Brief | File |
|---|---|
| Step 1: the filter, evidence rules, expected sources, wrong versions | `FILTER.md` (committed first, JS3-CP1) |
| 2.1: the reject audit with my verdicts, the false friend | `audit/reject-audit-v0.1.md`, summary in `runs/2026-11-26T02-20-53Z-filter-v0.1/audit-summary.md` |
| 2.2: the shortlist and its labels, relevance vs entailment, abstention + counterexample | `shortlist/claims.md`; FILTER.md §2 |
| 2.3: the tool server, transcripts, both evaluations | `src/jsa3/mcp_server.py`, `transcripts/`, `EVAL-OWN-SERVER.md`, `EVAL-OTHER-SERVER.md` |
| 2.4: where every number came from, one change, held-out, persistence | `SCORE.md`; held-out labels `labels/heldout-sheet.md` |
| Step 3: the sign-off and driver's seat | `SIGNOFF.md` |
| SOURCES, FRICTIONAL | `SOURCES.md`, `FRICTIONAL.md` |

## Privacy and boundaries

Priya Nair is fictional. There are no real résumés, contacts or transcripts here. The agent sends only GETs to `boards-api.greenhouse.io` and `api.ashbyhq.com`. It never applies, emails, messages or logs in. The tool server imports no network module, writes nothing outside `transcripts/`, and exposes one read-only capability. No keys are in this folder.
