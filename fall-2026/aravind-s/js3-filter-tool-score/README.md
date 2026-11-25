# Job-Search Agent 3: The Filter, the Tool, and the Score

INFO 7375, Prompt Engineering for Generative AI, Fall 2026. Aravind Sundaravadivelu (GitHub: AravindKumar2504). Assignment JS3.

This is layer 3 of the job-search agent I started in JS1. Layer 1 watched one board; layer 2 is a bounded loop over four
boards with a rule and a Claude judge. Layer 3 adds a written filter ([FILTER.md](FILTER.md)) that I audited by hand, a
shortlist whose every claim I labeled against the posting's own words, the filter offered to Claude as a tool through a
Model Context Protocol server that I evaluated, and a measured account of what moves the score. The agent never
applies, emails, messages or logs in, and every JS3 command works offline: the filter reads the board answers that
JS2's loop already saved.

**What I started from:** my JS2 agent (final commit `1779827`) and two live runs with its code unchanged on 2026-11-20
(`34aa5d6`): mine at 6:39 AM ET, where OpenAI's whole board was refused over one posting with an empty title, and one
Claude Code ran at my request a minute later. JS2's documents are in [js2/](js2/), JS1's in [js1/](js1/). GATE.md,
CONTRACT.md, BOUNDARY-TESTS.md and LABELING-RULE.md stay at the root, because the code and its tests read them.

**Jane Doe is fictional.** Her résumé (`persona/jane-doe.json`, unchanged since JS1) has a situation like mine (F-1
student, not a U.S. person, needs H-1B sponsorship later, earliest full-time start May 2027, 3 years of experience) but
none of my identity, an `@example.com` email and a 555-01xx phone number.

**Commit hashes** such as `45fc2c0` are commits of this repository,
https://github.com/AravindKumar2504/job-search-agent; each opens at
`https://github.com/AravindKumar2504/job-search-agent/commit/<hash>`, where its date and its files can be checked.
The course folder holds a snapshot of one commit (its SNAPSHOT.md), so the hashes do not resolve there.

## Where each part of the brief is

| The brief asks for | Where it is |
|---|---|
| The filter, as a versioned document with reasons, written before the build | [FILTER.md](FILTER.md) v1.0, commit `66e26d9` (2026-11-20, 11:27 PM ET), before the first JS3 code (`533155a`, 11:39 PM). Section 1 is mine, in four drafts ([filter-drafts/](filter-drafts/)). Version 1.1 is added below it (`5dff01f`, 2026-11-22); version 1.0 is unchanged |
| The filter over everything collected | [js3/filter-run/2026-11-21T044414Z/](js3/filter-run/2026-11-21T044414Z/report.md) (v1.0: 1,509 postings, 99 kept, 1,409 rejected, 1 "I cannot tell") and [2026-11-22T084738Z](js3/filter-run/2026-11-22T084738Z/report.md) (v1.1) |
| The reject audit: 30 or more random rejects judged by hand, what the sample can show, a named false friend | [js3/audit/2026-11-21T044414Z/](js3/audit/2026-11-21T044414Z/): the sealed kit (`c19dd8e`), my 55 verdicts (`45fc2c0`), [RESULTS.md](js3/audit/2026-11-21T044414Z/RESULTS.md) (`79df09c`), [AFTER-REVEAL.md](js3/audit/2026-11-21T044414Z/AFTER-REVEAL.md); the false friends are under "Results" |
| The source-grounded shortlist: every claim labeled, relevance versus entailment, an abstention rule | [js3/claims/2026-11-21T044414Z/](js3/claims/2026-11-21T044414Z/): my 105 labels (`1608a04`), [RESULTS.md](js3/claims/2026-11-21T044414Z/RESULTS.md) and [FLIP-CHECKS.md](js3/claims/2026-11-21T044414Z/FLIP-CHECKS.md) (`57041c4`, `cb4943a`), [ABSTENTION.md](js3/claims/2026-11-21T044414Z/ABSTENTION.md) |
| The tool server, its transcripts, and two evaluations with a trust decision | [js3/mcp/](js3/mcp/README.md): `job_agent/mcp_server.py`, the transcripts, [EVALUATION-OWN.md](js3/mcp/EVALUATION-OWN.md) and [EVALUATION-OTHER.md](js3/mcp/EVALUATION-OTHER.md), each ending with my trust decision (`d4c9eb0`), and the runtime traces of both servers ([js3/mcp/runtime/](js3/mcp/runtime/2026-11-25T023441Z/README.md), 2026-11-24) |
| What moves the score: the origin of every number, one change at a time, measured on held-out labels | [js3/score/](js3/score/README.md): [ORIGINS.md](js3/score/ORIGINS.md), [CHANGES-TO-MEASURE.md](js3/score/CHANGES-TO-MEASURE.md) (`1c9a37e`, written before the held-out answers were opened), [EXPERIMENTS.md](js3/score/EXPERIMENTS.md) (`cb1b50c`), on my held-out set [js3/heldout/2026-11-21T044414Z/](js3/heldout/2026-11-21T044414Z/README.md) (`1e2b1e1`) |
| A fresh test of v1.1 on labels that played no part in it (added 2026-11-24) | [js3/fresh/2026-11-22T084738Z/](js3/fresh/2026-11-22T084738Z/README.md): sealed with its predictions before any verdict (`9cdf591`), my 20 verdicts (`1bbbcf6`), [RESULTS.md](js3/fresh/2026-11-22T084738Z/RESULTS.md) (`c01dc04`) |
| The sign-off and the driver's seat | [js3/SIGNOFF.md](js3/SIGNOFF.md) |
| Sources and the split of work; my log | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

## Language and toolchain

- Python 3.9 or newer, standard library only: nothing to install. The 398 tests pass on Python 3.12.14 and on macOS's
  own 3.9.6 (run by Claude Code on 2026-11-24).
- No network and no Claude for any JS3 command. The filter reads the boards' answers saved by JS2's loop
  (`runs/2026-11-20T114036Z/`), each checked against the SHA-256 that the filter run recorded.
- The one live MCP run used the Claude Code CLI 2.1.326 that the Claude desktop app bundles, signed in with a claude.ai
  seat (no API key), on 2026-11-21.
- git, for the test that reads FILTER.md v1.0 from its own commit, and for the privacy test's file list.

## Commands (from the repo root)

```bash
python3 -m unittest discover -s tests -t .
```
398 offline tests, about 50 seconds.

```bash
python3 -m job_agent filter
python3 -m job_agent filter --filter-version 1.0
```
Applies FILTER.md (the newest version, or the one named) to the newest saved answer of each board, and writes
`js3/filter-run/<time>/` with `verdicts.json` and `report.md`. Offline.

```bash
python3 tools/score_audit.py js3/audit/2026-11-21T044414Z
python3 tools/score_claims.py js3/claims/2026-11-21T044414Z
python3 tools/heldout_experiments.py report
```
Recompute the audit's and the claims' results from my committed labels and the sealed answers (each checks the sealed
file's SHA-256 first), and rebuild EXPERIMENTS.md from the saved runs. The held-out measurement itself
(`python3 tools/heldout_experiments.py`) refuses to run a second time.

```bash
python3 -m unittest tests.test_aravind_own_rule -v
```
My own test, written from my R1 before reading the filter's code.

```bash
python3 tools/score_fresh.py js3/fresh/2026-11-22T084738Z
python3 tools/baselines.py --check
python3 tools/boilerplate_check.py --check
python3 tools/card_rebuild_check.py --check
python3 tools/mcp_runtime_trace.py check js3/mcp/runtime/2026-11-25T023441Z
```
Rescore the fresh set (it checks the sealed file's SHA-256 and that my verdicts are committed), check that the three
after-the-fact reports in `js3/checks/` rebuild from the committed files, and run both MCP servers again under the
audit hook to check that every recorded summary comes out the same (macOS, for `sandbox-exec`).

```bash
python3 tools/mutants.py
```
Plants 82 mistakes in a copy of the code, one at a time (JS1's and GATE.md's wrong versions, FILTER.md's W1 to W7 and
more, and six in the MCP server) and checks that the tests catch each one. About 20 minutes.

The MCP server, our client and the Claude Code run have their own commands in [js3/mcp/README.md](js3/mcp/README.md).

## What ran

- **2026-11-20:** the two starting runs (6:39 and 6:40 AM ET); FILTER.md v1.0 (11:27 PM); the filter engine and its
  first run, `2026-11-21T044414Z` (11:44 PM ET); the audit kit, sealed before any verdict.
- **2026-11-21:** the claims and held-out kits, both sealed before any label; the MCP server, our client's runs against
  both servers, and one live call from Claude Code (08:45 UTC); the two evaluations; 82 of 82 planted mistakes caught.
- **2026-11-22:** my 55 audit verdicts, 30 held-out verdicts and 105 claim labels (1:20 to 3:05 AM ET), each set
  committed before its answers were opened; the scoring; the card fix; my own test and my recomputation (3:18 and
  3:19 AM); the held-out measurement (3:36 AM); my v1.1 calls; FILTER.md v1.1 and its run (3:47 AM); the planted
  mistakes again after v1.1 (`js3/checks/`).
- **2026-11-24:** the MCP client fix (8:44 PM ET) after a read of eleven classmates' JS3 work; the fresh set for v1.1,
  sealed with Claude Code's predictions (9:01 PM), my 20 verdicts (9:07 PM) and its one scoring (9:08 PM); the
  after-the-fact checks in `js3/checks/` and the tests that rebuild every result; runtime traces of both MCP servers on
  Python 3.12.14 and 3.9.6 (9:34 PM).

## Results

- **The reject audit:** I agreed with the filter on 51 of 55 cards, with 0 wrong keeps. Among 30 random rejects there
  was 1 miss, card 17, so the most this sample allows (exact one-sided 95% bound) is 14.9% of the 1,409 rejects, about
  209. That miss came from the card, not the filter: the card had hidden "U.S. Person Required", which R5 had read; shown
  the line after the reveal, I rejected it, which makes it 0 in 30 and a bound of 9.5% (about 134). Both are reported.
  The filter's deciding rule there was my own R4: the title, "Forward Deployed Software Engineer, New Grad - Warp
  Speed", is one R4 excludes, so my blind Keep also went against my own rule; I kept R4 as written. FILTER.md v1.1
  rejects the same 1,409 postings as v1.0, so the bound holds for v1.1's rejects unchanged.
- **The MCP servers at run time** ([js3/mcp/runtime/2026-11-25T023441Z/](js3/mcp/runtime/2026-11-25T023441Z/README.md)):
  traced under a Python audit hook through our client's five sessions on Python 3.12.14 and 3.9.6, neither server
  wrote a file (ours wrote only its transcript, when asked), opened a socket or started a process, and with the
  network denied by `sandbox-exec` every answer was the same. On 3.9.6, though, our server loads the `subprocess`
  module, because the standard library's `platform` imports it; the evaluation's import-graph claim had missed that,
  and now says so. The server as evaluated (`a54c424`) and today's answer alike except for FILTER.md's hash.
- **Against constant answers** ([js3/checks/BASELINES.md](js3/checks/BASELINES.md), computed after the fact):
  "reject everything" agrees with me on 35 of the 52 audit cards I judged and "keep everything" on 17, against the
  filter's 51; on the held-out set, 15 and 12 of 27 against 27. 28 of the 30 random rejects fail R4 and only 2 sit
  near the boundary (an engineering title failing one other rule, 111 of the 1,409 rejects), so the clean audit is
  mostly a result on easy rejects. Rebuilt with today's card builder, no audit card besides 17 hid a line a rule
  reads ([CARD-REBUILD.md](js3/checks/CARD-REBUILD.md)). Topic points from sentences many postings share: 4 points,
  on two copies of one Palantir posting, and none in either top 10 ([BOILERPLATE.md](js3/checks/BOILERPLATE.md)).
- **False friends:** "growth" in "5+ years of experience in data science or growth analytics" made the years rule
  read a requirement as a sentence about the company (audit card 34). "build systems" in "build systems that consume ...
  ML-based signals" is a verb and a noun, yet it gave a shortlisted posting 5 points for developer tools (claim 09.8c).
  "from the start" was picked up as a start-date sentence (claim 09.6).
- **The claims:** the rule-based checker agrees with my labels on 101 of 105, and on 102 after the four flip checks.
  Relevance is not entailment: 09.8c is relevant (it has the topic word) and does not support the claim. No claim is
  contradicted, and that is by construction, not luck: every shortlisted posting passed the hard rules, which reject
  exactly what a contradicting line would say, so a contradiction would mean a rule had missed a line a person reads.
  None of the 105 claims showed one.
- **Abstention:** the posting-level "I cannot tell" fired once in 1,509 postings, the rule level 69 times (all on
  postings another rule rejected), and 30 of the 105 claims were insufficient by my labels.
- **What moves the score:** on my held-out set, v1.0's keep or reject agreed with all 27 cards I judged (bound 10.5%);
  none of six one-object changes moved a keep or a reject; the cutoff is what moved the recommendation (60: 22 of 27
  agree; 50: 27 of 27). FILTER.md v1.1 takes my three calls: a cutoff of 50, 10 points off for an export-control line,
  and no "build systems".
- **v1.1 on fresh labels (2026-11-24):** 20 postings I had never been shown, most of them ones whose recommendation
  v1.1 changes, sealed with Claude Code's predictions before I judged them. v1.1's recommendation agrees with me on 15
  of the 17 I judged, v1.0's on 7. Of the 12 postings v1.1 newly recommends I kept 10 (exact one-sided 95% bound on
  v1.1's misses there: 43.8%); I marked all 3 that the export-control penalty holds back "?"; the 5 controls came out
  as expected, so all three predictions held. My 2 rejects there, a frontend productivity role and a robotics
  control-systems role, are the first postings the filter kept that I rejected (the audit and the held-out set had
  none): both titles contain "Software Engineer", which my R4 passes, and both scored 50 with no topic group, so at a
  cutoff of 50 the score screened nothing and R4's title words alone let them through. "build systems" moves no
  recommendation here, so no card tested that call.

**The rule ledger** (each change, measured before it was made or kept):

| Rule or word | What happened | Measured | Date |
|---|---|---|---|
| Company words growth, revenue, customers (R7) | removed after measurement | 77 fires in 72 postings, every one a real requirement | 2026-11-21; removed in v1.1, 2026-11-22 |
| "build systems" (Developer tools) | removed after measurement | 7 scores on the whole run; the false friend in 09.8c | 2026-11-22 |
| The splitter after "U.S.", "e.g." and "i.e." | changed after measurement | hid one status line on an audit card and one on a held-out card | 2026-11-22 |
| An export-control line | 10 points off, added after measurement | 9 kept postings; all six of my "?" verdicts were over it or over clearance | 2026-11-22 |
| The shortlist cutoff | 60 changed to 50 after measurement | audit: I kept postings at 50, 55 and 60 alike; held-out: 22 of 27 at 60, 27 of 27 at 50 | 2026-11-22 |
| "Forward Deployed" (R4) | unchanged after measurement | the audit's one miss (card 17) also fails R5, and I reject it with the line shown | 2026-11-22 |
| A season wholly before the earliest start; other US-remote spellings | not added | 0 fires in 1,509 postings | 2026-11-21 |

## Known limits

- One day's saved answers (2026-11-20) of three boards: nothing live and no other boards. Every rate here is a
  sample's bound, not a rate for all postings.
- I judged compact cards in chat (every fact line, with the description cut to its first 32 words); one card hid a
  status line until the cards were fixed. For the fresh set, that chat view is committed (`CHAT-CARDS.md`, made from
  the cards by `tools/chat_cards.py`).
- Every label is mine: one labeler, so no agreement between labelers is measured.
- Constructed inputs: the tests' postings are constructed, and the MCP client's broken lines (a line that is not UTF-8,
  20,000 nested brackets, a path-traversal posting id) and the 82 mutants are planted. Every count under "Results"
  comes from the saved answers of 2026-11-20, not from these.
- The MCP server reads a line of any length (no size cap), which is fine for a local stdio tool and not for anything
  shared.
- My held-out set guided my v1.1 calls, so it is development data now. The fresh set tests v1.1 on 20 new labels:
  small draws from strata of one day's saved answers, not a rate for all postings.
- The MCP server is a subset of MCP 2025-11-25, not conformant and not shown to be secure, and it stays on FILTER.md
  v1.0, the version it was evaluated with. Two commits after my trust decision changed it or the modules it calls
  (`b8e3a25`, `5dff01f`), which by the evaluation's own terms reopens the decision ([EVALUATION-OWN.md](js3/mcp/EVALUATION-OWN.md),
  "Changes after the trust decision"); my call after them (2026-11-24): still pending, with the same scope. The
  runtime traces show what the servers did in these sessions only.
- Not in v1.1: the shortlist saying "the posting does not say" for claims 5 to 7, and two rules that never fired.

## Contents

| Path | What it is |
|---|---|
| [FILTER.md](FILTER.md), [filter-drafts/](filter-drafts/) | The filter (v1.0 and v1.1) and my four drafts of its Section 1 |
| [FILTER-CHANGES-PENDING.md](FILTER-CHANGES-PENDING.md) | What v1.0's run showed for v1.1, with its status |
| `job_agent/` | The agent: JS1's watch and rule, JS2's loop, and JS3's `filter.py`, `filter_run.py` and `mcp_server.py` |
| `tools/` | The kits, the scorers, the held-out experiment tool, the fresh set's kit, scorer and chat view, the after-the-fact checks, the MCP client, run script and runtime trace, the mutants |
| `tests/` | 398 tests |
| `js3/` | JS3's filter runs, kits, labels, results, MCP work, score work and sign-off |
| `runs/` | The board answers JS2's loop saved, which the filter reads |
| GATE.md, CONTRACT.md, BOUNDARY-TESTS.md, LABELING-RULE.md, `boards.json`, `persona/`, `prompts/`, `labels/`, `experiment/` | From JS1 and JS2, still read by the code |
| [js1/](js1/), [js2/](js2/) | The earlier assignments' documents |

**AI use:** Claude Code wrote the code, the tests and the tools, drafted FILTER.md Sections 2 to 7, both evaluations and
the reports, and organized my notes, at my direction. The rules in Section 1, every label, every decision, both trust
decisions and the sign-off are mine ([SOURCES.md](SOURCES.md)).
