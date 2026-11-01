# Action-surface comparison (Chapter 3)

**The task, done three ways on Oct 31, 2026:** judge whether the real Anthropic posting **5464234008, "Data Engineer"**, is relevant to the fictional persona Priya Nair. For the agent, the task also includes noticing that the posting is new. All three ways used Claude Code 2.1.316 with `claude-sonnet-5-5`. Each Claude conversation was fresh, and no session was saved.

> Drafted by Claude Code from the three runs below. The choice at the end is Hemanth's to confirm or change.

## What actually happened

| Way | When (ET) | What Claude was given | Result | Evidence |
|---|---|---|---|---|
| 1. **Paste into a chat** | 14:47:30 | The prompt-v1 contract with the posting and Priya's skills and title pasted into the message. No tools. | `not relevant`, medium confidence. Passed the validator. | `action-surface/runs.json` → `1-paste` |
| 2. **Give Claude a file to read** | 14:47:39 | The same instructions, but the posting and candidate were in `posting.json` and `candidate.json` in a throwaway folder. Only the **Read** tool was allowed. | `not relevant`, medium confidence, after 3 turns (it read both files). Passed the validator. | `action-surface/runs.json` → `2-file` |
| 3a. **Let an agent fetch and write its own state** (Claude Code as the agent) | 14:50:59 | A throwaway folder holding `resume.json` (the persona, contact fields included). The instruction was to fetch the board with curl, save the raw response, and write `seen_ids.json`. Tools: Bash, Read, Write. Only `Bash(curl:*)`, Read and Write were pre-approved. | It fetched the board: the raw file it saved has sha256 `1e5b62fe…7e88`, identical to the agent's own baseline. **It did not write the state file.** Its first command chained `mkdir && curl && python3`, and later it tried a `python3` step; the permission policy denied both. It then reported the failure honestly and asked for approval. | `action-surface/way3-claude-code-agent.json` (`permission_denials` lists both) |
| 3b. **Let an agent fetch and write its own state** (this repo's agent) | 14:44:06 | Python code does the fetch (allow-listed), saves the raw response, and writes `state/seen_ids.json`. Claude gets **no tools**, just the posting and Priya's skills and title as text, like way 1. | Seeded run: the posting was reported as new. Rule: `relevant`. Claude: `relevant`, medium confidence. | `runs/2026-10-31T144406-seeded-2/report.md` |

On the same posting, with the same prompt and minutes apart, Claude said **relevant** once (3b) and **not relevant** twice (1, 2). The rule says relevant, because the title has "Engineer" and the description names Python and SQL. The surface didn't cause that difference: ways 1 and 3b gave Claude identical text. It's the run-to-run variation the sampling report measures. The disagreement also shows why the report labels Claude's verdict a judgment and the rule's a record.

## What each way can read, write and send

| | 1. Paste into chat | 2. File to read | 3a. Claude Code as the agent | 3b. Python agent + tool-less Claude |
|---|---|---|---|---|
| **Can read** | only what's pasted | files Claude is allowed to Read (here, one folder; by default, the working directory and below) | anything its tools reach: the folder, plus the network via curl | Python reads the allow-listed board and the persona; Claude reads only the text it's handed |
| **Can write** | nothing | nothing | files in the folder (Write), plus anything Bash can do if approved | Python writes `runs/<id>/` and `state/` only; Claude writes nothing |
| **Can send** | the pasted text, to Anthropic | the file contents it reads, to Anthropic | the file contents and fetched data, to Anthropic; network requests to any host curl is pointed at | Claude: the posting text plus Priya's skills and title, to Anthropic. Python: one GET to `boards-api.greenhouse.io` |
| **Authority it needs** | none beyond the chat | read permission on a folder | network, a shell, and file writes. That needs a permission policy, and someone answering prompts or pre-approving commands | the network allow-list and the state folder are in code (`watch.py`); Claude needs none |
| **What could go wrong** | a person pastes a real résumé; nothing is remembered between runs, so "new since last time" can't exist; copy-paste errors pair a verdict with the wrong posting | Claude reads more than intended if the folder holds other files (a real résumé, `.env`); still no memory of what's new | it saw the persona's contact fields because the file was in its folder; curl isn't restricted to an allow-listed host, only by command name; a model-chosen state format; a fetch failure could be reported as "nothing new"; it can stall waiting for approval (it did) | a bug in our code (the tests cover the two wrong versions, the allow-list and overwrites); Claude's judgment varies run to run; posting text could carry instructions aimed at Claude (prompt injection), but Claude has no tools to act on them |

## The least autonomy that suffices

**Choice: way 3b.** Python code does the watching and holds the authority. Claude gets the surface of way 1, a chat with no tools.

- **Ways 1 and 2 can't do the task.** The task is "report only postings new since the last run", and that needs remembered state and a fetch on a schedule. Neither way remembers anything, and someone would have to fetch and paste every posting by hand.
- **Way 3a can do the task, but it gives the model more authority than the job needs.**
  - The fetch is a fixed GET to one host, and remembering ids is a set difference.
  - Neither needs judgment, so neither needs a model choosing shell commands.
  - In the real run, the model's own command choices are what stopped it: it chained a Python step the policy didn't allow.
  - It also had the persona's contact fields within reach.
- **In 3b, the only thing Claude does is the one thing code can't:** a judgment about fit, which is labeled as one.
  - Its blast radius is a string in a report.
  - Everything that touches the network or the disk is code that the contract describes and the tests check.

Confirmed by Hemanth, Oct 31, 2026: yes (asked whether Hemanth disagreed with this choice, the answer was "no").
