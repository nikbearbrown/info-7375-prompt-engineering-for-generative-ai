# Action-surface comparison (Chapter 3)

**Task:** decide whether one posting is worth Aarav's time, with a justification. Same question every time (prompt `claude_judge.v1` + the posting + Aarav's résumé and profile); only what Claude is allowed to touch changes.

**Posting:** 8336819, Blockchain Security Engineer, Bridge (Luxembourg). Chosen because the agent judged it in Run 2, so all three surfaces exist for the same posting.

**How each was run:** `reports/action_surface.py`, output in `reports/action_surface/results.json`. Surfaces 1 and 2 ran through `claude -p` with no settings, no MCP and no saved session, on `claude-sonnet-5-5`, 2026-10-31.

## What happened

| | 1. Paste into a chat | 2. Give Claude a file | 3. Agent fetches and writes its own state |
|---|---|---|---|
| How | Posting + résumé + profile pasted as text; no tools | Same material saved as `posting.txt`, `resume.json`, `profile.json` in an empty folder; only the Read tool | `python -m job_agent` (Run 2, `runs/2026-10-31T225910Z`) |
| Turns | 1 | 4 (three Reads, then the answer) | — |
| Verdict | not_relevant | not_relevant | rule: not_relevant (check 1b, title); Claude: not_relevant |
| Main reason | 8+ years required vs 2 + 2; Luxembourg | 8+ years required vs 2 + 2; Luxembourg | Claude: 8+ years; rule: title not a target role |

The verdict didn't depend on the surface. What changes is what each one can do, and what it costs when something goes wrong.

## What each can read, write and send

| | 1. Chat | 2. File | 3. Agent |
|---|---|---|---|
| **Can read** | Only what I paste | Files in the folder it's started in (here: three files I put there) | The Greenhouse board over the network; résumé, profile, data files, state file on disk |
| **Can write** | Nothing; I copy the answer myself | Nothing (Read only) | `evidence/raw/`, `runs/`, `state/stripe.state.json` |
| **Can send** | Its answer to me | Its answer to me | HTTP requests to `boards-api.greenhouse.io`; each posting + the résumé to Claude (via `claude -p`) |
| **Authority it needs** | My chat account; I choose every word it sees | Read access to that folder; I choose which files are in it | Network access, write access to the repo folders, my Claude Code login; allowed hosts fixed in code |
| **What could go wrong** | I paste the wrong posting or leave out part of the JD; I copy the answer wrong; no record unless I save it; can't tell what's new | Claude reads a file I didn't mean it to see if the folder holds more; still manual every time; no state | Fetches bad data and marks postings seen; a broken state file makes everything look new; a bug sends the résumé somewhere unexpected; it runs without me looking |

## Least autonomy that suffices

Claude's analysis, written before my decision below:

What "suffices" depends on the job. To judge **one posting I already have**, the chat surface is enough: Claude needs nothing but the text. The task of this assignment is bigger: **watch a board and report only what's new since last time**. That needs fetching, a saved raw response and a state file; the chat and file surfaces can't do it without me doing all of that by hand every day.

The agent in this repo splits the authority: the **program** holds the network and write access, narrowed by the allow-list and by writing state only after verdicts are saved; **Claude** gets the chat surface's access only (no tools, no files, no network: `claude -p --tools ""`), so the step that is a judgment can't act. Surface 2 adds nothing the agent needs, because the program already has the files and can paste them.

## My decision

**I choose the agent.**

- It's the most convenient, and the permissions it needs are already written into the tool and tested (the allow-list, the résumé guard, Claude with no tools), so I have fewer safety worries than with the other two.
- Pasting into a chat only took 1 turn here, which surprised me. That's because the test pasted everything at once: the full instructions, Aarav's résumé and his profile. If I only pasted a JD, the AI would have to ask me about my background and what kind of job I want, and that would take quite a few rounds.
- Giving Claude a file means giving it permission to read files. If I don't set that up carefully, it could read things I didn't mean it to.
