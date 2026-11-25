Exit: budget-exhausted (code 4). claude_calls budget: the budget of 20 Claude calls was used up (32 postings wait for Claude's judgment). ashby-openai unverified: job 482 has no title. greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 2 read, 2 unverified, 0 not visited. 655 postings in the answers read, 52 new since the last run, 43 gone since the last run, 2 new and relevant by the rule, 2 new and relevant in Claude's judgment, 0 judged by Claude after waiting, 32 waiting for Claude.

# Run 2026-11-20T113915Z

- Source: live
- Started (UTC): 2026-11-20T11:39:15Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 20/20, seconds 75.6/600
- Gate v1.0, contract v0.2; the code fingerprint and git commit are in the trace's first line
- Approval given on the command line: none

## Boards

| Board | Status | Postings | New | Gone |
|---|---|---:|---:|---:|
| ashby-openai | unverified | not read | 0 | 0 |
| greenhouse-verkada | read | 348 | 38 | 32 |
| lever-palantir | read | 307 | 14 | 11 |
| greenhouse-no-such-board-js2-test (fails on purpose) | unverified | not read | 0 | 0 |

## OpenAI (ashby/openai)

- URL: https://api.ashbyhq.com/posting-api/job-board/openai
- Status: unverified: job 482 has no title
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 200, 14,343,567 bytes, SHA-256 d595afc07e6388c74e510d380f637a28f71a64f29c05a599ec1a873941feb2e7, saved as boards/ashby-openai/attempt-1.json.gz (0.54 s)
- State: kept exactly as it was

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,157,532 bytes, SHA-256 1326899869f38b9bb6ea43bdd1b59c01cf9bc5de62649d9d558768827bbbf78a, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.41 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

### New since the last run (38)

#### Account Executive Public Sector, México

- id: `5291581007`
- Locations: Mexico City, Mexico
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291581007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Mexico City, Mexico" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Mexico City, Mexico, which is not in the United States and matches none of the résumé's regions, cities or remote locations. The title "Account Executive Public Sector" is not a role in title_includes. The posting also asks for 5-10+ years of experience against the candidate's 3, and says it will not sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Mexico City, Mexico"; "5-10+ years of quota-exceeding experience"; "We are unable to sponsor or take over sponsorship of an employment visa for this role"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/6947c82328.json.

#### Account Executive, Sydney

- id: `4086589007`
- Locations: Sydney, Australia
- Link: https://job-boards.greenhouse.io/verkada/jobs/4086589007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Sydney, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is Account Executive in Sydney, Australia, which is not a United States location in the preferred regions or cities, and is not a listed remote location. The title is not a software engineering role in title_includes. The posting also says it cannot sponsor a visa, which conflicts with the job seeker needing sponsorship.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d8e6d3f8f4.json.

#### Backend Engineer - Connectivity

- id: `5296748007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5296748007

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Backend Engineer - Connectivity" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "Backend Engineer", contains "Backend Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain says "1+ years backend engineering experience in a production environment", so N = 1, which is at most résumé experience.full_time_years 3.

**Claude's judgment (model output, not verified):** relevant

- Justification: Full-time role in San Mateo, CA (California is a preferred region). The title "Backend Engineer" has no level word, matches title_includes and contains no excluded word. The posting says it sponsors visas, asks for only 1+ years against the candidate's 3, and states no start date or clearance requirement.
- Résumé fields cited: preferences.employment_types, preferences.regions, preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, location, employmentType, descriptionPlain
- Quotes: "We do sponsor and take over sponsorship of employment visas for this role."; "1+ years backend engineering experience in a production environment"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/1a33044fde.json.

#### Channel Sales Manager, Colombia

- id: `5291606007`
- Locations: Mexico City, Mexico
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291606007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Mexico City, Mexico" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is a Channel Sales Manager role in Mexico City, so it fails the location check (not in the US), the level check (title contains 'Manager'), and the role check (not a listed title, and the title is sales-related). It also states the employer cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Channel Sales Manager, Colombia"; "Mexico City, Mexico"; "We are unable to sponsor or take over sponsorship of an employment visa for this role"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/008193c27f.json.

#### Channel Sales Manager, Ohio Valley

- id: `5106586007`
- Locations: Cleveland, OH United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5106586007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Cleveland, OH United States" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: Several criteria fail: Cleveland, OH is not in the preferred regions or cities, the title contains 'Manager' and the role 'Channel Sales Manager' is not in title_includes (and includes the excluded word 'Sales'). The posting also says it cannot sponsor a visa and asks for 4+ years of experience versus 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "4+ years of channel sales or partner management experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/e725ec8269.json.

#### Channel Sales Manager, Ohio Valley

- id: `5106588007`
- Locations: Pittsburgh, PA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5106588007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Pittsburgh, PA United States" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Channel Sales Manager" has the level word Manager, is not a role in title_includes, and contains "Sales" from title_excludes. Pittsburgh, PA is not in the preferred regions or cities. The posting also says it cannot sponsor a visa, and asks for 4+ years of experience against 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, preferences.cities, preferences.regions, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Channel Sales Manager, Ohio Valley"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "4+ years of channel sales or partner management experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/5c2a181587.json.

#### Director/Senior Manager, Government Affairs

- id: `5279827007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5279827007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Director/Senior Manager, Government Affairs" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains level words "Director" and "Senior" and "Manager", and it names a government affairs role, not one in title_includes. The posting also says it cannot sponsor a visa, and it asks for 8+ years of experience against the résumé's 3.
- Résumé fields cited: preferences.title_includes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Director/Senior Manager, Government Affairs"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "8+ years of progressive experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/430d361758.json.

#### Engineering Manager, Access Control

- id: `5302614007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302614007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Engineering Manager, Access Control" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Engineering Manager, Access Control" contains the level word "Manager" and its role part, "Engineering Manager", is not in title_includes. The posting also asks for 7+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Engineering Manager, Access Control"; "7+ years of professional software engineering experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d18cdf7bad.json.

#### Engineering Manager, Core Platform

- id: `5302617007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302617007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Engineering Manager, Core Platform" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Engineering Manager, Core Platform" contains the level word "Manager", and the part before the comma, "Engineering Manager", is not a role in the résumé's title_includes. The posting also asks for 4+ years of managing and 8+ years of software engineering experience, while the résumé has 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Engineering Manager, Core Platform"; "8+ years of work experience in a software engineering roles"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f9b6370c18.json.

#### Engineering Manager, Maps

- id: `5292769007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5292769007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Engineering Manager, Maps" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Engineering Manager, Maps" contains the level word "Manager", and the part before the comma, "Engineering Manager", does not name any role in the résumé's title_includes. Employment type, location (San Mateo, CA) and sponsorship all pass, but the level and role checks fail.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions
- Posting fields cited: title, employmentType, location
- Quotes: "Engineering Manager, Maps"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/6f79e66ae0.json.

#### Enterprise Account Executive, Colombia

- id: `5291075007`
- Locations: Mexico City, Mexico
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291075007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Mexico City, Mexico" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Mexico City, Mexico, which is not in the United States and not a listed remote location. The title 'Enterprise Account Executive' is not a preferred role and the posting asks for 5-10+ years of experience against the résumé's 3. It also says the employer cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, experience.full_time_years, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Mexico City, Mexico"; "5-10+ years of quota exceeding experience"; "We are unable to sponsor or take over sponsorship of an employment visa for this role"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/44634613ab.json.

#### Enterprise Account Executive, NSW

- id: `4140525007`
- Locations: Sydney, Australia
- Link: https://job-boards.greenhouse.io/verkada/jobs/4140525007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Sydney, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Sydney, Australia, which is not in the résumé's preferred U.S. regions, cities or remote locations. The title "Enterprise Account Executive" is not a software engineering role in title_includes. The posting also says it cannot sponsor a visa, and it asks for 5-10 years of experience against 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time"; "5-10 years of quota-carrying enterprise sales experience, ideally hunting new business."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c09aab35aa.json.

#### Enterprise Account Executive, Public Sector North - UK

- id: `5297849007`
- Locations: London
- Link: https://job-boards.greenhouse.io/verkada/jobs/5297849007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is located in London, UK, which is not in the résumé's preferred US regions, cities or remote locations. The title "Enterprise Account Executive" also matches none of the preferred engineering roles, and the Sales-related role is not a fit.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location
- Quotes: "Enterprise Account Executive, Public Sector North - UK"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/cd3dc7dd94.json.

#### Enterprise Account Executive, Public Sector South - UK

- id: `5300387007`
- Locations: London
- Link: https://job-boards.greenhouse.io/verkada/jobs/5300387007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in London, which is not in the résumé's preferred regions, cities, or remote locations. The title "Enterprise Account Executive" is not a role in preferences.title_includes. Employment type (FullTime) does match.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location, employmentType
- Quotes: "Enterprise Account Executive, Public Sector South - UK"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a668973030.json.

#### Enterprise Sales Development Representative

- id: `5293022007`
- Locations: Sydney, Australia
- Link: https://job-boards.greenhouse.io/verkada/jobs/5293022007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Sydney, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in Sydney, Australia, which is not in the preferred U.S. regions, cities or remote locations. The title "Enterprise Sales Development Representative" is not a software engineering role and contains the excluded word "Sales". The posting also says it cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c46003bf40.json.

#### Executive Assistant to VP of Sales

- id: `5294009007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5294009007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Executive Assistant to VP of Sales" contains the level word "VP". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Executive Assistant to VP of Sales" names no role in title_includes and contains the excluded word "Sales". The posting also says it cannot sponsor a visa, and the job seeker needs sponsorship. It asks for 2-5 years of Executive Assistant experience, which the résumé's 3 years of software work would not match in kind.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship
- Posting fields cited: title, descriptionPlain
- Quotes: "Executive Assistant to VP of Sales"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9830a8ce39.json.

#### Full Stack Engineer, Business Systems

- id: `5101666007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5101666007

**Rule verdict (record):** relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Full Stack Engineer, Business Systems" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): passes. The role part of the title, "Full Stack Engineer", contains "Full Stack Engineer" from résumé preferences.title_includes and no word from preferences.title_excludes.
- Check 5 (status): passes. Posting descriptionPlain contains none of the status phrases for résumé work_authorization.us_person false and needs_sponsorship true.
- Check 6 (start date): passes. Posting descriptionPlain asks for no start before résumé availability.earliest_full_time_start "2027-05".
- Check 7 (years of experience): passes. Posting descriptionPlain says "Bachelor's degree in a technical field, alongside 1–3 years of full-time software engineering experience in a production environment.", so N = 1, which is at most résumé experience.full_time_years 3.

**Claude's judgment (model output, not verified):** relevant

- Justification: Full-time role in San Mateo, CA, which matches the California region preference. The title "Full Stack Engineer" has no level word or excluded word. The posting says it sponsors visas and sets no start date, and its 1–3 years of experience fits the résumé's 3 years.
- Résumé fields cited: preferences.employment_types, preferences.regions, preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship, work_authorization.us_person, availability.earliest_full_time_start, experience.full_time_years
- Posting fields cited: title, location, employmentType, descriptionPlain
- Quotes: "We do sponsor and take over sponsorship of employment visas for this role."; "1–3 years of full-time software engineering experience in a production environment."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a54de0bb1a.json.

#### Global Sourcing Manager

- id: `5293617007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5293617007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Global Sourcing Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Global Sourcing Manager" contains the level word Manager and is not a software/engineering role in title_includes. The posting also says it cannot sponsor a visa, and the job seeker needs sponsorship.
- Résumé fields cited: preferences.title_includes, work_authorization.needs_sponsorship
- Posting fields cited: title, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c1d0a3567c.json.

#### Lead Product Manager, Access Management

- id: `5222017007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5222017007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Lead Product Manager, Access Management" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Lead Product Manager, Access Management" contains the level word "Lead", and the role before the comma, "Lead Product Manager", is not in the résumé's title_includes. The posting also asks for 6+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Lead Product Manager, Access Management"; "6+ years of product management experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/ee44fae818.json.

#### Mid-Market Account Executive, México

- id: `5291572007`
- Locations: Mexico City, Mexico
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291572007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Mexico City, Mexico" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in Mexico City, which matches none of the résumé's regions, cities, or remote locations. The title "Mid-Market Account Executive" is a sales role, not a software engineering title, and the posting asks for 5-10 years of experience against the résumé's 3. It also says it cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Mid-Market Account Executive, México"; "5-10 years of quota-exceeding experience"; "We are unable to sponsor or take over sponsorship of an employment visa for this role"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/0e02258c7e.json.

#### Physical Security Operations, Senior Manager

- id: `5292895007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5292895007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Physical Security Operations, Senior Manager" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Recruiting Program Coordinator

- id: `5294939007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5294939007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Recruiting Program Coordinator" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Recruiting Program Coordinator", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Regional Sales Director, TOK

- id: `5301451007`
- Locations: Tokyo, Japan
- Link: https://job-boards.greenhouse.io/verkada/jobs/5301451007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Tokyo, Japan" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Regional Sales Manager, Mid-Market, Philadelphia

- id: `5298284007`
- Locations: Philadelphia, PA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5298284007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Philadelphia, PA United States" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Sales Strategy and Operations | Channel Programs Specialist

- id: `5291267007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291267007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Sales Strategy and Operations | Channel Programs Specialist" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Sales Strategy and Operations", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Backend Engineer - Device Platform

- id: `5302623007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302623007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Backend Engineer - Device Platform" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Frontend Engineer - Access Control

- id: `5302630007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302630007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Access Control" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Frontend Engineer - Fleet Management

- id: `5287692007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5287692007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Fleet Management" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Frontend Engineer - Web Platform

- id: `5302631007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302631007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Web Platform" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior iOS Engineer

- id: `5302088007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302088007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior iOS Engineer" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Manager - Imaging Systems

- id: `5290383007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5290383007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Manager - Imaging Systems" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Recruiter - Marketing

- id: `5302824007`
- Locations: Austin, TX United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302824007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Austin, TX United States" has address city "Austin" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Senior Recruiter - Marketing" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Test Engineer, Cameras

- id: `5083834007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5083834007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Test Engineer, Cameras" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Staff Frontend Engineer - Mapping & Spatial Platform

- id: `5302618007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302618007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Frontend Engineer - Mapping & Spatial Platform" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Staff Software Engineer - Data Protection

- id: `5143763007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5143763007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Software Engineer - Data Protection" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Strategic Account Executive, Federal Government (Australia)

- id: `5197606007`
- Locations: Canberra, Australia
- Link: https://job-boards.greenhouse.io/verkada/jobs/5197606007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Canberra, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Content Delivery Manager

- id: `5225570007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5225570007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Content Delivery Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Technical Project Manager, Global Services

- id: `5297293007`
- Locations: New York City, NY United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5297293007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City, NY United States" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Technical Project Manager, Global Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)



### Still waiting for Claude (18)

Judged first next run: `5292895007`, `5294939007`, `5301451007`, `5298284007`, `5291267007`, `5302623007`, `5302630007`, `5287692007`, `5302631007`, `5302088007`, `5290383007`, `5302824007`, `5083834007`, `5302618007`, `5143763007`, `5197606007`, `5225570007`, `5297293007`

### Gone since the last run (32)

- `5161632007` Account Executive, Territory (Mid-Market)
- `5283634007` Backend Engineer
- `5194598007` Backend Engineer - Connectivity
- `5148663007` Channel Sales Manager, Southern Europe 
- `5221766007` Director, Channel Sales EMEA
- `5254501007` Engineering Manager, Access Control
- `5261461007` Engineering Manager, Atlas (Spatial Systems)
- `5283863007` Engineering Manager, Core Platform
- `5285417007` Enterprise Solutions Engineer, Brazil
- `5136810007` Enterprise Solutions Engineering Manager, Central SLED
- `5252722007` Executive Assistant, LATAM
- `5251251007` Field Marketing Manager, ANZ
- `4596545007` Marketing (Sales) Development Representative (Bilingual English/Japanese)
- `5275095007` MBA Full-Time Hire - Product Marketing, Solutions
- `5253871007` NPI Project Manager 
- `5267188007` Office Coordinator, LA (Fixed-Term/ Part-Time)
- `5262546007` Physical Security Associate, Events
- `5226851007` Regional Sales Manager, Mid-Market, Austin
- `5271607007` Senior Backend Engineer - Device Platform
- `5140211007` Senior Digital Growth Manager, JAPAC
- `5158660007` Senior Field Marketing Manager - Enterprise
- `5222833007` Senior Field Marketing Manager, Enterprise
- `5222828007` Senior Field Marketing Manager, Enterprise
- `5263675007` Senior Frontend Engineer - Access Control
- `5231632007` Senior Frontend Engineer - Streaming
- `5270380007` Senior Frontend Engineer - Web Platform
- `5283637007`  Senior Software Engineer - Cameras
- `5283644007` Software Engineer - Computer Vision
- `5173902007` Software Engineering Manager, Data Protection Platform
- `5231248007` (Sr) Manager, Strategic Finance & Business Operations - GTM 
- `5270383007` Staff Frontend Engineer - Mapping & Spatial Platform
- `5234561007` Supply Chain Manager, Aftermarket Operations

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,954,399 bytes, SHA-256 95b992f2009e7050780c9b9d219f3aa906e682f3e9a193a2c29df7d2f9db4f64, saved as boards/lever-palantir/attempt-1.json.gz (1.25 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)

### New since the last run (14)

#### Administrative Business Partner

- id: `ac978161-6f46-4f6b-ad9e-a258e642751c`
- Locations: London, United Kingdom
- Link: https://jobs.lever.co/palantir/ac978161-6f46-4f6b-ad9e-a258e642751c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, United Kingdom" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Forward Deployed Software Engineer - AUS Government

- id: `8f15d728-99cc-4003-9add-928bd72a7f30`
- Locations: Canberra, Australia
- Link: https://jobs.lever.co/palantir/8f15d728-99cc-4003-9add-928bd72a7f30

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Canberra, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Information Security Engineer - Infrastructure Security

- id: `36b26f06-1e25-4c33-8548-c9e70add0784`
- Locations: London, United Kingdom
- Link: https://jobs.lever.co/palantir/36b26f06-1e25-4c33-8548-c9e70add0784

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, United Kingdom" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Information Systems Security Engineer

- id: `e8bfc01c-620c-4b6a-b3f8-cd275228db06`
- Locations: Palo Alto, CA
- Link: https://jobs.lever.co/palantir/e8bfc01c-620c-4b6a-b3f8-cd275228db06

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Palo Alto, CA" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Information Systems Security Engineer" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Information Systems Security Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Intellectual Property Counsel

- id: `348befa6-dfc6-4838-8bbd-5bc93cb5bfdc`
- Locations: Denver, CO
- Link: https://jobs.lever.co/palantir/348befa6-dfc6-4838-8bbd-5bc93cb5bfdc

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Denver, CO" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Intellectual Property Counsel

- id: `51bafe1f-2e8e-4ba7-9692-880fcb4cbabe`
- Locations: New York, NY
- Link: https://jobs.lever.co/palantir/51bafe1f-2e8e-4ba7-9692-880fcb4cbabe

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York, NY" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Intellectual Property Counsel" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Intellectual Property Counsel", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Intellectual Property Counsel

- id: `6bfbb28e-f61d-4385-be0f-64d7d78d53cb`
- Locations: Palo Alto, CA
- Link: https://jobs.lever.co/palantir/6bfbb28e-f61d-4385-be0f-64d7d78d53cb

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Palo Alto, CA" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Intellectual Property Counsel" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Intellectual Property Counsel", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Intellectual Property Counsel

- id: `b53ba9c4-6549-4884-b456-7f8ba507d387`
- Locations: Washington, D.C.
- Link: https://jobs.lever.co/palantir/b53ba9c4-6549-4884-b456-7f8ba507d387

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Washington, D.C." match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Senior Tax Analyst

- id: `b4d82318-0ad6-4730-9b6e-2c8676b2e768`
- Locations: Palo Alto, CA
- Link: https://jobs.lever.co/palantir/b4d82318-0ad6-4730-9b6e-2c8676b2e768

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Palo Alto, CA" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Tax Analyst" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Site Reliability Operations Analyst - Legal

- id: `4a9e0649-a925-4b25-914d-1eea058a3e01`
- Locations: Washington, D.C.
- Link: https://jobs.lever.co/palantir/4a9e0649-a925-4b25-914d-1eea058a3e01

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Washington, D.C." match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Site Reliability Operations Analyst - Legal

- id: `773bb739-f011-4202-88d7-362a562df0d3`
- Locations: New York, NY
- Link: https://jobs.lever.co/palantir/773bb739-f011-4202-88d7-362a562df0d3

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York, NY" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Site Reliability Operations Analyst - Legal" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Site Reliability Operations Analyst", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Software Engineer, Internship - Connectivity Platform and Product

- id: `130ee501-bd22-4d44-b651-39581ef97743`
- Locations: New York, NY
- Link: https://jobs.lever.co/palantir/130ee501-bd22-4d44-b651-39581ef97743

**Rule verdict (record):** not_relevant

- Check 1 (employment type): FAILS. Posting employmentType is "Intern"; résumé preferences.employment_types is ["FullTime"].

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Software Engineer, Internship - Connectivity Platform and Product

- id: `eb496d6a-a960-43d3-a09b-e3843052f54e`
- Locations: Denver, CO
- Link: https://jobs.lever.co/palantir/eb496d6a-a960-43d3-a09b-e3843052f54e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): FAILS. Posting employmentType is "Intern"; résumé preferences.employment_types is ["FullTime"].

**Claude's judgment (model output, not verified):** waiting for Claude (budget)


#### Software Engineer, Internship - Data Connectors

- id: `45e4617d-d658-4b30-8dc9-378ca84a027a`
- Locations: New York, NY
- Link: https://jobs.lever.co/palantir/45e4617d-d658-4b30-8dc9-378ca84a027a

**Rule verdict (record):** not_relevant

- Check 1 (employment type): FAILS. Posting employmentType is "Intern"; résumé preferences.employment_types is ["FullTime"].

**Claude's judgment (model output, not verified):** waiting for Claude (budget)



### Still waiting for Claude (14)

Judged first next run: `ac978161-6f46-4f6b-ad9e-a258e642751c`, `8f15d728-99cc-4003-9add-928bd72a7f30`, `36b26f06-1e25-4c33-8548-c9e70add0784`, `e8bfc01c-620c-4b6a-b3f8-cd275228db06`, `348befa6-dfc6-4838-8bbd-5bc93cb5bfdc`, `51bafe1f-2e8e-4ba7-9692-880fcb4cbabe`, `6bfbb28e-f61d-4385-be0f-64d7d78d53cb`, `b53ba9c4-6549-4884-b456-7f8ba507d387`, `b4d82318-0ad6-4730-9b6e-2c8676b2e768`, `4a9e0649-a925-4b25-914d-1eea058a3e01`, `773bb739-f011-4202-88d7-362a562df0d3`, `130ee501-bd22-4d44-b651-39581ef97743`, `eb496d6a-a960-43d3-a09b-e3843052f54e`, `45e4617d-d658-4b30-8dc9-378ca84a027a`

### Gone since the last run (11)

- `9ace479e-a9e4-4610-a553-122d3831863a` Deployment Strategist
- `69ab7e24-8f5d-426e-84f7-6d3b2d4a7efd` Deployment Strategist, Internship - Warp Speed
- `37780e70-c7af-45e1-9be7-071df201c387` Deployment Strategist, New Grad - Warp Speed
- `51ea4a3b-7764-4c87-96e4-310e19c856d5` DevOps Engineer
- `c3f40e41-6258-4233-a7f9-091bf67df30b` DevOps Engineer
- `3db7e40a-28e0-4ad1-96c5-93de5bc96aa9` Forward Deployed Infrastructure Engineer, Internship - US Government
- `8f362a1f-1eff-4327-94c1-ff46e2101c69` Forward Deployed Infrastructure Engineer, Internship - US Government
- `1b694ba4-dfda-46b3-ae07-6392bcabb75c` Risk and Compliance Specialist - Global Trade
- `aa77156e-de75-4f36-9d2a-4ec04f97b3c6` Risk and Compliance Specialist - Global Trade
- `98bbe55b-f591-4272-a486-d82404d2c576` Site Reliability Operations Analyst - UK Government
- `168e1345-913c-4826-a926-a07d5cf10bba` US Government Subcontracts Manager

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.09 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
