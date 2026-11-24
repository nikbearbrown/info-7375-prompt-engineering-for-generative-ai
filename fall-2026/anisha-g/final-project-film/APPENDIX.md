# Appendix: the detail behind the film

## Methods: my plan, step by step
Step 1 = layer 1 (done), step 2 = layer 2 (done), step 3 = layer 3 (JS3, this week), step 4 = the final project's daily shortlist.

- **The data.**
  - **Sources:** the Greenhouse Job Board API (`boards-api.greenhouse.io/v1/boards/{slug}/jobs`) and the Lever Postings API (`api.lever.co/v0/postings/{slug}?mode=json`). Both are public, read-only GET requests, with no account.
  - **Boards so far:** klaviyo, datadog (Greenhouse) and palantir (Lever), plus a deliberately missing board (`no-such-board-7375`) to test the error policy.
  - **The persona:** fictional, Nadia Okafor (`persona/resume.json` in JS1; email `@example.com`, a 555 phone number). The agent refuses any résumé that isn't fictional.
- **Layer 1 (JS1, ran 2026-10-31).**
  - **Contract:** CONTRACT.md was committed (`509e6ca`) before any run. It was drafted together with the code, not before it.
  - **Watch:** a new-since-last-run watch by posting id.
  - **Two judges:**
    - a written rule (an analyst/analytics/BI title, AND ≥2 core skills, AND ≤3 years);
    - Claude via `claude -p`, in a fixed JSON format.
  - **The validator** rejects bad JSON, unknown résumé fields, and any quote not found in the posting.
- **Layer 2 (JS2, ran 2026-11-10).**
  - **Gate:** GATE.md was committed alone, before any code in that folder.
  - **Loop:** a bounded loop over 3 boards on 2 systems, with budgets of 5 boards, 15 requests and 60 seconds, and one retry on a timeout or blank body.
  - **Permission policy in code:** exact host allow-list, HTTPS GET only, writes only inside `reports/job-watch/`, overwrites only with approval, never delete.
  - **Tests:** 70 tests, written before the code. Two wrong versions are caught.
- **Layer 3 (JS3, planned, due this week).** A filter written as a versioned document, with reasons; evidence rules (supported / contradicted / insufficient, and "I cannot tell"); the agent offered to Claude as a tool over the Model Context Protocol; a score with the origin of every number.
- **The final project (planned).** One daily shortlist that combines the layers.
- **What it needs (B11: accounts, access, compute, token credits).** A laptop, Python 3's standard library, `curl`, and the public APIs: no paid API and no cloud compute. **The constraint is Claude credits:** on 2026-10-31 my Claude Code returned "You've hit your individual spend limit" mid-experiment, and the JS1 Claude calls then ran in Claude's workspace (disclosed in JS1). The plan: small batches, and keep every raw reply.

## Evaluation
- **Layer 1 results** (JS1 `reports/`, 2026-10-31, the 6:00 pm run):
  - **The revised prompt** agreed with my hand labels 10/10 on dev and 9/10 on held-out. The baseline scored 8/10 and 5/10, mostly from format failures.
  - **Sampling:** 4 calls on each of 5 postings gave the same verdict every time, including 4/4 disagreeing with my one "relevant" label.
  - **The limit:** 19 of my 20 labels were "not relevant", so an "always no" judge would score 19/20.
- **Layer 2 results** (JS2 `logs/`, 2026-11-10):
  - 18/18 boundary predictions matched;
  - live runs: klaviyo 145, datadog 394 and palantir 304 jobs, with the missing board's 404 reported as a failure (exit `incomplete`) and no value invented;
  - two deliberately wrong versions ended `finished`, and the independent check (a raw recount plus a live curl recount) caught both.
- **My pass mark for the final agent** (decided 2026-11-23):
  - **To pass:** agreement with my own hand labels of **at least 80%**, on **at least 30 new held-out postings** that I label myself, **at least 10 of them relevant**.
  - **Hard fails, whatever the score:** any quote in a justification that isn't in the posting text, or a failed board reported as "no new jobs". (I chose the 80% / 30+ / 10-relevant pass mark. For the hard fails I gave no preference, so Claude chose these two from my own JS1/JS2 rules.)
