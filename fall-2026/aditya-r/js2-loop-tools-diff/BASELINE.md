# JS1 baseline imported into JS2

_Drafted by Claude Code (2026-11-10). This file records provenance only; it contains no decisions by Aditya._

JS2 starts from Aditya's **Job-Search Agent 1** submission. The original is not modified. It stays posted at
[`fall-2026/aditya-r/js1-contract-and-watch/`](../js1-contract-and-watch/) (course-repo commit `693b7d3`, 2026-10-31).

## Source identity

| Item | Value | How checked (2026-11-10) |
|---|---|---|
| JS1 local development repo HEAD | `819f2e945a7b601b40cf550f5564899df25303a7` (20 commits, 2026-10-30 17:05 → 10-31 16:30 EDT; never pushed as history) | `git log` in Aditya's local JS1 repo |
| JS1 as posted in this repo | commit `693b7d3`, folder tree `4ccb1e5a6bf3…` | GitHub API: same tree hash as `git archive 819f2e9` |
| JS1 Canvas ZIP | sha256 `2464a5fc226680f4244044f4758dfc7ceda321067f6f177fa18b6b55cf2e03cd` | `diff -rq` against `git archive 819f2e9`: identical |

JS1's development history was posted as a single commit. Its commit hashes exist only in Aditya's local repo, and its exported log is a text file in the JS1 folder. JS2's history is committed step by step in this repository.

## What was imported (unchanged)

`agent/`, `tests/`, `resume/` (the fictional Priya Nair persona), `prompts/`, `state/seen.json` (JS1's Databricks state after its run 2 on 2026-10-30: 883 `baseline` + 258 `completed` ids) and `requirements.txt`.

All 23 files are byte-identical to `819f2e9`. Per-file SHA-256 values are in [`evidence/baseline/js1_import_manifest.sha256`](evidence/baseline/js1_import_manifest.sha256).

JS1's experiments, labels, action-surface material and saved evidence were **not** imported. They stay in the JS1 folder, and JS2 does not repeat those experiments.

## Inherited checks on the unchanged baseline

The commands and full output are in [`evidence/baseline/baseline_checks.txt`](evidence/baseline/baseline_checks.txt). Claude Code ran them on 2026-11-10 before any JS2 code existed:

- `pytest`: 72 passed (SYNTHETIC fixtures).
- `tests/mutation_check.py`: 3 of 3 planted JS1 wrong versions CAUGHT (MUTATION).
- JS1's `scripts/verify_evidence.py`: ALL CHECKS PASSED. It ran read-only on a temporary `git archive 819f2e9` extraction, because it needs JS1's evidence folders (REPLAY of JS1's saved evidence).

These checks show that the inherited code still behaves as JS1 documented. They do **not** show that it meets the JS2 gate.
