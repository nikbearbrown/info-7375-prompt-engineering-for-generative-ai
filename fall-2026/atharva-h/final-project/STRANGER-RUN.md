# Stranger run

## Part A: a person who did not build it — NOT DONE YET

The brief asks for someone who didn't help build SponsorSQL (a classmate, a friend or a TA) to run it from [README.md](README.md) on a clean machine. To be filled in by the owner:

- **Who:** ______ (name or role, and their relationship to the project)
- **Machine and Python version:** ______
- **What they ran:** (commands, in order) ______
- **Where they got stuck:** ______
- **What I changed because of it:** (commit) ______

If nobody is available, write that here, and keep part B as the record of the clean-clone test.

## Part B: clean-checkout test (done by Claude on 2026-11-21, not a stranger)

**What was done:**
- The committed folder was exported with `git archive` into an empty scratch directory, so only committed files were present. There was no `state/`, no `outputs/`, no database, and no data except `data/README.md`.
- The README steps were then followed with macOS's built-in `/usr/bin/python3` (3.9.6), not the Homebrew Python used during development.
- It was done twice: before the independent review (commit `07a677b`, [evidence/clean-checkout-07a677b.log](evidence/clean-checkout-07a677b.log)) and after the review fixes (commit `a8cbf96d`, [evidence/clean-checkout.log](evidence/clean-checkout.log)).
- Both logs are **filtered summaries**: real command output, trimmed to the summary lines.

| Step | Before review (`07a677b`) | After review fixes (`a8cbf96d`) |
|---|---|---|
| `python3 -m unittest discover -s tests -t .` | 28 tests, OK | 43 tests, OK |
| `python3 -m sponsorsql load <workbook> data/fy2026q3.sqlite` | 437,496 rows; checksum verified | 437,496 rows; checksum verified |
| `python3 -m sponsorsql evaluate` (development, v2) | not run | 9/10 |
| `python3 -m sponsorsql evaluate` (held-out) | 5/5 | 5/5 |
| `python3 -m sponsorsql failures` | 10/10 as predicted; controlled failure as predicted | 10/10 as predicted; controlled failure as predicted |

**Limits of part B:**
- The same Mac, the same user account and the same Claude session that built the project.
- The 252 MB download step (`curl`) wasn't repeated; the existing local copy was used, and the loader re-verified its checksum.
- It shows the committed files are complete and the commands work. It doesn't show the README is clear to someone else; only part A can.
