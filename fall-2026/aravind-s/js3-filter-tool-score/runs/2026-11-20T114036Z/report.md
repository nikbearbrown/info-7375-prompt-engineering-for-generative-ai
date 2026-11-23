Exit: budget-exhausted (code 4). claude_calls budget: the budget of 20 Claude calls was used up (12 postings wait for Claude's judgment). ashby-openai unverified: job 482 has no title. greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 2 read, 2 unverified, 0 not visited. 655 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 20 judged by Claude after waiting, 12 waiting for Claude.

# Run 2026-11-20T114036Z

- Source: live
- Started (UTC): 2026-11-20T11:40:36Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 20/20, seconds 72.4/600
- Gate v1.0, contract v0.2; the code fingerprint and git commit are in the trace's first line
- Approval given on the command line: none

## Boards

| Board | Status | Postings | New | Gone |
|---|---|---:|---:|---:|
| ashby-openai | unverified | not read | 0 | 0 |
| greenhouse-verkada | read | 348 | 0 | 0 |
| lever-palantir | read | 307 | 0 | 0 |
| greenhouse-no-such-board-js2-test (fails on purpose) | unverified | not read | 0 | 0 |

## OpenAI (ashby/openai)

- URL: https://api.ashbyhq.com/posting-api/job-board/openai
- Status: unverified: job 482 has no title
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 200, 14,343,567 bytes, SHA-256 d595afc07e6388c74e510d380f637a28f71a64f29c05a599ec1a873941feb2e7, saved as boards/ashby-openai/attempt-1.json.gz (0.51 s)
- State: kept exactly as it was

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,157,532 bytes, SHA-256 cface440ae606b2c8cfbf6a6567918f5a7b06ae9b41f317668908bb4e630fe86, saved as boards/greenhouse-verkada/attempt-1.json.gz (1.83 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

### Judged now, after waiting for Claude (18)

#### Physical Security Operations, Senior Manager

- id: `5292895007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5292895007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Physical Security Operations, Senior Manager" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level words "Senior" and "Manager", and its role (Physical Security Operations) is not in title_includes and contains the excluded word "Security". The posting also says it cannot sponsor a visa, and asks for 8–12+ years of experience against 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Physical Security Operations, Senior Manager"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "8–12+ years of security operations experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f22f05d7d6.json.

#### Recruiting Program Coordinator

- id: `5294939007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5294939007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Recruiting Program Coordinator" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Recruiting Program Coordinator", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Recruiting Program Coordinator" does not name any role in the résumé's title_includes (software/backend/data engineer roles). Employment type (FullTime) and location (San Mateo, CA) fit, but the role check fails.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions
- Posting fields cited: title, employmentType, location
- Quotes: "Recruiting Program Coordinator"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/259fac2a2d.json.

#### Regional Sales Director, TOK

- id: `5301451007`
- Locations: Tokyo, Japan
- Link: https://job-boards.greenhouse.io/verkada/jobs/5301451007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Tokyo, Japan" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Tokyo, Japan, which is outside the résumé's preferred US regions, cities and remote locations. The title says Director and its role part (Regional Sales Director) is not a listed role and includes the excluded word Sales. It also asks for 5-10+ years of experience against 3, and states it cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, experience.full_time_years, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Regional Sales Director, TOK"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "5–10+ years of experience leading a high-performing enterprise IT B2B sales team"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/bf20fd5ed1.json.

#### Regional Sales Manager, Mid-Market, Philadelphia

- id: `5298284007`
- Locations: Philadelphia, PA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5298284007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Philadelphia, PA United States" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Manager" and the role "Regional Sales Manager" is not a preferred title and includes the excluded word "Sales". The location Philadelphia, PA is not in the preferred regions or cities, and the posting says it cannot sponsor a visa, which conflicts with the job seeker's need for sponsorship.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, preferences.cities, preferences.regions, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Regional Sales Manager, Mid-Market, Philadelphia"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/dc613a7f27.json.

#### Sales Strategy and Operations | Channel Programs Specialist

- id: `5291267007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5291267007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Sales Strategy and Operations | Channel Programs Specialist" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Sales Strategy and Operations", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title's role part before the '|' is 'Sales Strategy and Operations', which is not in title_includes and contains the excluded word 'Sales'. Employment type and location (San Mateo, CA) fit, but the role check fails.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "Sales Strategy and Operations | Channel Programs Specialist"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/57ed881f9f.json.

#### Senior Backend Engineer - Device Platform

- id: `5302623007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302623007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Backend Engineer - Device Platform" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior", and the posting requires U.S. citizenship or permanent residency and states it offers no visa sponsorship. The job seeker is not a U.S. person and needs sponsorship. It also asks for 6+ years of experience against her 3.
- Résumé fields cited: work_authorization.us_person, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "This role requires U.S. citizenship or permanent residency for FedRAMP compliance"; "This role does not offer visa sponsorship."; "6+ years of experience building backend services"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/882c7f7f39.json.

#### Senior Frontend Engineer - Access Control

- id: `5302630007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302630007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Access Control" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and the excluded word "Frontend", and it does not name a role in title_includes. The posting also asks for 7+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Frontend Engineer - Access Control"; "7+ years of industry software engineering experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/3e445c18a8.json.

#### Senior Frontend Engineer - Fleet Management

- id: `5287692007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5287692007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Fleet Management" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and the word "Frontend", which is in title_excludes. The role before the dash is not in title_includes. Also, the posting asks for 4+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_excludes, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Frontend Engineer - Fleet Management"; "4+ years of experience building and shipping production web applications."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/5ff6bff5e0.json.

#### Senior Frontend Engineer - Web Platform

- id: `5302631007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302631007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Frontend Engineer - Web Platform" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and the word "Frontend", which is in the résumé's title_excludes. The role "Frontend Engineer" is also not among title_includes. Employment type and California location fit, and the posting offers visa sponsorship, but the title fails.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "Senior Frontend Engineer - Web Platform"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/405ce13783.json.

#### Senior iOS Engineer

- id: `5302088007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302088007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior iOS Engineer" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior iOS Engineer" contains the level word "Senior", and "iOS" is in title_excludes. The title also does not name a role in title_includes. Experience (5+ years vs 3) also exceeds the résumé's full_time_years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior iOS Engineer"; "Minimum of 5+ years of relevant work experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/10d1b7f16a.json.

#### Senior Manager - Imaging Systems

- id: `5290383007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5290383007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Manager - Imaging Systems" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Manager - Imaging Systems" contains level words Senior and Manager, and it names no role from title_includes. The posting also asks for 12+ years of experience, far above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Manager - Imaging Systems"; "12+ years of image systems development experience."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/7ee63b0d50.json.

#### Senior Recruiter - Marketing

- id: `5302824007`
- Locations: Austin, TX United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302824007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "Austin, TX United States" has address city "Austin" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Senior Recruiter - Marketing" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Recruiter - Marketing" contains the level word Senior and names a recruiter role, not any of the résumé's preferred engineering roles. The posting also states the employer cannot sponsor a visa, but the job seeker needs sponsorship. It also asks for 5+ years of experience, versus 3 on the résumé.
- Résumé fields cited: preferences.title_includes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role"; "5+ years of successful full-cycle recruiting experience"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/8ccac1e743.json.

#### Senior Test Engineer, Cameras

- id: `5083834007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5083834007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Test Engineer, Cameras" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and the excluded word "Camera", and it names "Test Engineer", which is not a role in title_includes. The posting does sponsor visas and its 2 year minimum fits 3 years of experience, but the title checks fail.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "Senior Test Engineer, Cameras"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9895e12e39.json.

#### Staff Frontend Engineer - Mapping & Spatial Platform

- id: `5302618007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5302618007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Frontend Engineer - Mapping & Spatial Platform" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Staff" and the excluded word "Frontend", and the part before the dash names "Frontend Engineer", which is not in title_includes. The posting also asks for 5+ years of experience, above the résumé's 3 years. Location (California) and employment type (FullTime) fit, and the posting does sponsor visas.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Staff Frontend Engineer - Mapping & Spatial Platform"; "5+ years of experience building complex, customer-facing web applications or high-performance graphics engines."
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/03c68a07c5.json.

#### Staff Software Engineer - Data Protection

- id: `5143763007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5143763007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Staff Software Engineer - Data Protection" contains the level word "Staff". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title begins with the level word "Staff", which fails the level check. The role is also a security-focused position and requires 8+ years of experience, while the résumé has 3 years.
- Résumé fields cited: experience.full_time_years, preferences.title_includes
- Posting fields cited: title, descriptionPlain
- Quotes: "Staff Software Engineer - Data Protection"; "8+ years of experience as a software engineer or security engineer that writes code"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/5c5cbc37ce.json.

#### Strategic Account Executive, Federal Government (Australia)

- id: `5197606007`
- Locations: Canberra, Australia
- Link: https://job-boards.greenhouse.io/verkada/jobs/5197606007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Canberra, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Canberra, Australia, which is not in the résumé's preferred regions, cities or remote locations. The title is Strategic Account Executive, which is not a preferred role. It also asks for 8+ years of experience against the résumé's 3, and says the employer cannot sponsor a visa.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "8+ years of enterprise sales experience"; "We are unable to sponsor or take over sponsorship of an employment visa for this role"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/251c9a6aad.json.

#### Technical Content Delivery Manager

- id: `5225570007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5225570007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Technical Content Delivery Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Content Delivery Manager" contains the level word "Manager" and names no role in the résumé's title_includes. The posting also says it cannot sponsor a visa, and the job seeker needs sponsorship. It asks for 5+ years of experience against 3 years.
- Résumé fields cited: preferences.title_includes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time"; "5+ years of combined experience in Technical Enablement"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/b673ef2e9e.json.

#### Technical Project Manager, Global Services

- id: `5297293007`
- Locations: New York City, NY United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5297293007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City, NY United States" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Technical Project Manager, Global Services" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Technical Project Manager" names no role in title_includes, and the posting requires 6+ years of experience against the résumé's 3. It also requires U.S. Citizen or Permanent Resident status for FedRAMP, which the job seeker lacks.
- Résumé fields cited: preferences.title_includes, experience.full_time_years, work_authorization.us_person
- Posting fields cited: title, descriptionPlain
- Quotes: "6+ years of experience as a Sales or Solutions Engineer"; "Must be a U.S. Citizen or Permanent Resident (Green Card)"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/5723e043b2.json.


## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,954,399 bytes, SHA-256 95b992f2009e7050780c9b9d219f3aa906e682f3e9a193a2c29df7d2f9db4f64, saved as boards/lever-palantir/attempt-1.json.gz (1.25 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)

### Judged now, after waiting for Claude (2)

#### Administrative Business Partner

- id: `ac978161-6f46-4f6b-ad9e-a258e642751c`
- Locations: London, United Kingdom
- Link: https://jobs.lever.co/palantir/ac978161-6f46-4f6b-ad9e-a258e642751c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, United Kingdom" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is onsite in London, United Kingdom, which is not in the résumé's preferred regions, cities, or remote locations. The title 'Administrative Business Partner' also matches none of the preferred software engineering roles.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location, workplaceType
- Quotes: "London, United Kingdom"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/0580c315b0.json.

#### Forward Deployed Software Engineer - AUS Government

- id: `8f15d728-99cc-4003-9add-928bd72a7f30`
- Locations: Canberra, Australia
- Link: https://jobs.lever.co/palantir/8f15d728-99cc-4003-9add-928bd72a7f30

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Canberra, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is onsite in Canberra, Australia, which is not in the United States and matches no preferred region, city or remote location. The title's role part, "Forward Deployed Software Engineer", contains the excluded words "Forward Deployed". The posting also requires an Active Security Clearance, which the job seeker cannot meet as a non-U.S. person.
- Résumé fields cited: preferences.title_excludes, preferences.regions, preferences.cities, preferences.remote_locations, work_authorization.us_person
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Forward Deployed Software Engineer - AUS Government"; "Canberra, Australia"; "Active Security Clearance"
- Model claude-sonnet-5-5, 2026-11-20, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/552b1608bb.json.


### Still waiting for Claude (12)

Judged first next run: `36b26f06-1e25-4c33-8548-c9e70add0784`, `e8bfc01c-620c-4b6a-b3f8-cd275228db06`, `348befa6-dfc6-4838-8bbd-5bc93cb5bfdc`, `51bafe1f-2e8e-4ba7-9692-880fcb4cbabe`, `6bfbb28e-f61d-4385-be0f-64d7d78d53cb`, `b53ba9c4-6549-4884-b456-7f8ba507d387`, `b4d82318-0ad6-4730-9b6e-2c8676b2e768`, `4a9e0649-a925-4b25-914d-1eea058a3e01`, `773bb739-f011-4202-88d7-362a562df0d3`, `130ee501-bd22-4d44-b651-39581ef97743`, `eb496d6a-a960-43d3-a09b-e3843052f54e`, `45e4617d-d658-4b30-8dc9-378ca84a027a`

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.09 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
