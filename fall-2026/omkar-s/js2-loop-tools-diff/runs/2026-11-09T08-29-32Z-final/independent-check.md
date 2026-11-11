# Independent check of run 2026-11-09T08-29-32Z-final

The agent reported **incomplete** (exit code 3).
This check found **1 contradiction(s)**.

| Check | Board | Result | Evidence |
|---|---|---|---|
| C1 | `greenhouse:klaviyo` | OK | sha256 matches trace |
| C1 | `greenhouse:hubspotjobs` | OK | sha256 matches trace |
| C1 | `ashby:linear` | OK | sha256 matches trace |
| C1 | `lever:spotify` | OK | sha256 matches trace |
| C1 | `greenhouse:webflow` | OK | sha256 matches trace |
| C1 | `greenhouse:klaviyoo` | OK | sha256 matches trace |
| C2 | `greenhouse:klaviyo` | OK | report says 152, raw recount says 152 |
| C2 | `greenhouse:hubspotjobs` | OK | report says 122, raw recount says 122 |
| C2 | `ashby:linear` | OK | report says 32, raw recount says 32 |
| C2 | `lever:spotify` | OK | report says 85, raw recount says 85 |
| C2 | `greenhouse:webflow` | OK | report says 0, raw recount says 0 |
| C2 | `greenhouse:klaviyoo` | OK | report says None, raw recount says None |
| C3 | `greenhouse:webflow` | CONTRADICTED | reference says 27 postings on 2026-09-26 (fall-2026/nik-bear-brown/lectern/ATS.md, 'Verified - reachable today' table); ashby has 22 postings for 'webflow' right now (https://api.ashbyhq.com/posting-api/job-board/webflow) |

## C3 probes for `greenhouse:webflow`

- greenhouse: `https://boards-api.greenhouse.io/v1/boards/webflow/jobs` -> HTTP 200, postings 0 (raw `independent-probes/greenhouse-webflow.json`)
- ashby: `https://api.ashbyhq.com/posting-api/job-board/webflow` -> HTTP 200, postings 22 (raw `independent-probes/ashby-webflow.json`)
- lever: `https://api.lever.co/v0/postings/webflow?mode=json` -> HTTP 404, postings None (raw `independent-probes/lever-webflow.json`)
