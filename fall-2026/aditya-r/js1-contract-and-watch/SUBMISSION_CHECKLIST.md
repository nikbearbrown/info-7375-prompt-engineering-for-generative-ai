# Rubric → evidence checklist

Status key: ✅ done and verifiable · ⏳ waiting on Aditya · ❌ not done

The clean-clone check (`scripts/clean_clone_check.sh`) passed at local commit `b2e4723`: 72 tests, 3/3 mutants caught, 16/16 evidence checks. It is re-run on the final tree before packaging.

## Implementation and explanation (60)

| Rubric item | Pts | Evidence | Status |
|---|---|---|---|
| Contract written first, with testable wrong versions, applied as written | 12 | `CONTRACT.md` (original draft `710b152` 17:05; approval and R1–R5 `22d2b42` 17:30, before any project code); `tests/test_wrong_versions.py`; `tests/mutation_check.py` → `evidence/mutation_check_output.txt` | ✅ |
| Watch: allow-listed fetch, raw response saved, new-since-last by id, baseline then a real second run, validated persona | 12 | `agent/board.py` with `tests/test_inputs.py`; `evidence/runs/*` (seeded baseline from the 2026-09-22 archive: 883 ids, 0 new; live run 2: 258 new); `state/seen.json`; `scripts/verify_evidence.py`; R3 guard | ✅ (run 1 is labelled **seeded**) |
| Sampling report: repeated verdicts, spread, honest conclusion | 10 | `SAMPLING_REPORT.md`, `experiments/sampling/raw/` (20 calls) | ✅ (20/20 agree with the hand labels) |
| Prompt experiment: one change, dev vs held-out, honest limits | 12 | `PROMPT_EXPERIMENT.md`, `prompts/`, `FROZEN.json`, `experiments/prompt_experiment/raw/` (40 calls), `labeling/` | ✅ scored; no difference between v1 and v2, reported as such |
| Action-surface comparison and the autonomy choice | 8 | `ACTION_SURFACE.md`, `action_surface/` (modes 2 and 3 real) | ✅ all three modes performed (mode 1 by Aditya; its reply failed the format check, reported as observed) |
| Sign-off with real "Not checked" entries, and the driver's seat | 6 | `README.md` (end) | ✅ signed (entered by Claude at Aditya's instruction, 2026-10-31 16:28 EDT) |

## Frictional (10)

| Item | Evidence | Status |
|---|---|---|
| Specific attempts and outcomes; checks, changes and learning; accepted, modified or rejected; traceability | `FRICTIONAL.md` process-log entries, linked to commits and files | ✅ process log and Aditya's own entries |

## GitHub posting (10)

| Item | Status |
|---|---|
| Folder `fall-2026/aditya-r/js1-contract-and-watch/` in `nikbearbrown/info-7375-prompt-engineering-for-generative-ai` | ✅ posted as one commit; its hash is given in Canvas (a commit can't contain its own hash) |
| Canvas gets the folder link and the final commit hash | ⏳ Aditya pastes them into Canvas |
| ZIP matches the posted folder | ✅ `scripts/package.sh` builds the ZIP from the same tree; it was diffed against the pushed folder after the push |

## Exclusions (checked before packaging)

- **Not in the ZIP:** `.venv/`, caches, `.env` and credentials (none exist), and any real résumé. The ZIP is built from tracked files only (`git archive`), and the assignment PDF is untracked.
- **Not published:** the screenshot from Aditya (it shows his username and host), and the claude.ai chat transcript (only Aditya's saved reply text and notes go in).
- **Privacy:** `scripts/privacy_scan.py` gives a limited pattern scan of tracked files. On 2026-10-30 it returned 6 findings, all synthetic test values in `tests/`.
