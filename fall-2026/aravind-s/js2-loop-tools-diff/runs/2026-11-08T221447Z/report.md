Exit: budget-exhausted (code 4). claude_calls budget: the budget of 20 Claude calls was used up (55 postings wait for Claude's judgment). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 3 read, 1 unverified, 0 not visited. 1464 postings in the answers read, 75 new since the last run, 69 gone since the last run, 4 new and relevant by the rule, 0 new and relevant in Claude's judgment, 55 waiting for Claude.

# Run 2026-11-08T221447Z

- Source: live
- Started (UTC): 2026-11-08T22:14:47Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 20/20, seconds 62.8/600
- Gate v1.0, contract v0.1; the code fingerprint and git commit are in the trace's first line
- Approval given on the command line: move my JS1 OpenAI state into the JS2 format

## Boards

| Board | Status | Postings | New | Gone |
|---|---|---:|---:|---:|
| ashby-openai | read | 816 | 75 | 69 |
| greenhouse-verkada | read | 343 | 0 | 0 |
| lever-palantir | read | 305 | 0 | 0 |
| greenhouse-no-such-board-js2-test (fails on purpose) | unverified | not read | 0 | 0 |

## OpenAI (ashby/openai)

- URL: https://api.ashbyhq.com/posting-api/job-board/openai
- Status: read
- Attempt 1: HTTP 200, 13,641,063 bytes, SHA-256 7aff4139e7e97306874e8b0cf659a2e4ad9ca5703261dda5c7885154c3e62d04, saved as boards/ashby-openai/attempt-1.json.gz (0.5 s)
- State: updated after this report (the trace records the write)

### New since the last run (75)

#### Technical Program Manager, Compute Infrastructure

- id: `8fb1615c-34bf-47c4-a1d1-b7b2f836bbd3`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/8fb1615c-34bf-47c4-a1d1-b7b2f836bbd3

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Compute Infrastructure" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title's role, "Technical Program Manager", is not in preferences.title_includes, and the title contains the level word "Manager". Additionally, the posting asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Technical Program Manager, Compute Infrastructure"; "Have 5+ years of experience leading major technical programs"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/dab8d8e3cc.json.

#### Head of Data Science, Strategic Finance

- id: `961d2951-ff59-494f-971e-fe25414c234c`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/961d2951-ff59-494f-971e-fe25414c234c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Head of Data Science, Strategic Finance" contains the level word "Head". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Head of Data Science, Strategic Finance" contains the level word "Head", and its role part, "Head of Data Science", matches none of the résumé's title_includes.
- Résumé fields cited: preferences.title_includes
- Posting fields cited: title
- Quotes: "Head of Data Science, Strategic Finance"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9b481b9f9a.json.

#### Civil & Structural Architect, Power Generation 

- id: `1a475859-21e3-45fc-9e93-8763aa1d0992`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/1a475859-21e3-45fc-9e93-8763aa1d0992

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): FAILS. Posting title "Civil & Structural Architect, Power Generation " contains the level word "Architect". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Architect" and names a civil/structural architect role, not any of the résumé's preferred roles. The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Civil & Structural Architect, Power Generation"; "8+ years of civil, structural, or architectural engineering experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f8b219d1f3.json.

#### AI Deployment Manager

- id: `5d66a54f-ad89-4155-ac37-9dcd7d52db34`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/5d66a54f-ad89-4155-ac37-9dcd7d52db34

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "AI Deployment Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "AI Deployment Manager" contains the level word "Manager" and does not name any role in the résumé's title_includes. The posting also asks for 6+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "AI Deployment Manager"; "Have 6+ years of experience in customer facing, enablement, or instructional roles"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9061a76eb0.json.

#### Product Operations Manager

- id: `0dc614c9-4eec-475f-b215-5480fe41317a`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/0dc614c9-4eec-475f-b215-5480fe41317a

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Product Operations Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Manager", and "Product Operations Manager" is not a role in the résumé's title_includes (software/backend/data engineer roles). The location, San Francisco, is in California, which fits, but the level and role checks fail.
- Résumé fields cited: preferences.title_includes, preferences.regions
- Posting fields cited: title, location
- Quotes: "Product Operations Manager"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/2dfe42bebf.json.

#### White Space Manager, Network & Data Halls

- id: `0ed12b35-0115-4ad3-81f5-ea1bb05c9f6b`
- Locations: San Francisco; US - Remote
- Link: https://jobs.ashbyhq.com/openai/0ed12b35-0115-4ad3-81f5-ea1bb05c9f6b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "White Space Manager, Network & Data Halls" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title's role part, "White Space Manager", names no role in preferences.title_includes, and it contains the level word "Manager". The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "White Space Manager, Network & Data Halls"; "8+ years of experience delivering or operating data center white space"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/30898e14fc.json.

#### AI Deployment Manager (Korean-Speaking)

- id: `b282adce-cabe-462b-b9ef-8fa01c4c5b82`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/b282adce-cabe-462b-b9ef-8fa01c4c5b82

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "AI Deployment Manager (Korean-Speaking)" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "AI Deployment Manager" contains the level word "Manager" and does not name any role in the résumé's title_includes. The posting also asks for 6+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "AI Deployment Manager (Korean-Speaking)"; "Have 6+ years of experience in customer facing, enablement, or instructional roles"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/04d5fed05e.json.

#### AI Deployment Manager (Japanese-Speaking)

- id: `c67d4a21-5677-4f93-8962-3ac618a6f6c2`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/c67d4a21-5677-4f93-8962-3ac618a6f6c2

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "AI Deployment Manager (Japanese-Speaking)" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "AI Deployment Manager" contains the level word Manager, and it names none of the résumé's title_includes roles (such as Software Engineer). The posting also asks for 6+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "AI Deployment Manager (Japanese-Speaking)"; "Have 6+ years of experience in customer facing, enablement, or instructional roles"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a860a71842.json.

#### Transformation Leads Regional Manager

- id: `8d332d03-1f38-40e3-85be-b4c99231a896`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/8d332d03-1f38-40e3-85be-b4c99231a896

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Transformation Leads Regional Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Transformation Leads Regional Manager" contains the level word "Manager" and does not name any role in the résumé's title_includes list. Both the level and role checks fail.
- Résumé fields cited: preferences.title_includes
- Posting fields cited: title
- Quotes: "Transformation Leads Regional Manager"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/620b19f133.json.

#### Account Director, Startups | New Business - France

- id: `df688f65-0159-4f0b-9944-0d9492c0b001`
- Locations: Paris, France
- Link: https://jobs.ashbyhq.com/openai/df688f65-0159-4f0b-9944-0d9492c0b001

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Paris, France, which is not in the résumé's preferred regions, cities, or remote locations. The title 'Account Director' has the level word Director and is not a software engineering role. It also asks for 6+ years of experience, and the résumé has 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Account Director, Startups | New Business - France"; "6+ years selling platform-as-a-service and/or software-as-a-service."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c179a5df74.json.

#### Product Marketing Lead, Verticals

- id: `8960d7b6-b345-478f-a5ad-67beaa32f425`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/8960d7b6-b345-478f-a5ad-67beaa32f425

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Product Marketing Lead, Verticals" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Lead" and names a product marketing role, not any role in title_includes. The posting also asks for 10+ years of experience, while the résumé has 3 full-time years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Product Marketing Lead, Verticals"; "10+ years of experience leading product marketing"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4545a714f5.json.

#### Senior Counsel, AI Product (Enterprise/API)

- id: `68b1e4ba-da3f-4712-ad14-8c12ebaa28a4`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/68b1e4ba-da3f-4712-ad14-8c12ebaa28a4

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, AI Product (Enterprise/API)" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and the role "Counsel" is not in the résumé's title_includes. The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Counsel, AI Product (Enterprise/API)"; "Have 8+ years of experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/b08c02a789.json.

#### Applied AI Engineer, Digital Natives

- id: `7be58f3a-6005-42ed-86fa-77773ebfb294`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/7be58f3a-6005-42ed-86fa-77773ebfb294

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in London, UK, which is not in the United States and matches none of the résumé's preferred regions, cities or remote locations. The title "Applied AI Engineer" is also not among the résumé's title_includes roles.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location
- Quotes: "This role is based in London."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/cf3a24c46d.json.

#### Controls Engineer, BMS & EPMS

- id: `a46ffc60-39c6-4b1e-bd0f-9c33a8b06703`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/a46ffc60-39c6-4b1e-bd0f-9c33a8b06703

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Controls Engineer, BMS & EPMS" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Controls Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title's role before the first comma is "Controls Engineer", which is not among the résumé's title_includes (software, data, platform, infrastructure, reliability engineer roles, etc.). Employment type (FullTime) and location (San Francisco, California) fit, but the role check fails.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions
- Posting fields cited: title, employmentType, location
- Quotes: "Controls Engineer, BMS & EPMS"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d932afe956.json.

#### Portfolio Product Marketing Lead

- id: `f7dbbb26-4880-4cf1-bdf9-b8aefa3572cd`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/f7dbbb26-4880-4cf1-bdf9-b8aefa3572cd

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Portfolio Product Marketing Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Portfolio Product Marketing Lead" contains the level word "Lead" and does not name any role in the résumé's title_includes. The posting also asks for 12+ years of experience, far above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Portfolio Product Marketing Lead"; "Have 12+ years of experience in B2B marketing"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4d95575663.json.

#### Forward Deployed Engineer (FDE) - NYC

- id: `9471b38b-f65c-4a01-9626-bd33fca90f1d`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/9471b38b-f65c-4a01-9626-bd33fca90f1d

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE) - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Forward Deployed Engineer (FDE)" does not name any role in title_includes, and it contains the excluded term "Forward Deployed". The posting also asks for 5+ years of experience, more than the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE) - NYC"; "Bring 5+ years of engineering or technical deployment experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/3c6a49e328.json.

#### Technical Program Manager, People Innovation Labs

- id: `87ef8476-e930-47ed-abc2-a1bedcc074fb`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/87ef8476-e930-47ed-abc2-a1bedcc074fb

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, People Innovation Labs" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Program Manager" has the level word "Manager" and does not name any role in title_includes. The posting also asks for 7+ years of experience, while the résumé has 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Technical Program Manager, People Innovation Labs"; "Have 7+ years of experience in technical program management"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/dc05dd9c63.json.

#### Growth Lead, Brazil

- id: `d0da9c00-a65b-49be-9ebf-a55c32642540`
- Locations: São Paulo
- Link: https://jobs.ashbyhq.com/openai/d0da9c00-a65b-49be-9ebf-a55c32642540

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "São Paulo" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in São Paulo, Brazil, which is not in the résumé's preferred U.S. regions, cities or remote locations. The title contains the level word "Lead" and "Growth Lead" is not a listed role. It also asks for 10+ years of experience, and the résumé has 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Growth Lead, Brazil"; "Location: Sao Paulo, Brazil"; "10+ years of experience across product growth"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c591bd585a.json.

#### Robotics Test Engineer

- id: `0369bd4b-bfb1-4c36-90cb-4e3a24365150`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/0369bd4b-bfb1-4c36-90cb-4e3a24365150

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Robotics Test Engineer" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Robotics Test Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Robotics Test Engineer" does not name any role in preferences.title_includes and contains the excluded word "Robotics". The posting also asks for 7+ years of experience, more than the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Robotics Test Engineer"; "7+ years of experience in hardware testing or validation"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/ef8574ddd6.json.

#### Head of Performance Marketing

- id: `cf0516c9-5227-4d7c-a8e9-219a4ac52422`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/cf0516c9-5227-4d7c-a8e9-219a4ac52422

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Head of Performance Marketing" contains the level word "Head". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Head" and names a marketing role, "Performance Marketing", rather than any role in the résumé's title_includes. Location (San Francisco) is not in preferences.cities and the posting doesn't name California, so it also fails the location check.
- Résumé fields cited: preferences.title_includes, preferences.cities, preferences.regions
- Posting fields cited: title, location
- Quotes: "Head of Performance Marketing"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4ea5b1c552.json.

#### Industry & Experiential Marketing Lead, Ads

- id: `5f3a3325-bc3c-4f92-8456-f22add6fe52b`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/5f3a3325-bc3c-4f92-8456-f22add6fe52b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Industry & Experiential Marketing Lead, Ads" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Content & Solutions Marketing Lead, Ads

- id: `c033c8a7-88bb-44d1-b299-2fd420be5f57`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/c033c8a7-88bb-44d1-b299-2fd420be5f57

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Content & Solutions Marketing Lead, Ads" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Applied AI Engineer, Enterprise - Healthcare Life Sciences (HLS)

- id: `6fc25168-bc4c-47a0-8601-583dfaf7fcbd`
- Locations: San Francisco; New York City; US - Remote
- Link: https://jobs.ashbyhq.com/openai/6fc25168-bc4c-47a0-8601-583dfaf7fcbd

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Applied AI Engineer, Enterprise - Healthcare Life Sciences (HLS)" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Applied AI Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Strategic Partner Lead, Creators & Culture, EMEA

- id: `bc58f2d0-9b24-4205-a799-5a5d18bf64ee`
- Locations: Paris, France
- Link: https://jobs.ashbyhq.com/openai/bc58f2d0-9b24-4205-a799-5a5d18bf64ee

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Global Security Investigator

- id: `81864df0-ce84-44af-8aef-e05dc5660793`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/81864df0-ce84-44af-8aef-e05dc5660793

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): FAILS. Posting title "Senior Global Security Investigator" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### User Education Lead

- id: `654f8dde-2ccb-4349-aeb7-40f454f28cce`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/654f8dde-2ccb-4349-aeb7-40f454f28cce

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "User Education Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Presentation Designer, Business Marketing

- id: `80ca9623-f911-45fc-b5dc-47ccfc60b395`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/80ca9623-f911-45fc-b5dc-47ccfc60b395

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Presentation Designer, Business Marketing" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Presentation Designer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Engineering Manager, API Multicloud

- id: `f363932f-2820-4056-9786-14cb697f4a93`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/f363932f-2820-4056-9786-14cb697f4a93

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Engineering Manager, API Multicloud" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### EDA Cloud & Developer Infrastructure Engineer

- id: `4f2d9849-ad00-48d5-a22f-0cb943723999`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/4f2d9849-ad00-48d5-a22f-0cb943723999

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "EDA Cloud & Developer Infrastructure Engineer" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "EDA Cloud & Developer Infrastructure Engineer", contains "Infrastructure Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain states no years of experience, which is not a requirement; résumé experience.full_time_years is 3.
- Caution (not a blocker): descriptionPlain says "export control laws and regulations, candidates for this role may need to meet certain legal status requirements as provided in those laws and regulations."

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Sales and Partnerships

- id: `45a0886d-a60d-4d5a-9afa-785a75042044`
- Locations: London, UK; Brussels - Remote; Madrid, Spain; Berlin, Germany; Zurich, Switzerland; Amsterdam, NL; Germany - Remote; Munich, Germany; Dublin, Ireland; Stockholm, Sweden; Abu Dhabi, UAE; UAE - Remote; Paris, France
- Link: https://jobs.ashbyhq.com/openai/45a0886d-a60d-4d5a-9afa-785a75042044

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK"; "Brussels - Remote"; "Madrid, Spain"; "Berlin, Germany"; "Zurich, Switzerland"; "Amsterdam, NL"; "Germany - Remote"; "Munich, Germany"; "Dublin, Ireland"; "Stockholm, Sweden"; "Abu Dhabi, UAE"; "UAE - Remote"; "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Account Director, Startups | New Business

- id: `50053f7b-c154-45af-b497-3298c826a15f`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/50053f7b-c154-45af-b497-3298c826a15f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Account Director, Startups | New Business" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Success - EMEA

- id: `b3c1b5a9-a8fe-49df-849b-d4a06a47562c`
- Locations: London, UK; Madrid, Spain; Munich, Germany; Dublin, Ireland; Abu Dhabi, UAE; Paris, France
- Link: https://jobs.ashbyhq.com/openai/b3c1b5a9-a8fe-49df-849b-d4a06a47562c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK"; "Madrid, Spain"; "Munich, Germany"; "Dublin, Ireland"; "Abu Dhabi, UAE"; "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Counsel, Trademark

- id: `e74c8ec3-3317-4fea-bb66-703dc2d55a51`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e74c8ec3-3317-4fea-bb66-703dc2d55a51

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, Trademark" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Sales Manager, ANZ | Large Enterprise

- id: `5c7a8915-07dd-4e8c-861a-5b0c647f17a2`
- Locations: Sydney, Australia
- Link: https://jobs.ashbyhq.com/openai/5c7a8915-07dd-4e8c-861a-5b0c647f17a2

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Sydney, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Account Director, Mid-Market Enterprise

- id: `e586578c-2489-4214-92c4-d9639339fe59`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e586578c-2489-4214-92c4-d9639339fe59

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Account Director, Mid-Market Enterprise" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Cyber AI Partner Director

- id: `b6736e0a-db0b-428f-ad14-448353a92243`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/b6736e0a-db0b-428f-ad14-448353a92243

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Cyber AI Partner Director" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### ML Silicon Performance Lead

- id: `67c8b37d-f856-4edf-adb7-1a5b0d07f6b3`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/67c8b37d-f856-4edf-adb7-1a5b0d07f6b3

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "ML Silicon Performance Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Accounting Lead, Hardware

- id: `bfecbfa0-6573-4c00-8215-50e271f411bc`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/bfecbfa0-6573-4c00-8215-50e271f411bc

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Accounting Lead, Hardware" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Intercompany Accountant

- id: `e183d73c-4eeb-4b75-9b69-435591bb535a`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e183d73c-4eeb-4b75-9b69-435591bb535a

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Intercompany Accountant" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Intercompany Accountant", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Growth Marketing Lead, EMEA

- id: `7d10d614-dc7c-427f-abc1-9a4d4ef7a82f`
- Locations: Dublin, Ireland
- Link: https://jobs.ashbyhq.com/openai/7d10d614-dc7c-427f-abc1-9a4d4ef7a82f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Dublin, Ireland" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### AI Deployment Manager - Builder

- id: `1790fe9e-2ac3-45df-894e-f731d243395f`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/1790fe9e-2ac3-45df-894e-f731d243395f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "AI Deployment Manager - Builder" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Editor, Research Team

- id: `85d4e269-af3f-4b62-91d3-8ede8361cd16`
- Locations: Seattle
- Link: https://jobs.ashbyhq.com/openai/85d4e269-af3f-4b62-91d3-8ede8361cd16

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Seattle" has address city "Seattle" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Editor, Research Team" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Editor", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Counsel, AI Safety & Cyber Incident Response

- id: `48bd347f-c799-48ac-aa5b-1b0dfbff90f7`
- Locations: San Francisco; Washington, DC
- Link: https://jobs.ashbyhq.com/openai/48bd347f-c799-48ac-aa5b-1b0dfbff90f7

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Counsel, AI Safety & Cyber Incident Response" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Counsel", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Staff Backend Engineer, Financial Engineering

- id: `02b170ae-de32-46f5-8ef1-844b268681fe`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/02b170ae-de32-46f5-8ef1-844b268681fe

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Backend Engineer, Financial Engineering" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Data Scientist, Analytics Enablement

- id: `5ceff3dd-3503-4ea0-9ade-eeb36b29f14e`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5ceff3dd-3503-4ea0-9ade-eeb36b29f14e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Data Scientist, Analytics Enablement" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Data Scientist", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Legal Discovery Program Manager

- id: `73a111f9-e83d-4cce-9148-2a32ccf1d251`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/73a111f9-e83d-4cce-9148-2a32ccf1d251

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Legal Discovery Program Manager" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineering Manager, Financial Services

- id: `8e7ba2dd-d632-4a8b-b95b-e2592f77a679`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/8e7ba2dd-d632-4a8b-b95b-e2592f77a679

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Forward Deployed Engineering Manager, Financial Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Program Manager, Capacity Analytics & Tooling

- id: `5cc72bc7-e6a0-40e0-9f60-23474cd9acdb`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5cc72bc7-e6a0-40e0-9f60-23474cd9acdb

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Capacity Analytics & Tooling" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Silicon Design Lead

- id: `5692fcec-bd48-40b4-9cd3-2c881faf176c`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/5692fcec-bd48-40b4-9cd3-2c881faf176c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Silicon Design Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


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

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Sales Development Leader,  Singapore

- id: `16596d69-1e40-499b-9d62-13e6f6a498de`
- Locations: Singapore
- Link: https://jobs.ashbyhq.com/openai/16596d69-1e40-499b-9d62-13e6f6a498de

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Singapore" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Executive Business Partner, EMEA (Strategy)

- id: `31b9754b-6ed1-4ee1-80ad-d087cba053c4`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/31b9754b-6ed1-4ee1-80ad-d087cba053c4

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Program Manager, Research Compute Services

- id: `e49133e6-4030-4295-b393-1725aa410344`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e49133e6-4030-4295-b393-1725aa410344

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Research Compute Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### BIM Designer & Coordinator: Civil

- id: `66453891-c75a-41c9-a7de-d0c67f23db4e`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/66453891-c75a-41c9-a7de-d0c67f23db4e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): passes. Posting title "BIM Designer & Coordinator: Civil" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "BIM Designer & Coordinator: Civil", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Program Manager, Global Infrastructure Planning

- id: `df242b29-6a84-4968-8d57-cbeec20dee67`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/df242b29-6a84-4968-8d57-cbeec20dee67

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Program Manager, Global Infrastructure Planning" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### AI Deployment Manager - Builder

- id: `c2016d32-1994-471d-8900-1b49259c647c`
- Locations: Singapore
- Link: https://jobs.ashbyhq.com/openai/c2016d32-1994-471d-8900-1b49259c647c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Singapore" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


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

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Software Engineer, Guardian 

- id: `a36322aa-829e-47b0-821d-d15a40733b83`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/a36322aa-829e-47b0-821d-d15a40733b83

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineer (FDE), Financial Services- NYC

- id: `c90cfa58-7513-4998-a1ce-f6168dd8fc95`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/c90cfa58-7513-4998-a1ce-f6168dd8fc95

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Financial Services- NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


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

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineer (FDE), Cyber - NYC

- id: `9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Cyber - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Applied AI Delivery Lead - NYC

- id: `20df76c8-aa7e-40d1-8602-28605ed5431b`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/20df76c8-aa7e-40d1-8602-28605ed5431b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Applied AI Delivery Lead - NYC" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Applied AI Delivery Lead - Remote in AMER

- id: `2c531790-726c-4d39-b3bd-900c59a09a4d`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/2c531790-726c-4d39-b3bd-900c59a09a4d

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): FAILS. Posting title "Applied AI Delivery Lead - Remote in AMER" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Content Maker

- id: `d4650f77-45ed-4bee-92ac-097a62fa6341`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/d4650f77-45ed-4bee-92ac-097a62fa6341

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Content Maker" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Content Maker", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineer (FDE), Cyber - SF

- id: `a84e6109-142f-45ae-80e1-05811732cca1`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/a84e6109-142f-45ae-80e1-05811732cca1

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Cyber - SF" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineer (FDE), Life Sciences - NYC

- id: `a12c3c93-51df-437d-862f-4892367fea32`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/a12c3c93-51df-437d-862f-4892367fea32

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Life Sciences - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Legal Program Manager

- id: `cda6eab0-edab-4dfc-8923-40ca3b0928b5`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/cda6eab0-edab-4dfc-8923-40ca3b0928b5

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Legal Program Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Controls Engineer, Power Generation & Microgird

- id: `554a6565-0c9a-42e8-8f6f-a22ba23f336b`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/554a6565-0c9a-42e8-8f6f-a22ba23f336b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Controls Engineer, Power Generation & Microgird" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Controls Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Mechanical Engineer, Power Generation

- id: `015de5ce-8210-418d-abc6-f8b8712f0dbd`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/015de5ce-8210-418d-abc6-f8b8712f0dbd

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Mechanical Engineer, Power Generation" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Mechanical Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Applied AI Engineer, Enterprise - EDU

- id: `087aa4f5-1192-413a-ba34-3ae324cf90e5`
- Locations: San Francisco; New York City; US - Remote
- Link: https://jobs.ashbyhq.com/openai/087aa4f5-1192-413a-ba34-3ae324cf90e5

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Applied AI Engineer, Enterprise - EDU" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Applied AI Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Electrical Engineer, Power Generation

- id: `94d44e8c-987f-4350-bb13-5a855be957db`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/94d44e8c-987f-4350-bb13-5a855be957db

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Electrical Engineer, Power Generation" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Electrical Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### GTM Strategy & Planning

- id: `41408133-b45f-4c7b-a0df-c050f16d92de`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/41408133-b45f-4c7b-a0df-c050f16d92de

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "GTM Strategy & Planning" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "GTM Strategy & Planning", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Business Development Manager, Product Partnerships

- id: `0cf4a8f4-a57a-494b-aad8-4df8ac096939`
- Locations: Munich, Germany; London, UK
- Link: https://jobs.ashbyhq.com/openai/0cf4a8f4-a57a-494b-aad8-4df8ac096939

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Munich, Germany"; "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Engineer (FDE), Life Sciences - SF

- id: `218c0b55-53bd-4df6-805d-321a8c2e7db7`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/218c0b55-53bd-4df6-805d-321a8c2e7db7

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Life Sciences - SF" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Data Scientist, Preparedness

- id: `bd1ac97f-20f9-4727-9f92-7064035a416f`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/bd1ac97f-20f9-4727-9f92-7064035a416f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Data Scientist, Preparedness" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Data Scientist", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)



### Still waiting for Claude (55)

Judged first next run: `5f3a3325-bc3c-4f92-8456-f22add6fe52b`, `c033c8a7-88bb-44d1-b299-2fd420be5f57`, `6fc25168-bc4c-47a0-8601-583dfaf7fcbd`, `bc58f2d0-9b24-4205-a799-5a5d18bf64ee`, `81864df0-ce84-44af-8aef-e05dc5660793`, `654f8dde-2ccb-4349-aeb7-40f454f28cce`, `80ca9623-f911-45fc-b5dc-47ccfc60b395`, `f363932f-2820-4056-9786-14cb697f4a93`, `4f2d9849-ad00-48d5-a22f-0cb943723999`, `45a0886d-a60d-4d5a-9afa-785a75042044`, `50053f7b-c154-45af-b497-3298c826a15f`, `b3c1b5a9-a8fe-49df-849b-d4a06a47562c`, `e74c8ec3-3317-4fea-bb66-703dc2d55a51`, `5c7a8915-07dd-4e8c-861a-5b0c647f17a2`, `e586578c-2489-4214-92c4-d9639339fe59`, `b6736e0a-db0b-428f-ad14-448353a92243`, `67c8b37d-f856-4edf-adb7-1a5b0d07f6b3`, `bfecbfa0-6573-4c00-8215-50e271f411bc`, `e183d73c-4eeb-4b75-9b69-435591bb535a`, `7d10d614-dc7c-427f-abc1-9a4d4ef7a82f`, `1790fe9e-2ac3-45df-894e-f731d243395f`, `85d4e269-af3f-4b62-91d3-8ede8361cd16`, `48bd347f-c799-48ac-aa5b-1b0dfbff90f7`, `02b170ae-de32-46f5-8ef1-844b268681fe`, `5ceff3dd-3503-4ea0-9ade-eeb36b29f14e`, `73a111f9-e83d-4cce-9148-2a32ccf1d251`, `8e7ba2dd-d632-4a8b-b95b-e2592f77a679`, `5cc72bc7-e6a0-40e0-9f60-23474cd9acdb`, `5692fcec-bd48-40b4-9cd3-2c881faf176c`, `80c40695-5cd7-4206-96b6-873158a8e696`, `16596d69-1e40-499b-9d62-13e6f6a498de`, `31b9754b-6ed1-4ee1-80ad-d087cba053c4`, `e49133e6-4030-4295-b393-1725aa410344`, `66453891-c75a-41c9-a7de-d0c67f23db4e`, `df242b29-6a84-4968-8d57-cbeec20dee67`, `c2016d32-1994-471d-8900-1b49259c647c`, `f430a2e7-78a8-40bc-8501-b7ff191ecad6`, `a36322aa-829e-47b0-821d-d15a40733b83`, `c90cfa58-7513-4998-a1ce-f6168dd8fc95`, `783704d7-5afa-45aa-899b-1d6799f73004`, `9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e`, `20df76c8-aa7e-40d1-8602-28605ed5431b`, `2c531790-726c-4d39-b3bd-900c59a09a4d`, `d4650f77-45ed-4bee-92ac-097a62fa6341`, `a84e6109-142f-45ae-80e1-05811732cca1`, `a12c3c93-51df-437d-862f-4892367fea32`, `cda6eab0-edab-4dfc-8923-40ca3b0928b5`, `554a6565-0c9a-42e8-8f6f-a22ba23f336b`, `015de5ce-8210-418d-abc6-f8b8712f0dbd`, `087aa4f5-1192-413a-ba34-3ae324cf90e5`, `94d44e8c-987f-4350-bb13-5a855be957db`, `41408133-b45f-4c7b-a0df-c050f16d92de`, `0cf4a8f4-a57a-494b-aad8-4df8ac096939`, `218c0b55-53bd-4df6-805d-321a8c2e7db7`, `bd1ac97f-20f9-4727-9f92-7064035a416f`

### Gone since the last run (69)

- `83b6755d-7785-4186-9050-5ef3ad127941` Software Engineer, Model Inference
- `fb5862cc-244c-410b-b287-47df89ad1e43` Software Engineer, Privacy
- `4d14449e-5e7f-45d4-b103-8776a6c87086` Software Engineer, Inference - Multi Modal
- `bc0d4a9f-235f-4a4b-a854-c6cb0322ccaa` Analytics Engineer, GTM
- `2b4aa186-a90c-4e6c-a544-5f2cc8558525` Commissioning and Quality Program Manager
- `68f7ef0f-97a4-47ce-ac0a-a442572ab7a7` Data Center Controls Network Engineer
- `0867dab4-ed8e-46d5-92ce-a769ebda7c03` Media Relations, Safety Communications 
- `d6476403-46f5-4748-aa19-25c52d241cdc` Manager, Revenue Accounting
- `d8ebcb30-c789-4e75-bf9b-a1e3fb09dd2f` Field Engineer
- `60d3700b-ba82-4fa6-a6bb-7b2b67070510` Researcher, Synthetic RL
- `7daff2af-1686-43fe-85c0-ca912c8747ac` Android Engineer, Ad Formats
- `efcc3430-14c8-4022-8350-8146ffb867ab` Data Scientist, Preparedness
- `09dcf3e6-c510-4e7a-af50-e3e401e0f043` Senior Technical Sourcer, Applications Engineering
- `c4723243-69e5-45e3-a1c4-ad16df988428` Senior Counsel, Corporate (M&A)
- `f6880901-6527-4b71-9f70-bc8d38989b84` Workday Engineer
- `e2afdede-a222-4825-b2fc-fec439a7c893` 3P Systems Architect
- `d4a191f9-58f6-4c89-95f0-0c23ea59a8e4` Intelligence Systems Analyst
- `c44a22a3-6d6f-41f3-bd54-3379034f3e59` AWS Specialist Seller, Strategic Pursuits
- `85fceac9-fb8a-4d71-a524-a8e5f1e9b01b` Software Engineer, Inference - Performance Optimization
- `93568fc5-8c7a-4cc1-8aad-198d67bf348f` Deployment Lead (DL), FDE - Singapore
- `e5c39e03-6121-47be-8bd3-f6128557b38f` GTM Strategy & Operations, Policy
- `f4467078-033c-4638-ac7e-69a532276d85` Account Director, Digital Natives Growth
- `544af761-e37a-450c-884b-b96506c1b883` US External Affairs Associate, Global Affairs
- `d45d6005-ad46-4c3c-8cfc-d312bffe01d5` Product Marketing Lead, ChatGPT Work
- `b15442c5-8e3c-4370-9abf-4b9c63f56de0` Android Engineer, ChatGPT ImageGen
- `e7a4ee23-138a-4004-916e-72a452e7d115` Backend Software Engineer, ChatGPT ImageGen
- `ad6b55f9-fa63-4860-b852-d90592e49d1c` BIM Designer & Coordinator
- `93a481a0-0ee9-4eb9-bb2b-691859af895a` Cyber Operations Strategist, Critical Harm Operations
- `6ba0ce24-ad32-4c3b-b49c-b373be9a8480` Data Center Compute, OpenHouse Savannah 2026
- `d969a2ff-fa51-4444-a061-c9369462141e` LATAM Public Policy Associate
- `894ce80d-c587-4ef0-92d2-b16deb9a06b9` Data Scientist, Cybersecurity 
- `a4981ed2-331a-4927-a95f-fabb64c9c799` Technical Program Manager, Enterprise
- `bce2bcbd-01e6-4afc-9109-d325483aa47e` Product Design Lead, Growth - Codex
- `569fcba5-c7a2-48ae-b580-e86e181adfd8` Account Director, Government
- `65bc2ffe-a622-47cd-949c-2ca8b7ec6951` Data Center Infrastructure Architect
- `bfd27251-5a50-4050-aa66-596a8db9a7a8` Solutions Engineer, Ads Solutions - Singapore
- `95283afd-0a20-4e15-9034-d34e88b66e5d` Customer Success Manager - Ads Solutions (Spanish speaking)
- `9d6520c0-4c28-472f-ae1f-82b03ee9429d` Engineering Manager, ChatGPT Search Infrastructure
- `de76301c-7289-40a5-972a-ab144f189b4f` Capture Manager, OpenAI for Government 
- `b60d3040-38e4-4abe-8af8-881286b10d50` Researcher, Safety Training, National Security
- `345bda68-5b8d-43e4-9c05-ecac06f03912` Strategy & Operations Lead — Korea
- `b2250643-bfd0-4ce6-abbf-cb7e8c8123ba` AI Infrastructure Engineer, pAGI
- `7f76be3a-38d0-4ff4-b997-9f1672e78bc0` Forward Deployed Engineer (FDE), Financial Services- NYC 
- `0adbf6f5-43bf-4c55-a0fd-10a0eff4bb3f` Product Marketing, Messaging Lead
- `dc82f20d-6695-42f1-90f4-841bdc3decef` Pricing Strategist
- `2d91e925-7d2d-4a7d-b824-70678ce9453e` Account Director, Digital Natives | MENA
- `3b2d32bd-2549-43d0-8dc2-8469bece5336` M&A Finance Integration Lead
- `74be2291-5744-40fd-9c65-7a4a516ebd48` Integrated Marketing Manager, EMEA
- `8dcf85ee-563d-40de-bc78-cf829404d212` Physical Engineering Business Lead (Special Situations)
- `f9c64ecf-d52a-44f0-9d9f-99575ae80d7f` Program Manager, Government Trusted Access
- `c9dffd0f-c4b2-461c-9aa2-d08bf1ca5e68` Growth Lead, France
- `7ded0fa1-4887-4de2-84c8-eecc756e86d9` Content Studio Lead
- `fe7039ce-51e2-4cfa-9ea5-507eb7a0eee1` Technical Program Manager, Robotics Infrastructure
- `cc6475e6-f71d-4f51-8d9d-4eb5a7822395` Senior Technical Recruiter, Consumer Devices - Singapore
- `3397617d-19dd-49d1-bf8f-57e02a9ebb63` Account Director, Enterprise | ANZ
- `395e9fe2-4d78-42dd-b3f7-603884915a59` Senior Manager, Supplier MDM Operations
- `c3d39767-3824-4d41-83dd-7b132834b122` Data Center Electrical R&D Engineer
- `5a4a52a0-2eee-4cde-8b9f-320ebff572a4` Design Engineer, Power Generation
- `cf29a76e-71a4-4e29-8a45-8cefdd301aca` Core Operations Lead, Community & Culture
- `7b70517d-8c96-4c4a-8e4a-37859cf68747` Strategy and Operations Lead, Creative Partnerships
- `aaf9aa75-e782-49a0-8820-79b96f343bb0` Program Manager, Critical Harm Operations
- `d1abed60-d3d1-4c8d-a58b-3a96139fbf4e` Site Civil, Structural & Architectural Lead (CSLA)
- `86133dea-e4e2-4030-b8e6-8f944be27b0e` Mechanical Lead
- `09462da9-e866-4e68-b5b4-438acc60e786` Art Director
- `0ed35971-23c6-4723-a5c6-c24ce0ca8350` Employer Brand, Communications & Social
- `e57629e3-8f87-4abe-aa08-1ff51f54d209` Designer
- `c3f0fb07-2153-4ba9-b812-cd7ceb363ae8` HSE and Portfolio Performance Lead
- `33250b88-936a-4994-950c-fc5fe346446c` Service Designer, Intelligence & Investigations
- `6ebd3534-d65b-4d90-ba96-6a54de31409d` Program Manager, Local Community Impact

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,091,423 bytes, SHA-256 c2ad7305148deb4aa9f09787c5a43c48e0f9978ae5e5805179a97d560f855127, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.39 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)
- First run of this board: every posting was recorded as seen, and none counts as new.

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,942,874 bytes, SHA-256 8ce0bf74addf9535ad893e502af565854d1d01450ae81712ea94f1db4b052ca9, saved as boards/lever-palantir/attempt-1.json.gz (1.22 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)
- First run of this board: every posting was recorded as seen, and none counts as new.

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.1 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
