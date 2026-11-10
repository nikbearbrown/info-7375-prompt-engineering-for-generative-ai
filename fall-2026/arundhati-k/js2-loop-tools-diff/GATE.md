# GATE — Job-Search Agent 2 (written before any code)

Arundhati K · INFO 7375 · Fall 2026

> **Provenance.** Drafted by Claude Code on 2026-11-10 at my request (I chose "Claude drafts, I edit"
> when I did not yet know how to set budgets or an error policy). I reviewed it and accepted it
> without edits at commit time; any change I make later goes under **Revisions**, dated, and the
> sections above stay as committed. Reviewed by: Arundhati K, 2026-11-10 (my reply in the Claude Code
> session: "Reviewed, commit it"). Committed before any code in this folder exists.

Started from: my JS1 agent (`../js1-contract-and-watch/`: Stripe on Greenhouse, persona Rohan Desai,
allow-listed GET-only fetcher). Board choices checked against the instructor's Lectern list
(`../../nik-bear-brown/lectern/sources.json`, probed 2026-09-26).

## 0. Boards

| # | board | ATS | why |
|---|---|---|---|
| 1 | `stripe` | Greenhouse | my JS1 board |
| 2 | `figma` | Greenhouse | second Greenhouse board, different size |
| 3 | `notion` | Ashby | second applicant-tracking system |
| 4 | `stripe-js2-does-not-exist` | Greenhouse | **fails on purpose** (bad name → 404) |

## 1. Exits

Exactly one exit per run, printed first in the report and saved in the trace.

| exit | when | what the report says |
|---|---|---|
| `finished` | every board in the list was visited, every one returned a valid, non-empty board, and no budget was hit | counts per board; new postings per board |
| `incomplete` | every board was visited, but at least one failed or came back empty-and-unverified | which boards succeeded (with counts), which did not and why; **no count for a failed board** |
| `budget-exhausted` | a budget (boards, requests, seconds) ran out before every board was visited | the budget that ran out, boards done, **boards never visited** |
| `error` | the run could not run safely: bad config, a permission-policy violation, or zero boards succeeded | the reason; nothing is written to the state file |

A run that stops is not a run that succeeded: only `finished` means "I looked at everything I was asked
to look at." Three boards OK and one failed is `incomplete`, never `finished`.

## 2. Budgets

| budget | max per run | why this number |
|---|---|---|
| boards | 5 | 4 boards today; 1 spare so adding a board is a deliberate edit, not a slow creep |
| requests | 8 | 1 GET per board (Greenhouse and Ashby return the whole board in one call) + at most 1 retry each for 4 boards |
| seconds | 120 | 4 requests × 30 s timeout (JS1's timeout) leaves no room; 120 s covers normal runs (~a few s) and stops a hung run |

Who may change a budget: only me, by a new dated line under **Revisions** below and the matching change
in `config/budgets.json`. The code reads the budget from that file and never raises it itself.

## 3. Repeat rule

"The same action" = the same method + normalised URL (scheme, host, path, sorted query) within one run.
The second time, the loop does **not** send the request: it records a `repeat-skipped` observation in the
trace and moves on. A board listed twice in the config is therefore fetched once.

## 4. Error policy

| failure | action | retries | why |
|---|---|---|---|
| 404 / bad board name | record `error: not-found`, continue to next board | 0 | the board does not exist; asking again returns the same 404 and wastes budget |
| other 4xx | record, continue | 0 | a client-side problem a retry cannot fix |
| timeout / connection error / 5xx | retry once after 2 s, then record and continue | 1 | can be transient; one retry is cheap and bounded by the request budget |
| not JSON / unexpected shape | record `error: bad-shape`, continue | 0 | the same bytes would come back |
| empty board (0 postings) | record `empty-unverified`, continue; run cannot be `finished` | 0 | an empty board might be real or might be broken; the agent cannot tell, so it escalates to me in the report |

Never: report a failed or empty board as "0 new jobs", reuse an old count for it, or mark its postings as
seen. A failed board shows `—` and the reason.

## 5. Permission policy

Enforced in code (`jsagent2/policy.py`), not in a prompt.

- **Hosts it may call:** `boards-api.greenhouse.io`, `api.ashbyhq.com`. https only, GET only, no
  credentials in the URL; a redirect is followed only if its target is also on the list.
- **Read:** anything inside this folder (`config/`, `persona/`, `out/`). Nothing outside it.
- **Write:** only inside `out/` in this folder. The path is resolved (`..` and symlinks followed) and must
  still be inside `out/`. A sibling like `out-evil/` is outside. A symlink inside `out/` that points
  elsewhere is refused.
- **Writes that need my approval:** overwriting `out/state/seen.json` (the seen-jobs state that decides
  what is "new" next run) and deleting anything. Approval = I pass `--approve-state-write` on the command
  line for that run; without it the run reports the write as `held-for-approval` and does not do it.
- **Never:** apply, email, message, log in, POST/PUT/DELETE, send cookies or tokens, or read my real
  résumé.

## 6. Wrong versions my tests must catch

1. An empty board reported as `finished` with "0 new jobs" (the finished wrong answer).
2. A failed board counted as 0 postings instead of no value.
3. A path check done with `startswith("out")` that lets `out-evil/` through.
4. A path check that does not resolve symlinks, so `out/link → /tmp` lets a write escape.
5. A host check that matches by substring, so `boards-api.greenhouse.io.evil.com` passes.
6. A retry loop that retries a 404 (or retries forever) until the request budget is gone.
7. A run that hits the budget but reports `finished` and silently drops the unvisited boards.

## Revisions

<!-- Later changes go here, dated, without editing the sections above. -->
