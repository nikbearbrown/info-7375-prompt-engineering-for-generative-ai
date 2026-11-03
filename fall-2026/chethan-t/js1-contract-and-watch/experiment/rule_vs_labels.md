# Rule vs my labels

Run: 2026-10-31T22:23:34-04:00  
Postings: raw/klaviyo_20261031T175121.json  
Labels: experiment/labels.csv

**Agreement: 18/20**

- dev: 10/10
- heldout: 8/10

| id | title | set | my_label | rule verdict | match |
|---|---|---|---|---|---|
| 8006729003 | Software Engineer II - SMS International | dev | not_relevant | not_relevant | yes |
| 8004625003 | Engineering Manager, Marketing Engineering & AI Agents - Amplify | dev | not_relevant | not_relevant | yes |
| 7984272003 | Head of Global Compensation | dev | not_relevant | not_relevant | yes |
| 7801047003 | Sr. Lead Software Engineer | dev | not_relevant | not_relevant | yes |
| 7597868003 | Senior Software Engineer - Profiles, Lists and Segments | dev | not_relevant | not_relevant | yes |
| 8037134003 | Global Mobility and Immigration Program Lead | dev | not_relevant | not_relevant | yes |
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | dev | relevant | relevant | yes |
| 7855798003 | Software Engineer II - Recommendations | dev | relevant | relevant | yes |
| 7855802003 | Senior Machine Learning Engineer | dev | not_relevant | not_relevant | yes |
| 7806009003 | Lead Project Manager | dev | not_relevant | not_relevant | yes |
| 7727703003 | Full Stack Software Engineer - People Systems | heldout | not_relevant | relevant | no |
| 7989325003 | Senior Security Engineer - Detection & Response | heldout | not_relevant | not_relevant | yes |
| 7861843003 | Sr. Staff Engineer, Applied AI (Customer Agent) | heldout | not_relevant | not_relevant | yes |
| 8041054003 | Software Engineer, Conversational Products & Agent Workflows | heldout | relevant | relevant | yes |
| 7559750003 | Principal Engineer, Core Infrastructure | heldout | not_relevant | not_relevant | yes |
| 8017125003 | Senior Lead AI Engineer - G&A Systems | heldout | not_relevant | not_relevant | yes |
| 7659972003 | Senior Security Engineer - Detection and Response | heldout | not_relevant | not_relevant | yes |
| 7783904003 | Senior Software Engineer, Platform Engineering | heldout | not_relevant | not_relevant | yes |
| 7997133003 | Lead Security Compliance Engineer | heldout | not_relevant | not_relevant | yes |
| 7792539003 | Software Engineer II (Mobile Developer - Android/Kotlin) - Mobile App Growth | heldout | not_relevant | relevant | no |

## Disagreements

- **7727703003** Full Stack Software Engineer - People Systems (heldout): my label `not_relevant`, rule `relevant`. Rule's reason: Relevant: title "Full Stack Software Engineer - People Systems" matches a target role (Software Engineer, Frontend Engineer, Full Stack Engineer); location "Boston, MA" is in the US (United States); description has no sponsorship, citizenship, or clearance restriction.
- **7792539003** Software Engineer II (Mobile Developer - Android/Kotlin) - Mobile App Growth (heldout): my label `not_relevant`, rule `relevant`. Rule's reason: Relevant: title "Software Engineer II (Mobile Developer - Android/Kotlin) - Mobile App Growth" matches a target role (Software Engineer, Frontend Engineer, Full Stack Engineer); location "Boston, MA" is in the US (United States); description has no sponsorship, citizenship, or clearance restriction.
