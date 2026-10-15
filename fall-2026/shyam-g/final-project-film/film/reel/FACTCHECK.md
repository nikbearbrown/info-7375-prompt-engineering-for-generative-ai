# FACTCHECK — stopline-pitch

Status: checked 2026-10-14 by Shyam Sundar Jayaraman Gopalakrishnan, with Claude Code (Opus 5.5). Every figure below was re-read from a file in this repository.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | B00 | StopLine is a small Python tool that checks a proposed decision against the evidence it cites | PASS | `stopline/engine.py`, `stopline/checks.py` | |
| 2 | B01 | When finished: repository, CLI, synthetic test set, tests, eval report that lists failures | PASS | Future tense ("will be"); the parts exist today in `stopline/`, `data/`, `tests/`, `reports/eval_report.md` | |
| 3 | B02 | Three outcomes; the most cautious wins; it never approves | PASS | `stopline/engine.py` (`PRECEDENCE`, `pick_outcome`); no approve outcome exists in `checks.py` | |
| 4 | B03 | Claude Code wrote most of the code on October 14 | PASS | `SOURCES.md` "What Claude contributed"; session date 2026-10-14 | |
| 5 | B03 | I have reviewed every check | PASS | Author's statement, 2026-10-14; exercises logged in `FRICTIONAL.md` | |
| 6 | B03 | Seventeen synthetic incidents, one outcome each | PASS | `reports/cli_output.txt`: 17 outcome lines, INC-001 to INC-017 | |
| 7 | B03 | Twelve tests passing | PASS | `reports/test_run.txt`: "Ran 12 tests", "OK" | |
| 8 | B03 | On-screen lines "INC-001 ACCEPT FOR REVIEW", "INC-003 HUMAN REVIEW REQUIRED", "Ran 12 tests OK" | PASS | Copied from `reports/cli_output.txt` and `reports/test_run.txt` (run 2026-10-14); spacing condensed | |
| 9 | B03 | Every incident and number is made up | PASS | `data/build_synthetic.py` header | |
| 10 | B04 | SAP QM usage decision checks results recorded, right lot, before the decision; can refuse or warn; checks structured results, not the written justification | EXEMPT | Author's own SAP experience (stated as such in narration: "from my experience"); not re-checked on a current S/4HANA system. Warn-and-force path: SAP KBA 1958483 public preview | |
| 11 | B04 | StopLine does not beat SAP yet; my tool misses the written-claim case too | PASS | `reports/eval_report.md` INC-016 miss | |
| 12 | B04 | On-screen two-column comparison | EXEMPT | Constructed sketch, labelled "sketch" on screen | |
| 13 | B06 | No language model in it | PASS | `stopline/` imports only the Python standard library | |
| 14 | B07 | The command-line run already works; saved output shows it ran | PASS | `reports/cli_output.txt` exit code 0 | |
| 15 | B08 | Two of seventeen cases get it wrong | PASS | `reports/eval_report.md`: 15 / 17 matched, 2 misses | |
| 16 | B08 | Claim cites 400 units from a lot of 1,200; every rule passes | PASS | `data/build_synthetic.py` INC-016 (E-022 `units_quarantined: 400`; description "lot of 1,200"); engine outcome ACCEPT FOR REVIEW | |
| 17 | B09 | Supplier scorecards and root-cause reviews in SAP as an analyst; Six Sigma Green Belt | PASS | Author's résumé (kept out of the repository) | |
| 18 | B10 | Exists today: engine, data, tests, report | PASS | Files in `stopline/`, `data/`, `tests/`, `reports/` | |
