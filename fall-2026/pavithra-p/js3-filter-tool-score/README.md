# Job-Search Agent 3: The Filter, the Tool, and the Score

INFO 7375 Prompt Engineering for Generative AI, Fall 2026 · Pavithra Prasad (`pavithra-p`) · Assignment JS3

My JS2 agent collects postings from four public boards. This layer decides what reaches the candidate, the fictional Rohan Mehta, and why:
* a filter I can read (`FILTER.md`, written first);
* an audit of what it rejected, against my own hand labels;
* a shortlist where every claim is checked against the posting's text;
* a tool server that offers the filter to Claude;
* a record of where every number came from, and of one change at a time measured on labels I held out.

The agent never applies, emails, messages anyone or logs in. It reads only public, no-login job-board endpoints on an allow-list (`config/hosts.json`), and the tool server can change nothing outside this folder.

## Results at a glance

| Part of the brief | What I did | Result | Where |
|---|---|---|---|
| Filter, written first | FILTER.md v1.0 committed alone before any filter code; three gates and a score, a reason for every rule, evidence rules, 3 wrong versions | 589 postings from 4 boards: v1.0 keeps 7, v1.1 keeps 15 | `FILTER.md`, `d9b1cf1` |
| Reject audit | 68 postings labelled by me, blind (30 random rejects, close calls, kept, gate close calls, 20 held-out), then a second pass on 27 | 5 of 30 random rejects wrong by my first labels (95% interval 7% to 34%); 1 of 30 by my second; false friend "Helm" (matched "HELM", an AI benchmark) | `AUDIT.md` |
| Source-grounded shortlist | 8 postings, 37 claims written by Claude with quotes, every claim labelled by me | 19 supported, 18 insufficient; Android matches my words but is mobile work (relevance is not entailment); the abstention rule passes only Android, which is its counterexample | `SHORTLIST.md` |
| Tool server | MCP server from scratch (one read-only tool), real transcripts with my client and with Claude as the client | Claude called it with only that tool; a crash and a version mismatch found in review, fixed and tested | `EVAL-SERVERS.md`, `transcripts/` |
| Other servers | a classmate's server (Lavanya Rajesh's `js3-postings`) and Claude Code's own `claude mcp serve`, probed the same way | Lavanya's: read-only and honest, same answers with the network blocked. `claude mcp serve`: 28 tools with no annotations; Read and Write worked outside its start folder with no prompt; a malformed request got no answer. Trusted: Lavanya's for search; `claude mcp serve` not | `EVAL-SERVERS.md` sections 2 to 4, `evidence/` |
| What moves the score | every number's origin; 6 filter changes and 1 context change, each alone, on 20 held-out labels | no change moved a held-out verdict (13 of 20 for all), partly because of the held-out design (`SCORE-REPORT.md` section 3); the context change flipped 9 of Claude's 20 verdicts with the same agreement | `SCORE-REPORT.md` |
| Sign-off | checks, 8 real "Not checked" items, signed; driver's seat | | `SIGNOFF.md` |
| Tests | 159 offline tests (80 from JS2, 79 new), including my own predictions | all pass | `tests/` |

Started from: my own JS2 folder, `fall-2026/pavithra-p/js2-loop-tools-diff/` at `bf7fe97`. It was copied unchanged in `e02dffe`: the collector, the permission policy, the JS1 rule and the fictional persona. From the Reallocation Engine I used only its example persona, through JS1 (`d08afdd`); I did not use its role scorer or recipes, or Lectern.

## Contents

| Path | What it is |
|---|---|
| `FILTER.md` | the filter (v1.0, committed alone in `d9b1cf1` before any filter code), the evidence rules, expected sources, wrong versions, and v1.1 with every rule added or rejected |
| `filters/` | the filter as data: `v1.0.json`, `v1.1.json`, and `changes/` (one file per single change) |
| `AUDIT.md`, `audit/` | the reject audit: the sample (`sample.json`), the blind labelling pages, my labels (`hand-labels.csv`, the second pass `reread-labels.csv`, the claims `claim-labels.csv`), the results tables |
| `SHORTLIST.md` | the source-grounded shortlist: every claim with its label, relevance versus entailment, the abstention rule and its counterexample |
| `agent/toolserver.py`, `serve.py`, `transcripts/` | the MCP tool server, written from scratch, and the real transcripts both ways |
| `EVAL-SERVERS.md` | my server and Lavanya Rajesh's server, evaluated the same way |
| `SCORE-REPORT.md` | every number's origin, one change at a time on the held-out labels, and why persistence is not training |
| `SIGNOFF.md` | the sign-off and the driver's seat table |
| `agent/` | `filter.py`, `evidence.py`, `shortlist.py`, `audit.py`, `toolserver.py`, `mcp_client.py`, `claims_page.py`, `collection.py`, `filter_wrong_versions.py`; the JS2 collector (`loop.py`, `tools.py`, `ats.py`, `policy.py`, `check.py`) |
| `prompts/` | the Claude prompts: `justify-v1.txt` (shortlist claims) and `judge-v1.txt` (Claude's verdict, for the context test) |
| `runs/20261125T204144Z/` | the collection run, the filter decisions (v1.0, v1.1), the shortlist and the two context runs, with every Claude reply saved |
| `evidence/raw/` | every response body from the collection, saved before parsing |
| `scripts/` | the transcript recorders and the tuning comparison |
| `tests/` | 159 offline tests: 80 carried from JS2 and 79 new (list below) |
| `SOURCES.md`, `FRICTIONAL.md` | what I used and what Claude contributed; my dated log |

## Language and toolchain

* Python 3.13.1, standard library only. Nothing to install.
* Claude Code 2.1.294 (`claude -p`) for the three real Claude uses: the shortlist justifications, Claude's held-out verdicts for the context test, and Claude as the client of my tool server. The model on the day was `claude-opus-5-5` (the CLI default).
* macOS (Darwin 25.5).

## Commands

Run everything from this folder. All but `watch` (public boards), `shortlist`, `judge` and `transcript_claude_client.py` (real Claude calls) are offline.

```bash
python3 -m unittest discover -s tests
```

| Command | What it does |
|---|---|
| `python3 -m agent watch` | one bounded collection over `config/boards.json` (JS2); raw responses to `evidence/raw/` |
| `python3 -m agent filter --filter filters/v1.1.json` | runs a filter file on the latest collection; writes `runs/<run>/filter-v<version>/` |
| `python3 -m agent draw-sample` | draws the audit sample (seed 20261125) and builds the blind labelling page |
| `python3 -m agent audit` | my hand labels against v1.0 on the tuning sets; writes `audit/results.md` |
| `python3 scripts/tune_changes.py` | each candidate change alone, on the tuning sets only |
| `python3 -m agent measure filters/v1.0.json filters/changes/*.json filters/v1.1.json` | each filter file on the held-out set |
| `python3 -m agent shortlist` | real Claude calls: a justification for each of the 8 shortlisted postings, then the checker's first label per claim; builds the claim-labelling page |
| `python3 -m agent judge full` and `python3 -m agent judge title` | real Claude calls: Claude's verdict on each held-out posting, with the full posting or the title only (`SCORE-REPORT.md` 2b) |
| `python3 -m agent reread-page` | builds the second-pass labelling page (27 engineering postings) |
| `python3 scripts/recheck_claims.py` | re-runs the evidence checker on the saved claims and compares it with my claim labels |
| `python3 scripts/audit_second_pass.py` | the audit of v1.0 on my second-pass labels (`AUDIT.md` section 8) |
| `python3 scripts/probe_claude_mcp_serve.py` | the same kind of probe on Claude Code's own MCP server, in a throwaway sandbox (Read and Write only) |
| `python3 scripts/redact_transcripts.py` | removes local paths and Claude Code setup lists from the transcripts before publishing |
| `python3 serve.py` | starts the tool server on stdio (an MCP client starts it this way) |
| `python3 scripts/transcript_own_server.py` | my scripted client against my server, both sides saved |
| `python3 scripts/transcript_claude_client.py` | Claude Code as the client, with only `score_posting` available |
| `python3 scripts/transcript_other_server.py <copy> [--blocked]` | the same client against a `git archive` copy of Lavanya's folder; `--blocked` runs it through `scripts/run_blocked.py` with the network blocked |
| `python3 scripts/shortlist_table.py` | rebuilds the claim tables in `SHORTLIST.md` from the saved replies and my labels |

## What ran

All on 2026-11-25. Times are UTC.

| When | What | Result | Evidence |
|---|---|---|---|
| 20:41 | Collection (the JS2 loop, unchanged) | 589 postings from 4 boards; `no-such-board` failed with HTTP 404 on purpose; run `incomplete` | `runs/20261125T204144Z/` |
| 20:45 | FILTER.md v1.0, approved by me, committed alone, before any filter code | | `d9b1cf1` |
| 20:48 | Filter v1.0 on all 589; the audit sample drawn and committed before any label | 7 keep, 582 reject, 0 cannot tell | `8b11679` |
| 20:55 to 20:57 | My 68 blind hand labels, in one pass | | `audit/hand-labels.csv` |
| after labelling | Two corrections at my request: non-US yes labels changed to no (2 rows) | | `audit/hand-labels.csv` (`original_label`, `correction` columns) |
| 21:00 to 21:05 | The audit and the candidate changes on the tuning sets; v1.1 committed before the held-out measurement | v1.0 35 of 48, v1.1 40 of 48 | `AUDIT.md`, `70ddf4b` |
| after `70ddf4b` | Every change alone on the held-out set | 13 of 20 for every version | `SCORE-REPORT.md` |
| 20:53 to 21:09 | Tool server transcripts: my client, Claude Code, and the other server | Claude called `score_posting` twice, with only that tool available | `transcripts/`, `EVAL-SERVERS.md` |
| 21:09:14 to 21:10:53 | The shortlist: 8 real Claude calls, all valid; then my labels on all 37 claims | 19 supported, 18 insufficient; the abstention rule lets only Android through, the counterexample | `SHORTLIST.md`, `runs/20261125T204144Z/shortlist-v1.1/`, `audit/claim-labels.csv` |
| 21:49 | My predictions for three constructed postings, then their test | 3 of 3 held | `tests/test_my_predictions.py` |
| 21:54 to 21:55 | My second pass on the 27 engineering postings of the tuning sets | 13 of 27 changed (yes to no); v1.0 agrees 21, v1.1 18 | `audit/reread-labels.csv`, `AUDIT.md` section 8 |
| 21:58 | Lavanya's server again, with the network blocked | the same 13 answers | `transcripts/client-other-lavanya-r-blocked-20261125T215826Z.jsonl` |
| 21:59 to 22:00 | Claude's verdicts on the 20 held-out postings, full posting and title only (40 real calls) | 13 of 20 both; 9 verdicts differ | `SCORE-REPORT.md` 2b, `runs/20261125T204144Z/judge-*/` |
| 22:01 | The tool server with the board list from config, with my client and with Claude | Claude called `score_posting` twice; the failed board answers "I cannot tell" | `transcripts/*-20261125T2201*` |
| 22:34 | The final tool server (after the review fixes), with my client and with Claude | the same; a list `params` is refused with -32602 and the session goes on | `transcripts/*-20261125T2234*` |
| 23:02 | Lavanya's server: the write check again, with its output saved | no file changed | `evidence/other-server-write-check.txt` |
| 23:09 and 23:16 | `claude mcp serve` probed in a sandbox (Read and Write only), twice: the first run hung on the last request, the second used a 20 s timeout | 28 tools, no annotations; Read and Write outside its folder with no prompt; no answer to a list `params` | `evidence/claude-mcp-serve-check.txt`, `transcripts/client-claude-mcp-serve-20261125T231622Z.jsonl` |

No collection was seeded: the postings come from one live run. Two random draws used a fixed seed so they can be repeated: the audit sample (20261125) and the order of the second-pass page (2026112502). Every fixture in `tests/` is labelled CONSTRUCTED.

## Tests (159, offline)

New in JS3 (79):
* `test_filter.py` (16): every gate, the score and threshold, the close calls, plain Engineer titles, the skill cap, whole words, "cannot tell" for a missing description or location, a filter file missing a key, a failed board never counted as rejected, and the v1.0 counts on the saved run.
* `test_filter_v1_1.py` (12): each v1.1 change against v1.0, on constructed postings and on the real postings behind it (the Lever country tag, the HELM false friend, the senior-in-text Ramp roles); the rejected change G is still rejected; the v1.1 count on the saved run; the two known word-rule limits (FILTER.md section 8).
* `test_my_predictions.py` (2): my own predictions for three constructed postings, made before the test, for v1.0 and v1.1.
* `test_judge.py` (6): Claude's context builder (the title context has no description), the reply validator, and the score.
* `test_run_blocked.py` (1): the network blocker really blocks a connection.
* `test_mcp_client.py` (2): my client records "no answer" from a silent server, and stops a server that never exits, instead of hanging.
* `test_filter_wrong_versions.py` (3): the three wrong versions in FILTER.md section 5 are each caught.
* `test_evidence.py` (13): the evidence rules, the fixed experience rule, and the abstention rule.
* `test_shortlist.py` (8): the reply validator (prose, wrong count, wrong mix, extra field), only shortlisted postings asked about, each reply saved before parsing, and an invalid reply never fixed.
* `test_toolserver.py` (16): the protocol (initialize, notifications, tools/list, unknown method and tool, parse error, params that are not an object, an unexpected error that must not end the session); the declared version is the one used; the tool scores like the filter, declares the boards from the config, answers "I cannot tell" for the failed board, refuses undeclared arguments, does not guess, makes no network connection, and writes only its transcript inside its folder.

Carried from JS2 (80): the loop, the permission policy, the independent check, the three board systems, the JS1 rule and résumé check, and the year ranges.

## Sign-off

`SIGNOFF.md`.
