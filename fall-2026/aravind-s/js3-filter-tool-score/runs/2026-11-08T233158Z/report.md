Exit: incomplete (code 1). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 3 read, 1 unverified, 0 not visited. 1464 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 15 judged by Claude after waiting, 0 waiting for Claude.

# Run 2026-11-08T233158Z

- Source: live
- Started (UTC): 2026-11-08T23:31:58Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 15/20, seconds 44.9/600
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
- Attempt 1: HTTP 200, 13,641,063 bytes, SHA-256 7aff4139e7e97306874e8b0cf659a2e4ad9ca5703261dda5c7885154c3e62d04, saved as boards/ashby-openai/attempt-1.json.gz (0.51 s)
- State: updated after this report (the trace records the write)

### Judged now, after waiting for Claude (15)

#### Forward Deployed Engineer (FDE), Cyber - NYC

- id: `9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Cyber - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Forward Deployed Engineer (FDE)" names no role in preferences.title_includes and contains the excluded phrase "Forward Deployed". The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE), Cyber - NYC"; "5+ years of software engineering experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/ce9b17a0e2.json.

#### Applied AI Delivery Lead - NYC

- id: `20df76c8-aa7e-40d1-8602-28605ed5431b`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/20df76c8-aa7e-40d1-8602-28605ed5431b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Applied AI Delivery Lead - NYC" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Applied AI Delivery Lead" contains the level word "Lead" and does not name any role in the résumé's title_includes. The posting also asks for 7+ years of experience, while the résumé has 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Applied AI Delivery Lead - NYC"; "7+ years of experience leading complex enterprise technology deployments"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/02145257d8.json.

#### Applied AI Delivery Lead - Remote in AMER

- id: `2c531790-726c-4d39-b3bd-900c59a09a4d`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/2c531790-726c-4d39-b3bd-900c59a09a4d

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): FAILS. Posting title "Applied AI Delivery Lead - Remote in AMER" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title 'Applied AI Delivery Lead' contains the level word 'Lead' and does not name any role in the résumé's title_includes. The posting also asks for 7+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Applied AI Delivery Lead - Remote in AMER"; "7+ years of experience leading complex enterprise technology deployments"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/3b2ef5ae2b.json.

#### Content Maker

- id: `d4650f77-45ed-4bee-92ac-097a62fa6341`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/d4650f77-45ed-4bee-92ac-097a62fa6341

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Content Maker" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Content Maker", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Content Maker" does not name any role in preferences.title_includes (software/backend/data engineer roles), so the role check fails. The posting also asks for 5+ years of experience, above the résumé's 3 full-time years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Have 5+ years of relevant experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/30a08d63fa.json.

#### Forward Deployed Engineer (FDE), Cyber - SF

- id: `a84e6109-142f-45ae-80e1-05811732cca1`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/a84e6109-142f-45ae-80e1-05811732cca1

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Cyber - SF" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title's role part, "Forward Deployed Engineer (FDE)", is not in title_includes and contains the excluded words "Forward Deployed". The posting also asks for 5+ years of experience, more than the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE), Cyber - SF"; "5+ years of software engineering experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/95e0fe112c.json.

#### Forward Deployed Engineer (FDE), Life Sciences - NYC

- id: `a12c3c93-51df-437d-862f-4892367fea32`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/a12c3c93-51df-437d-862f-4892367fea32

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Life Sciences - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Forward Deployed Engineer (FDE)" does not name any role in preferences.title_includes, and the title contains the excluded term "Forward Deployed". The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE)"; "Bring 5+ years of software/ML engineering"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/46711d562e.json.

#### Legal Program Manager

- id: `cda6eab0-edab-4dfc-8923-40ca3b0928b5`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/cda6eab0-edab-4dfc-8923-40ca3b0928b5

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Legal Program Manager" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Legal Program Manager" has the level word "Manager" and does not name any role in the résumé's title_includes (e.g., Software Engineer, Backend Engineer). Employment type and location (San Francisco, New York) would fit, but the level and role checks fail.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions, preferences.cities
- Posting fields cited: title, employmentType, location
- Quotes: "Legal Program Manager"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f3bcd8d42b.json.

#### Controls Engineer, Power Generation & Microgird

- id: `554a6565-0c9a-42e8-8f6f-a22ba23f336b`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/554a6565-0c9a-42e8-8f6f-a22ba23f336b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Controls Engineer, Power Generation & Microgird" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Controls Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Controls Engineer" is not among the résumé's title_includes roles (software, backend, platform, data engineer, etc.). The posting also asks for 8+ years of experience, while the résumé has 3 full-time years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Controls Engineer, Power Generation & Microgird"; "8+ years of hands-on experience designing, programming, integrating and commissioning industrial controls"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/cb09593250.json.

#### Mechanical Engineer, Power Generation

- id: `015de5ce-8210-418d-abc6-f8b8712f0dbd`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/015de5ce-8210-418d-abc6-f8b8712f0dbd

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Mechanical Engineer, Power Generation" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Mechanical Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Mechanical Engineer, Power Generation" names a role not in preferences.title_includes (Mechanical Engineer is not a listed software or infrastructure role). The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Mechanical Engineer, Power Generation"; "8+ years of mechanical engineering experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/301539f155.json.

#### Applied AI Engineer, Enterprise - EDU

- id: `087aa4f5-1192-413a-ba34-3ae324cf90e5`
- Locations: San Francisco; New York City; US - Remote
- Link: https://jobs.ashbyhq.com/openai/087aa4f5-1192-413a-ba34-3ae324cf90e5

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Applied AI Engineer, Enterprise - EDU" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Applied AI Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Applied AI Engineer" (before the comma) does not name any role in the résumé's title_includes, such as Software Engineer or Backend Engineer, so the role check fails. Employment type, location (US - Remote, New York) and no stated years or status barriers would otherwise pass.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "Applied AI Engineer, Enterprise - EDU"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/2a2cf32537.json.

#### Electrical Engineer, Power Generation

- id: `94d44e8c-987f-4350-bb13-5a855be957db`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/94d44e8c-987f-4350-bb13-5a855be957db

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Electrical Engineer, Power Generation" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Electrical Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Electrical Engineer, Power Generation" names a role (Electrical Engineer) not in title_includes. The posting also asks for 8+ years of experience, but the résumé has only 3 full-time years. Employment type and location (San Francisco, California) do fit.
- Résumé fields cited: preferences.title_includes, experience.full_time_years, preferences.employment_types, preferences.regions
- Posting fields cited: title, descriptionPlain, employmentType, location
- Quotes: "8+ years of electrical engineering experience"; "Electrical Engineer, Power Generation"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f8fce2aac6.json.

#### GTM Strategy & Planning

- id: `41408133-b45f-4c7b-a0df-c050f16d92de`
- Locations: New York City
- Link: https://jobs.ashbyhq.com/openai/41408133-b45f-4c7b-a0df-c050f16d92de

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): passes. Posting title "GTM Strategy & Planning" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "GTM Strategy & Planning", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "GTM Strategy & Planning" does not name any role in the résumé's title_includes (e.g. Software Engineer), so the role check fails. The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Have 8+ years of experience in GTM Strategy & Operations"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/51bcc51a6f.json.

#### Business Development Manager, Product Partnerships

- id: `0cf4a8f4-a57a-494b-aad8-4df8ac096939`
- Locations: Munich, Germany; London, UK
- Link: https://jobs.ashbyhq.com/openai/0cf4a8f4-a57a-494b-aad8-4df8ac096939

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Munich, Germany"; "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in Munich, Germany and London, UK, so it fails the location check. The title also has the level word "Manager" and is a business development role, not one of the preferred engineering roles. It asks for 10+ years of experience against the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, secondaryLocations, descriptionPlain
- Quotes: "Business Development Manager, Product Partnerships"; "10+ years of experience in product partnerships"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d568322a6f.json.

#### Forward Deployed Engineer (FDE), Life Sciences - SF

- id: `218c0b55-53bd-4df6-805d-321a8c2e7db7`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/218c0b55-53bd-4df6-805d-321a8c2e7db7

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Forward Deployed Engineer (FDE), Life Sciences - SF" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Forward Deployed Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Forward Deployed Engineer (FDE)" does not name any role in preferences.title_includes, and the title contains "Forward Deployed", which is in preferences.title_excludes. The posting also asks for 5+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Forward Deployed Engineer (FDE), Life Sciences - SF"; "Bring 5+ years of software/ML engineering"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/20d3b11125.json.

#### Data Scientist, Preparedness

- id: `bd1ac97f-20f9-4727-9f92-7064035a416f`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/bd1ac97f-20f9-4727-9f92-7064035a416f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Data Scientist, Preparedness" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Data Scientist", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Data Scientist, Preparedness" has the role "Data Scientist", which is not among the résumé's preferred title_includes (Software Engineer, Data Engineer, etc.). The role check fails, though employment type and San Francisco location (California is a preferred region) would otherwise fit.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions
- Posting fields cited: title, employmentType, location
- Quotes: "Data Scientist, Preparedness"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/1f479cf18f.json.


## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,091,423 bytes, SHA-256 c2ad7305148deb4aa9f09787c5a43c48e0f9978ae5e5805179a97d560f855127, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.38 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,942,874 bytes, SHA-256 8ce0bf74addf9535ad893e502af565854d1d01450ae81712ea94f1db4b052ca9, saved as boards/lever-palantir/attempt-1.json.gz (1.24 s)
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
