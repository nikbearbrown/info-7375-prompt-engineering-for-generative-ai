# Questions for writing GATE.md

> **Drafted by Claude Code (Opus 5.5) on 2026-11-08 as prompts only.** These are questions, not
> answers. `GATE.md` itself is Ashwin's writing. Nothing below is a decision.

## Facts to decide with (Claude Code probe, 2026-11-08, one GET each, no `?content=true`)

| URL | HTTP | Postings |
|---|---|---:|
| `boards-api.greenhouse.io/v1/boards/klaviyo/jobs` (your JS1 board) | 200 | 152 |
| `boards-api.greenhouse.io/v1/boards/hubspotjobs/jobs` | 200 | 122 |
| `boards-api.greenhouse.io/v1/boards/hubspot/jobs` | 404 | — |
| `boards-api.greenhouse.io/v1/boards/klaviyo-nonexistent-js2/jobs` | 404 | — |
| `api.ashbyhq.com/posting-api/job-board/notion` | 200 | 154 |
| `api.ashbyhq.com/posting-api/job-board/supabase` | 200 | 70 |
| `api.ashbyhq.com/posting-api/job-board/no-such-board-js2` | 404 (text/plain) | — |
| `api.lever.co/v0/postings/palantir?mode=json` | 200 | 305 |
| `api.lever.co/v0/postings/no-such-board-js2?mode=json` | 404 | — |

Lectern's `ATS.md` recorded on 2026-09-26 that `hubspot` returned an **empty 200** board. Today it
returned **404**. So "an empty board" is not something you can count on finding live; you may have to
show it as a labeled seeded replay. That is your call.

## 1. Exits

- What exact words will the loop print and save for each of: finished, incomplete, budget-exhausted, error?
- If 3 of 4 boards succeed and 1 fails on purpose, is the run "incomplete" or "finished"? Why?
- Does any exit except "finished" allow the seen-ids state to be updated? For which boards?
- What exit code (0, 1, 2…) does each one return, so a script can tell them apart?

## 2. Budgets

- Max boards per run? Max HTTP requests per run (counting retries)? Max wall-clock seconds per run?
- Per-request timeout in seconds?
- When the budget runs out mid-run, what happens to the boards not yet visited: reported as "not
  observed", never as "no new jobs"?
- Who may change a budget, and where is that written down (for example: only Ashwin, by editing
  `GATE.md` in a commit that says why)?

## 3. Repeat rule

- What makes two actions "the same": same URL? same board name and ATS? same request in the same run?
- What does the loop do when it sees a repeat: skip it, count it, stop the run?
- Is the same board listed twice in the config an error before any fetch, or a skip at run time?

## 4. Error policy

- Which failures, if any, get a retry: timeout? connection reset? HTTP 5xx? 429?
- Which never get a retry, and why: 404 (bad name)? 200 with an empty or malformed body? a redirect?
- How many retries, and how long to wait between them? Do retries count against the request budget?
- What does "escalate to me" look like: a line in the report? a non-zero exit? a file?
- After a board fails, does the loop continue to the next board or stop the whole run?

## 5. Permission policy

- Allowed hosts (exact list)? Only `https`? Redirects refused, as in JS1?
- Which folders may the program write to? Which may it only read?
- Which writes need your approval first, and how is approval given (a command-line flag you type? a
  file you create?) so that a prompt or a model reply can never grant it?
- What may it never do? (The brief requires at least: apply, email, message, log in.)
- Does Claude (the judge) get any tools at all in JS2?

## 6. Wrong versions

Name the plausible-but-wrong implementations your tests must catch. Questions to start from:

- What would an empty board look like if the loop treated it as "no new jobs"?
- What if a path check used `startswith("jobs")` and so allowed `jobs-evil`?
- What if a retry loop retried a 404 forever, or a budget counted boards but not retries?
- What if a failed board's ids were marked as seen, so its new postings were never reported later?
- What if a host check compared strings and allowed `boards-api.greenhouse.io.evil.example`?

## JS1 gaps you may want GATE.md (or README.md) to say something about

- No new posting appeared live in JS1; the full path ran only in tests and one labeled seeded replay.
- The held-out experiment was not clean (the only changed held-out case was the worked example).
- The watch's default prompt is `baseline-v1`, though `revision-v2` did better.
- `scripts/validate_course.py` exits 1 because of other students' files.
