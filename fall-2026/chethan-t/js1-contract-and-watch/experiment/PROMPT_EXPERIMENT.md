# Prompt experiment: baseline on dev

Date: 2026-10-31T22:23:34-04:00  
Prompt: `prompts/baseline.txt` (sha256 07ddb9d75b98)  
Raw replies: `prompt_experiment/raw/baseline_dev/`

Pass = Claude's verdict equals my label; an invalid reply is a fail.

**Dev pass rate: 10/10 (100%)**

| id | title | my label | Claude verdict | pass |
|---|---|---|---|---|
| 8006729003 | Software Engineer II - SMS International | not_relevant | not_relevant | yes |
| 8004625003 | Engineering Manager, Marketing Engineering & AI Agents - Amplify | not_relevant | not_relevant | yes |
| 7984272003 | Head of Global Compensation | not_relevant | not_relevant | yes |
| 7801047003 | Sr. Lead Software Engineer | not_relevant | not_relevant | yes |
| 7597868003 | Senior Software Engineer - Profiles, Lists and Segments | not_relevant | not_relevant | yes |
| 8037134003 | Global Mobility and Immigration Program Lead | not_relevant | not_relevant | yes |
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | relevant | relevant | yes |
| 7855798003 | Software Engineer II - Recommendations | relevant | relevant | yes |
| 7855802003 | Senior Machine Learning Engineer | not_relevant | not_relevant | yes |
| 7806009003 | Lead Project Manager | not_relevant | not_relevant | yes |

## Failures

None.

## Revision experiment: dev (revision)

Date: 2026-10-31T22:42:59-04:00  
Prompt (revision): `prompts/revision.txt` (sha256 43c60a70afc4)  
Raw replies: `prompt_experiment/raw/revision_dev/`

Pass = Claude's verdict equals my label; an invalid reply is a fail.

| prompt | set | pass rate | invalid |
|---|---|---|---|
| revision | dev | 10/10 (100%) | 0/10 |

| id | title | my label | revision | pass |
|---|---|---|---|---|
| 8006729003 | Software Engineer II - SMS International | not_relevant | not_relevant | yes |
| 8004625003 | Engineering Manager, Marketing Engineering & AI Agents - Amplify | not_relevant | not_relevant | yes |
| 7984272003 | Head of Global Compensation | not_relevant | not_relevant | yes |
| 7801047003 | Sr. Lead Software Engineer | not_relevant | not_relevant | yes |
| 7597868003 | Senior Software Engineer - Profiles, Lists and Segments | not_relevant | not_relevant | yes |
| 8037134003 | Global Mobility and Immigration Program Lead | not_relevant | not_relevant | yes |
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | relevant | relevant | yes |
| 7855798003 | Software Engineer II - Recommendations | relevant | relevant | yes |
| 7855802003 | Senior Machine Learning Engineer | not_relevant | not_relevant | yes |
| 7806009003 | Lead Project Manager | not_relevant | not_relevant | yes |

### Failures (dev)

None.

## Revision experiment: heldout (baseline, revision)

<!-- heldout run -->

Date: 2026-10-31T22:47:28-04:00  
Prompt (baseline): `prompts/baseline.txt` (sha256 07ddb9d75b98), commit a904c4b  
Prompt (revision): `prompts/revision.txt` (sha256 43c60a70afc4), commit 54d1a26  
Raw replies: `prompt_experiment/raw/baseline_heldout/`, `prompt_experiment/raw/revision_heldout/`

Pass = Claude's verdict equals my label; an invalid reply is a fail.

| prompt | set | pass rate | invalid |
|---|---|---|---|
| baseline | heldout | 8/10 (80%) | 2/10 |
| revision | heldout | 10/10 (100%) | 0/10 |

| id | title | my label | baseline | pass | revision | pass |
|---|---|---|---|---|---|---|
| 7727703003 | Full Stack Software Engineer - People Systems | not_relevant | not_relevant | yes | not_relevant | yes |
| 7989325003 | Senior Security Engineer - Detection & Response | not_relevant | not_relevant | yes | not_relevant | yes |
| 7861843003 | Sr. Staff Engineer, Applied AI (Customer Agent) | not_relevant | not_relevant | yes | not_relevant | yes |
| 8041054003 | Software Engineer, Conversational Products & Agent Workflows | relevant | relevant | yes | relevant | yes |
| 7559750003 | Principal Engineer, Core Infrastructure | not_relevant | invalid | no | not_relevant | yes |
| 8017125003 | Senior Lead AI Engineer - G&A Systems | not_relevant | not_relevant | yes | not_relevant | yes |
| 7659972003 | Senior Security Engineer - Detection and Response | not_relevant | invalid | no | not_relevant | yes |
| 7783904003 | Senior Software Engineer, Platform Engineering | not_relevant | not_relevant | yes | not_relevant | yes |
| 7997133003 | Lead Security Compliance Engineer | not_relevant | not_relevant | yes | not_relevant | yes |
| 7792539003 | Software Engineer II (Mobile Developer - Android/Kotlin) - Mobile App Growth | not_relevant | not_relevant | yes | not_relevant | yes |

### Failures (heldout)

- [baseline] **7559750003** Principal Engineer, Core Infrastructure: my label `not_relevant`, Claude `invalid` (no Claude verdict).  — `prompt_experiment/raw/baseline_heldout/7559750003_20261031T224827_531242.json`
- [baseline] **7659972003** Senior Security Engineer - Detection and Response: my label `not_relevant`, Claude `invalid` (no Claude verdict).  — `prompt_experiment/raw/baseline_heldout/7659972003_20261031T224851_777556.json`

## My conclusion
