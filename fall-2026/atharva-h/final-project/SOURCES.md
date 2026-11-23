# SOURCES

## What was used

| Item | What it is | Licence / terms | How it was used |
|---|---|---|---|
| DOL OFLC LCA disclosure workbook FY2026 Q3 | `LCA_Disclosure_Data_FY2026_Q3.xlsx`, 251,850,891 bytes, SHA-256 `f8ca8448…bd28b3`, downloaded 2026-10-24 from https://www.dol.gov/agencies/eta/foreign-labor/performance | U.S. government public information | The only data source. 18 of 98 columns loaded. Not redistributed (too large for GitHub). |
| Python 3 standard library | `sqlite3`, `zipfile`, `xml.etree`, `json`, `hashlib`, `unittest`, … | PSF License | Everything. No third-party packages. |
| SQLite | Bundled with Python (3.53.4) | Public domain | Database, authorizer, progress-handler budget |
| Claude (Claude Code, `claude-opus-5-5`) | The owner's Claude Code access | Anthropic terms | Wrote the code and documents with the owner (below). Separate subagents wrote the SQL proposals that were evaluated. |
| Brutalist toolkit (local checkout `ba2d0e0`), Manim Community 0.18.1, Remotion, Kokoro TTS (`am_onyx`, Apache-2.0 weights) | Used only to make the demo film | As listed in the toolkit; free local pipeline | `film/` (script, scenes, gate reports). No paid generation. |
| ChatGPT (GPT-6, high mode) | The owner's own test on 2026-10-24 | OpenAI terms | One saved comparison test (`evals/chatgpt-test-2026-10-24.md`). Not part of the system. |
| MyVisaJobs employer search (https://www.myvisajobs.com/employers/search.aspx), H-1B / LCA Salary Explorer (https://h1bhq.com/search, https://h1bhq.com/about) | Reviewed online in an earlier Claude session on 2026-11-21; not re-checked in this session | Their sites' terms | Named as existing alternatives only. No scraping, no data used. |

## What the owner wrote or did

- Chose the project, the dataset and the target role; ran the ChatGPT test (2026-10-24).
- Set the deadline, the four-minute film limit and the no-downloads constraint; approved the build (2026-11-21).
- Reported reviewing the answer key and preparation files (2026-11-21).
- **Still to do, and must be the owner's own:**
  - `FRICTIONAL.md`
  - the sign-off
  - the ship/narrow/defer/stop decision
  - a real gate decision
  - the stranger run

See [DRIVERS-SEAT.md](DRIVERS-SEAT.md).

## What Claude contributed

Claude (Claude Code, Opus 5.5) in sessions on 2026-11-21:
- **Code:**
  - wrote all code in `sponsorsql/` and `tests/`
  - wrote the answer-key and held-out-key scripts (`evals/build_answer_key.py`, `evals/build_heldout_key.py`), the loaders and the profile script
  - adapted `sponsorsql/load.py` from the earlier session's `evals/load_lca_sqlite.py`
- **Evaluation design:**
  - wrote `pre-mortem.md`, `CONTRACT.md` and prompt contracts v1 and v2 (v1 first drafted in an earlier session the same morning)
  - chose the five held-out questions
- **Runs:** ran every command in [evidence.md](evidence.md) and saved the outputs.
- **SQL proposals:** spawned three separate subagents to write the SQL proposals, and saved their replies word for word.
- **Review:** spawned one separate reviewer subagent for the audit note.
- **Documents:** drafted the packet documents, the README, this file and `DRIVERS-SEAT.md`. Did **not** write the owner's Frictional entries, the sign-off, or the decision.

**Rough estimate of code origin:** essentially all Python in this folder was written by Claude at the owner's direction; the owner's work is the direction, the decisions, and review (pending where noted). Claude responses shown as evidence are ones actually received on 2026-11-21, with dates in their provenance blocks.

## Style

Python follows PEP 8 in spirit (4-space indents, snake_case, line lengths around 100). No formatter was run.

## Licence

This folder's code and documents are submitted under the course repository's licence (`LICENSE` at the repository root).
