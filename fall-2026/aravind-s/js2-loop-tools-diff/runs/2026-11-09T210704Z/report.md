Exit: incomplete (code 1). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.

4 boards: 3 read, 1 unverified, 0 not visited. 1457 postings in the answers read, 15 new since the last run, 22 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 0 judged by Claude after waiting, 0 waiting for Claude.

# Run 2026-11-09T210704Z

- Source: live
- Started (UTC): 2026-11-09T21:07:04Z
- Budgets used: boards 4/5, requests 4/10, Claude calls 15/20, seconds 39.1/600
- Gate v1.0, contract v0.2; the code fingerprint and git commit are in the trace's first line
- Approval given on the command line: none

## Boards

| Board | Status | Postings | New | Gone |
|---|---|---:|---:|---:|
| ashby-openai | read | 811 | 11 | 16 |
| greenhouse-verkada | read | 342 | 4 | 5 |
| lever-palantir | read | 304 | 0 | 1 |
| greenhouse-no-such-board-js2-test (fails on purpose) | unverified | not read | 0 | 0 |

## OpenAI (ashby/openai)

- URL: https://api.ashbyhq.com/posting-api/job-board/openai
- Status: read
- Attempt 1: HTTP 200, 13,544,469 bytes, SHA-256 c43083ebe2e5b0cf67fe45ac620d6fcb53bf488c5b2b344a453d0ae457fb80bb, saved as boards/ashby-openai/attempt-1.json.gz (0.62 s)
- State: updated after this report (the trace records the write)

### New since the last run (11)

#### Manager, Forward Deployed Engineering - Munich

- id: `5d5b2256-ee0f-4ba6-a983-d62d0d70515d`
- Locations: Munich, Germany
- Link: https://jobs.ashbyhq.com/openai/5d5b2256-ee0f-4ba6-a983-d62d0d70515d

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Munich, Germany" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Munich, Germany, which matches no preferred region, city or US remote location. The title contains the level word "Manager", and its role part ("Manager, Forward Deployed Engineering") names no preferred role and includes the excluded term "Forward Deployed". The posting also asks for 8+ years of experience against the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Manager, Forward Deployed Engineering - Munich"; "Bring 8+ years of engineering or technical delivery experience"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/5420256eda.json.

#### Sales Manager, Enterprise - Japan

- id: `110d820b-fcbe-4f02-9203-5b6145132e60`
- Locations: Tokyo, Japan
- Link: https://jobs.ashbyhq.com/openai/110d820b-fcbe-4f02-9203-5b6145132e60

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Tokyo, Japan" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in Tokyo, Japan, which matches none of the résumé's regions, cities or remote locations. The title has the level word "Manager" and is a sales role, not a listed engineering title; it also contains the excluded word "Sales". It asks for 8+ years, above the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Sales Manager, Enterprise - Japan"; "8+ years leading Enterprise Sales teams"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/279703618d.json.

#### Strategic Sourcing Manager, Data Center Infrastructure, Electrical & Mechanical

- id: `e99a7881-e30a-40b4-849d-b039004d11ed`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/e99a7881-e30a-40b4-849d-b039004d11ed

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Strategic Sourcing Manager, Data Center Infrastructure, Electrical & Mechanical" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Manager" and the role "Strategic Sourcing Manager" is not in the résumé's title_includes. The posting also asks for 8+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Strategic Sourcing Manager, Data Center Infrastructure, Electrical & Mechanical"; "8+ years of experience in strategic sourcing, procurement, supplier management, or infrastructure supply chain."
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/01f43daf4f.json.

#### Account Director, Higher Education

- id: `dceee17e-1e37-448b-acd3-2f97e41a6af7`
- Locations: San Francisco; New York City; Seattle; US - Remote
- Link: https://jobs.ashbyhq.com/openai/dceee17e-1e37-448b-acd3-2f97e41a6af7

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Account Director, Higher Education" contains the level word "Director". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Account Director, Higher Education" contains the level word "Director", and the role is a sales role that matches none of the résumé's title_includes. The posting also asks for 10+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Account Director, Higher Education"; "10+ years of experience selling platform-as-a-service"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/993fd747c8.json.

#### Applied AI Engineer, Large Enterprise

- id: `0cbc002e-bd6e-4aa3-9dbc-ed7fe59511ea`
- Locations: Munich, Germany
- Link: https://jobs.ashbyhq.com/openai/0cbc002e-bd6e-4aa3-9dbc-ed7fe59511ea

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Munich, Germany" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The only location is Munich, Germany, which is not in a preferred U.S. region, city, or remote location. The title "Applied AI Engineer" also names no role in title_includes, and the posting asks for 5+ years of experience, more than the résumé's 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Munich, Germany"; "Applied AI Engineer, Large Enterprise"; "track record of 5+ years"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a0939ce02b.json.

#### Senior Counsel, Commercial (Health and Life Sciences)

- id: `167e2ee5-7280-4153-9490-5e7a8372e1dc`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/167e2ee5-7280-4153-9490-5e7a8372e1dc

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, Commercial (Health and Life Sciences)" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior" and names a legal counsel role, not one in the résumé's title_includes. The posting also asks for 10+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Counsel, Commercial (Health and Life Sciences)"; "Have 10+ years of relevant legal experience"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/a47a344eed.json.

#### Head of Community, EMEA

- id: `a19c76b4-f4ed-424b-afb0-c711ed7d9e2d`
- Locations: London, UK; Berlin, Germany; Paris, France
- Link: https://jobs.ashbyhq.com/openai/a19c76b4-f4ed-424b-afb0-c711ed7d9e2d

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK"; "Berlin, Germany"; "Paris, France" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Head" and names a community role, not any software or engineering role in title_includes. All locations are in London, Berlin and Paris, outside the preferred U.S. regions and cities, and the posting asks for 10+ years of experience against 3.
- Résumé fields cited: preferences.title_includes, preferences.regions, preferences.cities, experience.full_time_years
- Posting fields cited: title, location, secondaryLocations, descriptionPlain
- Quotes: "Head of Community, EMEA"; "Have 10+ years of experience building, leading or scaling communities"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/379761082d.json.

#### Solutions Engineer, Ads Solutions - NYC

- id: `eb3b695e-6c60-4875-b8bc-8f4d5d8a9bbb`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/eb3b695e-6c60-4875-b8bc-8f4d5d8a9bbb

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Solutions Engineer, Ads Solutions - NYC" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Solutions Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Solutions Engineer" does not name a role in title_includes and contains the excluded word "Solutions". The posting also asks for 5+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Solutions Engineer, Ads Solutions - NYC"; "Have 5+ years of experience in solutions engineering"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/9c12706d55.json.

#### Executive in Residence, Cyber

- id: `6384df1b-c2e0-4265-ad9b-d4a7bca706d6`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/6384df1b-c2e0-4265-ad9b-d4a7bca706d6

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Executive in Residence, Cyber" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Executive in Residence", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Executive in Residence" (before the comma) does not name any role in preferences.title_includes, such as Software Engineer. The role is a CISO-level executive position requiring CISO experience, far from the résumé's backend engineering background.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Executive in Residence, Cyber"; "Experience as a CISO or equivalent security executive"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/3b355de10d.json.

#### Senior Counsel, Litigation (Safety)

- id: `1a607736-8631-4fd9-a1a9-f790318d12d2`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/1a607736-8631-4fd9-a1a9-f790318d12d2

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, Litigation (Safety)" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Counsel, Litigation (Safety)" contains the level word "Senior" and the role before the first comma, "Senior Counsel", is not a software engineering role in title_includes. The posting also asks for 10+ years of experience, but the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Counsel, Litigation (Safety)"; "at least 10+ years of combined litigation experience"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/63b423e11a.json.

#### Partner Sales and Development Leader, Southern Europe

- id: `320f6132-7a72-425e-8045-4fd59f99f31c`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/320f6132-7a72-425e-8045-4fd59f99f31c

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The posting is in London, UK, which is outside the résumé's preferred U.S. regions, cities and remote locations. The title also fails the role check, since 'Partner Sales and Development Leader' names no role in title_includes, contains 'Sales' (a title_excludes word) and has the level word 'Leader' in the same family as Lead/Manager.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.remote_locations, preferences.title_includes, preferences.title_excludes
- Posting fields cited: title, location
- Quotes: "Partner Sales and Development Leader, Southern Europe"; "London, UK"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/43c0d2d040.json.


### Gone since the last run (16)

- `13cdb1b1-8c21-4bff-8201-f7ca904e181d` Critical Facilities Lead, Compute Infrastructure
- `61171d99-747f-441e-985d-20c010112ad8` Strategic Sourcing Manager, Data Center Infrastructure, Mechanical
- `fe753283-d232-4470-8e20-fbeb217ea9e2` Strategic Sourcing Manager, Data Center Infrastructure, Electrical
- `debaf5f8-c166-4b35-81c1-5bda75124373` Strategic Sourcing Manager,  Compute Infrastructure
- `7f299784-2c75-4d73-99e5-1e5043ec7b48` Data Scientist, B2B Demand Generation, Growth & Measurement
- `4d104ebe-64ff-4421-94c3-03a8982b19ea` Compute Infrastructure, Critical Facilities Manager
- `6cf91ff5-a811-435c-bf93-f3d958896599` RTL Design Engineer – Interconnect & Network Datapath
- `bb569a6b-a7e9-4c4d-a78e-d35349b2f9d9` Enablement Lead (Builder) - Tokyo
- `831e2f91-c213-4208-9eb3-4ce2cc6b9acf` Strategic Sourcing Manager, Data Center Infrastructure, Owner Furnished Equipment
- `fb8d253c-b0e9-48c3-870e-2c8e2d655a0d` Supply Chain Manager, Industrial Compute
- `df688f65-0159-4f0b-9944-0d9492c0b001` Account Director, Startups | New Business - France
- `756d8c20-649a-47f2-8012-553b5f6cb0c5` Data Scientist, B2B Strategy & Intelligence
- `65b255da-4fd9-414e-98d4-0bec4eecf8ff` Product Manufacturing & Quality Engineer 
- `1d8596f7-a81f-432f-9828-cfa915726b3f` Integrated Marketing Manager, AI Impact 
- `bc58f2d0-9b24-4205-a799-5a5d18bf64ee` Strategic Partner Lead, Creators & Culture, EMEA
- `85d4e269-af3f-4b62-91d3-8ede8361cd16` Editor, Research Team

## Verkada (greenhouse/verkada)

- URL: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true
- Status: read
- Attempt 1: HTTP 200, 4,069,671 bytes, SHA-256 7b43e4b4b7a47f8d47116a2b97dbaef3225252bf81f282bc34b4a9c5deb35d3f, saved as boards/greenhouse-verkada/attempt-1.json.gz (0.38 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: updated after this report (the trace records the write)

### New since the last run (4)

#### Enterprise Development Representative - Dutch or Swedish Speaking

- id: `5287089007`
- Locations: London
- Link: https://job-boards.greenhouse.io/verkada/jobs/5287089007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The job is in London, which is not in the résumé's preferred regions, cities or remote locations. The title is a sales role (Enterprise Development Representative), not one of the preferred engineering titles. The posting also says it cannot sponsor a visa.
- Résumé fields cited: preferences.cities, preferences.regions, preferences.title_includes, work_authorization.needs_sponsorship
- Posting fields cited: title, location, descriptionPlain
- Quotes: "This role would be based in our London Old Street office."; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c5b3da9e03.json.

#### Regional Vice President,  Central - Education

- id: `5287286007`
- Locations: Central, United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5287286007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "Central, United States" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Regional Vice President" contains the level word VP/Vice President and is not a software engineering role in title_includes. The location "Central, United States" matches no preferred region, city or remote location, and the role asks for 3+ years of sales leadership, not engineering.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, preferences.regions, preferences.cities, preferences.remote_locations
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Regional Vice President,  Central - Education"; "Central, United States"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/2ff69c5e06.json.

#### Senior Sales Recruiter, Early Careers

- id: `5281932007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5281932007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Sales Recruiter, Early Careers" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Sales Recruiter, Early Careers" has the level word Senior and the role is a recruiter, not in title_includes, and "Sales" is a title_exclude. The posting also says it cannot sponsor visas and asks for 5+ years of experience versus the résumé's 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, work_authorization.needs_sponsorship, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Sales Recruiter, Early Careers"; "We are unable to sponsor or take over sponsorship of an employment visa for this role, at this time."; "5+ years of successful full-cycle recruiting experience"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/2a1ce677e4.json.

#### Senior Software Engineer, Business Systems - Data Trust

- id: `5264711007`
- Locations: San Mateo, CA United States
- Link: https://job-boards.greenhouse.io/verkada/jobs/5264711007

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Mateo, CA United States" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Software Engineer, Business Systems - Data Trust" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Senior", which fails the level rule. The posting also asks for 5+ years of experience, above the résumé's 3 years of full-time experience.
- Résumé fields cited: experience.full_time_years, preferences.title_includes
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Software Engineer, Business Systems - Data Trust"; "5+ years of software engineering with a focus on data systems"
- Model claude-sonnet-5-5, 2026-11-09, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/4441315d33.json.


### Gone since the last run (5)

- `4950450007` National Channel Sales Manager, Convergint (Eastern US)
- `4945720007` National Channel Sales Manager, Convergint (Eastern US)
- `5144827007` National Channel Sales Manager, Convergint (Eastern US)
- `4950449007` National Channel Sales Manager, Convergint (Eastern US)
- `5221364007` Senior Software Engineer, Business Systems - Data Trust

## Palantir (lever/palantir)

- URL: https://api.lever.co/v0/postings/palantir?mode=json
- Status: read
- Attempt 1: HTTP 200, 5,927,545 bytes, SHA-256 900ed27b9d19a3fa52394216c06ed325be42248503e2eb14c594ef2cc2808297, saved as boards/lever-palantir/attempt-1.json.gz (1.53 s)
- Fields the rule reads, mapped from this system: id from id; title from text; jobUrl from hostedUrl; employmentType from categories.commitment; location from categories.allLocations (or categories.location), with country; descriptionPlain from descriptionPlain, then each of lists (heading and items), then additionalPlain
- State: updated after this report (the trace records the write)

### Gone since the last run (1)

- `1f007e36-a620-4d15-bf0b-70dc3f3439d8` Deployment Strategist - Spain

## (made-up name) (greenhouse/no-such-board-js2-test)

- URL: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true
- Status: unverified: the board answered HTTP 404, not 200
- This board is on the list to fail on purpose (GATE.md, Boards).
- **Needs you:** check the board name, or try again later.
- Attempt 1: HTTP 404, 38 bytes, SHA-256 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe, saved as boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz (0.12 s)
- Fields the rule reads, mapped from this system: id from id; title from title; jobUrl from absolute_url; employmentType from metadata "Employment Type"; location from location.name (split at ;); descriptionPlain from content (HTML entities decoded, tags removed)
- State: kept exactly as it was
