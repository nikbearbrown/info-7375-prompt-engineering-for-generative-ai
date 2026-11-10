Exit: budget-exhausted (code 4). claude_calls budget: the budget of 20 Claude calls was used up (15 postings wait for Claude's judgment). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 3 read, 1 unverified, 0 not visited. 1464 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 20 judged by Claude after waiting, 15 waiting for Claude.

# Run 2026-11-08T232915Z

- Source: live
- Started (UTC): 2026-11-08T23:29:15Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 20/20, seconds 62.5/600
- Gate v1.0, contract v0.2; the code fingerprint and git commit are in the trace's first line
- Approval given on the command line: none

## Boards

| Board | Status | Postings | New | Gone |
|---|---|---:|---:|---:|
| ashby-openai | read | 816 | 0 | 0 |
| greenhouse-verkada | read | 343 | 0 | 0 |
| lever-palantir | read | 305 | 0 | 0 |
| greenhouse-no-such-board-js2-test (fails on purpose) | unverified | not read | 0 | 0 |

## OpenAI (ashby/openai)

- URL: https://api.ashbyhq.com/posting-api/job-board/openai
- Status: read
- Attempt 1: HTTP 200, 13,641,063 bytes, SHA-256 7aff4139e7e97306874e8b0cf659a2e4ad9ca5703261dda5c7885154c3e62d04, saved as boards/ashby-openai/attempt-1.json.gz (0.45 s)
- State: updated after this report (the trace records the write)

### Judged now, after waiting for Claude (20)

#### AI Deployment Manager - Builder

- id: `1790fe9e-2ac3-45df-894e-f731d243395f`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/1790fe9e-2ac3-45df-894e-f731d243395f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "AI Deployment Manager - Builder" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "AI Deployment Manager" contains the level word "Manager" and does not name any role in preferences.title_includes (e.g. Software Engineer), so the level and role checks both fail.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "AI Deployment Manager - Builder"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/37ebbb8966.json.

#### Editor, Research Team

- id: `85d4e269-af3f-4b62-91d3-8ede8361cd16`
- Locations: Seattle
- Link: https://jobs.ashbyhq.com/openai/85d4e269-af3f-4b62-91d3-8ede8361cd16

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Seattle" has address city "Seattle" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Editor, Research Team" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Editor", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Editor, Research Team" names no role in title_includes (not a software or data engineering role) and contains the excluded word "Research". The posting also asks for 8+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Editor, Research Team"; "Have 8+ years of relevant editing experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f514fdae0f.json.

#### Counsel, AI Safety & Cyber Incident Response

- id: `48bd347f-c799-48ac-aa5b-1b0dfbff90f7`
- Locations: San Francisco; Washington, DC
- Link: https://jobs.ashbyhq.com/openai/48bd347f-c799-48ac-aa5b-1b0dfbff90f7

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Counsel, AI Safety & Cyber Incident Response" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Counsel", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Counsel, AI Safety & Cyber Incident Response" has the role "Counsel", which is not in the résumé's title_includes. The posting also asks for 5+ years of experience, above the résumé's 3 years of full-time experience.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "5+ years of relevant experience."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/526b4bd44d.json.

#### Staff Backend Engineer, Financial Engineering

- id: `02b170ae-de32-46f5-8ef1-844b268681fe`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/02b170ae-de32-46f5-8ef1-844b268681fe

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Backend Engineer, Financial Engineering" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Staff", which fails the level rule. The location (San Francisco) and employment type (FullTime) would otherwise fit the résumé's California region and FullTime preference.
- Résumé fields cited: preferences.title_includes, preferences.regions, preferences.employment_types
- Posting fields cited: title, location, employmentType
- Quotes: "Staff Backend Engineer, Financial Engineering"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/97f98ab0ab.json.

#### Data Scientist, Analytics Enablement

- id: `5ceff3dd-3503-4ea0-9ade-eeb36b29f14e`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5ceff3dd-3503-4ea0-9ade-eeb36b29f14e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Data Scientist, Analytics Enablement" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Data Scientist", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title before the comma is "Data Scientist", which is not in the résumé's title_includes (it lists Data Engineer, Software Engineer, etc.). The role check fails even though the location (San Francisco, but California region is a state, not matching the city text) and full-time type are otherwise plausible.
- Résumé fields cited: preferences.title_includes
- Posting fields cited: title
- Quotes: "Data Scientist, Analytics Enablement"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a5f2bbcc83.json.

#### Senior Legal Discovery Program Manager

- id: `73a111f9-e83d-4cce-9148-2a32ccf1d251`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/73a111f9-e83d-4cce-9148-2a32ccf1d251

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Legal Discovery Program Manager" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level words "Senior" and "Manager", and the role (Legal Discovery Program Manager) is not in the résumé's title_includes. The posting also asks for 10+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Legal Discovery Program Manager"; "10+ years of relevant experience in discovery, litigation support, legal operations, or related work"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4716eff197.json.

#### Forward Deployed Engineering Manager, Financial Services

- id: `8e7ba2dd-d632-4a8b-b95b-e2592f77a679`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/8e7ba2dd-d632-4a8b-b95b-e2592f77a679

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Forward Deployed Engineering Manager, Financial Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Manager" and the role "Forward Deployed Engineering Manager" is not a preferred title (it matches the excluded term "Forward Deployed"). The posting also asks for 10+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineering Manager, Financial Services"; "Bring 10+ years of engineering or technical delivery experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f5c7a3aa32.json.

#### Technical Program Manager, Capacity Analytics & Tooling

- id: `5cc72bc7-e6a0-40e0-9f60-23474cd9acdb`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5cc72bc7-e6a0-40e0-9f60-23474cd9acdb

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Capacity Analytics & Tooling" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Program Manager" contains the level word "Manager" and does not name any role in preferences.title_includes. The posting also asks for 5+ years of experience, which exceeds the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Technical Program Manager, Capacity Analytics & Tooling"; "Have 5+ years of experience leading technical programs or products"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/3d26fa08fc.json.

#### Silicon Design Lead

- id: `5692fcec-bd48-40b4-9cd3-2c881faf176c`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5692fcec-bd48-40b4-9cd3-2c881faf176c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Silicon Design Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Silicon Design Lead" contains the level word "Lead" and does not name any role in the résumé's title_includes. Location (San Francisco) is also not in the preferred California cities list, though California is a preferred region, so that point would pass, but the level and role checks fail.
- Résumé fields cited: preferences.title_includes, preferences.regions, preferences.employment_types
- Posting fields cited: title, location, employmentType
- Quotes: "Silicon Design Lead"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/1036f288e2.json.

#### Founding Full Stack Software Engineer, Consulting

- id: `80c40695-5cd7-4206-96b6-873158a8e696`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/80c40695-5cd7-4206-96b6-873158a8e696

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Founding Full Stack Software Engineer, Consulting" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "Founding Full Stack Software Engineer", contains "Software Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement; résumé experience.full_time_years is 3.

**Claude's judgment (model output, not verified):** relevant

- Justification: This is a full-time role in San Francisco (California is in the résumé's regions). The title "Founding Full Stack Software Engineer" has no level word and matches "Software Engineer" with no excluded word. The posting states no citizenship, clearance, sponsorship, start-date or years-of-experience requirement.
- Résumé fields cited: preferences.employment_types, preferences.regions, preferences.title_includes, preferences.title_excludes, work_authorization.us_person, work_authorization.needs_sponsorship, availability.earliest_full_time_start, experience.full_time_years
- Posting fields cited: title, location, employmentType, descriptionPlain
- Quotes: "Founding Full Stack Software Engineer, Consulting"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/1dddefe68e.json.

#### Sales Development Leader,  Singapore

- id: `16596d69-1e40-499b-9d62-13e6f6a498de`
- Locations: Singapore
- Link: https://jobs.ashbyhq.com/openai/16596d69-1e40-499b-9d62-13e6f6a498de

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Singapore" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in Singapore, which matches none of the résumé's regions, cities or remote locations. The title is a sales leadership role ("Leader", "Sales") that is not a software engineering title, and it also asks for 6–10+ years of experience against the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Have 6–10+ years of experience in sales, business development, or GTM roles"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/7eef261167.json.

#### Executive Business Partner, EMEA (Strategy)

- id: `31b9754b-6ed1-4ee1-80ad-d087cba053c4`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/31b9754b-6ed1-4ee1-80ad-d087cba053c4

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in London, UK, which matches none of the résumé's regions, cities or remote locations. The title "Executive Business Partner" is not a role in title_includes. The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "5+ years experience in a cross-functional executive assistant role or similar support function."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/e06906afd3.json.

#### Technical Program Manager, Research Compute Services

- id: `e49133e6-4030-4295-b393-1725aa410344`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e49133e6-4030-4295-b393-1725aa410344

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Research Compute Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Program Manager, Research Compute Services" has the level word "Manager", and its role part, "Technical Program Manager", is not in the résumé's title_includes. The "Research" in the title is after the comma, so it is not what decided this.
- Résumé fields cited: preferences.title_includes
- Posting fields cited: title
- Quotes: "Technical Program Manager, Research Compute Services"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/e70edc5837.json.

#### BIM Designer & Coordinator: Civil

- id: `66453891-c75a-41c9-a7de-d0c67f23db4e`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/66453891-c75a-41c9-a7de-d0c67f23db4e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): passes. Posting title "BIM Designer & Coordinator: Civil" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "BIM Designer & Coordinator: Civil", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "BIM Designer & Coordinator" does not name any role in the résumé's title_includes (such as Software Engineer). The posting also requires a minimum of 8 years of experience, while the résumé has 3. Employment type and remote location do fit.
- Résumé fields cited: preferences.title_includes, experience.full_time_years, preferences.employment_types, preferences.remote_locations
- Posting fields cited: title, descriptionPlain, employmentType, location
- Quotes: "BIM Designer & Coordinator: Civil"; "a minimum of 8 years of relevant experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/40188e7612.json.

#### Technical Program Manager, Global Infrastructure Planning

- id: `df242b29-6a84-4968-8d57-cbeec20dee67`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/df242b29-6a84-4968-8d57-cbeec20dee67

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Global Infrastructure Planning" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Program Manager" contains the level word "Manager" and does not name any role in preferences.title_includes. The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Technical Program Manager, Global Infrastructure Planning"; "Have 5+ years of experience in technical program management"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/82ebb7aff8.json.

#### AI Deployment Manager - Builder

- id: `c2016d32-1994-471d-8900-1b49259c647c`
- Locations: Singapore
- Link: https://jobs.ashbyhq.com/openai/c2016d32-1994-471d-8900-1b49259c647c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Singapore" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is located in Singapore, which is not in the United States and not a listed remote location. The title 'AI Deployment Manager' contains the level word 'Manager' and does not name a role in title_includes. Experience (4+ years) also exceeds the résumé's 3 years.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "This role is based in Singapore."; "Have 4+ years of experience in customer-facing or instructional roles"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9124a05750.json.

#### Software Engineer, Cyber Safeguards

- id: `f430a2e7-78a8-40bc-8501-b7ff191ecad6`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/f430a2e7-78a8-40bc-8501-b7ff191ecad6

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Software Engineer, Cyber Safeguards" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "Software Engineer", contains "Software Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement; résumé experience.full_time_years is 3.

**Claude's judgment (model output, not verified):** relevant

- Justification: The posting is full-time in San Francisco (California), and the title "Software Engineer" has no level word. The part before the comma matches title_includes and hits no excluded word. It has no citizenship, clearance or no-sponsorship language, no start date, and no stated years of experience, so all seven points hold.
- Résumé fields cited: preferences.employment_types, preferences.regions, preferences.title_includes, preferences.title_excludes, work_authorization.us_person, work_authorization.needs_sponsorship, availability.earliest_full_time_start, experience.full_time_years
- Posting fields cited: title, location, employmentType, descriptionPlain
- Quotes: "Software Engineer, Cyber Safeguards"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/bb61690ecd.json.

#### Software Engineer, Guardian 

- id: `a36322aa-829e-47b0-821d-d15a40733b83`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/a36322aa-829e-47b0-821d-d15a40733b83

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The only location is London, UK, which is outside the United States and matches none of the résumé's preferred regions, cities, or remote locations. Other criteria (full-time, title, no level word) pass, but location fails.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations
- Posting fields cited: location, secondaryLocations, workplaceType
- Quotes: "This role is based in our London office."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/09e843ff9b.json.

#### Forward Deployed Engineer (FDE), Financial Services- NYC

- id: `c90cfa58-7513-4998-a1ce-f6168dd8fc95`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/c90cfa58-7513-4998-a1ce-f6168dd8fc95

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Financial Services- NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title 'Forward Deployed Engineer (FDE), Financial Services- NYC' has a role part 'Forward Deployed Engineer' that is not in title_includes and contains the excluded phrase 'Forward Deployed'. The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE), Financial Services- NYC"; "Bring 5+ years of software engineering"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4b513280c9.json.

#### Software Engineer, Agent Platform

- id: `783704d7-5afa-45aa-899b-1d6799f73004`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/783704d7-5afa-45aa-899b-1d6799f73004

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Software Engineer, Agent Platform" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "Software Engineer", contains "Software Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement; résumé experience.full_time_years is 3.

**Claude's judgment (model output, not verified):** relevant

- Justification: Full-time role in New York (a preferred city, listed as a secondary location) and San Francisco, CA (preferred region California). The title "Software Engineer" has no level word and no excluded word. The posting has no U.S. person, clearance or no-sponsorship language, no start date and no required years of experience.
- Résumé fields cited: preferences.employment_types, preferences.cities, preferences.regions, preferences.title_includes, preferences.title_excludes, work_authorization.us_person, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, location, secondaryLocations, employmentType, descriptionPlain
- Quotes: "Software Engineer, Agent Platform"; "This role is based in San Francisco, CA."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/81762d53c7.json.


### Still waiting for Claude (15)

Judged first next run: `9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e`, `20df76c8-aa7e-40d1-8602-28605ed5431b`, `2c531790-726c-4d39-b3bd-900c59a09a4d`, `d4650f77-45ed-4bee-92ac-097a62fa6341`, `a84e6109-142f-45ae-80e1-05811732cca1`, `a12c3c93-51df-437d-862f-4892367fea32`, `cda6eab0-edab-4dfc-8923-40ca3b0928b5`, `554a6565-0c9a-42e8-8f6f-a22ba23f336b`, `015de5ce-8210-418d-abc6-f8b8712f0dbd`, `087aa4f5-1192-413a-ba34-3ae324cf90e5`, `94d44e8c-987f-4350-bb13-5a855be957db`, `41408133-b45f-4c7b-a0df-c050f16d92de`, `0cf4a8f4-a57a-494b-aad8-4df8ac096939`, `218c0b55-53bd-4df6-805d-321a8c2e7db7`, `bd1ac97f-20f9-4727-9f92-7064035a416f`

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,091,423 bytes, SHA-256 c2ad7305148deb4aa9f09787c5a43c48e0f9978ae5e5805179a97d560f855127, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.4 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,942,874 bytes, SHA-256 8ce0bf74addf9535ad893e502af565854d1d01450ae81712ea94f1db4b052ca9, saved as boards/lever-palantir/attempt-1.json.gz (1.43 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.1 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
