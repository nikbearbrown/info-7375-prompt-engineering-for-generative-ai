# Job-Search Agent 3 — The Filter, the Tool, and the Score

Saloni M · INFO 7375 · Fall 2026 · built and run 2026-11-26 (all run times UTC).

**Started from:** my own Job-Search Agent 2 (`../js2-loop-tools-diff/`). `js3/policy.py` and
`js3/fetch.py` are copied from JS2 (https, GET-only, two-host allow-list, writes only inside
`out/`). The boards are the same three. JS1 (`../js1-contract-and-watch/`) supplied the fictional
persona Priya Nair, the title keywords, the labeling rule, and the `claude -p` calling pattern.
No Reallocation Engine or Lectern code was used.

> **Status: hand labels and sign-off pending.** Everything a program or Claude can do has
> run. Nothing that needs Saloni's judgement has been filled in: the 57 dev audit verdicts, 30
> held-out labels, 72 claim reviews, the FILTER.md §6 decisions, and the sign-off.
> See "What is left" below.

| Read this | For |
|---|---|
| [FILTER.md](FILTER.md) | the filter as a versioned document, its reasons, evidence rules, sources, wrong versions (committed first, `e71f7177`) |
| [AUDIT.md](AUDIT.md) | the reject audit: seeded blind sample, the false friend `training`, candidates C1–C3 |
| [SHORTLIST.md](SHORTLIST.md) | 12 shortlisted postings, 72 Claude claims each labelled, relevance vs entailment, abstention and its counterexamples |
| [TOOL-SERVER.md](TOOL-SERVER.md) | the MCP server from scratch, real transcripts, and two evaluations (mine and `claude mcp serve`) |
| [SCORE.md](SCORE.md) | the origin of every number, one change at a time, persistence |
| [SIGNOFF.md](SIGNOFF.md) | sign-off (withheld until labelled) and driver's seat |
| [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) | what came from where · honest log |

## Language and toolchain

- **Python 3.13.5**, standard library only. No `pip install`, no virtualenv, no API key.
- **Claude Code CLI 2.0.20** (`claude -p`) for the Claude calls, model `claude-sonnet-5-5`
  (override with `CLAUDE_MODEL`). Only the shortlist and the experiments call Claude; the
  filter, the evidence checker, and the MCP server never do.
- macOS (Darwin 25.5), zsh. Built with Claude Code (desktop app, Claude Opus 5.5) on
  2026-11-26; see SOURCES.md.

## Exact commands

```sh
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/saloni-m/js3-filter-tool-score

python3 -m unittest discover -s tests -t . -v           # 32 tests, offline, < 1 s

python3 -m js3.collect                                  # live: 3 GETs -> out/snapshots/<UTC>/
python3 scripts/run_filter.py                           # filter v1.0 on the latest snapshot -> out/filter/v1.0/
python3 scripts/make_samples.py --seed 7375             # once; refuses to overwrite labels/*_sheet.csv

python3 scripts/label.py labels/audit_sheet.csv         # Saloni: 57 dev verdicts (blind)
python3 scripts/audit_report.py                         # errors per stratum, exact 95% intervals, word split
python3 scripts/experiments.py measure --sheet audit    # filter candidates C1-C3 on dev labels

python3 scripts/shortlist.py --n 12                     # 12 real Claude calls + claim labels
python3 scripts/label.py labels/claims_sheet.csv        # Saloni: agree/disagree with 72 claim labels

python3 scripts/mcp_client.py own                       # my server, audited, scripted calls
python3 scripts/mcp_client.py claude                    # Claude Code's `claude mcp serve`
python3 scripts/claude_uses_tool.py                     # Claude Code as client of my server (real call)
python3 -m js3.mcp_server                               # the server itself, on stdio

python3 scripts/experiments.py run                      # J0-J3: 120 real Claude calls
python3 scripts/label.py labels/heldout_sheet.csv       # Saloni: 30 held-out labels
python3 scripts/experiments.py measure                  # every variant vs held-out labels, once
```

A fresh clone uses the committed snapshot `out/snapshots/20261126T162725Z`. Running
`js3.collect` again adds a newer snapshot, and every later script uses the newest one, so the
samples and labels would no longer match. Re-collect only on purpose.

## What ran (2026-11-26)

| When (UTC) | What | Result | Evidence |
|---|---|---|---|
| 16:27:25 | live collection | 3/3 boards: anthropic 634, figma 141, openai 876 = 1,651 postings; 0 dropped, 0 short text | `out/snapshots/20261126T162725Z/collect_report.json` |
| 16:27 | filter v1.0 | 89 keep, 1,562 reject (759 vetoed by seniority) | `out/filter/v1.0/summary.json` |
| 16:28 | seeded samples (seed 7375) | 57 dev, 30 held-out, blind sheets | `labels/` |
| 16:30:46 | my MCP server, my client, audit hooks | 9 tool calls as expected; 0 network/subprocess events; only write = its own transcript | `out/mcp/*163046Z*` |
| 16:30:59 | `claude mcp serve`, my client | 16 tools, no annotations; Read ran without a prompt | `out/mcp/client-claude-mcp-serve-*` |
| 16:31:50 | Claude Code as client of my server | 1 search + 1 score; Claude then wrongly said it searched twice | `out/mcp/claude-client-*`, `out/mcp/transcripts/20261126T163150*` |
| 16:33 | shortlist, 12 Claude calls | 72 claims: 45 supported, 0 contradicted, 27 insufficient; 5 of 12 "I cannot tell" | `out/shortlist/shortlist.json` |
| 16:34:50–16:37:21 | J0–J3, 120 Claude calls | context change moved 24/30 verdicts; prompt 3/30; tools 3/30 | `out/experiments/` |
| — | candidates C1–C3 on all 1,651 | C1: 0 flips; C2: 34 keeps → reject; C3: 12 keeps → reject | `out/filter/C*/` |

## What is left (Saloni)

1. `python3 scripts/label.py labels/audit_sheet.csv`, then `python3 scripts/audit_report.py`. Fill
   AUDIT.md §2 from `out/audit_report.json` and confirm or reject the false friend (§3).
2. `python3 scripts/experiments.py measure --sheet audit`. Decide C1–C3 and write the outcome
   into FILTER.md §6 (and a v1.1 if any is adopted).
3. `python3 scripts/label.py labels/claims_sheet.csv` and note the disagreements in SHORTLIST.md §1.
4. `python3 scripts/label.py labels/heldout_sheet.csv`, then `python3 scripts/experiments.py measure`.
   Fill SCORE.md §3.
5. Write FRICTIONAL.md Part A. Edit, then sign or withhold, SIGNOFF.md.
6. Push the branch. Put the folder link and final commit hash in Canvas.
