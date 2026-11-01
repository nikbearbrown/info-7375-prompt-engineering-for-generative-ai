# Action-surface comparison (Chapter 3)

> Draft written by Claude Code on 2026-10-31 from the runs below; reviewed and edited by me before submission.

**Task (same all three ways):** decide whether Figma posting `6233040004` ("Data & Integration Engineer, Business Systems") is relevant to Jack Spencer, naming the résumé and posting fields behind the verdict.

**How it ran:** `python experiments/action_surface.py --id 6233040004` on 2026-10-31. There were three real Claude Code CLI runs (`claude-opus-5-5`, `--safe-mode`), each in its own empty temporary folder. Full outputs are in `experiments/results/action_surface_20261031T234559Z.json`.

| | 1. Paste into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| **Can read** | only the text in the prompt | files in its folder (`Read` tool) | files in its folder and the web, limited to `boards-api.greenhouse.io` by a tool permission (`WebFetch(domain:…)`) |
| **Can write** | nothing | nothing | files (`Write` tool) |
| **Can send** | nothing | nothing | HTTP requests to the allowed domain |
| **Authority it needs** | none beyond the model call | read access to one folder | network access, file write access, and a permission configuration I have to get right |
| **What could go wrong** | it judges only what I pasted, so a wrong paste gives a wrong answer | reads files it wasn't meant to if the folder holds more than the task | fetches the wrong URL; writes a wrong or partial id list that silently becomes "the record"; a looser permission lets it reach other hosts |
| **What actually happened** | 1 turn. Verdict **relevant**, as free-text Markdown with a field table | 3 turns, read both files. Verdict **relevant**, free text | 7 turns. It fetched the board, but its own note gives the source as `.../jobs` without `?content=true`, not the URL I gave. Verdict **relevant**. Its `Write` of `state.json` was **denied** (the temp path's short Windows form needed approval), so no state file exists. The id list it tried to write had 140 ids, which I checked against the saved raw response: 140 of 140 correct, none invented. |

**Observations from these runs:**
- None of the three free-form runs produced the fixed JSON shape the validator needs. Only the agent's own judge step, which gives Claude the prompt contract, does that.
- Run 3's id list was right this time. One correct run is not a guarantee. The agent's state is a *record*, and the code computes it from the saved raw bytes, so anyone can recompute it.

## Choice: the least autonomy that suffices

The agent uses **surface 1 (paste, no tools)** for the only step that needs Claude: the judgment. My Python code does the fetch, the allow-list check, saving raw evidence, and the state file.

Why:
- **The state file and the "new since last run" list must be exact and recomputable.** Code that diffs ids from saved bytes can be tested (`tests/test_watch_and_run.py`). A model writing the id list cannot, even when it happens to be right.
- **The allow-list is enforced in code** (`agent/fetch.py`, tested in `tests/test_resume_and_fetch.py`), including redirects. With surface 3 it depends on a tool-permission string, and run 3 already changed the URL it fetched.
- **Judging needs no tools.** With no tools, Claude can't read, write or send anything outside the prompt, so the worst failure is a wrong or invalid verdict. The validator rejects invalid ones, and the output labels every verdict as a judgment.
- **Surface 2 adds nothing here.** The code already has the posting text, so a file hop only adds a place for things to go wrong.
