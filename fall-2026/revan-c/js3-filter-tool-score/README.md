# Job-Search Agent 3 — The Filter, the Tool, and the Score

INFO7375 · Revan C. · gate in [FILTER.md](FILTER.md) · Chapters 7–9

A readable filter over the postings Job-Search Agent 2 collected, a reject audit and source-grounded shortlist I checked, a read-only tool server Claude can call, and one-change-at-a-time measurements of the filter and Claude conditions. The persona is fictional (`@example.com`, `555` phone). Nothing here applies, emails, messages, or logs in. The filter and tool server read a saved snapshot; the Claude conditions called an API with a key set in the local shell.

**Started from:** my Job-Search Agent 2 in this repository (its documents are now `JS2_README.md`, `JS2_SOURCES.md`, `JS2_FRICTIONAL.md`, `JS2_SIGNOFF.md`; JS1's are `JS1_*`). JS3 reuses JS2's saved snapshot, JS1's persona, JS1's text normalization (`jsagent/text.py`), and JS1's Claude judge and prompts. The filter, shortlist, tool server, and measurements are new, in `jsfilter/` and `tools/js3_*`. I did not use the Reallocation Engine or Lectern code. The other tool server evaluated is the Chapter 8 teaching server, copied unmodified into `third_party/`.

## Toolchain

- Python **3.12.14** (Homebrew, macOS) in `.venv`. The filter and server use the standard library only.
- `pytest==9.2.0`, `jsonschema==4.26.0`, `anthropic==2.3.0` (`requirements.txt`). Only the `claude_*` conditions call Claude and need `ANTHROPIC_API_KEY`.
- The teaching-server check script runs that server with the system `python3` (3.9.6 on this machine), in a temp folder.

## Setup

```bash
python3.12 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

## Commands

Every test (JS1, JS2, JS3):

```bash
.venv/bin/python -m pytest -q
```

Check that every FILTER.md wrong version (W1–W5, S1–S3) is caught by its named test:

```bash
.venv/bin/python tools/check_wrong_versions_js3.py
```

Run the filter on the snapshot and draw the audit sample (writes `runs/js3/filter_v1/`; deterministic). Once the label sheet has reviewed verdicts, this command refuses to overwrite it:

```bash
.venv/bin/python tools/js3_filter_run.py
```

Reject audit numbers from the hand verdicts:

```bash
.venv/bin/python tools/js3_measure.py audit
```

One change at a time (dev, then held-out once):

```bash
.venv/bin/python tools/js3_measure.py run --condition filter_v1 --set dev
```

```bash
.venv/bin/python tools/js3_measure.py run --condition filter_v1 --set held_out --final
```

Shortlist claims: I confirmed all 50 atomic labels in `runs/js3/shortlist/CLAIMS.csv`; `runs/js3/shortlist/SHORTLIST.md` renders them, and `SHORTLIST_ANALYSIS.md` explains the relevance-versus-entailment cases. Re-render with:

```bash
.venv/bin/python tools/js3_shortlist.py render
```

Tool server, scripted session through the recording tap:

```bash
.venv/bin/python tools/js3_mcp_client.py --label own-scripted -- .venv/bin/python -m jsfilter.mcp_server
```

Teaching server, scripted session and checks:

```bash
.venv/bin/python tools/js3_mcp_client.py --label teaching-scripted --script teaching -- .venv/bin/python -I third_party/ch8_teaching_server/main.py --stdio
```

```bash
sh tools/js3_teaching_checks.sh
```

**Claude as the client:** `.mcp.json` registers `js3-score-posting` for Claude Code sessions opened in this folder. It runs the server through `tools/mcp_tap.py`, which appends both directions to `runs/js3/transcripts/claude_code_session.jsonl`.

## What ran

The rows below link to saved local run evidence. Work after `d777c9d` remains uncommitted under the current no-commit instruction.

| What | When (UTC) | Result | Record |
|---|---|---|---|
| Filter v1 on the snapshot | 2026-11-25 | 215 scored (149/61/5, as FILTER.md expected): 4 kept, 1 below threshold, 210 hard-rule rejects, 0 unscorable; 15 closest calls | `runs/js3/filter_v1/summary.json` |
| Wrong-version check | 2026-11-25 | first run 10/11 caught (W1 survived); after strengthening the W1 test, 11/11 | `runs/js3/wrong_versions/` |
| Own server, scripted | 2026-11-25 22:06 | all 6 FILTER.md predictions matched | `runs/js3/transcripts/…own-scripted.jsonl` |
| Teaching server, scripted + checks | 2026-11-25 22:06, 22:09 | its 6 tests pass; its ready-on-initialize mutant also passes them | `runs/js3/transcripts/` |
| Real Claude Code client call | 2026-11-26 01:08 | Claude Code 2.1.330 called `score_posting(klaviyo, 8041054003)` through the tap; score 7, fate kept; client-session model not captured | `runs/js3/transcripts/claude_code_session.jsonl` |
| Reject audit after I confirmed 47 verdicts | 2026-11-26 00:46 | 0/30 random rejects wrongly rejected; 0/15 closest calls wrong; 2/4 kept postings wrongly kept | `REJECT_AUDIT.md`, `runs/js3/experiments/audit_report.json` |
| Deterministic score comparisons | 2026-11-26 00:46–00:47 | baseline, threshold 5, and R5 without `platform`: each 10/11 development and 11/11 held-out agreement; no variant adopted | `SCORE_REPORT.md`, `runs/js3/experiments/` |
| Claude prompt/context comparisons | 2026-11-26 01:24–01:28 UTC | baseline 11/11 dev and 11/11 held-out; revision 11/11 and 11/11; excerpts 10/11 and 11/11, with A41 false positive on dev | `SCORE_REPORT.md`, `runs/js3/experiments/` |
| Shortlist claim review and render | 2026-11-26 00:55 | 50 atomic claims: 11 supported, 5 contradicted, 34 insufficient; 0 unreviewed | `runs/js3/shortlist/CLAIMS.csv`, `SHORTLIST.md`, `SHORTLIST_ANALYSIS.md` |
| Final local recheck | 2026-11-26 UTC | 142 tests passed; all 11 wrong versions caught | `runs/js3/final_checks/` |

## Remaining limits

The tool server has scripted transcripts and a real Claude Code client transcript in `runs/js3/transcripts/claude_code_session.jsonl`. The three Claude prompt/context conditions each ran once on development and once on held-out labels. `SIGNOFF.md` signs the local implementation and saved evidence while listing the final archive, GitHub folder, and Canvas upload as unchecked. The local package has not been matched to a GitHub class folder or submitted to Canvas; the no-commit instruction remains in force.
