# Action-surface comparison (Chapter 3)

*Written by Claude Code on 2026-10-31 from the runs in `experiments/action-surface/`. Each way ran live once on 2026-10-31 through `claude -p --model opus` (it reported `claude-opus-5-5`); way C ran twice. Each `way-*/` folder holds the exact message, the command and flags (`command.json`), the full event stream (`events.jsonl`), and every file in the working folder afterwards. The runner is [action_surface.py](action_surface.py).*

**The task, the same all three ways.** Apply the contract's rule (the system part of `prompts/baseline-v1.md`) to Alex Morgan's résumé. For A and B that means one posting: 6555819, Staff Software Engineer, Backend, a hybrid NYC/Tempe/LA job. For C the agent first finds the new postings itself.

## What happened

| | A. Paste into a chat | B. Give Claude files to read | C. Agent fetches and writes its own state |
|---|---|---|---|
| Tools given | none (`--tools ""`) | `Read` | `Bash`, `Read`, `Write`; allowed: Read, Write and curl |
| Turns, cost | 1, $0.017 | 4, $0.063 | attempt 1: 6, $0.104 · attempt 2: 13, $0.231 |
| Result | Not Relevant, failed [3,4,5,6] | Not Relevant, failed [3,4,5,6] | attempt 1: did nothing; attempt 2: "no new postings", wrote `verdicts.json` = `[]` |
| Correct? | Same answer as the sampling calls; its condition 3 reading matches the ad | Same as A | Attempt 2's "0 new" was correct: recounted from the response it downloaded, 214 ids, all in the 232 seen. Its summary said state.json "has 228 ids" and "the other 14" closed; the real numbers are 232 and 18 |

## Way A: paste one posting into a chat

- **Can read:** only the text in the message (the rule, the résumé's rule fields and one posting).
- **Can write:** nothing.
- **Can send:** its reply.
- **Authority needed:** a Claude login and nothing else.
- **What could go wrong:** the answer can be wrong, or shaped by instructions hidden in the posting text. The validator rejects anything off-format but cannot catch a well-formed wrong verdict. That is why the rule's record sits next to it. Whoever pastes also decides what Claude sees, so a pasted real résumé would leave the machine.

## Way B: give Claude files to read

- **Can read:** in principle, any file the user can read. The `Read` tool takes absolute paths and is not limited to the folder. It read only the three files, but nothing stopped it from reading more.
- **Can write:** no tool to write with. Claude Code itself still created a project folder in `~/.claude/projects/`, even with `--no-session-persistence`.
- **Can send:** its reply, and whatever file contents it read go to the model.
- **Authority needed:** read access to the disk.
- **What could go wrong:** the same answer as A at about 3.7× the cost (4 turns instead of 1). A file-pointing prompt can be steered toward files that were never meant to be shared, by a posting or by a typo.

## Way C: let an agent fetch and write its own state

- **Can read:** the disk, and the network through curl.
- **Can write:** any path. It wrote its downloaded response and a Python script into its own scratch folder outside the working folder. They are saved in `way-C-attempt2/written-outside-its-folder/`.
- **Can send:** HTTP requests, through curl.
- **Authority needed:** shell, network and file-write permission.

What went wrong, observed:

- **The host-pinned permission broke the task.** Attempt 1 allowed only `Bash(curl -s https://boards-api.greenhouse.io/*)`. The agent wrote `curl -sS "https://…"`, with a different flag and quotes, so every fetch was refused, then it tried `python3` (also refused) and stopped. It reported honestly that nothing had changed.
- **The wider permission gave far more authority.** Attempt 2 allowed `Bash(curl *)`, which is curl to **any host**. From then on, the allow-list in the contract was held only by one sentence in the prompt. It did keep to the board host, and it added `?content=true` on its own.
- **Commands not on the list still ran.** `ls -la && cat state.json rule.md resume.json` ran in both attempts, and three `jq` commands ran in attempt 2, although only Read, Write and curl were named. Every curl it ran went to boards-api.greenhouse.io. A `jq --slurpfile` call was refused as "dangerous flags". So the real permission surface is the tool's own idea of what is safe, not the list I wrote.
- **Python was refused, so it typed the data by hand.** It typed all 232 seen ids into a `jq` command. A comparison against the state file found them correct, but a model hand-copying state is the failure Chapter 1 warns about.
- **Its summary had invented numbers.** In both attempts it said state.json held 228 ids. It holds 232. The work was right; the prose report was not, and it read like a fact.

Other risks this run did not trigger:

- A prompt injection in a posting can now act: fetch another URL or overwrite state.
- A miscounted diff silently drops or re-announces postings.
- Cost and turns grow with board size: 13 turns here for a zero-change day.

## Choice: the least autonomy that suffices

**The agent uses way A for judgment and plain code for everything else.**

- **Code does the fetching and the state.** `jsagent/fetch.py` fetches one allow-listed host, checks every redirect, and is tested (`tests/test_fetch.py`). `jsagent/watch.py` keeps the state by id, deterministically, and is tested (`tests/test_wrong_versions.py`), with a separate recount that matched live run 2.
- **Claude only answers about one posting at a time,** with no tools, and every answer goes through the validator (`jsagent/claude_judge.py`, `jsagent/validator.py`).

**Why this is enough:**

- **Nothing about the task needs Claude to act.** Fetching a JSON endpoint and diffing ids are exact operations that code does without error, and the record of them can be recomputed. The only step that needs a model is reading an ad's prose: hybrid or remote, which years count. A model needs no tools to read prose.
- **Way B adds disk reach and cost and gives the same answer.**
- **Way C needed more authority than the contract allows before it could do the job at all.** Attempt 1 failed under a tight permission. Attempt 2 needed curl to any host. It also wrote outside its folder, ran commands I did not list, and reported a wrong count.

**What this choice gives up.** The judge can't go and look at anything the code didn't give it, such as the posting's live page or a second board. For this layer, one board and one résumé, that is a loss worth taking.
