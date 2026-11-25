# GATE - Early Bird, JS2 slice

**Owner:** Vrajesh N. · **Written:** 2026-10-31, before any JS2 code
**Starting point:** my JS1 agent (`../js1-contract-and-watch/`, commit d19465d). The rule (R1-R4), the validator, the fictional resume and the seen-ids watch carry over unchanged.

> How this was written: Claude asked me multiple-choice questions on 2026-10-31, using board counts and 404 responses it had just fetched. My picks are marked *(chosen 10-31)*. Items marked *(proposed by Claude)* are Claude's draft, and each one carries my accept/change note.

## Boards *(chosen 10-31)*
Nine real boards on three ATS platforms, plus one deliberately bad board:

| Key | Platform | URL | Postings when checked 10-31 |
|---|---|---|---|
| ashby:commure | Ashby | `https://api.ashbyhq.com/posting-api/job-board/commure` | 84 |
| greenhouse:stripe | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | 745 |
| greenhouse:figma | Greenhouse | `.../boards/figma/jobs?content=true` | 140 |
| greenhouse:gleanwork | Greenhouse | `.../boards/gleanwork/jobs?content=true` (Glean) | 127 |
| greenhouse:databricks | Greenhouse | `.../boards/databricks/jobs?content=true` | 901 |
| greenhouse:doordashusa | Greenhouse | `.../boards/doordashusa/jobs?content=true` (DoorDash) | 439 |
| greenhouse:twitch | Greenhouse | `.../boards/twitch/jobs?content=true` | 63 |
| greenhouse:roblox | Greenhouse | `.../boards/roblox/jobs?content=true` | 268 |
| lever:palantir | Lever | `https://api.lever.co/v0/postings/palantir?mode=json` | 301 |
| greenhouse:stripe-typo | Greenhouse | deliberate failure *(chosen 10-31)*: a bad name that returned a real HTTP 404 on 10-31 | - |

## Exits
Every run ends with exactly one exit status and writes a trace (`reports/<label>-trace.jsonl`) and a summary (`reports/<label>.md`). **Stopping does not mean success.** `finished` only means the loop reached the end of the board list. Whether the numbers are right is a separate question, answered by the independent check (`python -m earlybird check`). *(proposed by Claude)*

| Exit | When | Seen-state written? | Process exit code |
|---|---|---|---|
| `finished` | every board was attempted and none ended in `error` | yes, for every board | 0 |
| `incomplete` | at least one board ended in `error`; the others ran | yes, only for boards that succeeded | 1 |
| `budget-exhausted` | a budget was reached before the next action; the boards not attempted are listed by name | yes, only for boards that succeeded | 3 |
| `error` | a permission refusal or an unexpected exception; the whole run stops at once and needs a human | no | 2 |

## Budgets *(chosen 10-31; first pick 6/8/120 raised once Claude pointed out 9 boards + 1 bad board do not fit)*

| Budget | Per run | Checked |
|---|---|---|
| boards | 12 | before each board starts |
| requests | 15 | before each request, retries included |
| seconds | 180 | before each request (wall clock since run start) |

- **Who can change them:** only me, by editing this table and the matching constants in `earlybird/gate.py` in a reviewed commit. *(proposed by Claude)*
- The command line may **lower** a budget for one run (`--max-requests 3`), never raise it. A higher value is refused. *(proposed by Claude)*

## Repeat rule *(proposed by Claude)*
- **Same action** = the same tool with the same arguments in one run. For `fetch`, that means the same normalized URL (lower-case host, same path and query).
- The first one runs. Any later identical action in the same run is **refused without touching the network**, recorded in the trace as `repeat-refused`, and does not use up the request budget.
- The single retry allowed by the error policy is not a repeat. It is recorded as `retry 1/1` and does use up the request budget.
- Fetching the same board on a later run is not a repeat. Re-checking boards across runs is the whole point of the watch.

## Error policy *(chosen 10-31)*

| What happened | Action | Why |
|---|---|---|
| HTTP 404 or other 4xx | no retry; board = `error` | a wrong name or a refusal is not fixed by asking again |
| timeout, connection error, HTTP 5xx | wait 5 s, retry **once**; if it fails again, board = `error` | these are often momentary; one retry costs 1 request out of 15 |
| response is not JSON, or has the wrong shape | no retry; raw bytes saved; board = `error` | the same server will send the same bytes |
| permission refusal (host, path, approval) | stop the whole run, exit `error`, needs a human | this is a bug or an attack, not a flaky network |

No value is ever invented for a failed board. Its count is `null` (not `0`) in the trace and the report says "error", never "0 new".

## Permission policy (enforced in `earlybird/policy.py`, not in a prompt) *(proposed by Claude)*
- **Hosts:** `api.ashbyhq.com`, `boards-api.greenhouse.io`, `api.lever.co`. Exact host match, `https` only, no username or password in the URL, `GET` only.
- **Read:** any file inside this folder. Nothing outside it.
- **Write without asking:** `data/raw/`, `data/state/`, `reports/`.
- **Write only with my approval:** `config/boards.json` (the board list). The agent shows the change and I must type `yes`. Anything else is a refusal.
- **Everything else:** refused, including any path that resolves (after `..` and symlinks) outside an allowed folder.
- **Never:** apply, email, message, or log in anywhere. There is no tool for any of these. The fetch tool sends no cookies or credentials and has no POST.

### Boundary cases, expected result written before the tests *(proposed by Claude)*

| # | Request | Expected |
|---|---|---|
| B1 | fetch `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | allowed |
| B2 | fetch `https://evil.example.com/jobs` | refused: host not on allow-list |
| B3 | fetch `https://api.lever.co.evil.com/v0/postings/x` (allowed host as a prefix) | refused: host not on allow-list |
| B4 | fetch `http://api.lever.co/v0/postings/palantir` (plain http) | refused: https only |
| B5 | fetch `https://me:pw@api.ashbyhq.com/posting-api/job-board/commure` | refused: credentials in URL |
| B6 | write `reports/run.md` | allowed |
| B7 | write `reports/../GATE.md` (`..` escape) | refused: outside writable folders |
| B8 | write `reports-evil/x.md` (sibling prefix of `reports`) | refused: outside writable folders |
| B9 | write `reports/link/x.md` where `reports/link` is a symlink to a folder outside the project | refused: resolves outside |
| B10 | read `config/boards.json` | allowed |
| B11 | read a file outside the project folder | refused |
| B12 | write `config/boards.json` with no approval | refused: needs approval |
| B13 | write `config/boards.json`, approver types `yes` | allowed |
| B14 | write `config/boards.json`, approver types `y` or nothing | refused |
| B15 | write `data/state/seen.json` | allowed |
| B16 | fetch with method `POST` to an allowed host | refused: GET only |

## Wrong versions the tests must catch *(proposed by Claude)*
1. **Lever read as `.get("jobs", [])`.** Lever returns a bare list, so Palantir parses to 0 postings and the run says `finished`, "0 new". This is also the finished-but-wrong demonstration.
2. **404 swallowed as an empty board.** The bad board shows "0 postings" and the run says `finished` instead of `incomplete`.
3. **Path check by string prefix** (`str(path).startswith(str(reports))`). This lets `reports-evil/` through (B8).
4. **Budget checked after the request.** Request 16 actually goes out.
5. **Retry on 404.** The bad board is fetched twice.

## Finished-but-wrong demonstration and independent check *(proposed by Claude)*
- Replay the saved responses with wrong version 1 plugged in. Expected: exit `finished`, Palantir "0 postings, 0 new". Clean and wrong.
- **Independent check** (`earlybird/check.py`): it does not use the agent's parser or the agent's report. It re-opens each raw file named in the trace, counts the items with its own few lines (`len(list)` or `len(obj["jobs"])`), and compares with the count the trace claims. It also flags any board whose count fell to 0 when the last state showed postings. Expected: it flags Palantir (claimed 0, raw file has about 300).

## Accept / change notes (mine)
- [x] 2026-10-31: I accepted the exits, budgets-only-lowered rule, repeat rule, permission policy, boundary cases B1-B16, wrong versions and the independent check as written (my answer to Claude's question: "Accept as written"). No changes.
