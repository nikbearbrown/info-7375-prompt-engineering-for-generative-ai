<!--
Written by Shreyash Yadav and pasted into the Claude Code session on 2026-11-09, before any code,
test or run existed for this assignment. Claude changed formatting only (headings and bullets).
The words are as pasted. Budgets change only by a new dated entry at the end of this file.
-->

# GATE — Job-Search Agent 2

## 1. Boards

OK with the suggested boards. I'll use Greenhouse `oscar` and `klaviyo`, Ashby `linear`, and Lever `palantir`. I'll also test `oscarhealth-doesnotexist` as a deliberate failure and `whoop` as an empty board. The loop should tell the difference between an empty board, a failed board, and a board with no new jobs.

## 2. Exits

`finished` means all requested boards were checked successfully, even if there are no new jobs. `incomplete` means at least one board failed or could not be checked, but the run still produced partial results. `budget-exhausted` means the run hit a limit before completing. `error` means something critical went wrong and the run cannot safely continue. Each report should show which boards succeeded, failed, or were skipped, along with the job counts that were actually verified. If 3 of 4 boards work, I would mark it `incomplete`, not `finished`.

## 3. Budgets

I'll use a maximum of 6 boards, 12 requests, and 120 seconds per run. These limits can only be changed by me through a new dated entry in `GATE.md`. The agent should not increase its own limits.

## 4. Repeat rule

The same action means requesting the same board and URL with the same parameters more than once in a run, unless it is an allowed retry. The loop should skip duplicate requests and record that they were skipped. It should not keep repeating an action that already succeeded.

## 5. Error policy

Retry once for a timeout or temporary server error (5xx), because those might recover. Don't retry a 404, invalid board name, or bad JSON automatically. Record the failure and continue with the remaining boards. If a problem needs a decision, flag it for my review. Never invent job counts or treat a failed request as zero jobs.

## 6. Permission policy

Only allow requests to `boards-api.greenhouse.io`, `api.ashbyhq.com`, and `api.lever.co`. The agent can write run results and logs inside `runs/`. Overwriting or deleting saved state or raw evidence requires my approval. It must never apply for jobs, send emails or messages, log into accounts, or access unrelated websites. Paths outside `runs/` should be rejected.

## 7. Wrong versions

My tests should catch these mistakes:

- Treating an empty board as successfully checked with zero new jobs without identifying that the board itself is empty.
- Silently skipping a failed board and marking the run `finished`.
- Allowing writes to `runs-evil/` because the name starts with `runs`.
- Retrying a 404 repeatedly instead of stopping.
- Reporting unverified job counts after a failed API response.

## 8. Review packet

OK with fixing the JS1 rule defects. I'll focus on counting experience only from mandatory qualifications, rejecting hybrid jobs even when they have a Remote tag, and making sure remote jobs can actually be worked from Massachusetts. I'll use the five real postings as test cases before making the changes, then run the same tests afterward to show what improved. I'll document the results and any remaining limitations instead of claiming everything works without evidence.

## Budget decisions

*Table added by Claude Code as the place for the dated entries section 3 asks for; the first row copies section 3.*

| Date | Boards | Requests | Seconds | Decided by |
|---|---|---|---|---|
| 2026-11-09 | 6 | 12 | 120 | Shreyash (section 3 above) |
