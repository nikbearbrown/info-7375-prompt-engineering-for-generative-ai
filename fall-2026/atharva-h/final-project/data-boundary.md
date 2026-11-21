# Data boundary

Packet document 2 of 10. Previous: [brief.md](brief.md) · Next: [action-surface-map.md](action-surface-map.md)

Every source and file the system touches, labelled **public**, **synthetic**, **internal**, **personal** or **unknown**, with retention and deletion. Checked against the files in this folder on 2026-11-21.

## Sources

| Source | Label | Where it lives | In GitHub? | Retention and deletion |
|---|---|---|---|---|
| DOL OFLC LCA disclosure workbook FY2026 Q3, `LCA_Disclosure_Data_FY2026_Q3.xlsx`, 251,850,891 bytes, SHA-256 `f8ca8448…bd28b3` | **Public** (U.S. government disclosure data) | Owner's machine, outside the repository | No: over GitHub's 100 MB limit. Anyone can download it from the DOL page (README has the command). | Kept for the course. Delete the file to remove it; the loader re-verifies the checksum on any new copy. |
| SQLite copy, `data/fy2026q3.sqlite` (about 86 MB) | **Public** (18 columns derived from the workbook) | `data/` (gitignored) | No | Rebuilt any time by `python3 -m sponsorsql load`. Delete freely. |
| Columns **not** loaded: employer contacts, attorneys, preparers, addresses, phones, emails, attorney bar fields (80 of 98 columns) | Public in the workbook, but **personal** in character (named people, emails, phones) | Never copied by this system | No | Not retained. `load.py` keeps only the 18 fields in `config.FIELDS`. |
| The 18 kept fields: case number and status, dates, visa class, job title, SOC code and title, worker count, employer name, trade name, employer ID (`EMPLOYER_FEIN`), worksite city and state, filed wage range and unit, prevailing-wage level, worksite count | **Public** | `data/fy2026q3.sqlite` | No (the database); yes, as small excerpts inside `evals/` results (employer names, case numbers, titles) | Excerpts are kept as evidence. The employer ID is used only to check spellings and is never shown in the film. |
| Development key `evals/answer-key-results.json`, held-out key `evals/heldout-key.json` | **Public** (counts derived from public data) | `evals/` | Yes | Frozen. Hashes in `evals/FREEZE.md`. |
| Synthetic test database built by `tests/fixtures.py` (12 invented rows, names like "Example Data LLC") | **Synthetic** | Created in a temporary folder during tests, then deleted | Only the code | Deleted automatically when the tests finish. |
| Model prompts and recorded replies `evals/proposals/*` | **Internal** (project working material; contains no personal data) | `evals/proposals/` | Yes | Kept as evidence of what the model actually returned. |
| ChatGPT test reply `evals/chatgpt-test-2026-10-24.md` | **Internal** (the owner's own test output; no personal data) | `evals/` | Yes | Kept as evidence. |
| Run state `state/` and exported answers `outputs/` | **Internal** | Local folders (gitignored) | No; selected runs are copied into `evidence/` | Delete freely. They hold questions, SQL and public rows only. |
| Owner's résumé, contacts, application tracker, real job-search inputs, conversation transcripts | **Personal** | Never used by this system | No | Not an input. Nothing in this folder reads them. |

No source is labelled **unknown**.

## Who is affected, and how they could contest a result

- **Employers named in the data:** a public filing is shown exactly as filed, with its case number. An employer who thinks a count is wrong can check the matching rows SponsorSQL shows, and correct the record with the DOL. SponsorSQL never edits the data.
- **People asking questions (students):** questions aren't sent anywhere except to the model adapter. The recorded adapter sends nothing. The live CLI adapter sends the prompt to Claude through the owner's Claude Code account.
- **Individual workers:** the loaded fields don't identify workers. Questions about a specific person's visa outcome are refused (`screen.py`).

## Terms of use

The data is public U.S. government information. SponsorSQL downloads it once, by hand, from the DOL page. It doesn't scrape any site.
