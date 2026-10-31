# Action-surface comparison (Chapter 3)

*Drafted by Claude Code from the committed evidence. Review by Atharva C.:
PENDING. Evidence: `logs/action_surface/runs.json` and
`logs/action_surface/agent_state.json`, produced by
`python3 -m tools.action_surface`.*

## The task, done three ways

On 2026-10-30 (07:53 UTC) I gave Claude (`claude-sonnet-5-5`) the same task
three times: judge posting 7776179 (Security Engineer, Bridge) for the Rohan
Desai persona, answering in the revision prompt's JSON format. Each was a
fresh `claude -p` session in its own empty temp folder. What each session
actually did was read back from its transcript, not assumed.

| | 1. Paste into a chat | 2. Give Claude a file | 3. Agent fetches and writes state |
|---|---|---|---|
| Tools given | none | `Read` | `WebFetch` (only `boards-api.greenhouse.io`), `Write`, `Read` |
| Tool calls it made | none | `Read posting.txt` | `WebFetch …/jobs/7776179`, `Write state.json` |
| Verdict | not relevant (valid) | not relevant (valid) | not relevant (valid) |
| Folder after | empty | `posting.txt` (unchanged) | `state.json` it wrote: `{"posting_id": 7776179, "verdict": "not relevant"}` |

## What each can read, write, and send

**1. Chat (no tools)**
- **Reads:** only the text my code put in the prompt.
- **Writes:** nothing.
- **Sends:** nothing beyond its answer.
- **Authority needed:** none.
- **What could go wrong:** I paste the wrong posting, or more than I meant
  to, such as a real résumé. There's no record unless my code keeps one.
  Mine does: the log and the raw response.

**2. File (Read tool)**
- **Reads:** the file I pointed it at. I allowed `Read` with no path limit,
  though, so it *could* have read any file my user account can read,
  including a real résumé elsewhere on disk. In this run it read only
  `posting.txt`.
- **Writes:** nothing.
- **Sends:** nothing.
- **Authority needed:** read access to the filesystem.
- **What could go wrong:** reading files it shouldn't, and private file
  contents ending up in a model call.

**3. Agent (fetch + write)**
- **Reads:** the web, limited to one domain by a permission rule, plus the
  filesystem.
- **Writes:** files. It chose the state format itself, and it records
  nothing about *what it saw*.
- **Sends:** HTTP requests.
- **Authority needed:** network, plus write access to disk.
- **What could go wrong, seen in this run:** `WebFetch` gave the page to a
  summarizer with the prompt "Return the job title, location name, and a
  summary of the content including required years". Claude judged *a
  summary written by another model*, not the posting, and no raw response
  was saved. My contract requires the raw response as evidence, and this
  mode broke that.
- **What could go wrong, not seen:** fetching other hosts if the rule were
  looser, overwriting files, and state that silently drifts from what my
  tests check.

## The choice: the least autonomy that suffices

*Draft. Atharva to confirm or rewrite in their own words.*

**Mode 1, with my own code around it.** My code does the fetching, the
allow-list, the raw-response saving, and the state file, and all of that is
tested (`tests/test_contract.py`). Claude gets only text and returns only a
verdict. Claude doesn't need to read files, browse, or write state to judge
a posting. Each of those adds a way to fail: here, mode 3 lost the raw
evidence, and mode 2 had read access to my whole disk. `agent/claude_judge.py`
runs mode 1: `--tools ""`, run from an empty folder.

## Not checked

- Whether the WebFetch domain rule actually blocks another host. I didn't
  try one.
- What the summarizer dropped from the posting in mode 3.
- One run per mode: no repeat sampling here.
