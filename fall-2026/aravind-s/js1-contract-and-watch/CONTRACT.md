# Contract: Job-Search Agent 1 (the contract and the watch)

Version 0.1, 2026-10-30. Written before any code. The decisions behind it are listed at the end.

The agent watches one public job board and remembers which postings it has seen. For each posting that is new since the last run, it gives two verdicts on whether the posting is worth a fictional persona's time: one from the written rule below (a record anyone can recompute) and one from Claude (a judgment, labeled as one).

## In

- **Board:** OpenAI's public board on Ashby, fetched with one `GET https://api.ashbyhq.com/posting-api/job-board/openai`. No login, no key, no cookies.
- **Allow-list:** exactly one host, `api.ashbyhq.com`, over HTTPS on port 443. The host must equal it exactly: no substring, prefix or suffix match. Redirects are not followed.
- **Résumé:** one JSON file for the fictional persona Jane Doe, `persona/jane-doe.json`. It must pass the résumé validator before anything else runs: `"fictional": true`, an email ending in `@example.com`, a phone number from 555-0100 to 555-0199, and every field the rule reads present with the right type.
- **Résumé fields the rule reads** (Jane's values in brackets):
  - `experience.full_time_years` [3]
  - `work_authorization.needs_sponsorship` [true]
  - `work_authorization.us_person` [false]
  - `availability.earliest_full_time_start` ["2027-05"]
  - `preferences.employment_types` [FullTime]
  - `preferences.regions` [California]
  - `preferences.cities` [Austin, Boston, Cambridge, New York, Seattle, Bellevue, Redmond]
  - `preferences.remote_locations` ["US - Remote", "Remote - US", "United States - Remote"]
  - `preferences.title_includes` [Software Engineer, Software Developer, Backend Engineer, Back-end Engineer, Full Stack Engineer, Full-Stack Engineer, Infrastructure Engineer, Platform Engineer, Data Engineer, Reliability Engineer]
  - `preferences.title_excludes` [Frontend, Front-end, Android, iOS, Mobile, Firmware, Hardware, Embedded, Camera, Robotics, Machine Learning, ML, Research, Security, Forward Deployed, Solutions, Support, Sales, Network]

  Other résumé fields (education, skills, projects) are read only by Claude.
- **What Claude receives:** the posting's `title`, `location`, `secondaryLocations`, `workplaceType`, `employmentType` and `descriptionPlain`, and the résumé without `name`, `email`, `phone` and `links`. Contact fields never leave the program.
- **State:** `state/seen.json` from the last run. If it does not exist, the run is the baseline.
- **Claude:** the Claude Code CLI on my Mac, signed in with my claude.ai seat. No API key. The model's name is recorded with every answer.
- **Broken input stops the run and changes no state:** a résumé that fails validation; a board answer that is not HTTP 200, is not JSON, has no `jobs` list or an empty one, or has a job without an `id` or a `title`; an unreadable state file. If a response arrived, it is still saved as evidence.

## Out

Every run writes a folder `runs/<run id>/`, where the run id is the UTC start time (for example `2026-10-30T230000Z`):

- `response.json`: the raw response, byte for byte, and `response.sha256` with its SHA-256.
- `report.md` and `report.json`, described below.
- `claude/`: for each Claude call, what was sent, the raw answer, and the validator's result.

It also updates `state/seen.json`: every posting id ever seen (ids are never removed), plus the last run's id, time, response hash and posting ids.

The report always starts with a counts line, even when nothing is new: postings in the response, new since the last run, gone since the last run, new and relevant by the rule, and new and relevant in Claude's judgment. The screen shows the same counts line and one line per new posting.

- **Baseline run** (no state file): records every id, reports `0 new`, and judges nothing.
- **Later runs:** a posting is new if its `id` was not seen in any earlier run. Gone postings (in the last run, missing now) are listed by id and title and are not judged. Changed text is not tracked in this version.
- **For each new posting:** id, title, locations, link (`jobUrl`), and two verdicts in separate sections:
  - **Rule verdict (record):** `relevant` or `not_relevant`. For `not_relevant`: the check that decided it, the posting field with the quoted text or value, and the résumé field with the value it was compared with. For `relevant`: the same citation for each of the seven checks, plus any caution (see check 5). Anyone can recompute it from the saved response and the résumé.
  - **Claude's judgment (model output, not verified):** `relevant` or `not_relevant`, its justification, the résumé fields and posting fields it cites, its quotes, the model name and the date. Or `no valid judgment`, with the reason, when the answer failed the validator or the call failed.
- **Claude's fixed output format:** one JSON object with exactly these five keys and nothing else.
  - `verdict`: `"relevant"` or `"not_relevant"`
  - `justification`: 1 to 3 sentences, at most 600 characters
  - `resume_fields`: at least one field path from the résumé sent, such as `"experience.full_time_years"`
  - `posting_fields`: at least one field from the posting fields sent, such as `"descriptionPlain"`
  - `quotes`: 0 to 3 excerpts copied word for word from the posting sent

  The validator rejects anything else: text that is not one JSON object, a missing or extra key, a verdict other than the two values, an empty justification or one over 600 characters, an empty `resume_fields` or `posting_fields`, a field that was not in what was sent, or a quote that does not appear word for word in the posting text sent (after collapsing runs of whitespace). There is no retry. A rejected answer is saved, and the verdict shows as `no valid judgment`.

## Refuses

1. **Any host not on the allow-list.** The fetch is refused before a connection opens, with an error naming the host, and nothing is fetched or saved. The same goes for `http://`, another port, and redirects.
2. **A real résumé, on screen or on GitHub.** The program accepts only a résumé that passes the persona checks under In. It never prints any résumé's name, email, phone or links, not even Jane's. A test scans every file in the repo and fails on any email address that does not end in `@example.com` (GitHub noreply addresses aside) and on any phone number outside 555-0100 to 555-0199. Runs on my real résumé come in a later version, from a private folder outside this repo.
3. **A model's judgment presented as a fact.** Claude's verdict always carries the label "Claude's judgment (model output, not verified)", sits in its own section, and is counted separately from the rule's.
4. **Acting for anyone.** It never applies, fills a form, emails or messages anyone, or logs in anywhere. It fetches only the board URL. It prints posting links but never opens them.
5. **Posting text as instructions.** Posting text is data. It is sent to Claude marked as data, Claude runs with no tools, no MCP servers and no saved session, and an answer that fails the validator is not used.
6. **Rewriting history.** It never deletes or edits a saved run. A run that fails partway leaves the state as it was.

## The rule

A posting is `relevant` only if it passes all seven checks, taken in this order. The first check it fails decides `not_relevant` and is the one cited. Matching ignores case. A "word" means a whole word, so `iOS` does not match "Studios".

1. **Employment type.** The posting's `employmentType` is one of résumé `preferences.employment_types`.
2. **Location.** At least one of the posting's locations (the primary one and each of `secondaryLocations`) fits. A location fits if its address (`address.postalAddress` for the primary location, the secondary location's own `address.postalAddress` otherwise) has country "United States" and its region (`addressRegion`) is in résumé `preferences.regions` or its city (`addressLocality`) is in `preferences.cities`, or if its location text is exactly one of `preferences.remote_locations`.
3. **Level.** The full title contains none of these words: Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished, Fellow, VP, Chief, Architect, Intern, Internship.
4. **Role.** The role part of the title (the text before the first comma, "|", "(", or hyphen, en dash or em dash with a space on each side) contains one of résumé `preferences.title_includes` and no word from `preferences.title_excludes`. Team names after the comma do not count, so "Full Stack Software Engineer, Sales Platform" passes.
5. **Status.** `descriptionPlain` contains none of these phrases:
   - when résumé `work_authorization.us_person` is false: "U.S. person", "US person", "U.S. citizen", "US citizen", "security clearance", "TS/SCI", "Top Secret", "green card", "permanent resident";
   - when résumé `work_authorization.needs_sponsorship` is true: "unable to sponsor", "not able to sponsor", "cannot sponsor", "will not sponsor", "does not sponsor", "do not sponsor", "no sponsorship", "without sponsorship", "sponsorship is not available".

   The word "sponsor" alone does not block ("executive technical sponsor"), and neither does "ITAR" alone (on this board it appears only as a skill, "ITAR/EAR"). A sentence containing "export control" that has none of the phrases above does not block either. If the posting is relevant, that sentence is shown as a quoted caution, for example "candidates for this role may need to meet certain legal status requirements".
6. **Start date.** `descriptionPlain` does not ask for a start before résumé `availability.earliest_full_time_start`: it contains none of "start immediately", "immediate start", "available immediately", "start ASAP", "start as soon as possible", and no sentence with the word "start" names a month and year earlier than that résumé date (May 2027 for Jane). A posting that says nothing about dates passes.
7. **Years of experience.** In `descriptionPlain`, look only at sentences (split at ". ", "! ", "? " and line breaks) that contain "experience", also inside a longer word such as "experienced". In them, find each number of years written as "N years", "N+ years", "N-M years" (hyphen or en dash), "N to M years" or "N or more years", with N in digits or as a word from one to ten. Take the smallest N found. The posting passes if N is at most résumé `experience.full_time_years`, or if no such sentence states years at all: stating no years is not a requirement. Upper bounds and months are not read.

**Worked example.** A real posting on the board on 2026-10-30, id `55150071-fce8-48f5-aea4-14ed78b83511`, "Software Engineer, Applied Emerging Talent (2027)":

1. FullTime: passes.
2. San Francisco, region California: passes.
3. No level word: passes.
4. Role part "Software Engineer", no excluded word: passes.
5. No status phrase: passes.
6. No start date: passes.
7. "0-1 years of experience in software engineering or a relevant field" gives N = 0, which is at most 3: passes.

Verdict: `relevant`.

## Wrong versions

Each one is a planted bug. The tests apply it to a copy of the code, and the test suite must fail.

1. **Saves seen ids too early.** Writes the new state before comparing against it, so every run after the baseline reports 0 new. Caught by: two saved responses where the second adds one posting; the second run must report exactly that posting as new.
2. **Any "sponsor" blocks.** Check 5 blocks whenever the text contains "sponsor". Caught by: a posting that contains the board's real sentence "You will serve as an executive technical sponsor for critical engagements" and no blocking phrase must stay relevant.
3. **Look-alike host passes.** The allow-list matches by substring, prefix or suffix. Caught by: `https://api.ashbyhq.com.evil.example/` and `https://notapi.ashbyhq.com/` must both be refused before any connection opens.
4. **Citation-free answer passes.** The validator accepts a Claude answer whose `resume_fields` or `posting_fields` is empty, or names a field that was not sent. Caught by: those answers must be rejected and shown as `no valid judgment`.

## What a failure looks like

2026-10-30: If Saturday's run lists as new any posting id already in Friday's saved response, or leaves out one that is not, this layer has failed.

## Where these choices come from

- **Decided on 2026-10-30, after checking how many of the board's 814 postings each option keeps:** the years rule (Jane has 3 years of work before her master's; up to 3 years passes, and a posting that states no years passes), the title lists (software engineering), all four wrong versions, and the failure sentence.
- **Decided earlier on 2026-10-30:** the board (OpenAI on Ashby, over Databricks after comparing both boards' counts); the persona Jane Doe, who is fictional and has my situation (F-1 student, not a U.S. person, needs H-1B sponsorship later, earliest full-time start May 2027, backend new grad, my locations) but none of my identity; Python standard library only; Claude through the Claude Code CLI with no API key.
- **Carried over from my Mode Build (2026-10-20):** an export-control sentence that says candidates "may need" to meet legal status requirements passes, with the quote shown.
- **Defaults I accepted:** contact fields never reach Claude; no retry on a rejected answer; the check order, the file names and the output format.
- **Board facts used above** come from one look at the live board on 2026-10-30, before the agent existed: 814 postings; "sponsor" never refers to visas; "ITAR" appears in one posting, as a skill; 25 postings carry the export-control sentence. That copy is not in this repo.
