# Action-surface comparison (Chapter 3)

Same task three ways: judge **posting 8128744** (Software Engineer, New Grad — SF / Seattle / New York) for
Rohan Desai under the CONTRACT §5 rule. My hand label for this posting: **RELEVANT** (Java, JavaScript, Go).

Surfaces 2 and 3 were run on 2026-10-31 (~23:08 UTC) through `claude -p` (Claude Code 2.1.283), no project
settings, no MCP servers. Outputs are saved under [`action-surfaces/`](action-surfaces/). Surface 1 was run by me twice
— a plain chat (Home tab, 7:22 PM ET, the main run) and a Code-tab session (7:18 PM ET) — see [`action-surfaces/1-chat-paste/REPLY.md`](action-surfaces/1-chat-paste/REPLY.md).

| | 1 · paste into chat | 2 · give Claude a file to read | 3 · agent fetches and writes its own state |
|---|---|---|---|
| how it ran | I pasted `PASTE-THIS.txt` (rule + posting) into a new plain chat (Claude app, Home tab) | `--tools Read`; cwd held `posting.md` + `resume_skills.json` | `--tools WebFetch,Read,Write`; WebFetch allowed only for `boards-api.greenhouse.io`; told to fetch `/jobs/8128744` and write `state.json` |
| can **read** | only what I paste (my extra Code-tab run had the project folder, tools and memory loaded — more than a chat needs) | any file the Read tool can reach — not limited to the two I named (nothing in the run stopped it) | the allowed host + local files |
| can **write** | nothing | nothing | files in its working directory (it wrote `state.json`) |
| can **send** | nothing beyond the chat | nothing | HTTP GETs to the allowed host |
| authority it needs | none beyond my account (if it is a plain chat) | read access to the folder | network + write access; I pre-approved the tools with `--allowedTools` |
| verdict it gave | plain chat: RELEVANT; Code tab: NOT RELEVANT ([replies](action-surfaces/1-chat-paste/REPLY.md)) | NOT RELEVANT ([output](action-surfaces/2-file-read/claude-output.json)) | NOT RELEVANT ([state it wrote](action-surfaces/3-agent-fetch-write/state-written-by-agent.json)) |
| matched my label? | plain chat yes; Code tab no | no | no |
| what went wrong / could go wrong | plain chat added a prose line before the JSON — my validator would reject it; nothing checked it but my eyes; I must copy the posting by hand each time, nothing is remembered between days, and a pasted posting can be the wrong one or cut off | quoted real text with correct résumé fields — the format held. Reads beyond the two files were possible. | **it ignored the evidence schema**: `evidence` became free-text sentences, so my validator's checks would reject it; the run used **two models** (`claude-opus-5-5` and `claude-haiku-5-5`) — WebFetch hands the page to a smaller model, so the judge may have seen a summary, not the raw posting; nothing saved the raw response; the state file is whatever the model chose to write; a wrong allow-list entry would let it fetch elsewhere |

Observed facts above come from the saved outputs: turns 3 (file) vs 4 (agent); cost reported $0.063 vs $0.075;
`permission_denials` empty in both runs.

## Which surface my agent uses, and why

_Written by me, 2026-10-31._

I would choose run.py because it makes the daily process easier without depending too much on the model. My code handles fetching the job postings, saving their IDs, keeping track of the raw posting data, and checking whether the model's output is valid. The plain-chat run gave me the expected classification, but it also included extra text instead of only the required JSON. The Code tab gave a different classification for the same posting, while Surface 3 gives the model more control, which can create more issues with formatting and processing the page.
