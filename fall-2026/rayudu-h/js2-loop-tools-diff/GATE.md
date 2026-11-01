# GATE.md — Job-Search Agent 2

> **Authorship.** Claude Code (Opus 5.5) wrote the headings as boilerplate on Oct 31, 2026, at Hemanth's request. It then asked Hemanth one question at a time and wrote each answer in. Every decision here is Hemanth's answer. No JS2 code existed while this was written.
>
> Gate written: Oct 31, 2026, finished Oct 31, 2026, 7:07 PM EDT · Commit: [hash, recorded before any JS2 code commit]

Builds on: Job-Search Agent 1 (`../js1-contract-and-watch/`, final commit `72141da`), with the same persona (Priya Nair) and the same rule.

## Boards

| Board | System | Endpoint |
|---|---|---|
| Anthropic | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` |
| Notion | Ashby | `https://api.ashbyhq.com/posting-api/job-board/notion` |
| Perplexity | Ashby | `https://api.ashbyhq.com/posting-api/job-board/perplexity` |
| Failure (a): bad name | Ashby | `https://api.ashbyhq.com/posting-api/job-board/notion-does-not-exist-js2` (answered `HTTP 404 Not Found` when checked on Oct 31, 2026) |
| Failure (b): timeout | Ashby | the real Perplexity endpoint with a deliberately tiny time limit (0.001 s) |
| Failure (c): empty response | Greenhouse shape | a saved file holding `{"jobs": []}`, labeled **SEEDED** wherever it's used |

Chosen by Hemanth, Oct 31, 2026: three boards across two systems (Greenhouse, Ashby), plus all three kinds of deliberate failure. (c) is also the setup for the required finished wrong answer: an empty board reported as "no new jobs".

> **From here down: proposed by Claude Code on Oct 31, 2026, after Hemanth said "do whatever is the best and efficient".** Each section is Hemanth's only once Hemanth accepts or changes it. Status: **accepted by Hemanth as written** ("accept"), Oct 31, 2026, 7:07 PM EDT.

## Exits

The run ends in exactly one of four states. Every one writes `runs/<id>/trace.jsonl` and `report.md`.

| Exit | When | What it reports |
|---|---|---|
| **finished** | every board on the list was fetched, checked and judged | new postings per board, with both verdicts (record and judgment) |
| **incomplete** | at least one board failed (after the error policy), but the run itself completed | the results for the boards that worked; for each failed board, the reason and **"no result"**. It never says "no new jobs" for a failed board |
| **budget-exhausted** | a limit below was reached before every board was tried | which budget, at which board; the boards never tried are listed by name |
| **error** | the run couldn't start or couldn't save its record: invalid résumé, unreadable state, bad config, a refused write | the reason. Nothing is judged and state is not advanced |

So any run that includes the deliberate failures ends **incomplete**. That's the honest outcome.

## Budgets

| Budget | Limit |
|---|---|
| Boards per run | 6 (3 real + 3 deliberate failures) |
| HTTP requests per run | 10 (one per board plus retries) |
| Wall clock per run | 120 s |
| Time limit per request | 30 s (0.001 s for failure b, on purpose) |
| Claude calls per run | 25 |

Who may change them: **only Hemanth**, by a dated edit to this file committed **before** the code that uses the new number. Claude may propose a change but never makes one.

## Repeat rule

- **The same action** means the same method and URL in one run. A second identical request is refused and logged; it doesn't count toward the budget, and it isn't sent.
- **The same posting** means the same (system, board, posting id). Ids are only unique inside one board, so the key always includes the board. A duplicate id inside one response is counted once and logged.
- Across runs, a posting is reported as new only once (the state file).

## Error policy

| Failure | Retry? | Why | Then |
|---|---|---|---|
| HTTP 404 / 410 (e.g. a bad board name) | **no** | permanent: retrying gets the same answer and wastes budget | board **failed**; the report asks Hemanth to check the name |
| timeout, connection error, HTTP 429 or 5xx | **once**, after 2 s | often transient; one retry bounds the load on the board and fits the budget | if the retry fails too: board **failed** |
| response not JSON, or the wrong shape | no | a retry won't fix a format change | board **failed**, raw bytes saved as evidence |
| **empty list** of postings where the last good run had some | no | it may be real, but a sudden empty board is more likely a broken fetch | board **unverified**: no "no new jobs", no state update for that board; the run is **incomplete** |

No failure is ever turned into a value. A failed or unverified board never produces "0 new".

## Permission policy (enforced in code, not in a prompt)

- **Hosts:** HTTPS GET only, to `boards-api.greenhouse.io` and `api.ashbyhq.com`. Every redirect target is checked against the same list.
- **Writes:** only inside this folder's `runs/` and `state/`. Each path is resolved first, so these are all refused:
  - `..`;
  - a prefix trick such as `runs-evil/` beside `runs/`;
  - a symlink that points outside.
- **Reads:** the persona file, the state, and saved fixtures inside this folder. A read request is never treated as permission to write.
- **Needs Hemanth's approval** (`--approve reset-state`): resetting or deleting a state file. That would make every posting "new" again.
- **Never:** apply, email, message, log in, send POST/PUT, follow links inside postings, or send the persona's contact fields to Claude.

## Wrong versions (the tests must catch them)

1. **An empty board reported as "no new jobs"** and the run marked finished. This is JS1's agent unchanged, and it's the finished wrong answer this assignment asks for.
2. **Retrying a 404.** It wastes budget, and with no limit it never ends.
3. **Checking paths by string prefix.** `path.startswith("runs")` accepts `runs-evil/`.
4. **Keying postings by id alone across boards.** Two boards with the same id collide, and a new posting goes missing.

## Amendments

> Added by Claude Code on Oct 31, 2026, at about 7:20 PM ET, while building. Each needed Hemanth's acceptance before it replaced the original text.

- **A1. Failure (b) moves from Perplexity to OpenAI (Ashby).** As written, failure (b) used the same URL as the real Perplexity board. The repeat rule refuses a second identical GET in one run, so the timeout would never be attempted. OpenAI's Ashby board (810 postings on Oct 31) is on an allowed host, and its URL is used nowhere else in the run. Status: **accepted by Hemanth** ("yes to A1 and A2"), Oct 31, 2026, 7:17 PM EDT.
- **A2. A retry under the error policy is not a "repeat".** The repeat rule refuses a second identical request, but the error policy allows one retry of the same GET after a timeout or 5xx. Reading: the repeat rule applies across board entries; the single retry inside one board's error policy is exempt, is logged as `retry`, and **does** count toward the request budget. Status: **accepted by Hemanth** ("yes to A1 and A2"), Oct 31, 2026, 7:17 PM EDT.
