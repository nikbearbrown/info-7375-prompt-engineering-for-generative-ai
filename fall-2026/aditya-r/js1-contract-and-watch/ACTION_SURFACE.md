# Action-surface comparison (Chapter 3)

**Task in every mode:** judge dev posting **6865698002** ("Software Engineer - New Grad (2027 Start)") against Priya Nair's résumé skills, using prompt contract v1 (SHA-256 recorded in each run file). The model is `claude-opus-5-5`.

Modes 2 and 3 were run on 2026-10-30 by `action_surface/run_modes.py` in fresh, isolated CLI sessions. Mode 1 was performed by hand by Aditya in claude.ai on 2026-10-31 (his notes say about 3:00 pm; model shown as "Opus 5.5 High"; memory off; outside any Project). The saved files are `action_surface/mode1_chat_response.txt` (unchanged) and `mode1_chat_notes.txt` (his own observations).

## What happened (observed)

| | Mode 1 — paste into chat | Mode 2 — Claude reads a file | Mode 3 — agent fetches and writes its own state |
|---|---|---|---|
| Run by | Aditya, claude.ai web chat | `run_modes.py mode2_file` | `run_modes.py mode3_agent` |
| Tools enabled | Not observable from the saved text. Aditya's notes record memory off and no Project; his notes say the tool settings can't be verified from the reply. | `Read` only, in an empty temp directory | `WebFetch` (restricted to `boards-api.greenhouse.io`), `Read`, `Write` |
| Tool calls made | None visible in the saved reply. The text is not an activity log. | 2 × `Read`: posting.json and resume_skills.json | `WebFetch` of the posting URL, `Read` of resume_skills.json, `Write` of state.json |
| Answer | `relevant`. **Rejected by our validator at the format stage:** the saved text uses typographic quotes `“ ”` (32 pairs, no ASCII `"`), so it isn't parseable JSON. Its two quotes do occur in the posting description, and its content matches the RECORD. Whether the quotes came from Claude or from copying and saving can't be told from the file. | `relevant`; JSON valid under our validator | `relevant`; JSON valid under our validator (both the final answer and the copy in state.json) |
| Raw evidence kept? | Only what Aditya copies by hand | The input files are ours, so yes | **No.** The agent saw only `WebFetch`'s processed version of the page, and no raw response was saved. |
| State format | None | None | Self-invented `{"seen_posting_ids": [...], "judgments": {...}}` |

**Observed detail from mode 3.** The agent wrote its own extraction prompt for `WebFetch`: *"Return the job id, the exact title, and the full description text verbatim (decode HTML). Specifically quote verbatim any sentences containing the words python, sql, spark, databricks, langgraph."* So the text it judged had already been filtered by a second model, following instructions the agent chose itself. Its quotes happened to be verbatim and passed validation. The mode does not guarantee that.

**Observed in mode 1.** A plausible, correctly reasoned answer was still unusable by a strict parser once it had passed through a chat interface and a manual copy. Every downstream step (state, reports, scoring) would have to rely on a human noticing and fixing it. The programmatic route (the CLI's `result` string, stored unchanged) produced 0 format failures in 40 experiment calls and 1 evidence failure in 259 watch attempts.

## Surfaces, authority and risks

Hypothetical risks are marked *(risk)*; observed facts are marked *(observed)*.

| | Mode 1 — chat | Mode 2 — file read | Mode 3 — agent with fetch and write |
|---|---|---|---|
| **Can read** | Only what is pasted | Files in its working directory | Any URL its `WebFetch` rule allows, plus local files |
| **Can write** | Nothing | Nothing (no Write tool) | Files in its working directory *(observed: it created state.json)* |
| **Can send** | Nothing beyond the chat | Nothing | HTTP requests to the allowed host. With a looser rule it could reach any host. |
| **Authority needed** | A human to copy data in and results out | Permission to read a chosen folder | Network permission plus file-write permission, and trust in a self-managed state format |
| **What could go wrong** | Formatting corrupted in transit: typographic quotes made the answer invalid JSON *(observed)*; copy/paste errors, or the wrong posting pasted *(risk)*; no record of which response belongs to which posting *(risk)*; the chat's memory or other features add context *(risk)* | A broad Read scope exposes unrelated files, such as a real résumé *(risk)* | Raw evidence never saved *(observed)*; the page is summarized by a second model before judging *(observed)*; the state format drifts between runs *(observed: invented ad hoc)*; prompt injection in posting text could steer the fetch or write calls *(risk)*; a too-wide allow rule would mean fetching off-list hosts *(risk)* |
| **Repeatable / auditable** | No | Partly | Low, because the agent decides its own procedure each run |

## Choice: the least autonomy that suffices

The task needs four things: a fetch from one fixed host, new-versus-seen bookkeeping, a deterministic rule, and one bounded judgment per posting. Only the judgment needs a model, and the judgment needs **no tools at all**.

The agent in `agent/` therefore splits the work:
- **Ordinary code** does the fetch. It is allow-listed, including redirects, and saves the raw response unchanged.
- **Ordinary code** keeps the state, in a fixed schema that is written atomically. An id becomes "completed" only after a valid judgment.
- **Claude** is called in **mode 1 form, programmatically**. The posting and the four skill arrays are pasted into a fresh, tool-less session (`--tools ""`, no MCP, no settings, no session persistence). It can read only what we send and can write or send nothing.

Mode 3's autonomy buys nothing this task needs, and costs the evidence trail the assignment requires. Mode 2 adds a file-system surface without benefit. The remaining residual risk is prompt injection inside posting text. It is mitigated, not eliminated:
- the prompt treats posting text as data;
- the model has no tools to act with;
- the validator rejects any output that isn't the fixed JSON with supported evidence.
