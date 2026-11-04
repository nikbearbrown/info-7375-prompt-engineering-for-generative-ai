# Action-surface comparison (Chapter 3)

**Task, same for all three:** is posting #5, "Software Engineer, AI Integrations" (Commure, id `39e07152-a3d2-47c0-8c5b-36e8b3a6cdf5`), relevant for a new grad who needs sponsorship?
**All three ran 2026-10-31.** Arm 1 was run by me (Vrajesh) by hand. Arms 2 and 3 were run with `claude -p` (claude-sonnet-5-5) from this folder; the commands are in "How each arm ran" below.
**Written by:** drafted by Claude from the outputs below; the arm-1 answer is the one I got and pasted back.

## What each arm returned (verbatim)

| Arm | Answer | Turns / cost |
|---|---|---|
| 1. Paste the posting into a claude.ai chat (me, by hand, about 9:50 am ET) | "not_relevant: The posting asks for 2+ years of professional software development experience, and the candidate is a new grad with none, so this isn't an entry-level role." | 1 message / subscription |
| 2. Give Claude one file to read (`arm2-file/posting.json`, `Read` tool only) | "not_relevant: The role is a Software Engineer in the US, but it requires 2+ years of professional experience, so it isn't entry level for a candidate with no work experience. The posting also says nothing about visa sponsorship." | 2 turns / $0.022 / 3 s |
| 3. Let an agent fetch the board and write its own state file (`WebFetch` limited to api.ashbyhq.com, `Write`, `Read`) | verdict `not_relevant`, same reason ("requires 2+ years"). **Its Write was denied** by the permission rule (see below). | 15 turns / $0.213 / 69 s, two models (Sonnet plus Haiku inside WebFetch) |

All three disagree with my hand label (`relevant`, since 2 years is under my rule's 3-year line). The way I asked did not change the verdict; the missing definition of "entry level" did.

## What each one can read, write and send

| | Can read | Can write | Can send / reach | Authority it needs | What could go wrong |
|---|---|---|---|---|---|
| 1. Chat paste | only what I paste | nothing on my machine | nothing; it can't fetch | none beyond my claude.ai login | I paste the wrong posting or my real resume. No record unless I copy it; no validator; the answer depends on how I worded it that day |
| 2. File read | one file I chose (Read was the only tool) | nothing | nothing | read access to one folder | it reads a different file than I meant; prose instead of my JSON format (arm 2 answered in prose, so my validator would reject it) |
| 3. Agent fetch + state | the whole board, through a fetch tool that **summarizes** (a 1.2M-character board read in 13 chunks) | the state file, and any other file the rule allows | HTTP to any host the rule allows | network plus write permission | wrong or partial ids written as memory; a too-wide rule lets it fetch other hosts or overwrite files; 10× the cost and 20× the time; **its own report was wrong** |

### What happened in arm 3
- I allowed `Write(./**)`. The agent wrote to an absolute path, the rule did not match, and the write was **denied**. The boundary held, but only because my rule was set up wrong. I did not rerun it with a wider permission.
- The denied write is kept in `arm3-output.json` (`permission_denials`). I checked its ids against the real 10-31 board: **84 ids, all 84 real, none missed.**
- But its summary said: "The `seen` list I was going to write has 86 posting ids … could be missing an id or two." The data was right and the model's description of the data was wrong. Had I trusted the sentence, I would have believed a false count.

## The choice: the least autonomy that suffices
**Early Bird uses less than any of the three.**
- Python code does the fetch (allow-listed to `api.ashbyhq.com`), saves the raw response and keeps `seen.json`. All of that is deterministic and tested.
- Claude is called with **no tools at all**: one posting and the resume as text in, one JSON verdict out, checked by the validator.

Why this is enough, and safer:
- Fetching and remembering ids are not judgment. Arm 3 shows that giving them to a model costs 10× more, routes the data through a summarizer, and produces a wrong self-report even when the data happens to be right.
- The only part that needs a model is the judgment. That needs read access to one posting, not to the network or my disk.
- A tool-less call can't fetch a host off my allow-list, can't touch `seen.json`, and can't see my real resume, which is never on disk in this folder.
- Arm 1 has the least autonomy, but it leaves no record, has no fixed format and can't be repeated. It works for a one-off check, not for a watch that runs every day.

## How each arm ran
- Arm 1 (my words: "I ran it around 9:50 am EST, and yes i pasted the exact prompt and also put job description from online resource"): I opened a new claude.ai chat and pasted "Relevant means: Software Engineer, United States, Entry Level. Candidate: new grad, MS Software Engineering, no work experience, needs visa sponsorship. Is this posting relevant? Answer relevant or not_relevant with one sentence of why." followed by the job description copied from the posting's web page. So arm 1 saw the page text I copied, not the API JSON that arms 2 and 3 saw. The answer above is the one I pasted back into Claude Code; no chat transcript is included in this folder.
- Arm 2 (started 2026-10-31T09:55:01-04:00): in `experiments/action-surface/arm2-file/`: `claude -p --model claude-sonnet-5-5 --tools Read --allowedTools Read --setting-sources "" --strict-mcp-config --no-session-persistence --output-format json "<same question, plus: Read the file posting.json>"`. Output: `experiments/action-surface/arm2-output.json`.
- Arm 3 (started 2026-10-31T09:55:18-04:00): in `experiments/action-surface/arm3-agent/`: `claude -p --model claude-sonnet-5-5 --tools WebFetch,Write,Read --allowedTools "WebFetch(domain:api.ashbyhq.com)" "Write(./**)" "Read(./**)" --setting-sources "" --strict-mcp-config --no-session-persistence --max-turns 12 --output-format json "<fetch the board, find the posting, judge it, write state.json>"`. Output: `experiments/action-surface/arm3-output.json`.
