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
- The committed folder (commit `07a677b`) was exported with `git archive` into an empty scratch directory, so only committed files were present. There was no `state/`, no `outputs/`, no database, and no data except `data/README.md`.
- The README steps were then followed with macOS's built-in `/usr/bin/python3` (3.9.6), not the Homebrew Python used during development.
- Log: [evidence/clean-checkout.log](evidence/clean-checkout.log). It's a **filtered summary**: real command output, trimmed to the summary lines with `head`/`tail`, with the commands written as headers (for example `<workbook>` stands for the local workbook path). It isn't a full raw transcript.

| Step | Result |
|---|---|
| `python3 -m unittest discover -s tests -t .` | 28 tests, OK |
| `python3 -m sponsorsql load <workbook> data/fy2026q3.sqlite` | 437,496 rows loaded; checksum verified |
| `python3 -m sponsorsql evaluate` (held-out) | 5/5, policy denials 0 |
| `python3 -m sponsorsql failures` | 10/10 as predicted; controlled failure as predicted |

**Limits of part B:**
- The same Mac, the same user account and the same Claude session that built the project.
- The 252 MB download step (`curl`) wasn't repeated; the existing local copy was used, and the loader re-verified its checksum.
- It shows the committed files are complete and the commands work. It doesn't show the README is clear to someone else; only part A can.
