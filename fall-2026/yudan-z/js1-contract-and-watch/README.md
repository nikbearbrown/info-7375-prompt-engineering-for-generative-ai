# Job-Search Agent 1 — The Contract and the Watch

## Executive summary

This is the first layer of my job-search agent. It watches one public job board (Pinterest on Greenhouse), remembers every posting id it has seen, reports only postings that are new since the last run, and judges each new posting twice:
- once by my written rule, a **record** anyone can recompute;
- once by Claude under a prompt contract with a strict validator, a **model judgment**, labeled as one.

I wrote the contract before any code (`CONTRACT.md`, commit `077c5e0`), and the tests were committed before the implementation. Two of those tests caught bugs in the generated code. The folder also holds the three Chapter 1–3 artifacts: a sampling report, a prompt experiment on 20 postings I labeled by hand, and an action-surface comparison.

- **Student:** Yudan Zhou
- **Persona:** fictional, `persona/resume.json` (`@example.com`, `555`)
- **Language:** Python 3

## Toolchain

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.14.2 (3.9+ should work; standard library only, no `pip install`) | everything |
| Claude Code CLI | 2.1.314, installed with `npm install -g @anthropic-ai/claude-code` (Node 20+), then `claude` once to log in | the Claude judge, the experiment, sampling, surfaces |
| OS | Windows 11; PowerShell and Git Bash | — |

Network access is needed only to `boards-api.greenhouse.io` (`config/allowlist.json`).

## Exact commands (run from this folder)

```bash
# 1. offline tests (no network, no Claude): 34 tests
python -m unittest discover -s tests -v

# 2. the watch: first run is the baseline (reports 0 new); later runs report new ids only
python -m agent.run --workdir runs/live                 # add --no-claude to skip the Claude judge

# 3. seeded second run against a saved response (labelled SEEDED)
python -m agent.run --workdir runs/seeded --from-file runs/seeded/earlier-response.SEEDED.json
python -m agent.run --workdir runs/seeded --from-file runs/live/evidence/20261030T230135Z-pinterest.json

# 4. Chapter artifacts (need the logged-in Claude CLI)
python -m experiment.sampling --ns 1 3 4 9 10 --times 4
python -m experiment.run_experiment --prompt contract_v1.txt --split dev       # also v2, and --split held-out
```

To try the watch without changing my submitted evidence, use a new folder, for example `--workdir runs/try` (its first run is a baseline). On Windows, set `PYTHONUTF8=1` if the console shows encoding errors. The seeded run and step 3 write into `runs/seeded/`. Delete `runs/seeded/state` first to repeat it from a clean start.

## What ran (all on 2026-10-30 unless noted)

| What | Result | Evidence |
|---|---|---|
| Tests | 34/34 pass | `tests/test_contract.py` |
| **Run 1, real baseline** | 170 Pinterest postings, **0 new** | `runs/live/evidence/20261030T230135Z-pinterest.json`, `runs/live/state/seen_ids.json`, `runs/live/run1-baseline-terminal.txt` |
| **Run 2, SEEDED** | constructed earlier response (165 = the real 170 minus 5 ids), then the real response, so **5 new**. Rule: 1 relevant. Claude: 5/5 valid. | `runs/seeded/` (`earlier-response.SEEDED.json` is labelled as constructed) |
| **Run 3, real second calendar day** (2026-10-31, about 20 hours later) | same 170 ids as day 1 (0 added, 0 removed), so **0 new**. Nothing was re-reported. | `runs/live/evidence/20261031T192702Z-pinterest.json`, `runs/live/run3-day2-terminal.txt` |
| Sampling (5 postings × 4 fresh calls) | verdicts stable; #4 consistently disagrees with my label; 1/20 invalid | `experiment/SAMPLING-REPORT.md` |
| Prompt experiment (10 dev + 10 held-out) | v1 9/10 and 8/10; v2 7/10 and 9/10, so no detectable difference | `experiment/PROMPT-EXPERIMENT.md` |
| Action surfaces (paste / file / agent) | paste chosen; file and agent outputs failed my validator; the agent had no raw bytes | `surfaces/ACTION-SURFACES.md` |

## Folder map

`CONTRACT.md` · `agent/` (watch, rule, judge, report, persona, run) · `tests/` · `config/allowlist.json` · `persona/resume.json` · `prompts/` (v1, v2) · `runs/` (raw responses, state files, reports) · `experiment/` · `surfaces/` · `SOURCES.md` · `FRICTIONAL.md`

---

## Sign-off — Job-Search Agent 1

**Checked**, and by which of my own tests:
- New-since-last by id: baseline reports none (`test_baseline_reports_nothing_new`); seen ids are never re-reported (`test_second_run_reports_only_unseen`); one id is reported once (`test_duplicate_id_in_one_response_reported_once`); only ids in this response (`test_only_postings_in_this_response`). These are my four failure conditions in §6.
- Evidence: the raw response is saved byte-for-byte (`test_raw_response_saved_unchanged`) and never overwritten (`test_same_second_runs_keep_both_evidence_files`).
- Refusals: a non-allow-listed host is refused before any request (`test_host_not_on_allowlist_is_refused`); a non-fictional résumé is refused (`test_real_looking_email_is_refused`, `test_non_555_phone_is_refused`).
- The rule R1–R9: one test per check, including the Canada and ITAR fixes.
- W1, verdicts joined by id (`test_verdicts_join_by_id_not_position`). W2, justifications must cite fields (`test_rejects_justification_citing_nothing`, `test_every_reason_names_both_fields`).

**How:**
- By tests written from the contract before the implementation existed (Claude wrote them; commit order `3fcb128` → `e008d0d`).
- By hand: I labeled 20 postings and read the held postings' requirement lines.
- By recomputation: I compared the agent surface's 170 ids with my baseline.
- With Claude's help: the code, the test code, and finding the truncation bug in a justification.

**Not checked:**
1. A real second calendar-day run with a genuine new posting. The real day-2 run (2026-10-31) found the board unchanged, so the only change shown is seeded.
2. Whether R4–R7's fixed phrase lists catch requirements worded any other way. The lists are complete by design, but real postings may use other phrasing.
3. Whether Claude's verdicts hold on any posting outside these 25, or on another day or model version.
4. A second person's labels. My 20 labels are the only ground truth, and #9/#14 may be my error.
5. macOS/Linux, and a Python older than 3.14.

**Not claiming:**
- That a `relevant` verdict means the job is worth applying to. The rule and Claude are both filters, not decisions.
- That v2 is better or worse than v1.
- That Claude's justification is the real reason for its verdict.

**Signed:** Yudan Zhou, 2026-10-31

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| What counts as relevant | proposed refinements | wrote the rule; accepted, modified or rejected each refinement | it is my career and my time | `CONTRACT.md` authorship line; FRICTIONAL #2–#4 |
| Ground truth | chose which postings to show | **labeled all 20, with reasons** | a model cannot be the answer key it is graded against | `experiment/labels.json` (`50a1f2d`, my reasons verbatim) |
| Disagreeing with Claude | suggested relabeling #3 | **kept #3 relevant** (co-op could move graduation) | only I know my plans | `labels.json` n=3 revision; FRICTIONAL #11 |
| Changing the rule | found the Canada `CA` gap; implemented R9 | **decided** the R3 revision; **proposed** R9 | rules are commitments a TA will hold me to | `CONTRACT.md` Revisions; `83ac0d1`, `08ca1ae` |
| The experiment's one change | suggested the R1 change | **approved** it, and stopped after one revision | choosing what to test is the judgment being graded | `prompts/contract_v2.txt` diff; FRICTIONAL #13 |
| Code, tests, drafts | wrote them | read the results, signed off on what was checked | — | commit history |
