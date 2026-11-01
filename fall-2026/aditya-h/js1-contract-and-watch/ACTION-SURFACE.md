# Action-surface comparison (Chapter 3)

**The task:** decide whether one new Stripe posting is relevant to the fictional Maya Sehgal persona under the CONTRACT rule (`title-us-v1`), with a justification that cites fields.

**What I ran:** I did the task three ways with the same model (`claude -p --model sonnet`, which reported itself as `claude-sonnet-5-5`), on 2026-10-31 between 22:59 and 23:05 EDT.

**Test posting:** 7994443, "Product Manager, Global Payouts" (New York; office `US`). It is not one of the 20 hand-labeled postings. Applying the rule by hand gives `relevant`.

Everything below is from runs I actually made. The prompts and outputs are in `experiments/action-surface/`. Raw transcripts stay on my machine (they are gitignored).

| | 1. Paste into a chat | 2. Give Claude files to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| **How it ran** | `--tools ""`. The résumé view and the posting were pasted into the one message (the v2 prompt). | `--tools Read`. The same instructions, but the résumé and posting were in `posting.json` / `resume.json`. | `--tools WebFetch,Read,Write,Edit`, with WebFetch limited to `boards-api.greenhouse.io`. It was told to fetch the board, diff against `state.json`, judge new postings, write `new_postings.json`, and update `state.json`. |
| **Can read** | Only what I pasted. | Any file the Read tool is allowed to open. It opened the two I gave it, but nothing in the CLI limited it to those two. | The web (through WebFetch, which is limited by domain here), plus local files. |
| **Can write** | Nothing; it only returns text. | Nothing. | Files in its working directory, including the state file that defines "new". |
| **Can send** | Nothing beyond the reply. | Nothing. | HTTP requests (through Anthropic's fetch tool, not directly from my machine). |
| **Authority it needs** | None beyond reading my prompt. | Read access to my disk. | Network access, plus write access to the state file. |
| **What happened** | 1 turn. Valid JSON, verdict `relevant`, citing `title`, `offices[0].name`, `location.name`. | 3 turns: two Reads (`posting.json`, `resume.json`), then valid JSON, verdict `relevant`. | 11 turns: five WebFetch calls, then it edited `state.json` and wrote `new_postings.json`. Verdict `relevant`, and it found the one id I had removed from the state (7994443). |
| **What went wrong or could** | It could misjudge, but it can't damage anything. My code still fetches, diffs and validates. | If my real résumé were on the same disk, nothing in this mode stops a Read of it. That would cross my "never show a real résumé" refusal. | See below. The answer was right, but the process broke three of my contract's guarantees. |

## What mode 3 actually did

These are from its transcript and output files.

- **The fetch was split up and summarized.** WebFetch returned the 465k-character feed in 100k-character chunks, each passed through a summarizing model. The agent needed five fetch calls; my contract says one request per run. It reported "743 postings" and admitted an entry was cut at a chunk boundary ("id 8203966 … I couldn't read it"). My own fetch at 22:41 saved 745. The board could have changed in those 20 minutes, so I can't say exactly which count is right. That is the point: **nobody can recompute this count**, because no raw response was saved.
- **No evidence was kept.** No raw response file was written. My CONTRACT's "Refuses 7" (every reported posting must exist in the saved raw response) can't be checked at all.
- **The state file was edited by hand-style edits.** It inserted the id with a string-replace `Edit` and set `last_run` to `"2026-10-31"`, a date with no time. That is *earlier* than the previous value (`2026-11-01T02:41Z`). It said: "I have no clock or shell here". A missed or duplicated id here would silently change what counts as "new" on every later run.
- **It saw less data.** It fetched the endpoint without `?content=true`, so it had no `offices` field: "offices were not available in the fetched data, so the location marker decides". Here that gave the right answer, but for an "N/A"-location posting (like "Staff Product Manager, Connect") it would have had nothing to decide with.

## My choice: the least autonomy that suffices

- **Fetch, state and diff:** deterministic Python (`jobwatch/fetch.py`, `state.py`, `watch.py`). There is one allow-listed request, the raw bytes are saved, and the state file is written atomically and only from a good fetch.
- **The Claude judgment:** **mode 1.** Claude gets pasted text, runs with no tools (`--tools ""`) from an empty temp directory, and its reply has to pass the validator.

**Why not mode 2:** it gave the same answer for this task, but it adds disk-read authority I don't need. That is the one capability that could expose a real résumé.

**Why not mode 3:** it gave the same verdict, but it couldn't keep a single one of the properties the watch exists for: one request, saved evidence, a recomputable "new". Giving a model write authority over the state file means the definition of "new" depends on the model's arithmetic.

## Limits of this comparison

- I ran each mode **once**, on one posting. This shows what each mode *can* do and what happened once, not how often it goes wrong.
- I didn't test whether mode 2's Read would actually open a file outside its folder. I'm going by the Read tool having no folder restriction in this setup, not by an attack I ran.
- Modes 1 and 2 ran from inside the course repo's folder, so a project `CLAUDE.md` could have been loaded. I didn't check whether it was. The watch's own judge runs from an empty temp directory to avoid this.
