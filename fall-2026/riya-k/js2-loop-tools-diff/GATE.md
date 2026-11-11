# GATE — Job-Search Agent 2

Riya Kapadnis · written 2026-11-09, **before any JS2 code existed**.
The decisions are mine (chosen in chat on 2026-11-09). Claude Code wrote them up in this wording, and I checked it.
Starting point: my JS1 agent (`../js1-contract-and-watch/`, final commit 3c098e1). Board slugs come from the instructor's
Lectern `ATS.md`, re-probed by hand on 2026-11-09 (see "Board facts" at the end).

## Boards for this run (6)

| # | Board | System | Purpose |
|---|---|---|---|
| 1 | `databricks` | Greenhouse | real board (continues JS1) |
| 2 | `anthropic` | Greenhouse | real board |
| 3 | `openai` | Ashby | real board |
| 4 | `notion` | Ashby | real board |
| 5 | `notarealco-js2` | Ashby | **fails on purpose**: bad name, returns HTTP 404 |
| 6 | `hubspot` | SmartRecruiters | **empty-board trap**: HubSpot is not on SmartRecruiters, but the API returns HTTP 200 with 0 postings |

## Exits

A run ends in exactly one of these. It always reports its status, which boards it ran, and the reason it stopped.
**A loop that stops is not a loop that succeeded.**

| Status | When | What it reports |
|---|---|---|
| `finished` | every board was read with a usable answer (HTTP 200, more than 0 postings, parsed) | per-board counts and new postings |
| `incomplete` | the loop ran through its list, but at least one board failed or was flagged `suspect_empty` | everything `finished` reports, plus each failed or flagged board with its reason, and "escalated to Riya" |
| `budget_exhausted` | a budget ran out before the list was done | what it did read, plus the boards it **never ran** |
| `error` | something outside a single board broke (bad config, a policy refusal, the state file can't be read) | the exception; no partial verdicts presented as a result |

A failed board is **never** reported as "0 postings" or "no new jobs." Its count is `null`, with the reason.

Because boards 5 and 6 are planted, **every live run of this list ends `incomplete` by design.** The `finished` exit is
shown by a run over boards 1–4 only, from saved responses, and labeled **seeded**.

## Budgets (per run)

- At most **6 boards**
- At most **10 HTTP requests** in total (6 boards plus room for up to 4 retries)
- At most **60 seconds** of wall-clock time

The loop checks the budget **before** each request. If the next request would go over, it stops with `budget_exhausted`.
**Only I change a budget, and only by adding a dated amendment to this file.** Code, a prompt, or Claude cannot raise it.
Retry waits count toward the 60 seconds. With 6 boards and one retry each, a bad day could need 12 requests, so the 10-request cap is real.

## The independent check (not part of the agent)

The finished-wrong-answer demo runs the loop in a **deliberately naive mode** (`--no-empty-guard`, wrong version #1 below),
labeled as a demonstration. In that mode the empty SmartRecruiters `hubspot` board is reported as "0 new" and the run says `finished`.
The agent's own report is not trusted to catch this. A **separate program** checks every board the report says has 0 postings
against a second source (for HubSpot: Greenhouse `hubspotjobs`) and flags any contradiction.
It has its own budget (**1 request per board checked**), uses the same host allow-list, and writes only to `runs/checks/`.

## Repeat rule

"The same action" = the same HTTP method plus the same full URL within one run.
- The loop makes each board's request **once**. The only allowed repeat is the single retry the error policy permits.
- Any other repeat is **blocked before it is sent**, recorded in the trace as `repeat_blocked`, and does not count as a new result.
- The same board listed twice in the config is read once (the duplicate is recorded as skipped).

## Error policy (per board)

| What happened | Action | Why |
|---|---|---|
| Timeout, connection error, HTTP 5xx | wait 2 s, **retry once**; if it fails again, mark the board `failed` | these can clear on their own, and a GET to a public board changes nothing, so retrying is harmless |
| HTTP 4xx (e.g. 404 bad name) | **no retry**; mark `failed` | a wrong name stays wrong, so a retry would only waste budget |
| HTTP 200 but the body doesn't parse or has the wrong shape | **no retry**; mark `failed` | the same bytes will come back |
| HTTP 200 with **0 postings** | mark `suspect_empty`, **escalate to me** | a real company with zero openings is rare; a wrong slug or wrong system is much more likely |

A failed or flagged board never stops the other boards. It makes the run `incomplete` and is escalated to me in the report.

## Permission policy (enforced in code, not in a prompt)

**Hosts the agent may call** (https, GET only):
`boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.smartrecruiters.com`. Every other host is refused before any connection is made.

**Folders it may write:** only inside the `--out` folder (default `runs/`). The resolved real path must be inside it, so
`..`, a look-alike sibling folder (`runs-evil` next to `runs`), an absolute path elsewhere, and a symlink pointing outside are all refused.

**Reads vs. writes:** it may read its config, the persona, and its own state and fixtures. Read permission never implies write permission.

**Needs my approval (`--approve`):** any write that **removes** posting ids from a state file (a reset, or shrinking it).
Without `--approve`, nothing is written and the refusal says why. Normal runs only add ids, so they need no approval.

**Never, under any flag:** apply to a job, email, message anyone, log in, send a POST/PUT/DELETE, or show a real résumé.
The persona is fictional (Arya Sahni, same as JS1).

## Wrong versions my tests must catch

1. **Empty board reported as success:** a 200 with 0 postings counts as "0 new" and the run says `finished`.
2. **Failure turned into a number:** a 404 board recorded as `postings: 0` instead of `null` plus the reason.
3. **Wrong exit:** the run says `finished` while a board failed, or while some boards were never run because a budget ran out.
4. **Retrying the wrong thing:** retrying a 404, retrying more than once, or retrying with no wait.
5. **Budget off by one:** making the 11th request, or starting a board after 60 s.
6. **Prefix path check:** `str(path).startswith("runs")` lets `runs-evil/x.json` through.
7. **Substring host check:** `"greenhouse.io" in url` lets `boards-api.greenhouse.io.evil.com` through.
8. **Symlink escape:** checking the path text but not the resolved real path.
9. **Intern posting rated relevant** (the defect my JS1 hand check found; the TA asked for the fix).

## Board facts (probed by hand with curl, 2026-11-09)

- Ashby `notarealco-js2` → 404 `Not Found`
- Greenhouse `hubspot` → **404** (Lectern's ATS.md says it returned an empty board in September; that is no longer true)
- Greenhouse `hubspotjobs` → 200 with postings (HubSpot's real board, used by the independent check)
- SmartRecruiters `hubspot` and `notarealco-js2` → 200 `{"totalFound":0,"content":[]}`, the empty-board trap

## Amendments

(none yet; each must be dated and say why)
