# Job-Search Agent 3: The Filter, the Tool, and the Score

INFO 7375 (Prompt Engineering and Agentic AI), fall 2026. Student: Deepak Kumaran T S. Persona: Riley Okafor, fictional (examples/persona_resume.json, @example.com).

## Starting point

- Started from my JS2 agent, personal repository commit b2ac533 (fall2026/deepak-kumaran-ts/js2-loop-tools-diff/), which carries the JS1 RECORD rule (JS1 commit b91c877). Lectern and the Reallocation Engine were not used.
- Imported from b2ac533 by `git archive`, byte-identical (90 files, `git hash-object` checked; commit 8aa2498): jobwatch/, tests/, scripts/, requirements.txt, pytest.ini, and, as a stated exception, the non-code files the JS2 tests read: examples/persona_resume.json, schema/resume.schema.json, prompts/README.md, prompts/v1.md, prompts/v2.md, fixtures/seeded/ (with SEEDED_README.md), evidence/manual-capture/20261110T184001Z/01-07 .body, evidence/manual/stripe_20261030T000804Z.raw, labels/make_split.py. JS2's runs/ and other evidence were not imported. config/budgets.json is byte-identical to b2ac533.
- FILTER.md provenance: sections 3 to 7 were drafted in a claude.ai chat (Claude Opus 5.5, 2026-11-25); sections 0 to 2 were formatted in a claude.ai chat from Deepak's answers; Deepak's edits and gate decisions, some worded with a claude.ai chat, are recorded in FILTER.md's provenance line and changelog; Claude Code worded the F07 to F09 "What it gets wrong" cells, which Deepak approved.

## Language and toolchain

- Python 3.15.0, standard library plus the pinned requirements: anthropic 2.3.0, jsonschema 4.26.0, pytest 9.2.0 (requirements.txt). No Anthropic API key is used.
- The Claude judge: Claude Code CLI 2.1.332 (`claude -p`) through the JS1 claude-cli backend's argv and environment (jobwatch/judge_cli.py, jobwatch/claude_judge.py), model claude-sonnet-5-5.
- The tool server: written from scratch with the standard library (jobwatch/mcp_server.py), Model Context Protocol revision 2026-07-28 over stdio.
- Phase 5e only: Node.js v24.21.0 and npm 11.19.0, to run the official filesystem reference server 2.3.0 in a /tmp sandbox.
- One entry point: `python -m jobwatch <command>`.

## Commands

Fresh clone, setup and tests (one command per line):

```
git clone https://github.com/DeepakKTS/INFO-7375-Prompt-Engineering-Agentic-AI.git
cd INFO-7375-Prompt-Engineering-Agentic-AI/fall2026/deepak-kumaran-ts/js3-filter-tool-score
python3.15 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
bash scripts/presubmit_check.sh
```

Rebuild from the committed run, offline (each writes the same files that are committed):

```
.venv/bin/python -m jobwatch verify runs/20261125T200226Z
.venv/bin/python -m jobwatch dataset --run runs/20261125T200226Z
.venv/bin/python -m jobwatch filter --dataset data/postings-20261125T200226Z.jsonl --version v1
.venv/bin/python -m jobwatch audit-stats --sheet audit/audit-v1.csv --filter data/filter-v1.jsonl --dataset data/postings-20261125T200226Z.jsonl
.venv/bin/python scripts/clopper_pearson_check.py 9 30
.venv/bin/python -m jobwatch measure-change --change C1 --sheet audit/snapshots/audit-v1@65c9863.csv --dataset data/postings-20261125T200226Z.jsonl
.venv/bin/python -m jobwatch experiment-filter --dataset data/postings-20261125T200226Z.jsonl --heldout-seed-a 7375011 --heldout-seed-b 7375012
.venv/bin/python -m jobwatch experiment-report --dataset data/postings-20261125T200226Z.jsonl --heldout-seed-a 7375011 --heldout-seed-b 7375012
```

Note: the final audit verdicts are the third pass, `audit/snapshots/audit-v1@65c9863.csv` (byte-identical to `audit/audit-v1.csv` at 65c9863). `audit/audit-v1.csv` at HEAD holds the unused fourth pass (f0568bc, 4 of 45 verdicts), so `audit-stats` on it does not reproduce the committed facts; the committed facts were generated from the 65c9863 sheet.

Live or one-time commands (network, Claude calls, or drawn once):

```
.venv/bin/python -m jobwatch loop --config config/boards.json
.venv/bin/python -m jobwatch heldout --dataset data/postings-20261125T200226Z.jsonl --seed-a 7375011 --seed-b 7375012
.venv/bin/python -m jobwatch audit-sheet --dataset data/postings-20261125T200226Z.jsonl --filter data/filter-v1.jsonl --seed 7375031 --heldout-seed-a 7375011 --heldout-seed-b 7375012
.venv/bin/python -m jobwatch label audit/audit-v1.csv
.venv/bin/python -m jobwatch shortlist --dataset data/postings-20261125T200226Z.jsonl --filter data/filter-v1.jsonl
.venv/bin/python -m jobwatch experiment-judge --dataset data/postings-20261125T200226Z.jsonl --heldout-seed-a 7375011 --heldout-seed-b 7375012 --arm title_text --run 1
```

`heldout` and `audit-sheet` refuse to run when their sheet exists (drawn once). The `label` command is Deepak's; it also takes `--clear`, `--checklist` or `--family`.

Tool server and the real client:

```
claude mcp add -s project jobwatch-js3 -- .venv/bin/python -m jobwatch mcp-server --dataset data/postings-20261125T200226Z.jsonl
claude -p --mcp-config .mcp.json --strict-mcp-config --allowedTools mcp__jobwatch-js3__score_posting --permission-mode dontAsk --no-session-persistence --output-format json "Use the score_posting tool to score greenhouse:stripe:8187574"
```

`.mcp.json` (committed) already holds the registration. The other server's run: scripts/run_other_server.py, as recorded in evidence/mcp/other-server/install.md.

## What ran (from committed files)

All on 2026-11-25 in this session, by Claude Code unless marked Deepak.

- Manual capture of 5 board endpoints, all HTTP 200, 1284 postings (evidence/manual-capture/CAPTURE.md, commit 3fe5a78).
- Collection: one live run, `runs/20261125T200226Z`, exit INCOMPLETE (3) as FILTER.md section 5 predicts: stripe 772, lever 6, palantir 305, linear 30, notion 172, stripe-js2-nonexistent HTTP 404 (commit 339fb49). verify: CLEAN.
- Dataset: 1285 postings, 25128 of 67401 body sentences boilerplate (data/postings-20261125T200226Z.meta.json, commit f0e59c7).
- Held-out set: 40 postings, stratum A 30 of a pool of 78 (seed 7375011), stratum B 10 of 421 (seed 7375012), drawn before any filter code (commit 30c52ef); labeled by Deepak (first pass, commit 8625eea); committed empty in e6fe828 after a `label --clear`; restored to the first-pass labels in 3d130ae, which the held-out report uses.
- Filter v1: keep 3, reject 1282, abstain 0, plus one board-level abstention (data/filter-v1.jsonl, commit e9573dc).
- Reject audit: 45 rows (3 close-call keeps, 30 random rejects, 12 near-decision rejects; no scored rejects existed). Deepak's verdicts: the third pass (checklist, commit 65c9863) is final; a fourth, family-mode pass was committed in f0568bc with 4 of 45 verdicts and is not used. Random-reject misses 9/30, exact 95% interval [0.1473, 0.4940], recomputed independently (AUDIT.md, commit fb02ee4).
- Rule changes C1 to C5 measured on the audit rows only; all rejected by Deepak's pre-set criterion, so the final filter is v1 (FILTER.md section 8; audit/changes/).
- Shortlist: 3 postings, 29 claims (23 from rules, 6 from 3 Claude judge calls, claude-sonnet-5-5); checker pre-labels all "quote found, not boilerplate"; Deepak labeled all 29 claims supported (shortlist/claims.csv, commit cec6a48); 0 disagreements with the pre-labels.
- Tool server: protocol probe (Claude Code's first message is server/discover, 2026-07-28; commit 4680a75); one real `claude -p` session scored two postings through it (evidence/mcp/transcripts/20261125T212227026816Z.jsonl, commit ae74ac0).
- Second server: @modelcontextprotocol/server-filesystem 2.3.0, run once in a /tmp sandbox with our scripted client (evidence/mcp/other-server/, commit 4bcabca).
- Experiments: E1 and E2 decisions on the 40 held-out postings (commit 3f782ce); E3: 120 Claude judge calls on the held-out postings, title+text twice then title only; every answer not_relevant, 0 of 40 moved between the identical runs and 0 of 40 between baseline and change, so no conclusion can be drawn (commit fefe60e). Deepak ran `experiment-report` (commit db0670b): held-out labels relevant A 20/30, B 8/10; every filter and judge arm agrees with them on A 10/30 and B 2/10, recall A 0/20 and B 0/8 (experiments/results.md).
- Tests: `.venv/bin/python -m pytest -q`: 738 passed in 5.42s (JS1 and JS2 tests unchanged from b2ac533; tests/js3/ added).

## Contents

| Path | What |
|---|---|
| FILTER.md | the filter as a versioned document, evidence and abstention rules, sources, wrong versions, held-out design, changelog |
| AUDIT.md | the reject audit (facts; Deepak's sections 7 to 9) |
| SHORTLIST.md | the source-grounded shortlist (facts; Deepak's labels and conclusions) |
| MCP_EVAL.md | both tool servers, declared versus actual (Deepak's trust decisions) |
| SCORE.md | origins of every number and the one-change-at-a-time experiments |
| SOURCES.md, SIGNOFF.md, FRICTIONAL.md | sources; Deepak's sign-off and driver's seat; Deepak's log |
| jobwatch/ | the agent: JS2 loop and policy, plus text.py, dataset.py, filter.py, audit.py, auditstats.py, measure.py, shortlist.py, claude_judge.py, label.py, heldout.py, sheets.py, stats.py, experiments.py, mcp_server.py, mcp_probe.py, js3cli.py |
| tests/ | JS1 and JS2 tests unchanged; tests/js3/ for this assignment |
| scripts/ | clopper_pearson_check.py (independent interval), mcp_client.py (scripted client), run_other_server.py, presubmit_check.sh |
| config/, runs/, state/, data/ | boards and budgets; the live run; loop state; dataset, filter output, posting texts |
| labels/, audit/, shortlist/, experiments/ | held-out sheet; audit sheet, facts and measured changes; claims and judge calls; Phase 6 outputs |
| evidence/ | manual capture, MCP spec pages, CLI help, probe, client session, transcripts, other server |
| prompts/ | js3_claims_v1.md and js3_relevance_v1.md (JS3); v1.md and v2.md (JS1, imported) |

## Disclosures

- Process: Claude Code ran Step 2 (the rule-change measurements, the shortlist and everything after) without waiting for Deepak's "labels done" message, and did not stop at Gate 4a for the claim labels; Deepak had asked it to continue without further relabeling. Deepak labeled the claims afterwards (cec6a48).
- Final audit verdicts: the third pass (65c9863) contains 15 checklist answers that contradict the question wording (8 seniority answers y on titles with Manager, Intern or Staff; 8 location answers y on locations outside the list; one row has both; AUDIT.md section 1).
- Held-out labels: the first pass (8625eea), never relabeled. They were committed empty in e6fe828 (16:09 ET) after a `label --clear`, and restored to the first-pass content in 3d130ae (16:42 ET); the held-out report (db0670b) was run on the restored labels.
- A wrong statement by Claude Code: from Phase 6 on (Phase 6 notes, SCORE.md section 2, this README and the Gate 7 report, 16:2x to 16:33 ET), Claude Code said the held-out labels in use were those committed in 8625eea, without checking the file's history again; at that time the committed file was the emptied e6fe828. Its one check, at about 16:06 ET, came before e6fe828 and showed 8625eea as the latest commit.
- Held-out set: while checking the format of the freshly drawn `labels/heldout.csv` (before Deepak labeled it, before any filter code), Claude Code printed its first 7 lines once, showing one posting's key, title and location. Later, the real-client `claude -p` session (not in safe mode) searched `labels/heldout.csv` for two posting keys on its own (MCP_EVAL.md section 1.4). No rule, weight, threshold or prompt was chosen from the held-out set. In Phase 6, Claude Code's permission check refused to let it open `labels/heldout.csv`, so Deepak ran `experiment-report` (db0670b).
- Labels: the audit verdicts went through three passes (the first two replaced after a consistency check found answers contradicting the labeling rule's wording; the final third pass still has 15 such answers, AUDIT.md section 1). A fourth, family-mode pass was committed in f0568bc with 4 of 45 verdicts; it is not used.
- Exceptions to "all disk and network access through jobwatch/tools.py": the Claude judge runs `claude -p` through the JS1 claude-cli backend (a JS1 module imported under JS2 Amendment A-1) from an empty temporary directory; the npm install, the GitHub source download and the spec-page fetches were development actions by Claude Code, outside the agent's allow-list. The policy gained optional per-command read and write folders and the tools an opt-in rewrite and append list; their defaults keep JS2's behavior.
- A test file I added (tests/js3/test_js3_mcp_probe.py) was committed failing once (bc396ea) and fixed in the next commit (6f374b9).

## Credits

- Claude Code (model claude-opus-5-5, Claude Code 2.1.332) wrote the code, tests, scripts and the fact sections of the documents, ran every command listed under "What ran" unless marked Deepak, and proposed review items that Deepak accepted, changed or rejected at the gates.
- A claude.ai chat (Claude Opus 5.5) drafted FILTER.md sections 3 to 7, formatted sections 0 to 2 from Deepak's answers, and worded some of Deepak's Gate 1 decisions.
- Deepak decided the boards, the filter rules, weights and threshold, every label and verdict, the rule-change criterion, and writes FRICTIONAL.md, SIGNOFF.md and every section marked as his.
