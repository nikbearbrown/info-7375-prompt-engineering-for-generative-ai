Exit: budget-exhausted (code 4). claude_calls budget: the budget of 20 Claude calls was used up (35 postings wait for Claude's judgment). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 3 read, 1 unverified, 0 not visited. 1464 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 35 waiting for Claude.

# Run 2026-11-08T222101Z

- Source: live
- Started (UTC): 2026-11-08T22:21:01Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 20/20, seconds 65.6/600
- Gate v1.0, contract v0.1; the code fingerprint and git commit are in the trace's first line
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
- Attempt 1: HTTP 200, 13,641,063 bytes, SHA-256 7aff4139e7e97306874e8b0cf659a2e4ad9ca5703261dda5c7885154c3e62d04, saved as boards/ashby-openai/attempt-1.json.gz (0.52 s)
- State: updated after this report (the trace records the write)

### Judged now, after waiting for Claude (55)

#### Industry & Experiential Marketing Lead, Ads

- id: `5f3a3325-bc3c-4f92-8456-f22add6fe52b`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/5f3a3325-bc3c-4f92-8456-f22add6fe52b

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Industry & Experiential Marketing Lead, Ads" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Lead" and names a marketing role, not one in title_includes. The posting also asks for 10+ years of experience, while the résumé has 3 full-time years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Industry & Experiential Marketing Lead, Ads"; "10+ years of experience in B2B marketing"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/fdb111c64d.json.

#### Content & Solutions Marketing Lead, Ads

- id: `c033c8a7-88bb-44d1-b299-2fd420be5f57`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/c033c8a7-88bb-44d1-b299-2fd420be5f57

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Content & Solutions Marketing Lead, Ads" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Lead" and the role (Content & Solutions Marketing Lead) is not in the résumé's title_includes, and it contains the excluded word "Solutions". The posting also asks for 10+ years of experience versus 3 years on the résumé.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Content & Solutions Marketing Lead, Ads"; "10+ years of experience in content marketing"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/401a730b04.json.

#### Applied AI Engineer, Enterprise - Healthcare Life Sciences (HLS)

- id: `6fc25168-bc4c-47a0-8601-583dfaf7fcbd`
- Locations: San Francisco; New York City; US - Remote
- Link: https://jobs.ashbyhq.com/openai/6fc25168-bc4c-47a0-8601-583dfaf7fcbd

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Applied AI Engineer, Enterprise - Healthcare Life Sciences (HLS)" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Applied AI Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The part of the title before the first comma is "Applied AI Engineer", which does not match any role in preferences.title_includes (e.g. Software Engineer, Backend Engineer). The location (US - Remote) and full-time type would otherwise fit, but the role check fails.
- Résumé fields cited: preferences.title_includes, preferences.remote_locations, preferences.employment_types
- Posting fields cited: title, secondaryLocations, employmentType
- Quotes: "Applied AI Engineer, Enterprise - Healthcare Life Sciences (HLS)"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/8156bbfc70.json.

#### Strategic Partner Lead, Creators & Culture, EMEA

- id: `bc58f2d0-9b24-4205-a799-5a5d18bf64ee`
- Locations: Paris, France
- Link: https://jobs.ashbyhq.com/openai/bc58f2d0-9b24-4205-a799-5a5d18bf64ee

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in Paris, France, which matches none of the résumé's regions, cities or remote locations. The title contains "Lead", a level word, and "Strategic Partner Lead" is not a listed engineering role. It also asks for 10+ years of experience, against the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Strategic Partner Lead, Creators & Culture, EMEA"; "Have 10+ years of experience in strategic partnerships"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/e3dadd8340.json.

#### Senior Global Security Investigator

- id: `81864df0-ce84-44af-8aef-e05dc5660793`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/81864df0-ce84-44af-8aef-e05dc5660793

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): FAILS. Posting title "Senior Global Security Investigator" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title has the level word "Senior" and the role "Global Security Investigator" is not in the résumé's title_includes (and contains the excluded word "Security"). The posting also asks for an active US security clearance or eligibility to obtain one, and 8+ years of experience exceeds the résumé's 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, work_authorization.us_person, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Global Security Investigator"; "An active US security clearance, or willingness and eligibility to obtain one."; "8+ years of investigative experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/ee15f6d55f.json.

#### User Education Lead

- id: `654f8dde-2ccb-4349-aeb7-40f454f28cce`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/654f8dde-2ccb-4349-aeb7-40f454f28cce

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "User Education Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "User Education Lead" contains the level word "Lead" and does not name any role in the résumé's title_includes (software/backend/data engineer etc.), so the level and role checks fail. Employment type and location (San Francisco, California) would otherwise fit.
- Résumé fields cited: preferences.title_includes, preferences.employment_types, preferences.regions
- Posting fields cited: title, location, employmentType
- Quotes: "User Education Lead"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/f8a8562003.json.

#### Presentation Designer, Business Marketing

- id: `80ca9623-f911-45fc-b5dc-47ccfc60b395`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/80ca9623-f911-45fc-b5dc-47ccfc60b395

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Presentation Designer, Business Marketing" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Presentation Designer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Presentation Designer" is not among the résumé's title_includes roles (software/backend/data engineer etc.). The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Presentation Designer, Business Marketing"; "Have 8+ years of professional experience in visual design"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/b6fd6ad1ed.json.

#### Engineering Manager, API Multicloud

- id: `f363932f-2820-4056-9786-14cb697f4a93`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/f363932f-2820-4056-9786-14cb697f4a93

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Engineering Manager, API Multicloud" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Engineering Manager, API Multicloud" contains the level word "Manager", and the role before the comma, "Engineering Manager", is not among the résumé's title_includes. Employment type and location (San Francisco, California) would fit, but the level and role checks fail.
- Résumé fields cited: preferences.title_includes, preferences.regions, preferences.employment_types
- Posting fields cited: title, location, employmentType
- Quotes: "Engineering Manager, API Multicloud"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/e0185d959b.json.

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

**Claude's judgment (model output, not verified):** no valid judgment

- No valid judgment: the answer failed the validator: justification has more than 3 sentences
- Call saved as claude/919a38a2ad.json.

#### Sales and Partnerships

- id: `45a0886d-a60d-4d5a-9afa-785a75042044`
- Locations: London, UK; Brussels - Remote; Madrid, Spain; Berlin, Germany; Zurich, Switzerland; Amsterdam, NL; Germany - Remote; Munich, Germany; Dublin, Ireland; Stockholm, Sweden; Abu Dhabi, UAE; UAE - Remote; Paris, France
- Link: https://jobs.ashbyhq.com/openai/45a0886d-a60d-4d5a-9afa-785a75042044

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK"; "Brussels - Remote"; "Madrid, Spain"; "Berlin, Germany"; "Zurich, Switzerland"; "Amsterdam, NL"; "Germany - Remote"; "Munich, Germany"; "Dublin, Ireland"; "Stockholm, Sweden"; "Abu Dhabi, UAE"; "UAE - Remote"; "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Sales and Partnerships" names no role in the résumé's title_includes and contains the excluded word "Sales". None of the posting's locations are in the United States, so the location fit fails too.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, preferences.regions, preferences.cities, preferences.remote_locations
- Posting fields cited: title, location, secondaryLocations
- Quotes: none
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/59e9ed5c36.json.

#### Account Director, Startups | New Business

- id: `50053f7b-c154-45af-b497-3298c826a15f`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/50053f7b-c154-45af-b497-3298c826a15f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Account Director, Startups | New Business" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title 'Account Director' contains the level word 'Director', and the role 'Account Director' is not among the résumé's title_includes. The posting also asks for 6+ years of experience, but the résumé has only 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Account Director, Startups | New Business"; "6+ years selling platform-as-a-service, cloud, or other API products."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c0b2629f23.json.

#### Technical Success - EMEA

- id: `b3c1b5a9-a8fe-49df-849b-d4a06a47562c`
- Locations: London, UK; Madrid, Spain; Munich, Germany; Dublin, Ireland; Abu Dhabi, UAE; Paris, France
- Link: https://jobs.ashbyhq.com/openai/b3c1b5a9-a8fe-49df-849b-d4a06a47562c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK"; "Madrid, Spain"; "Munich, Germany"; "Dublin, Ireland"; "Abu Dhabi, UAE"; "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: All posting locations are in the UK, Spain, Germany, Ireland, UAE and France, none in the U.S. or a preferred remote location. The title "Technical Success" also names no role in title_includes.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location, secondaryLocations, workplaceType
- Quotes: none
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/941d8adf3a.json.

#### Senior Counsel, Trademark

- id: `e74c8ec3-3317-4fea-bb66-703dc2d55a51`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e74c8ec3-3317-4fea-bb66-703dc2d55a51

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, Trademark" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Counsel, Trademark" contains the level word "Senior", and the role "Senior Counsel" is not among the résumé's title_includes (software/backend/data engineering roles). The posting also asks for 10+ years of experience, far above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Counsel, Trademark"; "Have 10+ years of leading complex trademark litigation and disputes"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/29d5c1dd2a.json.

#### Sales Manager, ANZ | Large Enterprise

- id: `5c7a8915-07dd-4e8c-861a-5b0c647f17a2`
- Locations: Sydney, Australia
- Link: https://jobs.ashbyhq.com/openai/5c7a8915-07dd-4e8c-861a-5b0c647f17a2

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Sydney, Australia" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in Sydney, Australia, which is not a U.S. location matching the résumé's regions, cities or remote locations. The title has the level word "Manager" and the role "Sales Manager" is not a preferred title (and contains the excluded word "Sales"). It also asks for 10+ years of experience against 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Sales Manager, ANZ | Large Enterprise"; "10+ years leading Enterprise Sales teams."
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9a07d04fd9.json.

#### Account Director, Mid-Market Enterprise

- id: `e586578c-2489-4214-92c4-d9639339fe59`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e586578c-2489-4214-92c4-d9639339fe59

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Account Director, Mid-Market Enterprise" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Account Director, Mid-Market Enterprise" contains the level word "Director", and the part before the comma, "Account Director", names no role in the résumé's title_includes. The posting also asks for 9+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Account Director, Mid-Market Enterprise"; "9+ years selling platform-as-a-service and/or software-as-a-service"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d87312996e.json.

#### Cyber AI Partner Director

- id: `b6736e0a-db0b-428f-ad14-448353a92243`
- Locations: New York City; San Francisco
- Link: https://jobs.ashbyhq.com/openai/b6736e0a-db0b-428f-ad14-448353a92243

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "New York City" has address city "New York" in the United States, which is in résumé preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"].
- Check 3 (level): FAILS. Posting title "Cyber AI Partner Director" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Cyber AI Partner Director" contains the level word "Director", and the role is a partner sales position that matches none of the résumé's title_includes entries (such as Software Engineer or Backend Engineer).
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title, descriptionPlain
- Quotes: "Cyber AI Partner Director"; "This is a hands-on partner sales role"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/51495c9974.json.

#### ML Silicon Performance Lead

- id: `67c8b37d-f856-4edf-adb7-1a5b0d07f6b3`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/67c8b37d-f856-4edf-adb7-1a5b0d07f6b3

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "ML Silicon Performance Lead" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "ML Silicon Performance Lead" contains the level word "Lead". The role part also contains the excluded word "ML" and does not name any role in title_includes.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes
- Posting fields cited: title
- Quotes: "ML Silicon Performance Lead"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/ae979cced5.json.

#### Accounting Lead, Hardware

- id: `bfecbfa0-6573-4c00-8215-50e271f411bc`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/bfecbfa0-6573-4c00-8215-50e271f411bc

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Accounting Lead, Hardware" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Accounting Lead, Hardware" contains the level word "Lead", and the role before the comma, "Accounting Lead", is not in the résumé's title_includes. The posting also requires 8+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Accounting Lead, Hardware"; "8+ years of progressive accounting experience"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/81718a9b6f.json.

#### Intercompany Accountant

- id: `e183d73c-4eeb-4b75-9b69-435591bb535a`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e183d73c-4eeb-4b75-9b69-435591bb535a

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Intercompany Accountant" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Intercompany Accountant", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Intercompany Accountant" is not a role in the résumé's preferences.title_includes (software/data/platform engineering roles), so the role check fails. Employment type and location (San Francisco, California) fit, but the role mismatch decides it.
- Résumé fields cited: preferences.title_includes, preferences.regions, preferences.employment_types
- Posting fields cited: title, location, employmentType
- Quotes: "Intercompany Accountant"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c6e0e63df6.json.

#### Growth Marketing Lead, EMEA

- id: `7d10d614-dc7c-427f-abc1-9a4d4ef7a82f`
- Locations: Dublin, Ireland
- Link: https://jobs.ashbyhq.com/openai/7d10d614-dc7c-427f-abc1-9a4d4ef7a82f

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Dublin, Ireland" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in Dublin, Ireland, which is outside the United States and matches none of the résumé's regions, cities or remote locations. The title also contains the level word "Lead" and does not name any of the preferred engineering roles.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes
- Posting fields cited: title, location
- Quotes: "Growth Marketing Lead, EMEA"; "Dublin, Ireland"
- Model claude-sonnet-5-5, 2026-11-08, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/8e9288633e.json.

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



### Still waiting for Claude (35)

Judged first next run: `1790fe9e-2ac3-45df-894e-f731d243395f`, `85d4e269-af3f-4b62-91d3-8ede8361cd16`, `48bd347f-c799-48ac-aa5b-1b0dfbff90f7`, `02b170ae-de32-46f5-8ef1-844b268681fe`, `5ceff3dd-3503-4ea0-9ade-eeb36b29f14e`, `73a111f9-e83d-4cce-9148-2a32ccf1d251`, `8e7ba2dd-d632-4a8b-b95b-e2592f77a679`, `5cc72bc7-e6a0-40e0-9f60-23474cd9acdb`, `5692fcec-bd48-40b4-9cd3-2c881faf176c`, `80c40695-5cd7-4206-96b6-873158a8e696`, `16596d69-1e40-499b-9d62-13e6f6a498de`, `31b9754b-6ed1-4ee1-80ad-d087cba053c4`, `e49133e6-4030-4295-b393-1725aa410344`, `66453891-c75a-41c9-a7de-d0c67f23db4e`, `df242b29-6a84-4968-8d57-cbeec20dee67`, `c2016d32-1994-471d-8900-1b49259c647c`, `f430a2e7-78a8-40bc-8501-b7ff191ecad6`, `a36322aa-829e-47b0-821d-d15a40733b83`, `c90cfa58-7513-4998-a1ce-f6168dd8fc95`, `783704d7-5afa-45aa-899b-1d6799f73004`, `9c1aa1f3-b4d0-48fa-814b-37d36ad0ad2e`, `20df76c8-aa7e-40d1-8602-28605ed5431b`, `2c531790-726c-4d39-b3bd-900c59a09a4d`, `d4650f77-45ed-4bee-92ac-097a62fa6341`, `a84e6109-142f-45ae-80e1-05811732cca1`, `a12c3c93-51df-437d-862f-4892367fea32`, `cda6eab0-edab-4dfc-8923-40ca3b0928b5`, `554a6565-0c9a-42e8-8f6f-a22ba23f336b`, `015de5ce-8210-418d-abc6-f8b8712f0dbd`, `087aa4f5-1192-413a-ba34-3ae324cf90e5`, `94d44e8c-987f-4350-bb13-5a855be957db`, `41408133-b45f-4c7b-a0df-c050f16d92de`, `0cf4a8f4-a57a-494b-aad8-4df8ac096939`, `218c0b55-53bd-4df6-805d-321a8c2e7db7`, `bd1ac97f-20f9-4727-9f92-7064035a416f`

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,091,423 bytes, SHA-256 c2ad7305148deb4aa9f09787c5a43c48e0f9978ae5e5805179a97d560f855127, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.37 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,942,874 bytes, SHA-256 8ce0bf74addf9535ad893e502af565854d1d01450ae81712ea94f1db4b052ca9, saved as boards/lever-palantir/attempt-1.json.gz (1.23 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.11 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
