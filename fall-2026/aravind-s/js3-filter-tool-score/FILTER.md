# FILTER.md: what reaches Jane, and why

Job-Search Agent 3 (INFO 7375). **Version 1.0, 2026-11-20.** Written before any JS3 code: this file's commit comes
before every JS3 code commit in `git log`. Later versions are added below with their dates; version 1.0 is never
edited.

**Who wrote what.**
- **Section 1 (the filter: rules R1 to R8, the topic words and the ranking) is mine.** I wrote it in four drafts
  on 2026-11-20. After each draft, Claude Code checked my rules against the code and the saved postings and
  told me what was wrong or unclear, and I rewrote it. The four drafts are kept word for word in
  [`filter-drafts/`](filter-drafts/). Section 1 below copies my lines; only the headings were made uniform.
- **Sections 2 to 7 were drafted by Claude Code** from my Section 1 decisions, the JS3 brief and chapter 7 of the
  book, because I asked it to decide the rest itself ("decide yourself whatever is best for this agent",
  2026-11-20). Section 6 lists the implementation choices Claude Code made for me.

## Section 1: The filter (mine)

My goal is to find software engineering and backend jobs that are a good match for Jane. I want the filter to consider her experience, location, work authorization and availability. I also want to avoid throwing away good opportunities just because a job title or description uses slightly different wording. Clear mismatches should be rejected, while less certain matches should stay in the results with an explanation.

### The rules

#### R1: Employment Type (CHANGE, Hard)

Check the employment type field. Keep only `FullTime`. Reject every other stated value, including `Intern`, `Intern/Co-op`, `Full Time - Fixed Term Employment`, `Fixed-Term`, `Contract` and `Scholarship`. If the employment type is missing, keep the posting but mark it as "cannot tell" and subtract 10 points from its score. I want to keep this rule strict because Jane is looking for a full-time position. None of today's 1,508 postings had a missing employment type, so the missing-value case still needs testing.

#### R2: Location (CHANGE, Hard and Soft)

Check the main location, secondary locations and structured address fields. One matching location is enough. If at least one location matches Jane's preferred US locations (California, Austin, Boston, Cambridge, New York, Seattle, Bellevue and Redmond) or US remote, keep the posting without a penalty. If the locations are in the US but outside her preferred areas, keep the posting and subtract 15 points. Reject postings when all available locations are outside the US because Jane's OPT work authorization only allows her to work in the US. If the location is missing or unclear, mark it as "cannot tell" and subtract 10 points. Do not use the job description to determine location. Today, 9 postings were rejected for being outside the US, and none of the other 99 fell into the other-US or unclear categories, so those soft cases still need testing.

#### R3: Job Level (KEEP, Hard)

Check the job title for these 15 exact words: Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished, Fellow, VP, Chief, Architect, Intern and Internship. Match complete words, not parts of other words. Reject a posting when one of these words appears in the title. I am keeping this as a hard rule because Jane has three years of experience and is looking for an appropriate early-career position. Titles such as Principal Software Engineer, Senior Staff Software Engineer and Engineering Manager are above the level she is targeting.

#### R4: Job Role (CHANGE, Hard)

Check only the job title, using the role part before the first comma, pipe, parenthesis or spaced hyphen.
Included phrases (12):

1. Software Engineer
2. Software Developer
3. Backend Engineer
4. Back-end Engineer
5. Full Stack Engineer
6. Full-Stack Engineer
7. Infrastructure Engineer
8. Platform Engineer
9. Data Engineer
10. Reliability Engineer
11. Machine Learning Engineer
12. ML Engineer

Excluded phrases (17):

1. Frontend
2. Front-end
3. Android
4. iOS
5. Mobile
6. Firmware
7. Hardware
8. Embedded
9. Camera
10. Robotics
11. Research
12. Security
13. Forward Deployed
14. Solutions
15. Support
16. Sales
17. Network

Full Stack Engineer and Full-Stack Engineer remain included. I am adding Machine Learning Engineer and ML Engineer because they are genuine engineering roles involving building software and technical systems. Machine Learning and ML alone are no longer excluded. Match complete words and phrases so that Data Engineer does not accidentally match Data Engineering Manager. The level check will still reject management positions.

#### R5: Work Authorization and Sponsorship (KEEP, Hard)

Check the job description for requirements involving US citizenship, security clearance or statements that the company cannot provide sponsorship. Reject a job when its requirements clearly conflict with Jane's situation. Jane is an F-1 student, is not a US person and will need H-1B sponsorship in the future. However, when a posting does not mention sponsorship, keep it rather than assuming that the company will not sponsor.

#### R6: Start Date (CHANGE, Hard)

Check the job description for a required start date. Reject positions that clearly require someone to start before May 2027. Also reject postings containing any of these exact phrases: "start immediately", "immediate start", "available immediately", "start ASAP", and "start as soon as possible". Keep postings where no start date is mentioned. Recognize abbreviated dates such as "Dec. 2026". If the date is unclear, keep the posting, mark it as "cannot tell" and subtract 10 points from its score. Jane cannot begin full-time work before May 2027, so an earlier required start date makes the job unsuitable.

#### R7: Years of Experience (CHANGE, Hard)

Check every sentence in the job description containing a number of years, even when the word "experience" is not included. Recognize numbers written as "N years", "N+ years", "N-M years", "N to M years" and "N or more years". Ignore numbers followed by "ago" and numbers preceded by "next".
Treat a sentence about the candidate's years of experience as a requirement by default. Only clear optional phrases excuse it: "is a plus", "a plus", "preferred", "preferably", "nice to have", "bonus", "desired" and "desirable". This means that an unmarked sentence such as "5+ years of software engineering experience" is still treated as required, even without the words "required" or "minimum".
For Jane's three years of experience, "3-5 years" and "3+ years" both pass because the minimum is three. A requirement of four or more years fails. Optional experience requirements do not cause rejection. Ignore sentences that clearly describe company growth or something unrelated to the candidate's experience.
If it is unclear whether the number refers to the candidate's experience or something else, mark it as "cannot tell" and subtract 10 points. If the minimum is three years or less, allow it to pass even when the wording is unclear because it does not exceed Jane's experience limit.

#### R8: AI Training and Data Annotation (ADD, Hard)

Check job titles for these exact phrases: AI Trainer, Data Annotator, Data Annotation Specialist, Data Labeler, Data Labeling Specialist, AI Rater, Model Rater and RLHF Annotator. Also check the description for sentences containing a clear main-responsibility phrase such as "primary responsibility", "main responsibility", "day-to-day work" or "most of your time", together with tasks such as "label data", "data labeling", "annotate examples", "data annotation", "rate AI responses" or "rate model outputs". Reject these postings because their main work is data labeling or rating rather than engineering. Do not reject genuine engineering roles involving machine learning systems, model development, training pipelines or AI evaluation tools. None of today's 1,508 postings matched these title phrases, but I want to keep this rule for future boards.

### Topic words: description-based ranking signals

Search the job description for these exact words and phrases. To receive points, a topic word and at least one of the following action words must appear in the same sentence:
Exact action words: build, builds, building, built, develop, develops, developing, developed, design, designs, designing, designed, implement, implements, implementing, implemented, maintain, maintains, maintaining, maintained, operate, operates, operating, operated.

* Backend: backend, back-end, server-side, server side. Do not match general back-office work.
* APIs: API, APIs, REST, RESTful, GraphQL, gRPC, endpoints. Match REST only when it appears in uppercase, so the ordinary word "rest" does not count.
* Distributed systems: distributed systems, distributed services, event-driven architecture, message queues, Kafka. Do not match references to employees working in different locations.
* Databases: SQL, PostgreSQL, MySQL, MongoDB, Redis, database schema, query optimization. Do not match general customer database or data-entry references.
* Cloud infrastructure: AWS, Amazon Web Services, GCP, Google Cloud, Azure, Kubernetes, Docker, Terraform, cloud infrastructure. Do not match general cloud-storage references.
* Microservices: microservice, microservices, service-oriented architecture. Do not match unrelated customer services.
* Developer tools: developer tools, developer platform, internal developer platform, SDK, CLI, build systems, CI/CD, developer experience. Do not match general business platforms.

Each topic group can add points only once, even if its words appear several times. I will use the reject audit to check whether these matches actually represent engineering work or whether some words are being matched for the wrong reason.

### How the ranking works

Every posting that passes the hard rules starts with 50 points.

* Add 5 points for each different technical topic group found in the description.
* Topic points are capped at 25.
* Subtract 15 points for US locations outside Jane's preferred areas.
* Subtract 10 points for a missing or unclear location.
* Subtract 10 points for a missing employment type.
* Subtract 10 points when the start date is "cannot tell".
* Subtract 10 points when the years of experience are "cannot tell".

A posting marked "cannot tell" is not automatically rejected. It stays in the results with a lower score so it can still be reviewed.
The minimum shortlist score is 60 points. This means a posting needs at least two different technical topic groups to reach the cutoff when there are no penalties. I chose this cutoff because I want the shortlist to contain jobs with a clear technical match rather than postings that only pass the basic requirements.
The agent will select the top 10 distinct postings that meet the minimum score. If the same company lists the same job title more than once, count it only once. To identify duplicates, convert the company name and job title to lowercase, remove extra spaces and compare them. Keep the newest posting when duplicates are found.
Sort by score from highest to lowest. If two postings have the same score, put the newest posting first. If the dates are also the same, sort by posting ID in alphabetical order. If a posting date is missing, treat it as older than postings with known dates.
These starting weights and the cutoff are hand-set for version 1.0. They are not trained or fitted using model data. I will use the reject audit and held-out labels to decide whether the weights, cutoff or shortlist size need to change.

### Note on counts and testing

The earlier counts were produced by Claude Code's scratch script using the second draft of these rules on saved run `2026-11-20T113915Z`. The third draft changes some of the rules, so those counts should not be treated as final results. I will use the built filter to calculate the actual counts and record them after testing.

## Section 2: The evidence rules (drafted by Claude Code)

The shortlist gives a reason for each posting it keeps. The reason is split into **claims**: one small statement
each, which a single passage of the posting can settle (a claim with "and" in it is split in two, chapter 7). Every
claim gets a quote from the posting's own saved text (title, location fields, employment type field or
description) and one label:

- **Supported:** a quoted passage of the posting states the claim, within its scope: the same role, the same
  place, the same time. The quote must appear word for word in the saved posting.
- **Contradicted:** a quoted passage of the posting states something that cannot be true at the same time as the
  claim. Example of the shape: the claim "asks for 3 years or fewer" against a passage "5+ years of software
  engineering experience".
- **Insufficient:** the closest passage is on the topic but does not settle the claim, and the row names what is
  missing. Silence is never support: a posting that does not mention sponsorship makes the claim "does not rule
  out sponsorship" insufficient, not supported (R5 keeps such postings, but the shortlist must not say more than
  the text does).
- **Not reviewed:** nobody has read the posting for this claim yet.

**Who may mark a claim supported:** only Aravind, after reading the posting. A rule-based checker labels every
claim first, and its labels are committed before Aravind labels; they are a second opinion, never the answer.

**When the agent must say "I cannot tell"** instead of answering:
1. **For a whole posting:** when the posting has no title or no description text. It gets no relevance verdict,
   it is listed with its reason, and it is never shortlisted. The rest of its board is still read.
2. **For one rule:** when R1, R2, R6 or R7 cannot decide (a missing employment type or location, an unclear start
   date, an unclear years sentence). Section 1 keeps such a posting and subtracts 10 points.
3. **For one claim:** when the claim's label is insufficient. The shortlist shows "I cannot tell" for that claim
   instead of a yes.

## Section 3: The expected sources (drafted by Claude Code)

Dated 2026-11-20, before the next run.

| Board | System and public endpoint | Why it is allowed | Postings expected at the next run |
|---|---|---|---|
| OpenAI | Ashby posting API, `api.ashbyhq.com/posting-api/job-board/openai` | public, no login, in GATE.md's allow-list | 830 to 880 (811 on 11/9, 854 on 11/20) |
| Verkada | Greenhouse board API, `boards-api.greenhouse.io/v1/boards/verkada/jobs` | public, no login, allow-listed | 330 to 365 (342, then 348) |
| Palantir | Lever postings API, `api.lever.co/v0/postings/palantir` | public, no login, allow-listed | 290 to 325 (304, then 307) |
| made-up board | Greenhouse, a board name that does not exist | fails on purpose (JS2) | HTTP 404, 0 postings, "unverified" |

**Fields the filter reads** (the agent maps all three systems to the same names): `id`, `title`, `location`,
`secondaryLocations` and the structured `address`, `employmentType`, `descriptionPlain`, `publishedAt`, `jobUrl`.
Jane's own facts (preferred locations, years of experience, earliest start, work authorization) come from
`persona/jane-doe.json`.

**What the agent answers when something is missing:**
- **A board that fails** (an HTTP error, a timeout, an answer that is not the expected JSON): the board is
  "unverified", nothing about it is judged, its saved state is kept, and the other boards are still read.
- **A posting with no title** (OpenAI's posting `1ae64ddb-505f-4ad2-a731-3a857e94edee` on 2026-11-20): that one
  posting is "I cannot tell"; the rest of the board is read. This changes JS2, which refused the whole board, so
  853 OpenAI postings went unread on 2026-11-20.
- **A posting with no description:** "I cannot tell" for the posting, since R5 to R8 and the topic words read the
  description.
- **No location or no employment type:** as Section 1 says ("cannot tell", minus 10 points).
- **No publication date:** treated as older than every dated posting (Section 1's tie rule).

## Section 4: Wrong versions the tests must catch (drafted by Claude Code)

Each wrong version is planted into a copy of the code as a deliberate mistake, and at least one test must fail
on it. If a wrong version survives, the tests are not finished.

| # | The wrong version | Why it is wrong | The test that must catch it |
|---|---|---|---|
| W1 | Role phrases match inside longer words (JS2's way) | "Data Engineer" matches "Data Engineering Manager" | that title, with no level word, must fail R4 |
| W2 | Years read only in sentences that say "experience" (contract v0.1) | misses "5+ years in one or more of: ML systems, ..." (posting 19) | that sentence must reject under R7 |
| W3 | Optional years treated as required (contract v0.2) | "5+ years of Go is a plus" rejects a posting R7 keeps | that sentence must pass R7 |
| W4 | One broken posting refuses its whole board (JS2 on 2026-11-20) | an empty title hides every other posting | a board answer with one empty-title posting must still return the others |
| W5 | Ties broken by the order postings arrive | the top 10 changes when the board reorders its list | the same postings in two orders must give the same top 10 |
| W6 | "REST" matched in any case | the word "rest" earns API points | a sentence "we build the rest of the platform" must earn no API points |
| W7 | Every location outside Jane's areas rejected (JS2's way) | a US posting outside her areas is kept by R2 with minus 15 | a Washington, D.C. posting must be kept with 15 points off |

## Section 5: The failure sentence, what this filter may claim, and the shortlist's claims (drafted by Claude Code)

**What a failure looks like (2026-11-20, before the build).** Written from Aravind's own worry in his first
draft, "I don't want to miss a potentially good opportunity": *If the reject audit finds a full-time, US,
early-career software posting that Jane meets, rejected because of a level word, a role phrase or a years
sentence the posting itself marks as optional, this filter has failed in the way that matters most.*

**What this filter may claim:** a ranking of the postings on three watched boards, on one day, by Jane's written
rules over each posting's saved text. **It may not claim** that a posting is right for Jane, that it is still open,
that the company sponsors visas, or that the list is complete (boards it does not watch, and postings its rules
wrongly reject, are both outside it).

**The claims a shortlist reason may make**, one small question each:
1. The posting is full time (R1).
2. It is in one of Jane's areas, or US remote (R2).
3. Its title has no level word (R3).
4. Its title names a software engineering role (R4).
5. It states no U.S.-person, clearance or no-sponsorship requirement (R5).
6. It requires no start before May 2027 (R6).
7. It asks for 3 years or fewer, or makes more years optional (R7).
8. It describes work in a given topic group, one claim per group that earned points.

**The abstention rule and its counterexamples.** The posting-level rule in Section 2 (no title, or no
description) is narrow on purpose.
- **A case it wrongly lets through:** a posting with a title and a long description that is mostly the company's
  standard text. The rule does not fire, yet its years and start claims all come out insufficient, and it can still
  rank high from topic words in an "about us" sentence such as "We build infrastructure for ...". The claim labels
  catch it; the abstention rule does not.
- **A case a stricter rule would wrongly refuse:** abstaining whenever the description is short (say, under 150
  words) would refuse a brief posting that states the role, the city, full time and "0 to 2 years" in a few lines,
  though every claim about it is supported.

## Section 6: Implementation choices (made by Claude Code, at Aravind's request)

1. **Sentences.** The agent's sentence splitter is kept (". ", "! ", "? ", line breaks), except that it no longer
   splits after a month abbreviation followed by a year, so "Dec. 2026" stays one date (R6; JS1's open gap).
2. **R6.** A sentence with the whole word "start" and a month and year before May 2027 rejects, as in contract
   v0.2. A sentence with "start" and a season or quarter word followed by a year, but no month ("Spring 2027",
   "early 2027", "Q1 2027"), is "cannot tell", unless that season or quarter lies wholly after May 2027 (summer,
   fall or autumn, Q3 or Q4 of 2027, or any season of 2028 or later). The five start phrases are matched
   anywhere in the description.
3. **R7.** In a range the smallest number is the minimum ("3-5 years" asks 3). Number words one to ten count. A
   years sentence counts as being about the company, not the candidate, when it contains one of: grew, grown,
   growth, founded, revenue, customers, history. Such a sentence passes if its number is 3 or less, and is
   "cannot tell" if it is more.
4. **R5.** The phrase lists are inherited unchanged from contract v0.2, check 5 (in Section 7). A sentence with
   "export control" stays a caution shown in the shortlist, not a reason to reject (Aravind's choice of 2026-10-20).
5. **R2.** A location is in the US when its structured address says United States, or else when its text has a US
   state code or "United States", "USA" or "US". "US remote" is one of Jane's remote phrases, or a Lever posting
   marked remote with country US (GATE.md). "Unclear" means no location field names a US place or another country
   (for example a bare "Remote").
6. **Topic words** match as whole words, ignoring case, except "REST", which must be uppercase. A group counts
   once per posting.
7. **Duplicates.** The company is the board. The normalized title is the title lowercased, with runs of spaces made
   one space. The newest copy is kept (a missing date counts as oldest), then the lower posting id.
8. **Where the program reads the rules.** Every word list and number above is read by the program from Section 7
   of this file. A test checks that Section 7 holds exactly the lists written in Section 1. Jane's facts are read
   from `persona/jane-doe.json`.
9. **"Everything the agent collected"** (for the reject audit) means the newest saved answer of each board when
   the audit runs. Older answers stay as evidence but are not filtered again, so each posting is judged once.

## Section 7: The machine-readable copy (written by Claude Code)

```json
{
  "version": "1.0",
  "date": "2026-11-20",
  "employment_type_keep": ["FullTime"],
  "level_words": ["Senior", "Sr", "Staff", "Principal", "Lead", "Manager", "Director", "Head", "Distinguished",
                  "Fellow", "VP", "Chief", "Architect", "Intern", "Internship"],
  "role_includes": ["Software Engineer", "Software Developer", "Backend Engineer", "Back-end Engineer",
                    "Full Stack Engineer", "Full-Stack Engineer", "Infrastructure Engineer", "Platform Engineer",
                    "Data Engineer", "Reliability Engineer", "Machine Learning Engineer", "ML Engineer"],
  "role_excludes": ["Frontend", "Front-end", "Android", "iOS", "Mobile", "Firmware", "Hardware", "Embedded",
                    "Camera", "Robotics", "Research", "Security", "Forward Deployed", "Solutions", "Support",
                    "Sales", "Network"],
  "status_us_person_phrases": ["U.S. person", "US person", "U.S. citizen", "US citizen", "security clearance",
                               "TS/SCI", "Top Secret", "green card", "permanent resident"],
  "status_sponsorship_phrases": ["unable to sponsor", "not able to sponsor", "cannot sponsor", "will not sponsor",
                                 "does not sponsor", "do not sponsor", "no sponsorship", "without sponsorship",
                                 "sponsorship is not available"],
  "caution_phrase": "export control",
  "start_phrases": ["start immediately", "immediate start", "available immediately", "start ASAP",
                    "start as soon as possible"],
  "start_unclear_words": ["spring", "summer", "fall", "autumn", "winter", "early", "mid", "late",
                          "Q1", "Q2", "Q3", "Q4"],
  "years_optional_phrases": ["is a plus", "a plus", "preferred", "preferably", "nice to have", "bonus", "desired",
                             "desirable"],
  "years_company_words": ["grew", "grown", "growth", "founded", "revenue", "customers", "history"],
  "years_max": 3,
  "action_words": ["build", "builds", "building", "built", "develop", "develops", "developing", "developed",
                   "design", "designs", "designing", "designed", "implement", "implements", "implementing",
                   "implemented", "maintain", "maintains", "maintaining", "maintained", "operate", "operates",
                   "operating", "operated"],
  "topic_groups": {
    "Backend": ["backend", "back-end", "server-side", "server side"],
    "APIs": ["API", "APIs", "REST", "RESTful", "GraphQL", "gRPC", "endpoints"],
    "Distributed systems": ["distributed systems", "distributed services", "event-driven architecture",
                            "message queues", "Kafka"],
    "Databases": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "database schema", "query optimization"],
    "Cloud infrastructure": ["AWS", "Amazon Web Services", "GCP", "Google Cloud", "Azure", "Kubernetes", "Docker",
                             "Terraform", "cloud infrastructure"],
    "Microservices": ["microservice", "microservices", "service-oriented architecture"],
    "Developer tools": ["developer tools", "developer platform", "internal developer platform", "SDK", "CLI",
                        "build systems", "CI/CD", "developer experience"]
  },
  "case_sensitive_words": ["REST"],
  "annotation_titles": ["AI Trainer", "Data Annotator", "Data Annotation Specialist", "Data Labeler",
                        "Data Labeling Specialist", "AI Rater", "Model Rater", "RLHF Annotator"],
  "annotation_responsibility_phrases": ["primary responsibility", "main responsibility", "day-to-day work",
                                        "most of your time"],
  "annotation_task_phrases": ["label data", "data labeling", "annotate examples", "data annotation",
                              "rate AI responses", "rate model outputs"],
  "ranking": {"start": 50, "per_topic_group": 5, "topic_cap": 25, "other_us_location": -15,
              "location_cannot_tell": -10, "employment_type_cannot_tell": -10, "start_cannot_tell": -10,
              "years_cannot_tell": -10, "shortlist_min": 60, "shortlist_size": 10}
}
```

## Version 1.1, 2026-11-22

Added after the reject audit, the claim labels and the held-out measurement (`js3/score/`). Version 1.0 above is not
edited. The filter command reads the newest Section 7 (the one below); the v1.0 filter run, the three kits, the
held-out experiments and the MCP server stay on version 1.0, the version they were built, measured or evaluated with.

**Aravind's changes** (his decisions of 2026-11-22, made from the audit and the held-out measurement, so the held-out
set is development data from now on):
1. **The shortlist cutoff is 50, not 60.** Every posting that passes the hard rules qualifies, and the score only
   orders them. Why: in the audit he kept every kept posting he judged, at 50, 55 and 60 alike, and on the held-out set
   a cutoff of 50 agreed with all 27 of his verdicts (60: 22 of 27).
2. **An export-control line costs 10 points.** It still never rejects, and it is still shown as a caution. Why: all
   six of his "?" verdicts were over that line or over clearance; the posting does not say whether Jane may take the
   job, so it ranks lower.
3. **"build systems" is no longer a Developer tools word.** Why: on shortlisted posting 09 it matched "build systems
   that consume and operationalize ML-based signals", a verb and a noun, and he labeled that claim insufficient (09.8c).

**Claude Code's implementation changes** (Section 6):
4. **Item 1:** the splitter no longer ends a sentence after "U.S.", "e.g." or "i.e.". Why: the cut hid "U.S. Person
   Required" from audit card 17, and R5's quote fell back to the bare phrase.
5. **Item 3:** the company words are grew, grown, founded and history; growth, revenue and customers are dropped. Why:
   they fired 77 times in the run, each time on a real requirement for the candidate (audit card 34 among them).

**Written down, not changed in behavior** (FILTER-CHANGES-PENDING.md):
6. `years_max` is Jane's value from her profile (3 years); Section 7 keeps it only as a copy the tests compare.
7. Posting dates come from Ashby's `publishedAt`, Greenhouse's `first_published` (else `updated_at`) and Lever's
   `createdAt`, read as UTC.
8. A posting with no id leaves its board unverified. When several hard rules fail, the deciding one is the first in
   the order R1 to R8.

**Not in 1.1:** a season wholly before the earliest start rejecting (item 2), and every US location that says remote
counting as US remote (item 4). Neither fired on any of the 1,509 postings, so the run gives no evidence either way;
they wait for a version with postings that test them. The shortlist's wording for claims 5 to 7 ("the posting does
not say", `js3/claims/2026-11-21T044414Z/ABSTENTION.md`) is not built yet.

## Section 7, version 1.1: the machine-readable copy (written by Claude Code)

The same as version 1.0's Section 7 except `version`, `date`, `splitter_keeps`, `years_company_words`, the Developer
tools group, `ranking.shortlist_min` and `ranking.caution_penalty` (a test checks that nothing else differs).

```json
{
  "version": "1.1",
  "date": "2026-11-22",
  "employment_type_keep": [
    "FullTime"
  ],
  "level_words": [
    "Senior",
    "Sr",
    "Staff",
    "Principal",
    "Lead",
    "Manager",
    "Director",
    "Head",
    "Distinguished",
    "Fellow",
    "VP",
    "Chief",
    "Architect",
    "Intern",
    "Internship"
  ],
  "role_includes": [
    "Software Engineer",
    "Software Developer",
    "Backend Engineer",
    "Back-end Engineer",
    "Full Stack Engineer",
    "Full-Stack Engineer",
    "Infrastructure Engineer",
    "Platform Engineer",
    "Data Engineer",
    "Reliability Engineer",
    "Machine Learning Engineer",
    "ML Engineer"
  ],
  "role_excludes": [
    "Frontend",
    "Front-end",
    "Android",
    "iOS",
    "Mobile",
    "Firmware",
    "Hardware",
    "Embedded",
    "Camera",
    "Robotics",
    "Research",
    "Security",
    "Forward Deployed",
    "Solutions",
    "Support",
    "Sales",
    "Network"
  ],
  "status_us_person_phrases": [
    "U.S. person",
    "US person",
    "U.S. citizen",
    "US citizen",
    "security clearance",
    "TS/SCI",
    "Top Secret",
    "green card",
    "permanent resident"
  ],
  "status_sponsorship_phrases": [
    "unable to sponsor",
    "not able to sponsor",
    "cannot sponsor",
    "will not sponsor",
    "does not sponsor",
    "do not sponsor",
    "no sponsorship",
    "without sponsorship",
    "sponsorship is not available"
  ],
  "caution_phrase": "export control",
  "start_phrases": [
    "start immediately",
    "immediate start",
    "available immediately",
    "start ASAP",
    "start as soon as possible"
  ],
  "start_unclear_words": [
    "spring",
    "summer",
    "fall",
    "autumn",
    "winter",
    "early",
    "mid",
    "late",
    "Q1",
    "Q2",
    "Q3",
    "Q4"
  ],
  "years_optional_phrases": [
    "is a plus",
    "a plus",
    "preferred",
    "preferably",
    "nice to have",
    "bonus",
    "desired",
    "desirable"
  ],
  "years_company_words": [
    "grew",
    "grown",
    "founded",
    "history"
  ],
  "years_max": 3,
  "action_words": [
    "build",
    "builds",
    "building",
    "built",
    "develop",
    "develops",
    "developing",
    "developed",
    "design",
    "designs",
    "designing",
    "designed",
    "implement",
    "implements",
    "implementing",
    "implemented",
    "maintain",
    "maintains",
    "maintaining",
    "maintained",
    "operate",
    "operates",
    "operating",
    "operated"
  ],
  "topic_groups": {
    "Backend": [
      "backend",
      "back-end",
      "server-side",
      "server side"
    ],
    "APIs": [
      "API",
      "APIs",
      "REST",
      "RESTful",
      "GraphQL",
      "gRPC",
      "endpoints"
    ],
    "Distributed systems": [
      "distributed systems",
      "distributed services",
      "event-driven architecture",
      "message queues",
      "Kafka"
    ],
    "Databases": [
      "SQL",
      "PostgreSQL",
      "MySQL",
      "MongoDB",
      "Redis",
      "database schema",
      "query optimization"
    ],
    "Cloud infrastructure": [
      "AWS",
      "Amazon Web Services",
      "GCP",
      "Google Cloud",
      "Azure",
      "Kubernetes",
      "Docker",
      "Terraform",
      "cloud infrastructure"
    ],
    "Microservices": [
      "microservice",
      "microservices",
      "service-oriented architecture"
    ],
    "Developer tools": [
      "developer tools",
      "developer platform",
      "internal developer platform",
      "SDK",
      "CLI",
      "CI/CD",
      "developer experience"
    ]
  },
  "case_sensitive_words": [
    "REST"
  ],
  "annotation_titles": [
    "AI Trainer",
    "Data Annotator",
    "Data Annotation Specialist",
    "Data Labeler",
    "Data Labeling Specialist",
    "AI Rater",
    "Model Rater",
    "RLHF Annotator"
  ],
  "annotation_responsibility_phrases": [
    "primary responsibility",
    "main responsibility",
    "day-to-day work",
    "most of your time"
  ],
  "annotation_task_phrases": [
    "label data",
    "data labeling",
    "annotate examples",
    "data annotation",
    "rate AI responses",
    "rate model outputs"
  ],
  "ranking": {
    "start": 50,
    "per_topic_group": 5,
    "topic_cap": 25,
    "other_us_location": -15,
    "location_cannot_tell": -10,
    "employment_type_cannot_tell": -10,
    "start_cannot_tell": -10,
    "years_cannot_tell": -10,
    "shortlist_min": 50,
    "shortlist_size": 10,
    "caution_penalty": -10
  },
  "splitter_keeps": [
    "U.S.",
    "e.g.",
    "i.e."
  ]
}
```

## Changelog

- **1.0, 2026-11-20:** first version, written before the JS3 build.
- **1.1, 2026-11-22:** cutoff 50, an export-control line costs 10 points, "build systems" dropped (Aravind's
  calls); the splitter keeps "U.S.", "e.g." and "i.e.", and three company words are dropped (Claude Code's). See
  "Version 1.1" above.
