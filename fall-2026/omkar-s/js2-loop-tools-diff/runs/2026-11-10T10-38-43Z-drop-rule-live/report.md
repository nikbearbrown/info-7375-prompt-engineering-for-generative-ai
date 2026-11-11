# Run 2026-11-10T10-38-43Z-drop-rule-live: **INCOMPLETE** (exit code 3)

> no answer from: greenhouse:webflow (empty_unverified), greenhouse:klaviyoo (error)

Requests used 6/12 · boards attempted 6/8 · 2.038 s of 90 s · persona Aarav Patel (fictional)

| Board | Status | Why | Postings | New | Removed | Attempts |
|---|---|---|---:|---:|---:|---:|
| `greenhouse:klaviyo` | ok | http_200 | 148 | 0 | 4 | 1 |
| `greenhouse:hubspotjobs` | ok | http_200 | 125 | 5 | 2 | 1 |
| `ashby:linear` | ok | http_200 | 32 | 0 | 0 | 1 |
| `lever:spotify` | ok | http_200 | 85 | 4 | 4 | 1 |
| `greenhouse:webflow` | empty_unverified | HTTP 200 with zero postings; not reported as 'no new jobs' | 0 | null | null | 1 |
| `greenhouse:klaviyoo` | error | not_found | null | null | null | 1 |

## Boards with no answer

- `greenhouse:webflow`: **empty_unverified**, HTTP 200 with zero postings; not reported as 'no new jobs'. Postings: 0 observed; new: null (an empty board is not evidence of 'no new jobs').
- `greenhouse:klaviyoo`: **error**, not_found. Postings: null (null = not observed; no value invented).

## New postings since the last run

### Global Category Specialist (greenhouse:hubspotjobs, `8346343`)
<https://www.hubspot.com/careers/jobs/8346343?gh_jid=8346343> · Remote - Colombia

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Global Category Specialist" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Remote - Colombia" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: none found in posting.content -> 0 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

### Lead Data Analyst (greenhouse:hubspotjobs, `8147286`)
<https://www.hubspot.com/careers/jobs/8147286?gh_jid=8147286> · Remote - Ireland

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Lead Data Analyst" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Remote - Ireland" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: resume.skills.languages[SQL] found in posting.content -> 1 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

### Manager, PreSales DACH (greenhouse:hubspotjobs, `8225811`)
<https://www.hubspot.com/careers/jobs/8225811?gh_jid=8225811> · Flex - Berlin, Germany

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Manager, PreSales DACH" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Flex - Berlin, Germany" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: resume.skills.languages[SQL] found in posting.content -> 1 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

### Senior Manager, Customer Trust Enablement (greenhouse:hubspotjobs, `8073610`)
<https://www.hubspot.com/careers/jobs/8073610?gh_jid=8073610> · Remote - USA

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Senior Manager, Customer Trust Enablement" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Remote - USA" vs resume.personal.location="Boston, MA" -> PASS (US remote)
- C skills: none found in posting.content -> 0 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B PASS, C FAIL)

### Senior Solutions Engineer - Polish speaking  (greenhouse:hubspotjobs, `8066767`)
<https://www.hubspot.com/careers/jobs/8066767?gh_jid=8066767> · Remote - Spain

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Senior Solutions Engineer - Polish speaking " does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Remote - Spain" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: none found in posting.content -> 0 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

### Analyst, Royalty Operations (lever:spotify, `a4651332-6400-40e8-8c22-5491e7a34161`)
<https://jobs.lever.co/spotify/a4651332-6400-40e8-8c22-5491e7a34161> · Stockholm

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Analyst, Royalty Operations" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Stockholm" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: resume.skills.languages[Python, SQL] found in posting.content -> 2 of 15, need 2 -> PASS
- verdict: not_relevant (A FAIL, B FAIL, C PASS)

### Machine Learning Engineering Manager II (lever:spotify, `ea20d13d-aedc-4d02-a4aa-b6d6b1400aed`)
<https://jobs.lever.co/spotify/ea20d13d-aedc-4d02-a4aa-b6d6b1400aed> · New York, NY; Boston, MA; Remote (United States)

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Machine Learning Engineering Manager II" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="New York, NY; Boston, MA; Remote (United States)" vs resume.personal.location="Boston, MA" -> PASS (US city (New York, NY; posting.offices[] has a United States office))
- C skills: none found in posting.content -> 0 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B PASS, C FAIL)

### Retention & Engagement Marketing Lead (lever:spotify, `9057bb9b-3aa2-49ba-9fd0-a9395018d0ea`)
<https://jobs.lever.co/spotify/9057bb9b-3aa2-49ba-9fd0-a9395018d0ea> · Mumbai

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Retention & Engagement Marketing Lead" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Mumbai" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: none found in posting.content -> 0 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

### Senior Accountant, General Ledger Accounting (lever:spotify, `3616d255-dd0f-4771-a0c8-92bdc2abdccd`)
<https://jobs.lever.co/spotify/3616d255-dd0f-4771-a0c8-92bdc2abdccd> · Stockholm

**Record (JS1 rule, recomputable): not_relevant**

- A role: posting.title="Senior Accountant, General Ledger Accounting" does not contain "Software Engineer" (resume.experience[].title: Software Engineer (Co-op); Software Engineer) -> FAIL
- B location (US): posting.location.name="Stockholm" vs resume.personal.location="Boston, MA" -> FAIL (not a US location)
- C skills: resume.skills.languages[SQL] found in posting.content -> 1 of 15, need 2 -> FAIL
- verdict: not_relevant (A FAIL, B FAIL, C FAIL)

