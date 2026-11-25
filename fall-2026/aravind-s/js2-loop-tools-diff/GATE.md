# Gate: Job-Search Agent 2 (the loop, the tools and the diff)

Version 1.0, 2026-11-07. Written before Claude Code changed any code for JS2. The decisions behind it are listed at the end.

This file extends [CONTRACT.md](CONTRACT.md) v0.1 from one board to a list of boards. Where the two differ (the boards, the allow-list, the state and run folders, and which posting fields the rule reads on Greenhouse and Lever), this file wins. The rule's seven checks are unchanged.

One run of the loop visits each board on the list once, in the listed order, under fixed budgets. It records every observation in a trace and ends with exactly one of four exits.

## Boards

`boards.json` lists each board as a system and a name. It never holds a URL: the program builds the URL from one fixed template per system.

| System | Request the program builds |
|---|---|
| Ashby | `GET https://api.ashbyhq.com/posting-api/job-board/{name}` |
| Greenhouse | `GET https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true` |
| Lever | `GET https://api.lever.co/v0/postings/{name}?mode=json` |

- The course run's list: OpenAI (Ashby), Verkada (Greenhouse), Palantir (Lever), and one board that fails on purpose, the made-up Greenhouse name `no-such-board-js2-test`. It is marked `"deliberate_failure": true` in the list. On 2026-11-06 a made-up name answered HTTP 404 on all three systems.
- A board name is 1 to 64 characters: lowercase letters, digits and hyphens, starting with a letter or digit. Anything else refuses the whole list before any request.

## Exits

Every run ends with exactly one exit. The report and the screen start with it, followed by every reason that applies.

| Exit | Code | When |
|---|---|---|
| finished | 0 | Every board on the list answered, was read and was saved, no budget ran out, and every new posting has both verdicts. |
| incomplete | 1 | The run ended on its own terms, but at least one board is unverified: it failed under the error policy, so its postings are not known for this run. A run with the deliberate failure ends here, unless a budget also ran out (see the order below). |
| budget-exhausted | 4 | A budget ran out. The report says which one, what was done, and what was not: boards not visited, and new postings still waiting for Claude's judgment. |
| error | 2 or 3 | The run could not go on: a broken input (2: résumé, board list, state file) or a refused request or write (3). No state changes. |

If more than one applies, the exit is the first in this order: error, budget-exhausted, incomplete, finished. Only `finished` means every board was read. A loop that stops is not a loop that succeeded.

## Budgets

Per run:

| Budget | Limit | Checked |
|---|---|---|
| Boards | 5 | when the list is read |
| HTTP requests, retries included | 10 | before each request: a request that would be the 11th is not sent |
| Claude calls | 20 | before each call |
| Wall clock | 600 seconds from the start | before each request and each Claude call |

- One request may take at most 30 seconds.
- The rule judges every new posting in the run, because it is local and free. New postings past the 20th Claude call keep their rule verdict and wait in the board's state, in order, for Claude. The next run judges them first.
- **Who may change a budget:** only a new version of this file, with the decision written under "Where these choices come from". The numbers live in one place in the code, and a test fails if they differ from this table. A command-line flag may lower a budget for one run and is refused if it tries to raise one.

## Repeat rule

- **The same action** is the same method and the same URL, compared after the program builds the URL.
- In one run the loop never sends the same action twice, except the one retry the error policy allows. The trace labels that request as a retry, and it counts against the request budget.
- A board listed twice (same system and name, ignoring case) is visited once. The second entry is reported as a repeat and skipped.
- The same Claude call (same board, posting id, prompt and model) is never made twice in one run.

## Error policy

For a board whose request or answer fails:

- **Transient failures** (a timeout, a dropped or refused connection, a DNS failure, HTTP 429, HTTP 500 to 599): one retry after 5 seconds, if the budgets allow it. A retry is sound here because a GET changes nothing on the server, these failures often clear by themselves, and one retry costs one request from the budget. If the retry fails too, the board is unverified.
- **Answers a retry cannot fix** (HTTP 404 or another 4xx, a redirect, an answer that is not JSON, a missing or empty jobs list, a job without an id or a title): no retry. The board is unverified.
- **An unverified board:** any answer that arrived is saved as evidence; its state stays exactly as it was; none of its postings counts as new or gone; no value is filled in for it; the report escalates it to me ("needs you": check the board name, or try again later). The other boards go on.
- **A refused request** (host, path or method) is never retried and stops the run with exit 3, saving no state. The program builds every URL itself, so a refusal means the code or the list is wrong.

## Permission policy

Enforced in the program, not in a prompt. Every network call and every file write goes through one checking module.

- **Hosts:** exactly `api.ashbyhq.com`, `boards-api.greenhouse.io` and `api.lever.co`, over HTTPS on port 443, with no user or password in the URL. No substring, prefix or suffix match.
- **Requests:** GET only, and only to the three board paths above, one path pattern per system. Redirects are not followed. No cookies, keys or login headers. Proxy settings from the environment are ignored.
- **Writes:** only inside the repo's `runs/` and `state/`. A path is checked after it is resolved, so a path with `..`, a folder whose name only starts the same way (`runs-evil` beside `runs`), an absolute path elsewhere, and any symlink along the way are all refused.
- **Reads:** the résumé (`persona/`), the prompts (`prompts/`), the board lists, `state/` and `runs/` (for replays). Reading the résumé is allowed; writing it is refused.
- **Writes that need my approval:** replacing or deleting an existing board's state. A normal run only adds to a board's state, because seen ids are never removed, and that needs no approval. Anything else (ids dropped, a board's state reset, an old-format state file replaced, a state file deleted) is refused unless I pass `--approve "<reason>"` on the command line. The trace records the approval, its reason and the time. Moving JS1's `state/seen.json` (OpenAI) into the JS2 format is the first such write.
- **Never:** apply, fill a form, email or message anyone, log in, open a posting link, or call a host or path not listed above. Claude runs with no tools, as in JS1.

## Postings from three systems

The rule reads Ashby fields (CONTRACT.md, The rule). For the other two systems the program maps each posting to those fields as follows, and a test covers each line with saved answers.

| The rule reads | Ashby | Greenhouse | Lever |
|---|---|---|---|
| id, title, link | `id`, `title`, `jobUrl` | `id`, `title`, `absolute_url` | `id`, `text`, `hostedUrl` |
| employment type (check 1) | `employmentType` | the metadata field named "Employment Type" ("Full-Time" counts as FullTime; any other value is kept as written); if there is none, not stated | `categories.commitment` ("Full-time" counts as FullTime, "Internship" as Intern; any other value is kept as written) |
| locations (check 2) | the primary and secondary `address.postalAddress` | `location.name`, split at ";" | `categories.allLocations` (or `categories.location`), with `country` |
| description text (checks 5 to 7) | `descriptionPlain` | `content`, HTML entities decoded and tags removed | `descriptionPlain`, then each of `lists` (heading and items, tags removed), then `additionalPlain` |

- **Location text** like "San Mateo, CA United States" or "Palo Alto, CA" is read as city, then a US state code. The state code gives the region ("CA" is California), and "New York City" counts as the city New York. Text that is exactly one of the résumé's remote locations fits, as in JS1. A Lever posting with `workplaceType` "remote" and `country` "US" fits as US remote.
- **Not stated passes:** a posting with no employment type passes check 1, the way a posting that states no years passes check 7. Check 3 still turns away titles with "Intern" or "Internship".
- **Lever's requirements** sit in `lists`, not in `descriptionPlain` (seen on Palantir on 2026-11-06). Leaving them out would pass postings whose requirements were never read.

## Wrong versions

Each one is planted in a copy of the code by `tools/mutants.py`, and the tests must fail on each. JS1's four wrong versions still apply.

1. **Failure shown as success:** (a) a 404 board read as zero postings and reported "0 new"; (b) an empty jobs list read the same way; (c) a run with an unverified board reported `finished`. Caught by tests with saved 404 and empty answers, which require the board to be unverified and the run to end `incomplete`.
2. **Failed board counted as gone:** an unverified board's postings from the last run reported as gone. Caught by a test where a board answers on run 1 and fails on run 2: gone must be 0 and its state unchanged.
3. **Path tricks:** the write check (a) compares path strings, so `runs-evil` passes; (b) checks before resolving `..`; (c) follows a symlink. Caught by the boundary tests.
4. **Budget leaks:** (a) a retry not counted against the request budget; (b) the request budget checked after sending, so an 11th request goes out; (c) a command-line flag that raises a budget. Caught by tests with a stand-in network that counts requests, and a test that a raise is refused.

## The finished wrong answer and its independent check

- **The demonstration:** wrong version 1(a), planted in a copy of the code and run on the saved answers of a real run. That makes it a labeled replay, not a live run. It ends `finished` with exit 0 and reports 0 new for the deliberate-failure board: clean, and wrong.
- **The independent check:** `tools/check_run.py` reads only the saved raw answers and the report, never the agent's code. It recomputes each board's status, postings, new and gone, and flags (1) any board whose saved answer is not HTTP 200 with a non-empty jobs list but is not reported unverified, and (2) any exit that does not follow from the per-board results.

## The trace

Each run writes `runs/<run id>/trace.jsonl`, one line per observation: the budgets at the start, each permission check, each request and its answer (status, bytes, SHA-256, seconds), each parse, each decision (retry or not, unverified or not), each state write and any approval, each Claude call, and the exit. `trace.md` shows the same as a table. Each board's raw answer is saved under `runs/<run id>/boards/<system>-<name>/`.

## Where these choices come from

- **Decided on 2026-11-06 at 3:47 PM ET, after reading all the grader feedback:** the boards (OpenAI on Ashby, Verkada on Greenhouse and Palantir on Lever, all from my real target list) and a made-up Greenhouse name as the board that fails on purpose.
- **Decided on 2026-11-07 at 12:57 AM ET, from measurements:** the budgets (the boards checked on 2026-11-06 answered in 0.1 to 1.05 seconds, the seven Claude calls in my JS1 run 2 took 2.0 to 5.6 seconds each, and OpenAI adds about 10 postings a day); one retry, for transient failures only; my approval for replacing or deleting a board's state; and all four wrong versions.
- **Defaults I accepted when I approved this file (2026-11-07, 1:42 AM ET):** the four exits, their codes and their order; the repeat rule; the 5-second retry wait and the 30-second request timeout; boards as a system and a name, never a URL; GET-only path patterns; a refused request stops the run; the field mapping for Greenhouse and Lever, including "not stated passes" for employment type.
