# Action-surface comparison — facts from the three runs

Posting 8546367002 (AI Engineer – Forward Deployed Engineering), revision prompt
(`prompts/judge-revision.txt`, sha256 `0af3b5c3…`), Oct 26, 2026. Every
reply was checked with `judge.validate()` against the 12:40 ET saved
description (`runs/postings/databricks_job_8546367002_2026-10-26T12-40-58-0400.json`).
My hand label for this posting is "not relevant". This file records what
happened; the choice of the least autonomy that suffices, and its defense, are
written separately.

| | 1. Chat (claude.ai) | 2. File (`claude -p`, Read only) | 3. Agent (`claude -p`, WebFetch + Write) |
|---|---|---|---|
| Record | `runs/action_surface/chat_2026-10-26T23-07-00-0400.json` | `runs/action_surface/file_2026-10-26T22-54-11-0400.json` | `runs/action_surface/agent_2026-10-26T22-54-37-0400.json` |
| When (ET) | 23:07 (reported by me, to the minute) | 22:54:11 | 22:54:37 |
| Run by | me, in a new claude.ai chat; web search off | `experiments/action_surface.py --mode file --live` | `experiments/action_surface.py --mode agent --live` |
| Could read | only what I pasted (`chat_paste.txt`), plus whatever my claude.ai settings add | files in its temp folder, which held only `posting.txt` | `boards-api.greenhouse.io` through WebFetch; no Bash |
| Could write | nothing | nothing | one path: `judge-record.json` in its temp folder |
| Could send | the conversation, to Anthropic under my claude.ai account | its reply | a request to the allowed host, and its reply |
| Enforced by | nothing beyond what I pasted | Claude Code permissions (`--tools Read`, `dontAsk`) | Claude Code permissions (`WebFetch(domain:…)`, one `Edit(…)` path, `dontAsk`) |
| Authority needed | my claude.ai account | my Claude plan login through Claude Code, no API key (environment held only `HOME`, `USER`, `PATH`); Claude Code permissions given: `--tools Read`, `--allowedTools Read`, `--permission-mode dontAsk` | my Claude plan login through Claude Code, no API key (environment held only `HOME`, `USER`, `PATH`); Claude Code permissions given: `--tools WebFetch,Write`, `--allowedTools WebFetch(domain:boards-api.greenhouse.io)` and `Edit(…/judge-record.json)` for one file in its temp folder, `--permission-mode dontAsk` |
| Actually did | not observable | 1 Read of `posting.txt` | 2 WebFetch calls to the posting URL, then 1 Write |
| Refused calls | not applicable | none | none |
| Files left | not applicable | `posting.txt` (unchanged) | `judge-record.json` |
| Model | "Claude Opus 5.5" as shown in the chat; not pinned or reported | `claude-opus-5-5` reported | `claude-opus-5-5` and `claude-haiku-5-5` reported |
| Verdict (judgment) | not checkable (reply was not valid JSON) | not_relevant | not_relevant |
| Passed validation | **no: not valid JSON** | yes | yes (reply and written file, identical) |
| What went wrong | Reply had curly quotes (“ ”) every time I copied it; source unknown (chat output, Copy button, or pasting). Nothing in it could be checked automatically, although the visible verdict (not_relevant) and quote looked right to me. | nothing observed | A second, unpinned model processed the fetched page; the WebFetch output was not saved, so the text the agent judged can't be shown (see README, Known limits); it fetched the live page, not the 12:40 snapshot. |
