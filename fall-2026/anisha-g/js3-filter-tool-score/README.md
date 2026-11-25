# Job-Search Agent 3: The Filter, the Tool, and the Score
**Anisha Gaikar · INFO7375 · `fall-2026/anisha-g/js3-filter-tool-score/`**

**What I started from:**
- **My own JS2 agent** (`../js2-loop-tools-diff/`): its allow-list permission policy (`watcher/policy.py` → `js3/policy.py`, same hosts, GET/HTTPS only, no apply/login/message paths), its fetch pattern and its 5-board budget.
- **My JS1 work** (`../js1-contract-and-watch/`): the **fictional persona** Nadia Okafor (`persona/resume.json`, copied unchanged) and the two **Claude prompts** (`prompts/js1_baseline.txt`, `prompts/js1_revised.txt`, unchanged).
- I did **not** use the Reallocation Engine. I borrowed one idea from Lectern: the filter is a versioned document where every added, cut and rejected rule is recorded (FILTER.md §5).

**Language and toolchain:**
- **Python 3**, standard library only; run with Python 3.14.7 on macOS. Nothing to install for the agent, the tests or the tool server.
- **Claude Code 2.1.332** (`claude` CLI): the MCP client in the real transcripts, and `claude -p` for the Claude judge experiments.
- **Node 26 + npm**, only to run the *other* tool server I evaluated (`@modelcontextprotocol/server-filesystem@2.2.0`).
- `git`, `shasum`.
- Claude (Claude Code, Opus 5.5) for the build (SOURCES.md).

## Exact commands (from a fresh clone, inside this folder)
```bash
python3 -m unittest discover -s tests -t .        # all tests (78)
bash tools/make_logs.sh                            # logs/01-03: tests unchanged since freeze; both wrong versions FAIL; real code passes
python3 -m js3.collect                             # live: 5 boards -> data/corpus.jsonl.gz (+ collection_summary.json)
python3 -m js3.filter filters/filter_v1.0.json     # decisions -> out/decisions_v1.0.jsonl   (also v1.1, v1.2)
python3 tools/make_shortlist.py filters/filter_v1.0.json   # source-grounded shortlist -> out/shortlist_v1.0.md
python3 tools/draw_sets.py                         # the seeded audit + held-out draw (already committed; re-running reproduces it)
python3 -m js3.judge                               # the blind hand-judging sheet (a human answers; Claude does not)
python3 -m js3.report                              # audit + held-out tables -> out/report_original.md (and _corrected.md)
python3 tools/check.py                             # independent recount (does not import js3)
python3 toolserver/server.py                       # the MCP-shaped tool server on stdio
python3 toolserver/client.py own toolserver/script_own.json -- python3 toolserver/server.py   # my scripted client
claude -p "Use the score_posting tool to score posting id greenhouse:stripe:8189909" \
  --mcp-config toolserver/configs/claude-mcp.json --strict-mcp-config \
  --allowedTools mcp__js3__score_posting --tools "" --output-format stream-json --verbose     # real Claude Code session
python3 -m js3.claude_judge B B2 E1 E2 E3 E4       # the Chapter 9 Claude runs (real calls, about $2.50; raw replies in runs/)
```

## What ran (all on my Mac, 2026-11-25; commits in order)
| Commit | Time (ET) | What |
|---|---|---|
| `7ee4178` | 14:02 | **FILTER.md v1.0, alone, before any code** |
| `340c11f` | 14:09 | Tests + 2 wrong versions written **from FILTER.md, before any code**: `logs/00`, 44 errors (no code yet); frozen in `tests.frozen.sha256` |
| `42fef19` | 14:11 | The implementation: `logs/02` shows the tests **fail** on both wrong versions (substring: 4 failures, word-count: 8), and `logs/03` shows 64/64 pass |
| `0810190` | 14:12 | **Live collection**, 5/5 boards, 1,734 postings (`logs/10`); filter v1.0 keeps 11 (`logs/11`); the audit seed, the draw and the blind sheet, **before any judging** |
| `f30af68` | 14:18 | Tool server transcripts: 4 real Claude Code sessions, my scripted client, the other server; the Chapter 9 experiment plan **before any Claude call** |
| `4b4dffd` | 14:20 | 180 real Claude judge calls on the held-out set (before my verdicts existed) |
| `2c8683c` → `4eddf21` | 14:21 | Filter v1.1: tests first (`logs/04` fail), then code (`logs/05`) |
| `017f3ca` → `6551bd8` | 14:23 | Evidence bug found by re-reading labels: regression test first (`logs/06` fails), then the fix (`logs/07`, 73/73) |
| `474e2d5` | 14:51 | **My 76 hand verdicts** (judged 14:27–14:51), frozen by hash before any comparison |
| `d6a5279`, `df3d67f` | 14:55 | Server description fixed after my own evaluation; run 5 (3 sessions) |
| `7c66429` → `7658ac6` | 14:58–14:59 | Filter v1.2 (R5 US-only, my decision): tests first (`logs/08`), then code (`logs/09`, 78/78) |
| `b2e2721` | 15:02 | Independent check, 9/9 PASS (`logs/41`) |
| *(re-judge)* | 15:39–15:41 | My 5 re-judged items: same verdicts, corrected reasons; no number changed |
| *(final)* | | Sign-off. The final hash is in Canvas |

## Where each requirement is
| Requirement | File |
|---|---|
| Gate: filter with reasons, evidence rules, expected sources, wrong versions; versioned | [FILTER.md](FILTER.md) (v1.0 gated in `7ee4178`; v1.1/v1.2 in §5 and the change log) |
| Filter run on everything collected | `out/decisions_v1.{0,1,2}.jsonl`, `logs/11-13` |
| Reject audit: 30 random rejects + close calls + kept sample judged by hand, what the sample can show, false friends, rules added/cut/rejected | [AUDIT.md](AUDIT.md), `labels/hand_verdicts.jsonl`, `out/report_original.md`, FILTER.md §5 |
| Source-grounded shortlist, every claim labelled, relevance ≠ entailment, abstention rule + counterexample | [SHORTLIST.md](SHORTLIST.md), `out/shortlist_v*.json` |
| Tool server from scratch, real transcripts both ways, both evaluations | [TOOLSERVER.md](TOOLSERVER.md), `toolserver/`, `transcripts/` |
| What moves the score: origin of every number, one change at a time, held-out | [WHAT_MOVES_THE_SCORE.md](WHAT_MOVES_THE_SCORE.md), `runs/` |
| Wrong versions the tests catch | `wrong_versions/`, `logs/02_*` |
| Sources, honest log | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

## Results in one paragraph
- **The collection:** filter v1.0 kept **11 of 1,734** postings.
- **Random rejects:** I judged 30 random rejects and found **0** I wanted. On 30 that's consistent with a true miss rate of up to about 11% (Wilson 95%), or about 0–196 of the 1,723 rejects: an estimate, not a count.
- **The keeps were the problem:** of all 11 keeps, I wanted **1**. The filter matches "analyst job that names her skills", and my reasons were about location, internship eligibility and finance roles, none of which v1.0 sees.
- **v1.1 and v1.2:** v1.1 fixed two false friends. v1.2's US-only rule turned 3 false keeps in the held-out set into correct rejects.
- **The held-out set has a single "y" in 30**, so "always say no" ties the best scorer and **no accuracy improvement can be claimed**.
- **The evidence gate** dropped 3 keeps whose skills were only "preferred", including the top-scoring posting.

## Sign-off: Job-Search Agent 3
- **Checked** (each by a named test or check that I ran on my Mac; logs in `logs/`):
  - **Filter rules R1–R4, the score and ranking:** `tests/test_filter.py` (28 tests).
  - **Both FILTER.md wrong versions are caught:** substring match fails 4 tests and word-count ranking fails 8 (`logs/02_*`).
  - **v1.1 and v1.2 rules:** `tests/test_filter_v11.py`, `tests/test_filter_v12.py`. Each failed before its code (`logs/04`, `logs/08`) and passed after (`logs/05`, `logs/09`).
  - **Evidence labels and "I cannot tell":** `tests/test_evidence.py`, `tests/test_evidence_regression.py` (failed before the fix, `logs/06`).
  - **Allow-list policy, parsers, and a failed board reported as failed, not 0:** `tests/test_policy_collect.py`.
  - **Tool server:** handshake, one declared tool, errors and two-way transcript (`tests/test_toolserver.py`); 4 + 3 real Claude Code sessions.
  - **The saved data:** recounted independently by `tools/check.py` (9/9 PASS, `logs/41`).
  - **The audit:** by hand, 76 blind verdicts.
- **How:**
  - **By a test written before the code:** all of `tests/` was written from FILTER.md before the implementation (commits `340c11f`, `2c8683c`, `017f3ca`, `7c66429`) and frozen by hash.
  - **By hand:** the 76 verdicts (reasons worded with help from another Claude chat), re-judging the 5 slips, and checking 3 shortlist postings against their quotes.
  - **By recomputation:** `tools/check.py`.
  - **With Claude's help:** Claude wrote all the code, the tests (from my FILTER.md), the experiment plan and the drafts of these documents. Claude also re-read the 49 shortlist labels; the 3 relevance≠entailment postings I checked myself are listed in SHORTLIST.md. Another Claude chat helped me word most of my audit reasons; the verdicts are mine.
- **Not checked:**
  1. **Accuracy on more than one positive.** The held-out set has one "y", so I couldn't measure whether any change improves accuracy.
  2. **Other days and boards.** One collection (14:11, 2026-11-25) from 5 boards; postings change daily, and other boards may format text differently (headings, "(2) years").
  3. **Evidence labels beyond the 11 keeps.** The labeller is a rule set; it was checked on 49 claims and a regression test, not on the 1,723 rejects.
  4. **The other server's dynamic `roots`** and its earlier CVEs (TOOLSERVER.md §4).
  5. **The R5 place lists outside this corpus.** "Remote", "N/A" and unseen cities pass by default.
- **Not claiming:**
  - that a "kept" or "shortlisted" posting is worth Nadia's time (my own audit says it mostly isn't);
  - that 0/30 means the filter never wrongly rejects;
  - that any Claude configuration is better than another beyond these 30 postings;
  - that anything was trained;
  - that the tool server is safe to expose beyond my own machine.
- **Signed or withheld:** Anisha Balshiram Gaikar(Anisha Gaikar, 2026-11-25)

## Driver's seat
| Task | Claude should | I should | Why |
|---|---|---|---|
| Collect and filter | fetch allowed boards, run the written rules, report failed boards as failed | choose the rules and the boards, and change them only by a written decision (FILTER.md §5) | the rules encode what *I* want; Claude can apply them, not choose them |
| Label evidence | quote the sentence and label each claim; say "I cannot tell" when the text doesn't say | spot-check the labels against the posting | the labeller had a bug I only found by re-reading (SHORTLIST.md) |
| Measure | compute counts, intervals and repeat runs; propose candidate rules with their effect | decide which rule to adopt or reject, and keep the held-out set untouched | a measured number doesn't decide what matters; I chose R5 and rejected FP&A |
| Tool server | answer only what it declares; refuse to apply or email | decide whom to trust and what to expose | annotations are claims; trust is my decision |
| **Is this posting worth my time?** | give the verdict of my written rules, with quotes | **make the call** | *: ____. Evidence from this assignment: the filter and Claude both kept postings I said no to, for reasons only I knew to apply (my graduation date against internship windows, where I can live, which fields I want). Of the 11 postings the filter kept, I wanted 1. |

## Privacy and boundaries
- **Persona:** fictional (Nadia Okafor, @example.com, 555 number). No real résumé, contacts, tracker or conversation transcripts are in this folder.
- **Network:** public endpoints only, behind the allow-list in `js3/policy.py`. GET only. The agent never applies, emails, messages or logs in.
- **The tool server:** read-only. It has no network code, and it writes only its own transcript into `transcripts/`.
- **Transcripts:** local machine paths are redacted (`transcripts/REDACTIONS.md`).

## Notes for TAs
- `shasum -a 256 -c tests.frozen.sha256` shows **FILTER.md: FAILED on purpose**. FILTER.md was frozen with the v1.0 tests and later got §5 and its change log; §1–4 are unchanged from `7ee4178`. Every test file still says OK (`logs/01`).
- **A parallel draft from 2026-11-13** (a different persona, "Riley Park", and 24 boards) was sitting **untracked** in this folder. It was never committed. Before building I moved it out of the repo (FRICTIONAL.md).
- **Some transcripts predate fixes.** Tool-server transcripts and the E4 runs before `6551bd8` used the evidence code with the heading bug, and those before `d6a5279` show the old tool description. The transcripts are kept exactly as recorded (TOOLSERVER.md §3).
