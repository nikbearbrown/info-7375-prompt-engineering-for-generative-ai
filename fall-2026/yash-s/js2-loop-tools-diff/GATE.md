# Job-Search Agent 2 — Gate

**Date:** 2026-11-09  
**Course:** INFO 7375, Fall 2026  
**Starting point:** My Job-Search Agent 1 project

## 1. Exits

My agent will watch multiple job boards using a bounded loop.

The loop must always stop and report why it stopped.

I will use four exit statuses:

### Finished

The agent processed every board in the planned run without any unresolved failures.

It stayed within the request, time, and board budgets.

It reports the number of boards checked, new postings found, and requests used.

Finished means the planned work was completed. It does not automatically mean every relevance judgment is correct.

### Incomplete

The agent could not finish checking one or more boards, but it continued with the remaining boards when it was safe to do so.

For example, if a board returns HTTP 404, the agent records the failure and continues.

It reports which boards succeeded, which failed, and what information is missing.

A failed board must not be reported as having zero new jobs.

### Budget-exhausted

The agent reached its maximum number of boards, requests, or seconds before completing the planned work.

It stops instead of increasing its own limits.

It reports which budget was reached, what work was completed, and which boards were not checked.

### Error

The agent encountered a problem that prevents it from continuing safely.

Examples include invalid configuration, a permission violation, corrupted state, or failure to save required evidence.

It stops and reports the error without pretending that the run succeeded.

### Exit Decision

If several problems occur, the agent must record all of them.

A blocking safety or state-integrity error takes priority. Otherwise, an exhausted budget takes priority over incomplete work. A board failure that does not stop the run results in incomplete.

The agent must never report finished if a required board failed or was not checked.

## 2. Budgets

I will set the following limits before building the loop:

| Budget | Maximum |
|---|---|
| Boards attempted in one run | 4 |
| HTTP requests in one run | 6 |
| Total elapsed time | 120 seconds |
| Retries per failed board | 1, only for a timeout or temporary server error |

These limits include the deliberate failure board.

A retry counts as another request and must stay within the time budget.

The agent cannot silently increase any budget.

Only I can change these limits. I must make a new dated decision in GATE.md before running the code with different values.

### Planned Boards

| Board | Applicant-tracking system | Board slug |
|---|---|---|
| Databricks | Greenhouse | `databricks` |
| Anthropic | Greenhouse | `anthropic` |
| OpenAI | Ashby | `openai` |
| Deliberate failure | Greenhouse | `databricks-misspelled` |

These are the planned boards, not results from a new live run.

I expect to make one listing request per board when no retry is needed.

### Starting State

Databricks will start using a copy of my final JS1 state file, which contains 924 previously seen posting IDs.

This allows the first JS2 run to identify postings that are new since my last JS1 watch on October 31.

Anthropic and OpenAI will start with new state files. Their first successful runs will be baselines and report zero new postings.

The deliberately misspelled board has no previous state.

I will preserve my original JS1 state file and will not modify the submitted JS1 project.

### Run Configuration

Each run will use an explicit list of boards.

My main live demonstration will include all four planned boards, including the deliberate failure.

My separate finished-wrong-answer demonstration will use a controlled, clearly labeled test configuration without the deliberately failing board.

This allows that demonstration to reach a finished status while the independent checker identifies an incorrect result.

## 3. Repeat Rule

I will consider an action repeated if it uses the same HTTP method, URL, and request parameters during the same run.

The agent should not fetch the same board again without a reason.

It should use the earlier observation instead of making an unnecessary request.

One retry is allowed for a timeout or temporary server error because that kind of failure may be temporary.

The retry must be recorded as a separate attempt and count toward the request budget.

The agent must not keep retrying until it gets the answer it wants.

Posting IDs will be tracked separately for each board.

A posting that was seen in a previous run is not new, even if it disappears and later returns.

## 4. Error Policy

I want the agent to record failures without inventing results.

### HTTP 404 or Invalid Board Name

Do not retry.

Record the board, request, error, and time.

Continue with other boards if it is safe.

Mark the overall run incomplete.

### Timeout or Temporary Server Error

Allow one retry if the request and time budgets permit it.

If the retry also fails, record the board as unavailable and continue with other boards when safe.

### Empty Response

The agent will treat a well-formed response with an empty job list as a valid observation.

For example, `{"jobs": []}` can result in zero new postings for a Greenhouse-style response.

However, a missing response, invalid JSON, or an unexpected response structure is not a valid empty job list.

For my finished-wrong-answer demonstration, I will use a separate independent checking script to compare the reported board count with an earlier saved response.

If a board that previously contained postings suddenly reports zero, the independent checker will flag it for review.

The initial loop will not perform this comparison itself. This is a known limitation that I plan to investigate in my Chapter 6 review packet.

This demonstration will be labeled as constructed or seeded and will not be presented as a real live board result.

### Invalid JSON or Unexpected Response Structure

Record the failure and keep any safely captured raw response as evidence.

Do not guess the number of postings.

Do not update the successful state for that board.

A failure on one board due to invalid JSON or an unexpected response structure makes the overall run incomplete if the remaining boards can be processed safely.

A corrupted shared state file or an inability to preserve required evidence results in an error because continuing could make the saved results unreliable.

### Permission Violation or Corrupted State

Stop safely and report an error.

Do not continue with an unsafe path or modify the corrupted state.

### State Updates

Only update a board's seen IDs after its response has been validated and the required evidence has been saved.

A failed board must not overwrite its previous state.

The trace must record every attempted action, observation, failure, retry, and exit decision.

## 5. Permission Policy

The permission rules must be enforced in Python code, not only through instructions to Claude.

### Allowed Network Hosts

The agent may make HTTPS requests only to:

- `boards-api.greenhouse.io`
- `api.ashbyhq.com`

The hostname must match exactly.

HTTP is not allowed.

Redirects are not allowed, including redirects to another host.

The agent must not send requests to unrelated hosts.

### Allowed Reads

The program may read the fictional Priya Nair resume from the project's `persona/` folder.

It may also read its own configuration, saved responses, and state files needed for the watch.

Read permission does not automatically give write permission.

### Allowed Writes

The program may write generated evidence to its designated `runs/` folder and state files to its designated `state/` folder.

The exact output and state directories must be configured before a run.

Paths must be checked using resolved filesystem paths, not only string prefixes.

The program must refuse writes that escape their approved folders through:

- `..` path traversal
- Look-alike folder prefixes
- Symbolic links pointing outside
- Absolute paths outside the allowed directories

Ordinary evidence writes inside the approved output folder are allowed.

A validated normal state update is permitted by the watch policy.

Resetting an existing state file or overwriting its contents outside the normal validated update procedure requires my explicit approval.

Approval must be a separate, explicit input. Claude must not approve its own restricted actions.

Approval does not override the host allow-list or permit writes outside approved folders.

The program can verify that an explicit approval flag was provided, but it cannot independently verify who entered that flag.

I am responsible for granting approval. The program must not treat Claude's generated text as approval.

### Evidence Preservation

Evidence files are create-only.

A new run must never overwrite the raw responses, traces, or reports from an earlier run.

If a generated filename already exists, the agent must select a new unused filename or safely refuse the write.

This carries forward the evidence overwrite fix from JS1.

### Actions the Agent Must Never Perform

The agent must never:

- Apply for a job
- Send emails or messages
- Log into job websites
- Contact recruiters or employers
- Upload or publish my real resume
- Access private job accounts
- Treat a model's judgment as a verified fact
- Change its own budgets or permissions

The agent can collect public postings and report relevance judgments.

I will make the final decision about every job.

## 6. Wrong Versions My Tests Must Catch

### Wrong Version 1: Failed Board Reported as Zero New Jobs

A board returns an error, but the loop treats that failure as an empty list and reports "0 new jobs."

This is wrong because the agent did not successfully observe the board.

My tests must catch this by checking the board status and making sure an error is not recorded as a successful empty result.

### Wrong Version 2: Incorrect Output-Folder Checking

A permission checker allows a path because its text starts with the approved folder name.

For example, if `runs/` is allowed, the checker also allows `runs-evil/`.

This is wrong because `runs-evil/` is outside the permitted folder.

My tests must check actual resolved paths and refuse the look-alike directory.

### Wrong Version 3: Repeated Requests Ignore the Budget

The loop retries the same failed request again and again without counting each attempt.

This is wrong because the agent could exceed the request or time budget.

My tests must confirm that every attempted request counts and the loop stops at its limit.

I plan to keep a rerunnable wrong-version check in the project so I can repeat it after changes.

## 7. What a Failure Looks Like

**Written before implementation, 2026-11-09:**

A failure would be my agent reporting that it finished checking every board even though one board returned an error, or writing outside its permitted folder without my approval.

I will compare this prediction with the actual test and run results.

## 8. My Responsibility

Claude Code may help implement the loop, the permission checker, and the tests.

I am responsible for reviewing the rules, running the tests, checking the saved evidence, and deciding whether a code change is acceptable.

I will not change the gate afterward just to make a failing test pass.

If I need to change a rule, I will add a dated explanation before testing the new behavior.

## Additional Decision — 2026-11-09: Review Packet Defect

My original plan was to investigate the empty-board limitation in my Chapter 6 review packet.

However, my first real JS2 run revealed a different problem.

The deliberately failing board returned HTTP 404. The agent correctly marked the overall run incomplete, but its console output showed `new=0`, and `summary.json` contained `new_count: 0` for that failed board.

This breaks my gate because the agent never successfully observed that board and cannot know how many new postings it has.

I decided to use this real defect for my review packet instead of the empty-board limitation.

I will write a failing test for both incorrect outputs before asking Claude Code to fix the implementation.

The empty-board limitation remains documented, and my independent checker demonstrates that a finished run can still be wrong.
