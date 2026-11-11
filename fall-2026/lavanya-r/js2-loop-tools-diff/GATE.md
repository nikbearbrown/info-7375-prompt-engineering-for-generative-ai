# GATE — Job-Search Agent 2

**Author:** Lavanya R. **Written:** 2026-11-10, before Claude Code changed any JS2 code.

**How this was written (honest provenance):**
- On 2026-11-10 Claude offered options for each section as multiple-choice cards. I picked every decision marked **[my pick]**.
- The short reasons after each pick come from the option text Claude wrote. I chose that option; I did not write those words.
- After my first pass, Claude pointed out that three of my picks conflicted with each other or with the brief. I changed all three; see "Changes" at the end. My first picks are kept there.
- Rows marked **[Claude's default, accepted]** are details I was not asked about. Claude proposed them and I accepted them before any code was written.
- My JS1 feedback asked me to write the rule in my own words instead of picking from options. I did not fully do that here; the two "In my own words" paragraphs (sections 1 and 4) are where I did. Claude fixed only grammar and punctuation in them.

## 1. Exits

A run ends in exactly one of four ways. The run report and the trace always name the exit, the reason, and every board's status. A run that stops is not a run that succeeded.

| Exit | When | Report says | Process exit code |
|---|---|---|---|
| `finished` | every planned board was fetched, parsed and had at least one job; no budget ran out | per-board counts and new jobs | 0 |
| `incomplete` | at least one board failed or was flagged `suspicious_empty`, but the run itself kept going to the end | which boards failed and why; their counts are `null`, never `0` | 2 |
| `budget_exhausted` | a budget (boards, requests or seconds) ran out before every board was visited | which budget, and the list of boards **not visited** | 3 |
| `error` | the run itself could not continue: bad config, a permission refusal, an unexpected crash | the error; what was done before it | 1 |

- 4 boards with 1 broken ends as **`incomplete`** [my pick]: it didn't see every board, so it says which one failed.
- If both a failure and a budget stop happen, `budget_exhausted` wins, because boards were left unvisited. [Claude's default, accepted]

**In my own words:** A run with 1 broken board is incomplete because I was not able to view all the jobs on all the boards, so the run cannot be marked as finished.

## 2. Budgets

| Budget | Max per run |
|---|---|
| Boards | **10** [my pick] |
| Requests (every HTTP request, **including retries**) | **20** [my pick] |
| Seconds (wall clock for the whole run) | **120** [my pick] |
| Seconds per single request (timeout) | 20 [Claude's default, accepted] |

- **Who may change a budget:** only me, by editing this file with a date and a reason [my pick]. The numbers live in `config/budgets.json` and the code checks they match this table. No command-line flag can raise them, and the agent cannot raise its own limits.
- The budget is checked **before** each request. When it runs out, the loop stops and the remaining boards are listed as `not_visited`. [Claude's default, accepted]

## 3. Repeat rule

- **"The same action"** = the same ATS host + the same board name, ignoring capital letters [my pick]. `Databricks` and `databricks` on Greenhouse are the same; `databricks` on Greenhouse and on Lever are not.
- **What the loop does:** skips the second one and writes `skipped: repeat` in the trace [my pick]. A skipped repeat costs no budget.
- A retry allowed by the error policy below is not a repeat. It is the same board's one permitted second try, and it counts against the request budget. [Claude's default, accepted]

## 4. Error policy

| What happened | What the loop does | Retry? | Recorded as |
|---|---|---|---|
| HTTP 404 (board name doesn't exist) | skip the board, continue the loop | **no**: the name won't exist a second later either [my pick, changed; see Changes] | `failed: not_found`, jobs `null` |
| Timeout / connection error | wait 2 s, try **once** more, then give up on that board | **once**: slowness can be temporary [my pick] | `failed: timeout`, jobs `null` |
| HTTP 5xx (server error) | same as timeout | once (the option I picked for 404 said "only timeouts and 5xx get the one retry") | `failed: server_error`, jobs `null` |
| Other HTTP 4xx (e.g. 403) | skip, continue | no [Claude's default, accepted] | `failed: http_<code>`, jobs `null` |
| HTTP 200 but the body isn't JSON or isn't the expected shape | skip, continue | no [Claude's default, accepted] | `failed: bad_body`, jobs `null` |
| HTTP 200 with **0 jobs** | flag it; do **not** call it "no new jobs"; do not update that board's state [my pick, changed; see Changes] | no | `suspicious_empty`, jobs `0`, new jobs `null` |
| Every board failed | end the run as `error` | — | [Claude's default, accepted] |

- **Never invent a value.** A failed board's job count and new-job count are `null`, never `0`, and it is never added to the totals.
- **Escalate to me:** every failed or suspicious board is listed at the top of the run report, for me to look at. The agent does not try to fix board names itself.

**In my own words (why no retry on 404):** 404 means the server could not find the page that was asked for. There is no point retrying the same page again and again, because the same URL will just show 404 again. It is better to change something first (for example, fix the board name) and then try the link again. There is no need to waste budget on something that clearly cannot be found.

## 5. Permission policy

Enforced in the program (`agent/policy.py`), not in a prompt. Every network call and every file read or write goes through it.

**Hosts.** Exactly these three, `https` only, `GET` only [my pick, changed; see Changes]:
- `boards-api.greenhouse.io`
- `api.lever.co`
- `api.ashbyhq.com`

Redirects are checked against the same list. Look-alike names (`api.lever.co.evil.example`, `evilgreenhouse.io`) are refused.

**Writes.** Only inside `runs/` and `state/` in this JS2 folder [my pick]. The real path is resolved first (following `..` and symlinks) and must sit inside one of those two folders. A name that only *starts with* the folder name, like `runs-evil/`, is refused.

**Reads.** Only inside my JS1 and JS2 folders (`fall-2026/lavanya-r/js1-contract-and-watch/` and `.../js2-loop-tools-diff/`) [my pick].

**Needs my approval.** Overwriting an existing file in `state/`, the saved list of jobs already seen [my pick]. Approval is given by me typing `y` at the prompt, or by passing `--approve-state` on a command I run myself. With no approval, the state file is not written and the report says so. [mechanism: Claude's default, accepted]

**Never.**
- Apply, email, message, or log in (required by the brief). There is no code for any of these. The policy refuses any action other than `fetch_board`, `read_file` or `write_file`.
- Read files outside my JS1 and JS2 folders [my pick].
- Send any résumé data to a website [my pick]. Requests are bare GETs to the board URL: no body, no query values taken from the résumé.

## 6. Wrong versions my tests must catch

Plausible-but-wrong implementations [my picks]:

1. **Empty board = "no new jobs".** A board that returns 0 jobs is reported as a quiet day instead of being flagged.
2. **"Contains" host check.** The host check asks "does the URL contain `greenhouse.io`?", so `greenhouse.io.evil.example` gets through.
3. **Retries skip the budget.** The budget counts boards but not retries, so retries can go past the 20-request limit.

The boundary tests also cover the `runs-evil/` prefix trick and the symlink escape, because the brief requires them.

## Changes (before any code), 2026-11-10

Claude pointed out three conflicts in my first picks. I changed all three:

| Section | First pick | Problem Claude pointed out | Final pick |
|---|---|---|---|
| 4, zero jobs | report "no new jobs" | contradicted wrong version 1, which I had also picked | flag as `suspicious_empty` |
| 5, hosts | any name ending in `greenhouse.io` / `lever.co` / `ashbyhq.com` | a plain "ends with" also lets in `evilgreenhouse.io`; close to the "contains" check I marked as wrong | exactly the 3 hosts |
| 4, 404 | retry 3 times | the brief asks why a retry is sound, and a missing name won't appear on retry; also costs 4 of 20 requests | no retry |
