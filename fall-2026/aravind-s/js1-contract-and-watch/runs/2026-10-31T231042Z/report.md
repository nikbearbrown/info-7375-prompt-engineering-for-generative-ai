Run 2026-10-31T231042Z. 810 postings in the response, 7 new since the last run, 11 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment.

# Run 2026-10-31T231042Z

- Board: https://api.ashbyhq.com/posting-api/job-board/openai
- Source: live fetch
- Response: response.json, 13,509,762 bytes, SHA-256 64cbf679bd52b760b1db08b19bc51ae29d489281b5633d48d0e82093783cce87
- Started (UTC): 2026-10-31T23:10:42Z
- Résumé: jane-doe.json (fictional persona, validated)
- Contract: v0.1
- Code: job_agent fingerprint 31e795a933a1e2e6342f3591bf9d609296b6ee0ad7f9308510efd5a7b8dc92b4 (git commit 3a4a83151fdd42aa5032a9b96cc6d7d33808e255; the fingerprint is what ran, even with uncommitted changes)

## New since the last run (7)

### Senior Counsel, AI Product

- id: `36a746ab-66a6-4f3e-b164-3ca8fa9e0658`
- Locations: Washington, DC; San Francisco
- Link: https://jobs.ashbyhq.com/openai/36a746ab-66a6-4f3e-b164-3ca8fa9e0658

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting secondaryLocations[0].location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Senior Counsel, AI Product" contains the level word "Senior". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Senior Counsel, AI Product" has the level word Senior, and its role (Counsel) is not in the résumé's title_includes. The posting also asks for 8+ years of experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Senior Counsel, AI Product"; "Have 8+ years of experience"
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/eab06a5f7c.json.

### Applied AI Delivery Lead - Mountain View

- id: `18b4427e-b168-475e-a1e2-92a86c73f0f0`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/18b4427e-b168-475e-a1e2-92a86c73f0f0

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Applied AI Delivery Lead - Mountain View" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Applied AI Delivery Lead" contains the level word "Lead" and does not name any role in the résumé's title_includes. The posting also asks for 7+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Applied AI Delivery Lead - Mountain View"; "7+ years of experience leading complex enterprise technology deployments"
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/d61cdb83a3.json.

### Manufacturing Quality Engineer, Data Center Equipment

- id: `2df14230-1cb5-4727-a34e-f480303e4212`
- Locations: US - Remote
- Link: https://jobs.ashbyhq.com/openai/2df14230-1cb5-4727-a34e-f480303e4212

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location is "US - Remote", which is one of résumé preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"].
- Check 3 (level): passes. Posting title "Manufacturing Quality Engineer, Data Center Equipment" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Manufacturing Quality Engineer", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Manufacturing Quality Engineer" is not among the résumé's title_includes roles. The posting also asks for at least 10 years of data center experience, well above the résumé's 3 years of full-time experience.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "At least 10 years of data center industry experience spanning quality engineering and project management."
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/38c31aa71e.json.

### Applied AI Delivery Lead - London

- id: `ec0aa7c7-8995-4e01-9939-594a94549f85`
- Locations: London, UK
- Link: https://jobs.ashbyhq.com/openai/ec0aa7c7-8995-4e01-9939-594a94549f85

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): FAILS. Posting locations "London, UK" match none of résumé preferences.regions ["California"], preferences.cities ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"] or preferences.remote_locations ["US - Remote", "Remote - US", "United States - Remote"] (region and city count only with country United States).

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The role is in London, UK, which matches none of the preferred regions, cities or remote locations. The title also has the level word "Lead", and "Applied AI Delivery Lead" names no role in title_includes. The posting asks for 7+ years of experience, while the résumé has 3.
- Résumé fields cited: preferences.regions, preferences.cities, preferences.title_includes, experience.full_time_years
- Posting fields cited: title, location, descriptionPlain
- Quotes: "Applied AI Delivery Lead - London"; "7+ years of experience leading complex enterprise technology deployments"
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/2082102736.json.

### Research Program Manager, Safety Systems

- id: `d769a04e-c300-454a-8c68-1c93d04a6bb6`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/d769a04e-c300-454a-8c68-1c93d04a6bb6

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Research Program Manager, Safety Systems" contains the level word "Manager". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Research Program Manager, Safety Systems" has the role "Research Program Manager", which is not in title_includes and contains the excluded word "Research". It also asks for 5+ years of experience versus the résumé's 3.
- Résumé fields cited: preferences.title_includes, preferences.title_excludes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Research Program Manager, Safety Systems"; "Have 5+ years of experience in technical safety work"
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/c170c9e015.json.

### Lead Counsel, Commercial (Energy - Infrastructure)

- id: `687d42ab-42dd-4ab7-9675-2468896746e9`
- Locations: San Francisco
- Link: https://jobs.ashbyhq.com/openai/687d42ab-42dd-4ab7-9675-2468896746e9

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): FAILS. Posting title "Lead Counsel, Commercial (Energy - Infrastructure)" contains the level word "Lead". The level words are fixed in CONTRACT.md, check 3, so no résumé value is compared; the résumé field behind the check is experience.full_time_years 3.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title contains the level word "Lead" and the role "Counsel" is not in the résumé's title_includes. The posting also asks for 10+ years of legal experience, above the résumé's 3 years.
- Résumé fields cited: preferences.title_includes, experience.full_time_years
- Posting fields cited: title, descriptionPlain
- Quotes: "Lead Counsel, Commercial (Energy - Infrastructure)"; "10+ years of legal experience"
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/1af2917c65.json.

### Product Growth

- id: `65dd3a22-32f8-4559-875a-bbb923664c87`
- Locations: San Francisco; New York City
- Link: https://jobs.ashbyhq.com/openai/65dd3a22-32f8-4559-875a-bbb923664c87

**Rule verdict (record):** not_relevant

- Check 1 (employment type): passes. Posting employmentType is "FullTime"; résumé preferences.employment_types is ["FullTime"].
- Check 2 (location): passes. Posting location "San Francisco" has address region "California" in the United States, which is in résumé preferences.regions ["California"].
- Check 3 (level): passes. Posting title "Product Growth" contains none of the level words (CONTRACT.md, check 3); résumé experience.full_time_years is 3.
- Check 4 (role): FAILS. The role part of the title, "Product Growth", contains none of résumé preferences.title_includes.

**Claude's judgment (model output, not verified):** not_relevant

- Justification: The title "Product Growth" does not name any role in the résumé's title_includes (Software Engineer, Backend Engineer, etc.), so the role check fails. Employment type and New York location would otherwise fit.
- Résumé fields cited: preferences.title_includes
- Posting fields cited: title
- Quotes: none
- Model claude-sonnet-5-5, 2026-10-31, prompt baseline.txt (SHA-256 d616ca168220); call saved as claude/079ed7ecb5.json.

## Gone since the last run (11)

- `1eb6ef0f-0e51-46d3-b888-c1a4c22c190a` Enterprise Account Associate- EMEA (French Speaking)
- `56e699e0-421f-40d1-aad1-20cf6609794f` Strategic Finance, B2B Partnerships
- `609cb338-a168-42c1-8e77-5837826136b1` Program Manager, Partner Content & Storytelling
- `43ba8b53-4643-4544-bb21-f13efe99e0a0` Product Designer, Youth
- `60be7108-c540-4839-87a8-41f19a75c1ce` Global Head of Events
- `923eebc8-5591-4057-892f-5825de1a5460` HR Business Partner, EMEA
- `70042d81-4db6-4c5c-bdb2-76c133ee2917` Machine Learning Engineer, Growth
- `3d064454-c0c3-4225-bc2c-6d8c0f8735b2` Backend Software Engineer, Cooperative AI (Evals) 
- `d95a5b8b-35fb-4ae2-9f6c-594ed24e49f7` Software Engineer
- `6fd09d8c-f1d9-4c60-bb47-f63d8a96c10b` Content Marketing Manager, Events
- `9711a982-851c-4f55-a5ae-080ea4bad520` Events Designer, Business Marketing
