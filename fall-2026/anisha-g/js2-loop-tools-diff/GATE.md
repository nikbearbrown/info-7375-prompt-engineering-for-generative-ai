# GATE.md — Job-Search Agent 2
Anisha Gaikar · 2026-11-09 · Written **before Claude Code touched any code**.
The decisions in this file are mine. ChatGPT drafted the wording of my answers on 2026-11-09. I read each one, changed some, and chose what to keep before any code was written. I gave them to Claude in chat, and Claude copied them into this file unchanged.
[Attribution corrected 2026-11-09 ~3:35 pm. The first version of this line, in commit cdc62ba, said the words were all mine; that was not accurate. Nothing else in this file was changed.] Anything in [square brackets] is a note added for clarity, not a change to my answer.

## 1. Exits — how a run ends
- **Finished** — I checked every board on the list. I'd report how many boards I checked and how many new jobs I found, even if the count is zero.
- **Incomplete** — Some boards worked, but others failed. I'd report the jobs I found and list which boards failed and why.
- **Budget-exhausted** — I hit a limit while there was still work left. I'd say which limit I hit, what I found so far, and which boards I couldn't finish.
- **Error** — The run couldn't start, couldn't continue, or failed to check any board successfully. I'd report what went wrong and where it stopped.

## 2. Budgets
I'd allow 5 distinct boards, 15 requests, and 60 seconds per run. Retries count toward the request limit and share the same 60-second clock. Only I, as the person running it, can change those limits before a run starts.

## 3. Repeat rule
If the same board shows up twice, I'd skip the duplicate and note it in the report. Fetching it again wastes a request and could count the same jobs twice. A retry after a failed request is handled separately.

## 4. Error policy
If the board name is wrong, I'd report it and move on. If the request times out or returns a blank body, I'd retry once, as long as there's enough budget left. One retry gives a temporary glitch a chance to clear. The fetch is read-only, and the retry still counts against the limits. If it fails again, I'd report the failure and continue to the next board. A valid response with an empty jobs list counts as a successful check.

## 5. Permission policy
I'd let the agent create new reports only in reports/job-watch/ [first answer said reports/greenhouse-watch/; I changed it in 5c]. It should ask me before overwriting an existing report. It should never write outside that folder, change source code or settings, delete files, expose credentials, or publish results on its own.

**5a. Allowed hosts.** I'd allow read-only GET requests to boards-api.greenhouse.io and api.lever.co for public job listings. That covers two systems. If a URL or redirect points to any other host, including api.ashbyhq.com, I'd block the request and report which host was blocked.

**5b. Never list.** The agent must never apply for a job, send an email, send a message, or log in to any account.

**5c. Report folder.** I'd change it to reports/job-watch/ because the agent watches more than one platform. It can create new reports only in that folder and must ask me before overwriting an existing report.

## 6. Wrong versions my tests should catch
1. **A failed board looks like it had zero new jobs.** I'd test one board that returns a valid empty jobs list and another that times out twice. The first should show zero new jobs. The second should show a failure, and the run should be incomplete.
2. **Retries sneak past the request limit.** I'd make request 15 time out while another board is still waiting. The loop should make no 16th request and report budget-exhausted, with the timeout and the unchecked board listed.
