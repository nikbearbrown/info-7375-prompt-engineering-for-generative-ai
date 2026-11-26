# SOURCES: Job-Search Agent 3

## What I used

| Source | Used for | Terms |
|---|---|---|
| The JS3 assignment brief and course Chapters 7 to 9 | the task, the sign-off template, the grading parts | course material |
| My JS2 work, `fall-2026/pavithra-p/js2-loop-tools-diff/` at `bf7fe97` | the starting point: the collector, the permission policy, the JS1 rule and the persona, copied unchanged in `e02dffe` | my own work |
| [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html), `boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | Pinterest and Figma | public, no login; one GET per board |
| [Lever Postings API](https://github.com/lever/postings-api), `api.lever.co/v0/postings/{company}?mode=json` | Spotify, and `no-such-board` (fails on purpose) | public, no login; one GET per board |
| Ashby public job posting API, `api.ashbyhq.com/posting-api/job-board/{board}` | Ramp | public, no login; one GET per board |
| [The Reallocation Engine](https://github.com/nikbearbrown/the-reallocation-engine) `search/examples/aarav-patel/`, commit `d08afdd` | the fictional persona (renamed Rohan Mehta in JS1) | course repository |
| [MCP specification, server tools, version 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/server/tools), read 2026-11-25 | the message shapes (`initialize`, `tools/list`, `tools/call`), unknown tools as error -32602, and annotations being untrusted | public specification |
| Lavanya Rajesh's tool server `js3-postings`, `fall-2026/lavanya-r/js3-filter-tool-score/mcp/server.py` in the course repository, Lavanya's folder at `d32b8bc` | the second server I evaluated (`EVAL-SERVERS.md`). I ran it from a `git archive` copy outside my folder; none of its code is in my folder | course repository |
| Claude Code 2.1.294's own MCP server, `claude mcp serve` (installed on my machine) | the third server I evaluated (`EVAL-SERVERS.md` section 4), using only Read and Write on made-up files in a throwaway folder. The idea came from Ashwin T.'s JS3 (`fall-2026/ashwin-t/js3-filter-tool-score/evaluations/other-server/`), which I saw while comparing our work. Only the idea was used; no code or text was taken | my NEU Claude Code access |
| Python 3.13.1 standard library | all code and tests | PSF licence |
| Claude Code 2.1.294, model `claude-opus-5-5` | writing the code and tests, the shortlist claims, and Claude as the tool client (below) | my NEU Claude Code access |

I also looked at the file lists and FILTER.md section headings of two classmates' JS3 folders (`tushar-p`, `anisha-g`), and at which server two classmates evaluated (`rayudu-h`, `anisha-g`: the official filesystem server). This was for layout only, and to choose a different second server. No text or code was taken.

## What I made

* Approved FILTER.md v1.0 before any filter code (`d9b1cf1`), and decided version 1.1, including rejecting change G against my own labels.
* The 68 blind posting labels (`audit/hand-labels.csv`), and the request to correct my non-US yes labels to no (two changed).
* The 37 claim labels (`audit/claim-labels.csv`), and the five changes after review (#29, #32, then #6, #8, #14).
* The 27 second-pass labels (`audit/reread-labels.csv`), and my predictions for three constructed postings (`tests/test_my_predictions.py`).
* The decision to keep v1.1 after my second pass preferred v1.0.
* Kept Claude Code's choice of Lavanya's server as the one to evaluate.
* The sign-off's signature, and the two reflections in `FRICTIONAL.md` ("Expected" and "Learned"), in my own words. After a review I changed one phrase in "Learned" from "correctly classified" to "agreed with my labels on".
* No AI decided my posting labels, my second-pass labels or my claim labels; I typed the claim labels to Claude Code as a numbered list.

## What Claude contributed

Claude Code (Opus 5.5) in this session:
* drafted FILTER.md v1.0 from my JS1 rule, for my approval, and the v1.1 section from the tuning results;
* wrote all the new code: `filter.py`, `evidence.py`, `shortlist.py`, `audit.py`, `toolserver.py`, `mcp_client.py`, `claims_page.py`, `collection.py`, `filter_wrong_versions.py`, `serve.py` and `scripts/`;
* wrote all the new tests except the predictions in `test_my_predictions.py`, and the labelling pages;
* ran the collection, the filter, the sample draw, the audit, the tuning comparison and the held-out measurement, and recorded the transcripts;
* applied the location correction I asked for, which changed two labels;
* checked the MCP specification with a web-fetch agent;
* read Lavanya's server code before running it, and found the differences in `EVAL-SERVERS.md`;
* pointed out that my labels said yes to non-US, Staff and Intern postings, and that two of my claim labels did not follow my own rule;
* graded the draft as a strict TA and listed fixes; then built the second-pass page, the prediction test, the blocked-network runner, the board list from config, the checker fix and the Claude context test;
* drafted `README.md`, `AUDIT.md`, `SHORTLIST.md`, `SCORE-REPORT.md`, `EVAL-SERVERS.md`, `SIGNOFF.md` and this file, and drafted `FRICTIONAL.md` from what I did and decided. The "Expected" and "Learned" lines in it are my own words.

Claude through `claude -p`, a separate call with no tools:
* wrote the 37 shortlist claims and quotes (`runs/20261125T204144Z/shortlist-v1.1/claude/`, 2026-11-25, 21:09 to 21:10 UTC);
* gave the 40 held-out verdicts, 20 with the full posting and 20 with the title only (`runs/20261125T204144Z/judge-full/`, `judge-title/`, 21:59 to 22:00 UTC);
* acted as the MCP client of my server, with only `score_posting` available (`transcripts/claude-client-*.jsonl`).

Claude Code also ran an independent strict-TA review of the folder with a separate agent (re-running the tests and scripts from a copy), then made the fixes it found (listed in `EVAL-SERVERS.md`, `AUDIT.md` section 8 and `SCORE-REPORT.md` section 3), including the transcript redaction and the saved write check.

## Other AI

* ChatGPT reviewed my drafts three times as a strict TA (2026-11-25), using a zip and a prompt Claude Code prepared. I pasted its findings back, and Claude Code checked each one against the files and fixed the real ones. These included the server crash on a list `params`, the cached filter version, the two word-rule limits (now documented), a client that could hang, and wording slips. ChatGPT did not write any file here.

## Constructed or real

* Real: the collection (`evidence/raw/`, `runs/20261125T204144Z/`), every Claude reply, every transcript, and my label files, each with its date and time.
* Constructed, and labelled CONSTRUCTED: every test fixture in `tests/`.
* No collection was seeded: the postings come from one live run. The audit sample and the second-pass order were drawn with fixed seeds (20261125 and 2026112502), so they can be drawn again.
* The persona is fictional. My real résumé, contacts and conversation transcripts are not in this folder.
