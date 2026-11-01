# Action-surface comparison

The same task three ways: judge posting **7855793003** (Software Engineer II, Test Frameworks &
Tooling, Klaviyo, Boston) for Supriya Sharma. Surfaces 1 and 2 used the `revision-v2` prompt rules.
Claude Code drafted the table from the saved records listed below; the decision at the end is Ashwin's.

**Surface 3 has two kinds of evidence.** The watch's two **live** runs found no new posting, so they never
asked Claude anything. To put this posting through the real watch, Claude Code ran one **SEEDED REPLAY**
(`3-watch-seeded/`, details in its `NOTES.md`). It replays run 2's unmodified live response against a scratch
copy of the state with 7855793003 removed, using `--prompt prompts/revision-v2.md`. The watch's **default**
prompt is `baseline-v1` (`jobwatch/watch.py`). With that prompt, Claude said NOT_RELEVANT to this posting in
all five calls (sampling and dev). An earlier draft of this table used an experiment verdict for surface 3;
the seeded replay replaces it.

| | 1. Chat paste | 2. File read | 3. Agent with its own state (the watch) |
|---|---|---|---|
| Where it ran | claude.ai chat, new conversation | `claude -p`, run by `action-surfaces/file_read.py` | Live: `python3 -m jobwatch` (run 1), `python3 -m jobwatch --judge claude` (run 2). Seeded: `action-surfaces/seeded_watch.py` |
| Who ran it | Ashwin, by hand, 2026-10-31 | Claude Code, 2026-10-31T18:05:00Z | Ashwin, both live runs. Claude Code, the seeded replay, 2026-10-31T18:44:21Z |
| What Claude could touch | Only the pasted text | The Read tool only (`--tools Read`), started in a temp folder holding `resume.json` and `posting.json` | Nothing: each Claude call is `--tools ""` from an empty folder. The Python program holds the access |
| Can read | What Ashwin pastes | Files it can reach with Read (the folder held only the two inputs) | Claude: only the prompt. Program: one allow-listed URL, the persona file, its own state |
| Can write | Nothing outside the chat | Nothing (no Write or Bash tool) | Claude: nothing. Program: `runs/<timestamp>/` and `state/seen_ids.json`, state last |
| Can send | Nothing; the chat is its only output | Nothing; no network tool | Claude: nothing. Program: one GET to the allow-listed URL, with redirects refused. It never applies, emails or logs in |
| Authority it needs | A claude.ai account; Ashwin's hands | Claude Code on this machine, permission to read one folder | Claude Code on this machine, plus network access to one public endpoint and write access to two folders, given to the Python program, not to Claude |
| Who fetches the posting | Ashwin copies it | Someone must save it to a file first | The program, from one allow-listed URL |
| Who remembers what was already seen | Ashwin | Nobody | `state/seen_ids.json`, updated only after a complete run |
| Can it notice a new posting tomorrow? | No, unless Ashwin checks the board | No | Yes, by id. Live runs: 156 ids, 0 new. Seeded replay: the one removed id was reported as new |
| Saved record | Only what Ashwin pastes back | The prompt, inputs, reply, and selected envelope fields in `record.json` (model, turn count, permission denials). The full envelope and tool-call trace were **not** saved | Raw response and SHA-256 per run, and per new posting a rule record, AI judgment, raw Claude reply and report; the seeded replay also keeps its starting state |
| Validated | Yes, afterwards, by the same validator: VALID | VALID | Live runs: nothing to validate (0 new). Seeded replay: VALID, before it entered the report |
| Model shown | Not recorded by the chat UI | claude-opus-5-5 | Seeded replay: claude-opus-5-5. No call in the live runs |
| Turns | 1 | 3, as reported by the envelope. Which tool calls they were was not recorded | 1 per new posting (`--tools ""`) |
| Verdict on 7855793003 | RELEVANT | RELEVANT | Seeded replay: RULE RECORD RELEVANT; AI JUDGMENT RELEVANT, no disagreement. Not judged in the live runs |
| Human work per day | Visit the board, read, paste each posting | Save each posting to a file, run, read | Run one command, read one report |
| What goes wrong if Claude misbehaves | One bad answer in a chat | It could read any file Read can reach; the folder held only the two inputs, and other paths were not tested | A bad answer is rejected or labeled; Claude cannot fetch, write state or act |

All three surfaces gave RELEVANT with valid evidence, the watch only in the seeded replay. The comparison is mostly about what each
surface can reach, do and record, which comes from its setup rather than from this one answer.

Records:
- `1-chat-paste/`: `prompt.txt` and `reply.txt`. Ashwin pasted the reply back; the validator was run on it afterwards.
- `2-file-read/`: `prompt.txt`, `inputs/`, `reply.txt` and `record.json`.
- The watch, live: `../runs/` and `../state/seen_ids.json`.
- The watch, seeded: `3-watch-seeded/` (`NOTES.md`, `command.txt`, `state-before-seeded.json`, `state/`, `runs/`).

## Decision: the least autonomy that suffices

Written by Ashwin Thankachan, 2026-10-31:

I would choose the watch because it can automatically check for new jobs, remember which ones it has already seen, and save the results. Chat paste works for checking one job, but I would have to do everything manually. File read lets Claude access the files, but it still cannot automatically monitor new postings or remember previous results. The watch gives enough automation for this task without giving Claude unnecessary tools or control, since Python handles the workflow and Claude only makes the relevance decision.
