# Sources and contributions

## What was used

- **The brief:** the Canvas text, pasted by Shreyash on 2026-11-25. The course repository's copy,
  `assignments/assignment-js3-the-filter-the-tool-and-the-score.md`, was read the same day.
- **Starting point:** my JS2 folder `fall-2026/shreyash-y/js2-loop-tools-diff`, at the submitted commit
  `177d5a8`. `jsagent/`, `tests/`, `demo/`, `persona/`, `boards.json`, `budgets.json`, `GATE.md` and
  `GATE-NOTES.md` were copied unchanged in `07075a6d`.
- **From JS1** (`bb193d9`):
  - The two judge prompts were copied byte for byte into `prompts/` (sha256 `60bc794a…` and
    `827c5127…`; the first matches JS1's own call records).
  - `jsagent/claude_judge.py` and `jsagent/validator.py` were adapted into `js3/judge.py`, so that ids
    are strings.
- **Lectern** (the instructor's, `fall-2026/nik-bear-brown/lectern/`): `keywords.json`, where the filter
  is a file and every added or cut word is measured, and `audit_rejects.py`, the two-part reject sample
  (uniform, plus closest calls). Both were read on 2026-11-25. No code was copied.
- **Boards:** the public job-list endpoints of Greenhouse (oscar, klaviyo), Ashby (linear) and Lever
  (palantir, whoop, and the deliberately non-existent oscarhealth-doesnotexist).
  - Today's live run is `runs/20261125T220655Z/`.
  - JS2's three runs were read from the JS2 folder. The raw job objects of the 152 postings that closed
    since are kept in `data/inherited/js2-postings.json`, with the run, file and sha256 they came from.
- **The other tool server:** `chrome-devtools-mcp` 1.10.1 from npm. Its author is Google LLC, its licence
  Apache-2.0, and its repository is https://github.com/ChromeDevTools/chrome-devtools-mcp. It was
  already in this Mac's npx cache from earlier use, and nothing was downloaded for this assignment.
- **MCP:**
  - The message shape (JSON-RPC 2.0 over stdio; `initialize`, `notifications/initialized`,
    `tools/list`, `tools/call`; protocol versions 2025-06-18, 2025-03-26 and 2024-11-05) came from
    Claude Code's knowledge of the published specification. No MCP SDK was used.
  - What a real client actually sends came from the saved transcripts.
- **Classmates:** one classmate's JS3 commit subjects, and the file names in one of those commits, were
  visible in the course repository's `git log` on 2026-11-25. None of their files was opened, and
  nothing was taken.
- **Tools:**
  - Python 3.14.6 standard library;
  - Claude Code (model `claude-opus-5-5`) as the coding agent;
  - the `claude` CLI 2.1.331 for every Claude run (opus, plus haiku in condition S);
  - Node 24.22.2 and Google Chrome 157 (headless, temporary profile) for chrome-devtools-mcp;
  - `git`, `shasum`.

## What Shreyash wrote or decided

| Part | Where |
|---|---|
| FILTER.md v1: answers 1–13 (16:58 EST) and the follow-up reasons and decisions A–C (17:05 EST). Claude Code changed formatting only and added labeled quotes of his earlier documents. | `FILTER.md` (`5e6a7703`, `3163fdb5`) |
| All 70 hand verdicts, with his reasons, including the 4 he changed after seeing more of an ad | `labels/hand-verdicts.jsonl` (frozen in `667a2932`) |
| The v1.1 decisions after measuring: adopt A1, A2, A4 and B4; reject A3 and A5 | FILTER.md "Version 1.1" (`61e0d4c0`) |
| The three claim labels where the code and Claude disagreed, and the B4 evidence-rule exception | SHORTLIST.md section 4 |
| Both trust decisions | TOOLSERVER.md, sections 2 and 3 |
| The README summary and the "why the judgment stays mine" paragraph | `README.md` |
| Part 1 of FRICTIONAL.md | `FRICTIONAL.md` |
| The signature | the sign-off in `README.md` |

## What Claude Code contributed

| Part | Notes |
|---|---|
| All new code in `js3/` and all new tests (`tests/test_js3_*`) | The filter's, v1.1's and each fix's tests were committed before the code they test. The tool server's tests were written after the server. |
| `FILTER-NOTES.md`, the reading of FILTER.md as code | Each choice FILTER.md did not force is marked **choice**. |
| The audit draw, the blind labeling tool, and the chat batches shown to Shreyash | It was Claude Code's excerpts that once hid a requirement (AUDIT.md section 3). |
| Every measurement, and the "Measured" lines in FILTER.md v1.1 | One of them ("36") was stated before it was run; it carries a dated correction. |
| Running the live collection, the four MCP sessions, the chrome-devtools-mcp check, and all Claude runs | at Shreyash's request in this assignment |
| The read-only source audit of chrome-devtools-mcp | by a Claude Code helper that ran no code |
| Drafts of `README.md` (except the summary, the driver's seat paragraph and the signature), `AUDIT.md`, `SHORTLIST.md`, `TOOLSERVER.md`, `SCORE.md`, this file, and Part 2 of `FRICTIONAL.md` | written from the files |

## Claude runs, all on 2026-11-25 (EST)

Each was a fresh `claude -p` session from an empty folder, with no settings files and no saved session.

| Run | Calls | Model | Cost (USD) |
|---|---|---|---|
| Tool sessions 1–3 (TOOLSERVER.md) | 3 | claude-opus-5-5 | 0.15 |
| Judge conditions B, B2, B3, P, C, T (SCORE.md) | 144 | claude-opus-5-5 | 4.60 |
| Judge condition S | 24 | claude-haiku-5-5 | 0.03 |
| Independent claim labels, runs 1 and 2 (SHORTLIST.md) | 10 | claude-opus-5-5 | 0.58 |
| One smoke test of the judge before the conditions ran (17:27; its output was printed in the session and not saved) | 1 | claude-opus-5-5 | 0.05 |
| **Total** | **182** | | **5.41** |
