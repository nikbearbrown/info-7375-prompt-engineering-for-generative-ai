# Action-surface comparison (Chapter 3)

**Task:** decide whether posting #3 (Solutions Engineer, New York City, id 8886384002) is relevant for Arya, in the same
JSON verdict shape. I did it three ways on 2026-10-31 between 23:56 and 23:57 UTC, each a fresh `claude -p` call with
model `claude-sonnet-5-5`. Records: `experiments/action_surface/{1-chat-paste,2-file-read,3-agent-fetch-write}.json`
(prompt, exact command, every tool call, files after the run, and the final reply). Full stream transcripts were kept on
my machine and not committed.

Caveat on the first run: these three prompts used a shorter output-format line than `v1_baseline.md`, without the list of
allowed field names, and all three replies failed the validator. So I **re-ran all three on 2026-11-01 00:32 UTC with v1's
full output-format block** (records `*-v1format.json`). See "Re-run" below. The first run is kept as it happened.

## What ran and what came back

| | 1. Paste into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| Tools enabled | none (`--tools ""`) | `Read` | `WebFetch`, `Read`, `Write` (WebFetch allowed only for `boards-api.greenhouse.io`) |
| Tool calls made | none | Read `posting.json`, Read `resume.json` | WebFetch the posting URL, Read `resume.json`, Read `state.json`, Write `state.json`, Write `verdict.json` |
| Verdict | not_relevant | **relevant** | not_relevant |
| Passes my validator? | no: invented field names (`experience[0].title`, quoted posting text) | no: field names with explanations attached | no: `personal.location` and quoted requirements as fields |
| Files after the run | none | none | `state.json` = `{"seen_ids": [8886384002]}`, `verdict.json` |

The same posting got **two different verdicts across three surfaces** within one minute. Posting #3 is the borderline
case that also flipped in SAMPLING.md, so this mostly shows that #3 is close to the line, not that one surface judges better.

## Re-run with the v1 output format (2026-11-01, 00:32:14–00:32:27 UTC)

| | 1. Chat paste | 2. File read | 3. Agent fetch + write |
|---|---|---|---|
| Verdict | relevant | relevant | not_relevant |
| Passes my validator? | **yes** | **yes** | **yes** |
| Tool calls | none | Read ×2 | WebFetch, Read ×2, Write ×2 |
| Files after | none | none | `state.json` = `{"seen_ids": [8886384002]}`, `verdict.json` |

- With the full format, all three surfaces passed, so the first run's failures came from the prompt, not the surface.
- Surface 3 said not_relevant in both runs, while 1 and 2 split. One possible reason, which I did **not** test: surface 3
  judges from WebFetch's summary of the page, not the full posting text the other two see. With one posting and two runs,
  this could also just be the #3 variation from SAMPLING.md.

## Read, write, send, authority, and what could go wrong

| | 1. Chat paste | 2. File read | 3. Agent with fetch + write |
|---|---|---|---|
| **Can read** | only what I paste | the two files I named (it read only those). The `Read` tool takes a path argument; I did **not** test whether it could open files outside its folder | any page WebFetch is allowed to reach, plus local files |
| **Can write** | nothing | nothing | files in its working directory (it rewrote `state.json` itself) |
| **Can send** | nothing beyond the model call | nothing beyond the model call | HTTP requests to the allowed domain |
| **Authority it needs** | none | read access to my disk | network access and write access to my state file |
| **What could go wrong** | I paste the wrong posting, or my real résumé, by hand | it reads a file I didn't intend, e.g. a real résumé sitting in the same folder | it corrupts or overwrites the seen-ids state (the watch then re-reports or silently drops postings). WebFetch hands the model a **summary** of the page made from its own prompt ("Return the full job title, location, …"), not the raw response, so **no raw evidence is saved** and I can't recompute what it saw. With a looser allow-list it could fetch anything. |

## My choice: the least autonomy that suffices

**Surface 1 (no tools: the posting is pasted in as text), with my code doing the pasting, fetching and state-keeping.**
Surface 2 adds nothing the task needs: Claude never has to open a file if my code hands it the text. That's how `jsagent/` is built:

- **My Python fetches**, behind a hard-coded allow-list (`ALLOWED_HOSTS` in `jsagent/watch.py`), saves the raw response
  byte for byte, and owns the state file. These are deterministic jobs that need recomputable evidence, and Surface 3 gave up exactly that evidence.
- **Claude only judges.** It gets the posting and the persona as text, with **no tools at all** (`--tools ""` in
  `jsagent/claude_judge.py`), so it's Surface 1 driven by my code instead of my copy-paste, which also removes the risk of pasting the wrong thing by hand.
- **The validator** (`jsagent/contract.py`) is what makes any surface usable. With a loose format line, all three surfaces invented
  their own field names. With the exact format, all three passed.

Surface 3 isn't needed: the agent doesn't do anything there that my own Python can't do more checkably. It would add
network and write authority and remove the raw evidence the contract requires.
