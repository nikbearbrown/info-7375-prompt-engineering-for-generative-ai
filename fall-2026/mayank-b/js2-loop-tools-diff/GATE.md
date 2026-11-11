# GATE — Job-Search Agent 2 (the loop, the tools, the diff)

## Executive summary

**What this is.** The rules my job-search agent must obey, written on 2026-11-10 **before any JS2 code existed**: how a run may end, how much it may spend, what counts as repeating itself, what it does when a board fails, what it may touch, and the wrong programs my tests must catch.

**Why it comes first.** Claude Code writes the code against this file, and I check the code against this file. A rule written after seeing the output would only describe the output.

**What it decides.** The agent reads at most 5 public job boards per run through two ATS APIs, writes only inside its own run folder, and never applies, emails, messages or logs in. A run that ends is not a run that succeeded. Whether the jobs it reports are right is judged by a separate checker against floors I set, never by the agent's own report.

**Authorship.** My answers are verbatim in `notes/gate-answers-2026-11-10.md`. Claude Code wrote this file from them; its edits are listed at the end.

---

## 1. Exits

The loop ends in exactly one of four statuses. **None of them means "the answers are right".**

| Exit | When | What the run reports |
|---|---|---|
| `finished` | every planned board entry was attempted within budget. A board that failed and was handled still counts as attempted (decision 1a). | per-board result `ok` / `error`, new jobs per `ok` board, and the "needs Mayank" line |
| `incomplete` | at least one planned entry was **not attempted for a reason other than budget**: it was skipped as a repeat | which entries were skipped and why |
| `budget-exhausted` | a cap in §2 was reached before every planned entry was attempted | which cap, and which boards were never tried |
| `error` | a run-level fault that must stop everything: invalid plan or budget config, a planned host off the allow-list, a write refused by the permission policy, invalid persona | the reason. **`state/` is not touched.** |

- `finished` is **not** success (decision 1b). Success is a separate judgment: the independent checker (§5) plus my review.
- Process exit codes: `0` = no board needs me · `3` = at least one `error` or `suspect` board needs me (decision 4b-B) · `2` = run-level `error`.

## 2. Budgets

| Cap | Value | Checked |
|---|---|---|
| Boards per run | **5** | before each board is attempted (repeats skipped without a request don't count) |
| HTTP requests per run (including retries) | **10** | **before** each request is sent: the 11th request is never sent |
| Wall-clock seconds per run | **60** | before each request. A request already in flight may finish up to its timeout past the cap; the trace records the actual elapsed time. |
| Timeout per request | **10 s** | by the HTTP call |

**Who may change a budget:** only me, by a new dated line in the Decisions log (§9). The values live in `config/budgets.json`; a test fails if that file differs from the table above (decision 2b).

## 3. Repeat rule

- **The same action** = the same ATS **and** the same board slug, compared after URL-decoding and case-folding. `Notion` = `notion`; `Jasper%20AI` = `Jasper AI`.
- On a repeat the loop **does not send the request**, writes `skipped: repeat` to the trace, and does not count it against the request or board budgets (decision 3b). A run with a skipped repeat ends `incomplete` (§1), because the plan as written was not carried out as written.

## 4. Error policy

A board **fails** when it returns HTTP 4xx/5xx, times out, has a network error, or returns a body that is not the JSON shape its ATS promises.

| Failure | Retry? | Why |
|---|---|---|
| timeout, connection error, HTTP 5xx | **once**, if the request budget allows | transient: the same request can succeed a moment later |
| HTTP 404 / any other 4xx | **never** | the same request fails the same way; a retry is repetition, not progress |
| malformed body (not JSON / wrong shape) | **never** | same reason |

After the final failure the board is marked `error` with the reason, **its saved state is left untouched** (no seen-ids written, none erased), and the loop moves to the next board.

**Escalation (decision 4b = A + B + C):**
- **A.** The report's first line reads `NEEDS MAYANK:` followed by every `error` board (from the loop) and every `suspect` board (from the checker). The agent **never changes a slug, a plan or a floor itself.**
- **B.** The program exits with code **3** whenever that line is non-empty.
- **C.** An `error` or `suspect` board's seen-ids are **held**: even with a valid `--approve-state`, they are not updated until I acknowledge that board by name with `--ack <ats>/<slug>`.

**Never** (4c): report a failed board as "0 jobs" or "no new jobs", or copy an earlier run's jobs in as if they were fetched.

## 5. The finished-wrong answer and its independent check

A run can end `finished` and still be wrong. The planned demonstration: Greenhouse slug `hubspot` returns HTTP 200 with an empty job list, because HubSpot's real board is `hubspotjobs` (Lectern `ATS.md`, verified 2026-09-26). The agent then honestly reports "0 jobs, 0 new", which is false about HubSpot.

**The check (decision 5a):** `checker/check.py`, a separate program that **does not import the agent's code**. It reads only:
1. the run's **saved raw responses** (never the agent's report), and
2. `config/expected-boards.json`, a floor per board **that I write, each with a named source** (decision 5b). No source means the floor is `unknown`, and an unknown floor is never filled in with a guess.

A board is `suspect` if its raw response holds **0 postings**, **fewer than its floor**, or **more than 80% fewer than the previous run's raw response** for the same board.

## 6. Permission policy (enforced in code, not in a prompt)

| | Allowed | Why this is the least that works |
|---|---|---|
| **Hosts** | `boards-api.greenhouse.io`, `api.ashbyhq.com`. Exact host match, `https` only, **GET only**, **redirects refused** | the two public, unauthenticated APIs the boards need. Exact match blocks `boards-api.greenhouse.io.evil.com`; refusing redirects stops an allowed host handing the request to one that isn't. The Claude judge from JS1 is **out**, so `api.anthropic.com` is not on the list. |
| **Read** | `config/`, `persona/`, `state/`, `runs/` | the plan, caps, persona, the last approved state, and earlier runs for the 80% comparison. Nothing else is needed. |
| **Write, no approval** | `runs/<this-run-id>/` only | the run's own record (trace, raw responses, report, proposed state). It changes nothing a future run depends on. |
| **Write, needs my approval** | `state/seen-ids.json` only | this decides what future runs call "new", so a wrong write silently changes every later report |
| **Never** | any other path; `..` escapes, sibling-prefix paths (`runs-evil`), symlinks that resolve outside the allowed folder; apply, email, message, log in, submit forms, any non-GET request, reading or sending credentials, following redirects | none of these is needed to read a public board |

**Paths are judged by where they resolve to** (`Path.resolve()`, which follows symlinks), and containment is checked with path components (`is_relative_to`), **not string prefixes**.

**Approval (decision 6c):** `--approve-state <run-id>` approves only when the value is a string **exactly equal** to the run id being applied. `yes`, `1`, `true` or another run's id are refused. Approval is a separate command run after the checker. It refuses to proceed if the checker's output for that run does not exist.

## 7. Wrong versions my tests must catch

| # | Wrong version | Caught by |
|---|---|---|
| W1 | **Prefix trick:** containment by `str(path).startswith(str(root))` lets `runs-evil/x` through | boundary test |
| W2 | **Symlink escape:** a link inside `runs/<id>/` pointing outside is followed | boundary test (the review-packet defect, §8) |
| W3 | **Truthy approval:** `--approve-state yes` or `1` approves a write | boundary test |
| W4 | **Empty board = fine:** `hubspot`'s empty list reported as "no new jobs" with no flag | checker test |
| W5 | **Failure as zero:** a 404 board reported as 0 jobs instead of `error` | loop test |
| W6 | **Stopped = success:** a budget-exhausted run labelled `finished` | loop test |
| W7 | **Repeat counted as progress:** the same board fetched twice and both counted | loop test |
| W8 | **Host check by substring:** `boards-api.greenhouse.io.evil.com` passes | boundary test |
| W9 | **(mine) State wiped on failure:** a failed board's seen-ids are saved as empty, so the next run reports every job as new | loop + approve test |

`scripts/wrong_versions.py` plants each one and shows which test fails.

## 8. Review-packet change (Chapter 6)

The defect: JS1's `safeWrite` checks containment after `path.resolve`, which cleans `..` but **does not follow symlinks**. A link inside an allowed folder can point anywhere. JS2's first permission code ports that behaviour faithfully. The packet:
1. reproduce it with a failing test written **before** the patch;
2. ask Claude Code for the fix;
3. read the diff as a change in behaviour and check scope;
4. run the commands myself;
5. accept, revise or reject on that evidence;
6. name one case the test still misses.

## 9. My failure sentence and the decisions log

**Failure sentence (2026-11-10):** *If my loop were wrong, I would see a board reported as "no new jobs" while its saved raw response is empty or an error.*

**Decisions log** (the only way a budget or rule changes):

| Date | Decision | By |
|---|---|---|
| 2026-11-10 | Initial gate: budgets 5 boards / 10 requests / 60 s / 10 s; rules above | Mayank Bhadrasen |

## Changes Claude made when turning my answers into this file

1. Defined `incomplete` precisely: an entry skipped as a repeat makes the run `incomplete`. My answers listed the four exits but didn't define it.
2. Said that the request and seconds caps are checked **before** each request, and that a request in flight may finish past the 60 s cap. My answer gave only the numbers.
3. Added exit code `2` for a run-level error, next to my `3` (4b-B) and `0`.
4. Made approval a separate command that refuses to run before the checker has written its output for that run. That's how 4b-C can know which boards are `suspect`.
5. Added "why this is the least that works" to each permission row, the defence the TA asked for in JS1's feedback.
6. Board name format for `--ack` is `<ats>/<slug>`.
