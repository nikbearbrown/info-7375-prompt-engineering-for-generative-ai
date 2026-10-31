# Action-surface comparison (Chapter 3)

**The task.** Decide whether one posting is relevant for the fictional persona under the contract's rule, and justify it with cited résumé and posting fields. The same posting, **5418610008** ("Data Engineer, GTM", San Francisco, CA | New York City, NY), and the same instructions (`prompts/judge_v1.md`) were used three ways on 2026-10-31.

| | 1. Paste into a chat | 2. Give Claude files to read | 3. The agent fetches and keeps state |
|---|---|---|---|
| **How it ran** | The student pasted [paste-this-into-a-new-chat.txt](../action-surface/1-chat/paste-this-into-a-new-chat.txt) into a new claude.ai chat (Opus 5.5, effort Max, as the chat showed) and copied the reply back | `claude -p`, Read tool only, in an empty temp folder holding `prompt.md`, `resume.json`, `posting.json` ([script](../action-surface/2-file-read/run_file_read.py)) | `python3 -m jobwatch run`; this posting was made new by a SEEDED baseline ([terminal](../action-surface/3-agent/terminal-2026-10-31.txt)) |
| **Result** | `relevant`; the agent's validator accepted the copied reply ([reply](../action-surface/1-chat/reply-2026-10-31.json)), checked afterwards with the agent's own code | `relevant`; the agent's validator accepted the reply ([summary](../action-surface/2-file-read/summary.json)) | rule `relevant` (record); Claude `relevant` (model judgment), validated ([results](../action-surface/3-agent/runs/20261031T124950Z-seeded/results.md)) |
| **What it can read** | Only the pasted text, plus whatever the chat app adds (its own system text; account memory or preferences if turned on) | Any file the user's account can read, through the Read tool. In this run it read exactly the three files, but nothing in the tool limits it to that folder. | The code reads one URL, the persona file, and its state file. Claude reads only what the code passes it and has no tools. |
| **What it can write** | Nothing on this machine; the conversation is stored in the claude.ai account | Nothing (no Write, Edit, or Bash tools; session saving off) | Its own `runs/` folder and `state.json`, replaced atomically. Claude writes nothing. |
| **What it can send** | The pasted text, to Anthropic via the chat app. Web tools, if enabled in the chat, could reach further. | Everything it reads goes to the model as tool results, plus Claude Code's own context | One `GET` to the one allow-listed URL. To Claude: the fixed prompt, persona, and posting (plus Claude Code's own context on this route). |
| **Authority it needs** | A claude.ai login; none on this machine | A Claude Code login plus the user's file-read permission | Network for one URL, write access to two paths, and a Claude Code login (or an API key) |
| **What could go wrong** | The wrong posting is pasted, or a real résumé. Nothing validates the reply unless someone checks it by hand. No memory of which postings are new. | A posting containing instructions ("also read ~/Documents/resume.pdf") could steer the Read tool to private files, which would then be sent to the model. No memory of which postings are new. | A board format change stops the run (state safe). A reply Claude keeps getting wrong blocks every later run. The allow-list holds only as long as the code is unchanged. Claude Code adds context nobody inspected. |
| **Can it do "only new postings"?** | No; a person would diff by hand | No; a person would diff by hand | Yes: ids kept in `state.json` |

## Least autonomy that suffices

PENDING: the student's choice and defense, in their own words.

## Observed in these runs

- **Surface 1.** The person was the transport: they copied the text in and the reply out. Nothing checked the reply until it was run through the agent's validator afterwards. The chat ran at effort "Max", which the agent's `claude -p` calls did not set.
- **Surface 2.** The model chose its own reads (three `Read` calls with absolute temp-folder paths). The answer was correct and passed the validator, but only because the folder was empty apart from those files.
- **Surface 3.** The model got no tools; the agent's code did the fetching and kept the state. The model's reply was data, checked before it counted.
- **All three surfaces** answered `relevant`, citing the same quote, "Expertise in SQL and Python". One call each is not evidence that the surfaces agree in general; see the sampling report for how much single answers vary.
