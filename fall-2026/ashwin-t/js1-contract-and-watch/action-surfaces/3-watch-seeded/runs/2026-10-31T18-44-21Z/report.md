# Job watch: klaviyo, 2026-10-31T18:44:21Z

**Mode: SEEDED REPLAY**

- **Replayed from a saved file, no network:** `runs/2026-10-31T16-09-43Z/raw-response.json`
- **That response was actually collected:** 2026-10-31T16:09:43Z
- **SHA-256:** `79ac81247d2b186636f068069582ac400e1f7b541c832bcd3b0447e3446ec908`
- **SEEDED REPLAY:** this file was modified on purpose; it is not a fresh live observation.

| Postings observed | Previously seen | New | RELEVANT by rule | AI valid | AI failed | Disagreements |
|---:|---:|---:|---:|---:|---:|---:|
| 156 | 155 | 1 | 1 | 1 | 0 | 0 |

## New postings

| id | title | RULE RECORD | AI JUDGMENT | disagree |
|---|---|---|---|:-:|
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | RELEVANT | RELEVANT |  |

## Software Engineer II, Test Frameworks & Tooling (7855793003)

Boston, MA · offices: Boston · https://www.klaviyo.com/careers/jobs/7855793003?gh_jid=7855793003

**RULE RECORD: RELEVANT**

| title | seniority | location | skills |
|:-:|:-:|:-:|:-:|
| PASS | PASS | PASS | PASS |

- `posting.title="Software Engineer II, Test Frameworks & Tooling" contains "software engineer" (title_check PASS)`
- `posting.title="Software Engineer II, Test Frameworks & Tooling" contains no excluded seniority term (seniority_check PASS)`
- `posting.location.name="Boston, MA" contains "boston", meeting resume.preferred_locations[0]="Boston" (location_check PASS)`
- `resume.skills[0]="Python" matched posting.content="n an e2e test or optimizing a python integration test, you are rea"`
- `resume.skills[3]="Redis" matched posting.content="helm, buildkite data: mysql, redis, kafka ai tools: integration"`
- `resume.skills[5]="Kubernetes" matched posting.content="t infrastructure and ci: aws, kubernetes, terraform, helm, buildkite d"`
- `3 distinct résumé skill(s) found in posting.content; 2 required (skills_check PASS)`

**AI JUDGMENT** (Claude, model `claude-opus-5-5`, asked 2026-10-31T18:44:21Z, prompt `revision-v2`): **RELEVANT**. This is a model's opinion, not a verified fact.

> This is a Boston-based Software Engineer II role that asks for 2+ years of experience, which is within reach for a New Grad. The backend stack includes Python, Kubernetes and Redis, all on the résumé.

- `resume.experience_level` ↔ `posting.title`: "Software Engineer II, Test Frameworks & Tooling"
- `resume.experience_level` ↔ `posting.content`: "you have 2+ years of software engineering experience"
- `resume.preferred_locations[0]` ↔ `posting.location.name`: "Boston, MA"
- `resume.skills[0]` ↔ `posting.content`: "backend: python, django, go"
- `resume.skills[5]` ↔ `posting.content`: "aws, kubernetes, terraform, helm, buildkite"
- `resume.skills[3]` ↔ `posting.content`: "data: mysql, redis, kafka"
