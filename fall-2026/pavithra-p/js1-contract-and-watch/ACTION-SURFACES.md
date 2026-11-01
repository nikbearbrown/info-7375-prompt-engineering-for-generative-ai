# Action-surface comparison (Chapter 3)

The task: judge one posting for Rohan Mehta (fictional) with my contract's rule. The posting is Pinterest 7832348, "Staff Software Engineer, Batch Processing Platform". It was one of the 8 new jobs in run 2 (2026-10-31). The same rule text (`experiment/prompts/baseline.md`) was used all three ways.

| Way | How it ran | Saved |
|---|---|---|
| 1. Chat | I pasted `action-surfaces/1-chat/paste-into-claude-ai-7832348.txt` into a new claude.ai chat on 2026-10-31 (model shown: Opus 5.5, high) and pasted the reply back | `action-surfaces/1-chat/reply-7832348.json` |
| 2. File | `python3 -m agent surfaces 7832348`: Claude Code (`claude -p`, model `claude-sonnet-5-5`) with only the Read tool, in a temporary folder holding `posting.txt` and `resume.json`, 2026-10-31T17:42:48Z | `action-surfaces/2-file/` (the files it was given, the prompt, the reply) |
| 3. Agent | `python3 -m agent watch` (run 2, 2026-10-31T17:39:02Z): fetched the board, saved the raw response, wrote `state/seen_ids.json`, and asked Claude (`claude -p`, no tools) about each new job | `evidence/runs/run-20261031T173902Z.md`, `evidence/claude/watch/20261031T173902Z/7832348.json` |

All three said Not Relevant for the same reason: the title has "Staff", and the description asks for "Minimum 6 years of experience" (line 23 of `action-surfaces/2-file/given/posting.txt`). All three replies passed the validator. The written rule (the record) says Not Relevant too.

## What each way can read, write and send

| | 1. Chat (claude.ai) | 2. File (Claude Code, Read tool) | 3. Agent (`python3 -m agent watch`) |
|---|---|---|---|
| **Reads** | only the text I paste | any file its Read tool is pointed at. I gave it two, but the command does not limit Read to that folder | `boards-api.greenhouse.io` only (allow-list, redirects re-checked), the résumé file, its own state file |
| **Writes** | nothing on my machine; the chat is kept in my claude.ai account | nothing (no Write, Edit or Bash tool); my script saves its reply | the raw response, the run report, `state/seen_ids.json`, Claude's saved replies, all inside the project folder |
| **Sends** | the pasted text to Anthropic | the files it reads to Anthropic, including the résumé's (fictional) email and phone | one GET with no body to Greenhouse; the posting and the résumé's skills, experience and education (no email or phone) to Claude |
| **Authority it needs** | my claude.ai login, and me copying by hand | my Claude Code login and permission to use Read without asking | network access to one host, write access to its own folder, my Claude Code login |
| **What could go wrong** | I paste the wrong résumé (even my real one) or the wrong posting; copy mistakes; no record unless I save it; I have to check the board myself every day; a different model from the agent | it reads more than it needs; a posting with hidden instructions could try to make it read other files on my Mac; it still cannot fetch or remember what is new | a bug in the state file could hide new jobs forever; the board changes its format; Claude gives an invalid reply (2 of 8 in run 2); a code change adds a host |
| **Guard in this project** | the paste text leaves out email and phone (`test_chat_text_has_no_email_or_phone`) | only the Read tool, and a folder holding only the two files (`test_file_way_gives_only_the_read_tool_and_saves_the_reply`) | allow-list and GET only (`test_fetch`), raw saved before the state, atomic state write, a bad response leaves the state unchanged (`test_watch`), invalid replies saved and never repaired (`test_claude_judge`) |

## The least autonomy that suffices

The job is: every day, show me only the new postings, each with a justified verdict. The chat and the file ways cannot fetch the board or remember what was already seen, so I would have to do both by hand every day. They do not suffice.

So the watch needs the agent, but the autonomy is split:

* The fixed Python code does the actions: one GET to one allowed host, and writes only inside its own folder. It never applies, emails, messages or logs in.
* Claude gets no tools at all (`--tools ""`). It only sees the text the code gives it, the same as in the chat, and it cannot fetch, read files or write the state. Its reply is a judgment that the validator checks, not an action.

This gives Claude less autonomy than way 2, where it could read files. The extra power the agent has (fetching and writing state) sits in code that the tests check.

## Limits

* One posting is enough to compare the surfaces, not to compare the models. All three agreeing here does not show they agree in general.
* The chat used Opus 5.5 (high), as shown in claude.ai. The other two used `claude-sonnet-5-5`.
* I did not test whether the Read tool in way 2 would really read a file outside its folder.
