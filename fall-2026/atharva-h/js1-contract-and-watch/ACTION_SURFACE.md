# Action-surface comparison (Chapter 3)

On 2026-10-31 I gave Claude the same task three ways. The task was to judge posting 8877421002 for the fictional persona under the rule in `CONTRACT.md`. That posting is Point72's "Technical Business Analyst" in New York, from the label pool. All three ways used the same model: a fresh Claude Code subagent of my session.

| | 1. Paste the posting into a chat | 2. Give Claude a file to read | 3. Let an agent fetch and keep its own state |
|---|---|---|---|
| Evidence | `experiments/action_surface/1_chat_paste/` | `experiments/prompt/v2_path_syntax/development/prompts/8877421002.txt` and `.../raw/8877421002.txt` | `experiments/action_surface/3_agent_fetch/` |
| What it can read | Only the text I pasted | The prompt file, through a Read tool that could open any file my session can | Anything my session can: every file, plus the network through the shell |
| What it can write | Nothing; it can only reply | One answer file, through a Write tool that could write anywhere | Any file. It wrote `raw.json` (1.5 MB) and its own `state.json` |
| What it can send | A reply to me | A reply to me | HTTP requests to any host (it ran `curl`), and anything else the shell can reach |
| Authority it needs | None beyond reading my message | Read and write permission in this folder | Shell, network, and file write |
| Tool calls (harness count) | 1, the hand-back only | 3: read, write, hand-back | 10: 2 reads, 6 shell commands (1 failed), 1 listing, hand-back |
| Wall time | about 7 s | about 12 s | about 73 s |
| Verdict | `needs_human`, passes the validator | `needs_human`, passes the validator | `needs_human`, in its own free-form state format that no validator checks |

All three gave the same verdict, for the same reason: the posting says nothing about sponsorship. What differed was what each could have done.

## What could go wrong

1. **Paste into a chat.**
   - I could paste the wrong posting or a stale copy.
   - Nothing records what was pasted unless I save it myself.
   - The answer reaches the record only if someone copies it. Here, my session copied it into `answer.txt` verbatim, which is a transcription step a validator can't see.
2. **Give Claude a file.**
   - The file could be swapped or edited between writing and reading.
   - The Read and Write tools aren't limited to that one file. The subagent stayed in bounds here (3 calls), but only because it was told to.
3. **Let the agent fetch and keep state.**
   - The host allow-list is an instruction, not code. Nothing stops `curl` from reaching another host.
   - A posting carrying injected instructions would reach an agent that has network access and write access.
   - The state file's format is whatever the agent decides. Its first `curl` failed on shell quoting and it improvised a fix. That's harmless here, but it shows the agent works out its own steps.
   - It is the slowest of the three by roughly 6–10×.

## Limits of this comparison
- I ran each way once, on one posting.
- Tool-call counts for ways 1 and 2 come from the harness. For way 3, the agent's own list of calls matches the harness count of 10, but I didn't inspect its transcript.
- I checked way 3's outputs on disk: exactly two files, and 206 ids in `state.json` matching 206 jobs in `raw.json`.

## The autonomy I choose

**Choice:** the least autonomy that is enough is way 1's surface, delivered by code. `watch.py` does the fetching, the allow-list check (enforced in code, redirects included), the raw save, and the state file. Claude receives one posting as text and returns one JSON object. The intended path is `claude -p --tools ""`: no tools, no network, no file writes. That is a programmatic paste that leaves a record (`claude_prompts/`, `claude_raw/`).

**Why not way 1 by hand:** pasting by hand leaves no record and doesn't scale to a daily watch.

**Why not way 3:**
- Fetching and diffing ids are deterministic jobs that code does better and a TA can recompute.
- Way 3 needs shell, network, and write authority that judging one posting never needs.
- That authority is exactly what a prompt injection inside a posting would exploit.

**What I actually ran:** in this submission the Claude judge ran as subagents with Read and Write tools, which is way 2. That's more authority than the design needs, because the `claude` CLI wasn't logged in (see `FRICTIONAL.md`). The `claude -p --tools ""` path is in `judge.call_cli` but was not run.
