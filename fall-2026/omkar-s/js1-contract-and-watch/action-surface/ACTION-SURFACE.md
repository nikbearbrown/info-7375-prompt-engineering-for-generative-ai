# Action-surface comparison (Chapter 3)

The same task, done three ways: **judge one Klaviyo posting for Aarav under the prompt contract.**

| | 1. Paste into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| How it was run | `claude -p` with **no tools**. The posting text is pasted into the prompt. | `claude -p --tools Read` in a folder holding only `posting.json` + `resume.json` | `claude -p` with fetch and write tools in a scratch folder. Claude fetches the board itself and writes `state.json` |
| Can read | only what was pasted | files Claude chooses to open (in practice, the cwd and anything the Read tool can reach) | the network (any URL WebFetch accepts unless restricted), plus the files in the folder |
| Can write | nothing (text reply only) | nothing | files in the folder, including its own state |
| Can send | nothing | nothing | HTTP requests to whatever host it decides on |
| Authority needed | none beyond the prompt | read access to a folder | network egress + write access; a mistake persists in state |
| What could go wrong | stale/partial paste; format drift | reads more than intended (e.g. a real résumé next to it) | fetches a host off the allow-list, writes a state that hides postings, re-reports or loses ids, follows instructions embedded in posting text |
| Result when run (2026-10-26 ~01:38 UTC, posting 7855793003 "Software Engineer II, Test Frameworks & Tooling"; not one of the 20 experiment postings) | valid, **relevant**. 1 turn, $0.029, `claude-sonnet-5-5`. Cited title, location.name and content | valid, **relevant**. 3 turns (it opened both files), $0.034. Same fields cited | valid, **relevant**. 5 turns, $0.096. **Two models**: `claude-haiku-4-5` (WebFetch's page reader) + `claude-sonnet-5-5`. It wrote `state.json` with **160/160 correct ids, none invented** (checked against our raw response). But it fetched the endpoint **without `?content=true`**, so it never saw the ad text, and said so: *"Posting content and departments were not available."* It cited only title and location.name, and still said relevant |

## What the runs showed (facts, written by Claude Code)

- All three surfaces gave the same verdict on this one posting. One posting cannot separate them on accuracy. They differed in **what the verdict rested on** and **what was left behind**.
- Surface 3 chose its own URL and dropped the posting text. It did not invent ids, and it said honestly that content was missing, but it still returned a confident verdict. Nothing in the output contract forces "not enough evidence". The validator passed it because `posting_fields` only listed fields it really used.
- Surface 3 also routed the board data through a second model (Haiku, inside WebFetch) that the prompt never mentioned.
- Raw envelopes for all three are in `action-surface/runs/*/envelope.json`, and surface 3's state file is `runs/3-agent/left-behind-state.json`. Rerun with `python3 action-surface/run_three_ways.py 7855793003 runs/raw-klaviyo-2026-10-25T22-59-08Z.json`.

## The choice

> [Omkar, verbatim, 2026-10-30 20:06 UTC] "i will go with way 1 because claude only reads the postings and gets it to me"

> [Omkar, verbatim, 2026-10-31 22:35 UTC] What would worry me about way 3 running every day unattended: "the proper job postings and not the fake one's"

That is also how `jsagent` is built. `claude_judge.call_claude` runs `claude -p --tools ""` in an empty temporary folder, so Claude can read only the prompt. The allow-listed fetch (`fetch.py`) and the state file (`watch.save_state`) are plain Python that Claude never controls.
