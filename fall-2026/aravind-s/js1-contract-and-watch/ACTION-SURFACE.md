# Action-surface comparison

The same task, done three ways on 2026-10-30, each with more autonomy than the last: judge one posting (the contract's worked example, `55150071-fce8-48f5-aea4-14ed78b83511`, "Software Engineer, Applied Emerging Talent (2027)") for Jane, and record which posting ids were seen. All three used Claude Code 2.1.309 on my claude.ai seat (no API key), the model `claude-sonnet-5-5`, the system prompt `prompts/baseline.txt`, and the judge's lockdown flags: no MCP servers, no user or project settings, no saved session, the `dontAsk` permission mode. Claude Code's own init event, saved in each run's record (linked below), confirms no MCP servers, no skills and no slash commands, and lists three built-in plugins; it does not report memory files.

| | 1. Paste the posting into a chat | 2. Give Claude a file to read | 3. Let an agent fetch and write its own state |
|---|---|---|---|
| How it ran | The agent's own Claude judge: the posting's six fields and the résumé without contact fields, pasted on stdin; `--tools ""` | `--tools Read`, in a new empty folder holding `posting.json` and `resume.json` | `--tools WebFetch,Write`, WebFetch allowed only for `api.ashbyhq.com`, Write in a new empty folder |
| Can read | Only the text pasted to it | Any file in its working folder (the CLI's help says `--restricted` confines file tools to it; not tested here) | Any address on the allowed host, with any path and query it picks; the files it writes |
| Can write | Nothing | Nothing | Files in its working folder |
| Can send | Its answer | Its answer | Requests to `api.ashbyhq.com` that it composes; its answer |
| Authority it needs | The seat's login | The login, plus read access to a folder | The login, plus the network and write access to a folder |
| What happened | One turn, 4.6 s, a valid answer: `relevant` ([record](experiment/check/)) | Two Read calls (`posting.json`, then `resume.json`), three turns, 5.3 s, the same verdict ([record](experiment/surfaces/file.json)) | Two fetches, the second with `?includeCompensation=false` added on its own; both failed with "maxContentLength size of 10485760 exceeded" (the board's answer is 13.5 MB). No state file was written. Its reply explained the failure, then still gave a verdict, `not_relevant`, adding "This is not a judgment on the posting itself." ([record](experiment/surfaces/agent.json)) |
| What could go wrong | The pasted text can carry instructions; here it is framed as data, Claude has no tools, and the validator rejects any other output. A person or a program must keep the state. | It reads whatever is in the folder: a real résumé left there by mistake would be read and quoted. Text in a posting could ask it to open other files there. | It decides what to request (it changed the address once already). Its fetch tool takes a prompt with the address (see the recorded inputs), so what comes back is an answer to that prompt, not the raw response: there is nothing to save or hash. A state file built from that answer could list ids it never saw, and a failed fetch still ended in a verdict. |

## The choice: the least autonomy that suffices

I choose way 1, with the program around it doing the rest. The judgment needs only two things, the posting's text and the résumé, and way 1 gives Claude exactly those and nothing else. Fetching the board and remembering ids are exact jobs that a short program does reliably: the host allow-list is in code, the raw response is saved byte for byte with its SHA-256, and ids are never removed. Way 3 handed the network and the disk to a model for those same jobs, and on this board it could not read the answer at all, changed the request on its own, and still produced a verdict it said was not a judgment. Way 2 adds a read surface and buys nothing: the same verdict, one more tool, and a folder that must never hold a real résumé.

What this costs: the program has to be kept up when a board changes its format, and Claude cannot follow a link to learn more than the six posting fields it is given. For one board and one persona, that is the right trade.

## What this comparison did not test

- Way 3 on a board small enough for the fetch tool (it might then succeed, or return a partial list).
- A posting with instructions planted in its text, on ways 2 and 3.
- More than one run of each way: each ran once, so the timings and turn counts are single observations.
