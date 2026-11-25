# Job-Search Agent 3: The Filter, the Tool, and the Score

Yash Saraf · INFO 7375, Fall 2026 · persona: **Priya Nair (fictional)**

This layer decides which saved postings reach Priya and why. It has five parts:
- a filter written as a document before any code ([`FILTER.md`](FILTER.md));
- a hand-labeled audit of what the filter rejected and kept;
- a shortlist where every claim is checked against the posting's own text;
- a from-scratch tool server that Claude used in two real sessions;
- a one-change-at-a-time experiment on held-out labels.

It builds on my JS1 and JS2 work; see [`SOURCES.md`](SOURCES.md).

## Status

| Part | State |
|---|---|
| FILTER.md v1.0 → v1.1, written before code | Done (`f50b5001`, `9d78317d`) |
| Filter, tests, first full run, audit sample | Done (`c5dd2f44`) |
| My 60 audit labels | Done (`e926b963`) |
| Audit results, shortlist, tool server and evaluations, experiment set-up, docs | Committed (`e3166fe0`) |
| My 20 held-out labels, blind | Done (`810de710`), committed before the experiment report was run |
| **Trust decisions, rule-change decisions, sign-off, driver's seat, FRICTIONAL** | **Not done.** These are mine to write ([`SIGNOFF.md`](SIGNOFF.md), [`mcp/EVALUATION.md`](mcp/EVALUATION.md), [`experiments/RULE-CHANGE-LOG.md`](experiments/RULE-CHANGE-LOG.md), [`FRICTIONAL.md`](FRICTIONAL.md)) |

## Language and toolchain

- **Python 3.9.6** (`/usr/bin/python3` on macOS), **standard library only**: no packages to install. The tests also pass on Python 3.13.5.
- **Claude Code 2.1.331**, used only for the two live tool-server sessions, through its bundled command-line binary (see "Commands").
- **Input data:** the saved JS2 responses and fictional persona in `../js2-loop-tools-diff/`, read in place, never written. In a clone of the course repository, that folder sits next to this one. To run from the Canvas zip alone, unzip `Saraf_Yash_INFO7375_JS2.zip` next to it. No step uses the network.

## Commands

Run every command from this folder, with `PYTHONDONTWRITEBYTECODE=1` set (it keeps cache files out of the folder).

```bash
cd fall-2026/yash-s/js3-filter-tool-score
export PYTHONDONTWRITEBYTECODE=1

python3 -m unittest discover -s tests     # 103 tests
python3 wrong_versions.py                 # plants each FILTER.md section 9 wrong version; all must be caught

python3 run_filter.py                     # a NEW run folder under runs/ (create-only); the first run is committed
python3 audit_report.py                   # audit numbers from my labels -> audit/sample-…/audit-results.md
python3 shortlist.py                      # labeled claims -> shortlist/ (the CSV is create-only)
python3 experiment.py flips               # exact flips for each pre-registered change
python3 experiment.py report              # -> experiments/REPORT.md, from tuning + held-out labels

# Samples (already drawn; both refuse to overwrite an existing folder)
python3 sample_audit.py --run runs/filter-v1.1-2026-11-18T212545Z
python3 sample_audit.py --heldout experiments/flips-filter-v1.1-2026-11-18T212545Z.json \
    --exclude-sheet audit/sample-filter-v1.1-2026-11-18T212545Z/labeling-sheet.csv

# Tool server (stdio). A scripted client session, and a replay of any recorded session
python3 mcp_server.py
python3 mcp_client.py --steps mcp/probes/own-server.json --out mcp/transcripts/<new-name>.jsonl -- python3 mcp_server.py
python3 mcp/replay.py mcp/transcripts/server-session-2026-11-25T042642Z-8611.jsonl

# The live Claude session (uses my Claude Code account; this is how sessions 1 and 2 ran).
# `claude` was not on my PATH; I used the binary bundled with the VS Code extension:
#   ~/.vscode/extensions/anthropic.claude-code-2.1.331-darwin-arm64/resources/native-binary/claude
claude -p "$(cat mcp/claude-prompt.txt)" --mcp-config mcp/claude-mcp-config.json --strict-mcp-config \
  --tools "" --allowedTools "mcp__jobfilter__score_posting,mcp__jobfilter__search_saved_postings" \
  --output-format stream-json --verbose --no-session-persistence > mcp/transcripts/local-only/<name>.raw.jsonl
```

## What ran

All times are UTC.

| When | What | Result |
|---|---|---|
| 2026-11-18 21:25 | `run_filter.py` on all saved postings | 2,418 postings: 0 confirmed, 63 review, 2,355 rejected ([report](runs/filter-v1.1-2026-11-18T212545Z/report.md)) |
| 2026-11-18 | `sample_audit.py`, seed 20261118 | 60 postings in five groups; hand fields blank |
| 2026-11-24 | I labeled the 60 postings | Committed as `e926b963` |
| 2026-11-24 | `audit_report.py` | [audit-results.md](audit/sample-filter-v1.1-2026-11-18T212545Z/audit-results.md). 1 of 30 random rejects I would have kept (95% Wilson 0.6%–16.7%, a sample estimate). Named false friend `agentic systems`: removing it moves row 60 from review to rejected |
| 2026-11-24 | `experiment.py flips` | The baseline reproduced all 2,418 saved results exactly. Flips: X1 44, X2 8, X3 0 |
| 2026-11-24 | `sample_audit.py --heldout`, seed 20261124 | 20 blind held-out postings, all unlabeled |
| 2026-11-24 | `shortlist.py` | 120 claims: 104 on the 10 review candidates, 16 on two outside examples. Every claim labeled supported, contradicted or insufficient ([SHORTLIST](shortlist/SHORTLIST-filter-v1.1-2026-11-18T212545Z.md)) |
| 2026-11-25 04:18 and 04:26 | Two real Claude Code sessions using only my tool server | Both completed. Claude called the tools, declined to apply or write a file, and in session 2 found an undocumented tie order ([evaluation](mcp/EVALUATION.md)) |
| 2026-11-25 04:21 | The same robustness probe against my server and the Lesson 8 server | Both crashed on one deeply nested line. Mine was fixed and re-probed at 04:21:40 |
| 2026-11-25 | I labeled the 20 held-out postings, blind | Committed as `810de710` |
| 2026-11-25 | `experiment.py report` | X1 (threshold 55): 9 of 15 held-out flips improved; 95% Wilson 36%–80%, **inconclusive**. X2 (two topics): 5 of 5 held-out flips improved; all 8 of its flips are labeled, so it is a count, 7 better and 1 worse ([REPORT](experiments/REPORT.md)) |
| 2026-11-25 | Tests on Python 3.9.6 and 3.13.5; `wrong_versions.py` | 103 tests pass on both. Baseline passes, and 6 of 6 wrong versions are caught |

## Where each deliverable is

| Brief item | File |
|---|---|
| The filter as a versioned document | [`FILTER.md`](FILTER.md) |
| Code and tests | `*.py`, [`tests/`](tests/), [`rules/`](rules/) |
| Reject audit with my hand verdicts | [`audit/sample-…/labeling-sheet.csv`](audit/sample-filter-v1.1-2026-11-18T212545Z/labeling-sheet.csv), [`audit-results.md`](audit/sample-filter-v1.1-2026-11-18T212545Z/audit-results.md), the texts in `source-text.md` |
| Source-grounded shortlist and its labels | [`shortlist/`](shortlist/). Relevance versus entailment and the abstention counterexample are at the end of the SHORTLIST file |
| Tool server, transcripts, both evaluations | [`mcp_server.py`](mcp_server.py), [`mcp_client.py`](mcp_client.py), [`mcp/transcripts/`](mcp/transcripts/), [`mcp/EVALUATION.md`](mcp/EVALUATION.md) |
| One change at a time | [`SCORE.md`](SCORE.md), [`experiments/REPORT.md`](experiments/REPORT.md), [`experiments/RULE-CHANGE-LOG.md`](experiments/RULE-CHANGE-LOG.md), [`audit/heldout-…/`](audit/heldout-filter-v1.1-2026-11-18T212545Z/) |
| Sign-off and driver's seat | [`SIGNOFF.md`](SIGNOFF.md) |
| Sources, AI use, honest log | [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) |

## Tests

103 tests in 8 files. Every posting built inside a test is CONSTRUCTED, and labeled as such.

| File | Tests | What they protect |
|---|---:|---|
| `test_wrong_versions.py` | 14 | FILTER.md section 9 wrong versions: substring matching, counting boilerplate, US city locations, missing experience treated as eligible |
| `test_experience.py` | 20 | Rule 8: AND/OR units, preferred requirements, unrelated year counts, the CONSTRUCTED degree-dependent OR case |
| `test_decisions.py` | 20 | Rules 1, 5, 6 and the section 4 decision order; the two shortlists |
| `test_rules_and_data.py` | 6 | The rules files match FILTER.md; the saved data is complete |
| `test_sampler.py` | 6 | Reproducible audit and held-out draws; tuning postings never drawn again |
| `test_shortlist.py` | 9 | The claim checker's labels; the false-friend effect in the audit report |
| `test_experiment.py` | 11 | Exactly one value changes; flip judging; count versus estimate; interval values |
| `test_mcp_server.py` | 17 | Lifecycle, declared tools, argument checks, error codes, the deep-nesting regression, no outward imports, the only write being the transcript, a real subprocess session changing nothing else |

## Honesty labels

- **Past tense** means it ran, and the evidence is in this folder.
- **Every Claude response shown is one I actually got,** with its date and model (`SOURCES.md`).
- **Sample estimates are reported as ranges, never as rates for all postings.**
- The confirmed shortlist was empty, so wrong confirmations were not measured.
- The postings were saved on 2026-11-10 and may no longer be open.
- **The agent never applies, emails, messages or logs in.** The tool server can write only its own transcript, inside this folder.
