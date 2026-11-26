# CONTRACT.md — Job Search Agent

**Written:** October 29, 2026  
**Persona:** Kiran Joshi (fictional)  
**Board:** Stripe on Greenhouse

## What this agent does

This agent checks one public job board, remembers which posting IDs it has already seen, and evaluates newly discovered jobs against Kiran Joshi's fictional resume. It produces a rule-based result and a separate Claude judgment. The two results must stay separate: the rule is reproducible, while Claude's answer is an opinion based on the available text.

The agent is for job discovery only. It will not apply for jobs, contact employers, log in to job sites, or claim that a job is a guaranteed fit.

## 1. Persona and resume

Kiran Joshi is a fictional early-career software engineer. The supplied resume says `"fictional": true`; the names, employers, schools, dates, projects, and contact details are invented. The agent uses the exact fixture at:

`persona/kiran-joshi.resume.example.json`

Kiran's target roles are Software Engineer, Full-Stack Software Engineer, Backend Engineer, and Frontend Engineer. The target levels are New Grad, Entry Level, SWE I, and SWE II. The resume includes professional and project experience with TypeScript, JavaScript, Java, Python, SQL, C#, React, Next.js, Node.js, Express, Spring Boot, PostgreSQL, MongoDB, Redis, Elasticsearch, RabbitMQ, Kafka, AWS, GCP, Docker, Kubernetes, GitHub Actions, Sentry, Prometheus, and Grafana. Go and Terraform are explicitly listed as familiar with but not shipped, so they do not count toward the primary skill threshold.

## 2. Board

I am using Stripe's public Greenhouse board.

- Board identifier: `stripe`
- Public board: `https://boards.greenhouse.io/stripe`
- API endpoint: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
- Automated job-board host: `boards-api.greenhouse.io`

I chose Stripe because the title and skill rule has a mix of matches and non-matches on this board, making it possible to test both outcomes. The board changes over time, so the agent must use the response it actually fetches and must not hard-code a posting count.

Stripe does not always include the word “Senior” in titles. Therefore, the title filter will not catch every senior-level job. This is a known limitation; the agent must not claim that every returned match is definitely entry-level.

## 3. Inputs and requirements

The agent needs:

1. Board identifier `stripe`.
2. The approved resume fixture at `persona/kiran-joshi.resume.example.json`.
3. A local state file holding previously seen posting IDs and any pending model judgments.
4. HTTPS network access to the Greenhouse API.
5. A Claude subscription and an officially supported way to use it from the environment, such as Claude Code if available.

A Claude subscription is not the same as Anthropic API access and does not automatically provide an API key. The contract does not require an Anthropic API key. If the subscription cannot be used through an officially supported interface in this environment, the rule step still runs and the model judgment is marked unavailable; the agent must not pretend a model call happened.

The resume path and state path should be configurable. The state file must be stored inside the configured project data directory. The agent must validate the resume before sending any resume content to a model.

## 4. resume fields used by the rule

The rule reads these resume JSON paths:

- `$.target.roles[*]`
- `$.target.levels[*]`
- `$.target.locations[*]`
- `$.target.excluded[*]`
- `$.skills.languages[*]`
- `$.skills.frontend[*]`
- `$.skills.backend[*]`
- `$.skills.data[*]`
- `$.skills.messaging[*]`
- `$.skills.cloud_devops[*]`
- `$.skills.observability[*]`

`$.target.locations[*]` ("United States", "Remote (US)") is applied as a hard geographic constraint: only postings whose location is established as US-based may receive `MATCH` (§6.4). The rule does not count `$.skills.familiar_with_not_shipped[*]`.

The rule does not use the persona's name, contact details, school names, employer names, or dates as matching signals. Claude may use Kiran's experience and project bullets for its qualitative judgment, but those fields do not alter the rule verdict.

The target role phrases are taken from `$.target.roles[*]`, not from a separate hard-coded role list. The implementation may use documented aliases for common title variants, as defined below.

## 5. Posting fields used by the agent

The agent reads these fields from the Greenhouse response:

- `id` — stable posting identifier used for deduplication
- `title` — role-title check
- `location.name` — primary location field; used to establish whether the role is US-based (§6.4)
- `updated_at` — metadata only; it does not decide whether a posting is new
- `content` — job description and requirements
- `departments[*].name` — additional text, if present

The request uses `?content=true`. I inspected a raw response on October 29, 2026 (`evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json`) and confirmed the shape: a top-level object with a `jobs` array and a `meta.total` count. A missing optional field contributes an empty value. A missing or invalid posting ID is a data-quality error and must be reported rather than replaced with an invented ID.

Greenhouse's `content` field contains HTML that has been escaped into text. Before matching, the agent must decode HTML entities, strip HTML tags, decode any remaining entities, and normalize whitespace. Matching still cites the original source path, such as `$.content`; it must not invent a JSON path for the cleaned text. The cleaned text is only an in-memory representation used for matching. Posting paths in records are relative to the posting object (`$.content`); hand checks also give the posting's position in the raw response (`$.jobs[566]`).

## 6. Deterministic rule

I want a classmate to be able to apply this rule by hand and reach the same result.

### 6.1 Title check

The title is lowercased and trimmed. The following title aliases count as the same role family:

- `software engineer` matches the role `Software Engineer`
- `full-stack`, `full stack`, and `fullstack` match `Full-Stack Software Engineer`
- `backend`, `back-end`, and `back end` match `Backend Engineer`
- `frontend`, `front-end`, and `front end` match `Frontend Engineer`

The title must contain both the role family and the word `engineer` (or a documented equivalent title phrase): `software engineer`, `full-stack engineer`, `backend engineer`, or `frontend engineer`. The aliases only normalize the family word, not the job itself: `backend`, `back-end`, or `back end` count only in a title phrase such as `Backend Engineer`, `Back-End Software Engineer`, or `Back End Engineer`; `frontend`, `front-end`, and `front end` count only in phrases such as `Frontend Engineer`, `Front-End Software Engineer`, or `Front End Engineer`. `Backend Data Analyst` and `Frontend Designer` do not pass. “Software Engineering” by itself does not count as “Software Engineer.” “Software Engineering Internship” is excluded. The word `intern` and the word `internship` both cause rejection.

The title exclusions implement the intent of `$.target.levels[*]` and `$.target.excluded[*]`: they are a fixed, documented interpretation of those fields for this version, not a runtime parser that dynamically converts every phrase in those arrays into a new rule. The title is rejected if it contains any of these markers as a whole word or defined abbreviation: `senior`, `sr`, `sr.`, `staff`, `principal`, `lead`, `manager`, `director`, `intern`, `internship`, `III`, `IV`, `L3`, or `L4`. `SWE I` and `SWE II` are allowed. Because Kiran's listed target levels stop at SWE II, titles marked III, IV, L3, or L4 are excluded. This is a simple title heuristic and will miss senior jobs whose titles omit a seniority marker.

### 6.2 Skill check and special cases

The eligible skill set comes from the resume skill paths in section 4. Each distinct skill counts at most once, no matter how many times it appears in the posting. Matching is case-insensitive unless a special case below says otherwise. Skills are searched in the posting title, cleaned content, and department names.

The agent must decode escaped HTML and strip tags before searching. It must not treat punctuation removal as the only normalization rule, because that would make `C#` become a stray `c` and create false matches.

Use these matching rules:

- `C#` matches the exact token `C#`; it must not match the letter `c` by itself.
- `Node.js` matches `Node.js` or `NodeJS`, case-insensitively.
- `Next.js` matches `Next.js` or `NextJS`.
- `React` counts only when written as `React`, `React.js`, or `ReactJS` with the technology name's capitalization preserved in the source. A lowercase plain-English “react” does not count. A sentence-initial “React” can still be a false positive (for example, “React quickly to incidents”) because the rule cannot reliably infer grammar from capitalization alone; this is a known limitation.
- `Express` counts only as `Express.js`, `ExpressJS`, or in the phrase `Express framework`; a plain-English “express interest” does not count.
- `REST` counts only in the phrases `REST API`, `RESTful API`, or `REST services`; a plain-English “the rest of the team” does not count.
- `Front End`, `Front-End`, and `Frontend` are equivalent for the title check, but are not automatically treated as a resume skill.
- Other skills use case-insensitive whole-word matching after HTML cleanup: the characters next to the match must not be letters or digits. Multiword skills must appear as consecutive words.

For the `React`, `Express`, and `REST` special cases, capitalization and context are part of the rule. This avoids counting common English words as technologies. If the source does not contain the required technology form, that skill does not count.

### 6.3 Explicit exclusions

The rule also checks the posting text for these explicit exclusion phrases:

- U.S. citizenship: `must be a U.S. citizen`, `U.S. citizens only`, `United States citizens only`, or `citizenship required`
- Security clearance: `security clearance required`, `active clearance required`, or `must hold a clearance`
- Unpaid work: `unpaid position`, `unpaid role`, `unpaid internship`, or `this is an unpaid opportunity`

These checks implement the intent of `$.target.excluded[*]` using the exact phrase list above; the agent does not dynamically interpret arbitrary new prose in that resume field. They are case-insensitive after HTML cleanup, and the whole cleaned title and content are searched, not an excerpt. The agent does not infer an exclusion from silence or from ambiguous wording. This is a literal phrase list, not a general legal interpretation.

### 6.4 US-based location check

The job must be based in the United States. This is a hard rule condition, not a preference for Claude to weigh. The check reads `$.location.name` as one string and returns exactly one label: `US_BASED`, `NON_US`, or `NOT_ESTABLISHED`. Only `US_BASED` can lead to `MATCH`.

A **US signal** is any of:

1. The token `US`, `USA`, `U.S.`, or `United States`, matched case-sensitively, with no letter directly before or after it (so `US-Remote` and `US - Remote` count, but the pronoun “us” does not).
2. A comma, a space, and then an uppercase two-letter state or district code: `AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY` (for example `Seattle, WA`). A code that is not preceded by “, ” does not count, so the words “in” and “or” never count as Indiana or Oregon.
3. One of these city names or abbreviations, case-insensitively, as a whole word: `Atlanta`, `Chicago`, `New York`, `New York City`, `San Francisco`, `South San Francisco`, `Seattle`, `Washington DC`, `ATL`, `CHI`, `NYC`, `SEA`, `SF`.

A **non-US signal** is any of these names, case-insensitively, as a whole word:

- Countries: `Australia`, `Belgium`, `Brazil`, `Canada`, `France`, `Germany`, `India`, `Ireland`, `Israel`, `Japan`, `Luxembourg`, `Mexico`, `New Zealand`, `Poland`, `Romania`, `Singapore`, `Spain`, `Sweden`, `Taiwan`, `Thailand`, `UK`, `United Kingdom`
- Cities: `Amsterdam`, `Auckland`, `Bangalore`, `Bangkok`, `Barcelona`, `Bengaluru`, `Berlin`, `Bucharest`, `CDMX`, `Dublin`, `London`, `Madrid`, `Melbourne`, `Munich`, `Paris`, `Sao Paulo`, `Stockholm`, `Sydney`, `Taipei`, `Tokyo`, `Toronto`, `Tor`, `Toro`, `Vancouver`

The label is:

- `US_BASED` — at least one US signal and no non-US signal.
- `NON_US` — at least one non-US signal and no US signal.
- `NOT_ESTABLISHED` — no signal of either kind (for example `N/A`, `na`, `LOCATION`, `AMER`, or a bare `Remote`), or signals of both kinds (for example `Chicago, Toronto` or `US, Canada`). A posting listed for both US and non-US locations is not treated as US-only.

**Rescue from the description.** If `$.location.name` has no signal of either kind, the agent searches the cleaned `$.content` for these exact phrases, case-insensitively: `must be based in the united states`, `must be located in the united states`, `united states only`, `us only`, `u.s. only`, `usa only`, `remote within the united states`, `remote in the united states`, `remote from the united states`, `us-based only`, `u.s.-based only`, `usa-based only`. If one is present the label is `US_BASED` and the evidence cites `$.content`. No other wording rescues a posting. A location with both kinds of signal is never rescued.

The agent does not infer location from the employer's headquarters, salary currency, time zone, or assumptions about where a role is usually hired, and it does not use a geocoder. The lists above were built from every distinct `location.name` value in the October 29, 2026 Stripe response (294 values). A new location spelling that is in neither list is `NOT_ESTABLISHED` until a committed contract amendment adds it. This is a conservative evidence rule: an unknown location is not proof that a job is outside the US, but it is not enough to qualify for this US-only search.

### 6.5 Final verdict

A posting is `MATCH` if and only if all four conditions are true:

1. Its title matches one of the role families derived from `$.target.roles[*]` and passes the title exclusions.
2. At least two distinct eligible resume skills match the cleaned posting title, content, or department text.
3. None of the explicit exclusion phrases in section 6.3 appears in the cleaned posting text.
4. The US-based location check in section 6.4 returns `US_BASED`.

Otherwise the verdict is `NO_MATCH`. When multiple conditions fail, record all applicable reasons, not only the first one. The rule does not guess whether an employer sponsors a work visa; sponsorship is left to Claude's separate judgment and must be described as uncertain if the posting does not say.

## 7. Output format and evidence

For each new posting, the agent writes one JSON record with this shape:

```json
{
  "posting_id": "123456",
  "title": "Software Engineer",
  "location": "Seattle, WA",
  "updated_at": null,
  "rule_verdict": {
    "label": "MATCH",
    "location_check": {
      "label": "US_BASED",
      "evidence": ["$.location.name"],
      "reason": "The posting lists Seattle, WA, which is a US location."
    },
    "evidence": [
      {
        "term": "TypeScript",
        "resume_path": "$.skills.languages[0]",
        "posting_path": "$.content"
      },
      {
        "term": "Node.js",
        "resume_path": "$.skills.backend[0]",
        "posting_path": "$.content"
      }
    ],
    "reason": "The title passes the role check, two distinct resume skills appear in the posting, no exclusion phrase appears, and the location is US-based."
  },
  "model_judgment": {
    "status": "VALID",
    "label": "RELEVANT",
    "summary": "The role appears worth reviewing based on the supplied evidence.",
    "evidence": [
      {
        "resume_path": "$.experience[0].bullets[0]",
        "posting_path": "$.content",
        "reason": "The resume describes relevant shipped experience that relates to the posting description."
      }
    ],
    "uncertainties": ["The posting does not state whether sponsorship is available."]
  }
}
```

The example is only a schema illustration; the posting ID and values are not a claim about a verified live vacancy.

For each rule verdict, `location_check` must be present and include `label` (`US_BASED`, `NON_US`, or `NOT_ESTABLISHED`), one or more valid source paths, and a short reason. A `MATCH` must have `location_check.label: "US_BASED"`.

For each rule verdict, `evidence` is an array with one entry per distinct matched skill. Every entry must pair exactly one `term`, one `resume_path`, and one `posting_path`; this makes it unambiguous which resume skill was found in which posting field. The resume path must point to the skill value that matches `term`, and the posting path must point to the original raw field containing that match. Valid posting paths include `$.title`, `$.content`, and `$.departments[0].name`. The validator checks that both paths exist and that the cited term is actually supported by their values after the specified cleanup and normalization.

For a `NO_MATCH`, the record still lists any skill evidence that did match and explains every gate that failed, including location when relevant. It must not claim a skill matched without a complete evidence entry.

The `model_judgment` must also cite evidence: each entry in its `evidence` array pairs one `resume_path` and one `posting_path` with a short `reason`. Every path must exist in the actual input objects. If any cited path is missing or invalid, the judgment is rejected by the validator.

## 8. Claude judgment format and validation

Claude's judgment uses a fixed JSON format with exactly these keys and no others:

```json
{
  "label": "RELEVANT",
  "summary": "A short explanation of the assessment.",
  "evidence": [
    {
      "resume_path": "$.skills.backend[0]",
      "posting_path": "$.content",
      "reason": "The posting mentions a technology listed in Kiran's resume."
    }
  ],
  "uncertainties": ["Sponsorship policy is not stated."]
}
```

`label` must be exactly `RELEVANT` or `NOT_RELEVANT`. This makes the model result comparable with the hand labels in the prompt experiment. It is still a model judgment, not a verified fact. `RELEVANT` means Claude thinks the posting is worth considering; it does not mean Kiran is qualified for certain or will get an interview.

The validator rejects a reply if it is not valid JSON, has any text before or after the JSON object, is wrapped in Markdown code fences (including ```json fences), has missing keys, has extra keys, uses a label other than the two allowed values, gives a field the wrong type, or cites a resume/posting path that does not exist. Arrays must have the exact types defined by the schema. `summary` must be a string. `uncertainties` may be an empty array but must always be present. Every evidence entry must pair a real resume path with a real posting path and a short reason.

The agent may retry one time after a validation failure, using the same schema instructions. It must not silently repair or reinterpret an invalid reply. The sampling report records and scores the first reply before any retry, so retry behavior does not hide the model's initial formatting or judgment variation. If the second reply is invalid, it records `model_judgment.status` as `INVALID_OUTPUT`, keeps the raw reply in a separate diagnostic field or local diagnostic log, and does not treat it as a valid label. The raw reply must not be allowed to overwrite the structured output. If no model call can be made, the status is `UNAVAILABLE`; if a call fails after being attempted, the status is `ERROR`.

Claude's evidence paths must be real paths in the supplied resume and posting. A path that looks plausible but does not exist is a validation failure.

## 9. Baseline and run statuses

The first successful, valid fetch is a baseline, not a run that reports every posting as new. Its status is `BASELINE`. It reports the number of postings fetched, the number of valid unique IDs seen, `new_count: 0`, and whether the state was saved. All IDs from the baseline are stored as seen, but the baseline still reports `new_count: 0`. IDs are retained cumulatively so a posting that disappears and later reappears is not treated as new again. No postings receive new-posting judgments on the baseline run.

On later runs, a posting is new only if its ID is not in the cumulative seen-ID set (§10). The run report must distinguish:

- `SUCCESS_WITH_NEW` — fetch and validation succeeded and new IDs were found
- `SUCCESS_NO_NEW` — fetch and validation succeeded and no new IDs were found
- `FETCH_FAILED` — the request failed or returned an unsuccessful HTTP status
- `EMPTY_RESPONSE` — the request succeeded but the postings array was empty
- `INVALID_RESPONSE` — the response could not be parsed or had the wrong shape
- `PARTIAL_FAILURE` — the fetch worked, but one or more record judgments or another later step failed

An empty response is not the same as a successful run with no new IDs. The report must not describe a fetch failure, invalid response, or empty response as `SUCCESS_NO_NEW`.

The baseline report includes fetched count, unique valid IDs seen, zero new postings, and state-save result. It does not claim that all existing jobs were judged.

## 10. State, pending judgments, and retries

The state file stores the board identifier, the set of all valid posting IDs ever seen on a successful fetch, the last successful fetch timestamp, and any posting IDs whose Claude judgment is still pending or invalid. The seen-ID set is cumulative, not a snapshot: once an ID has been seen, its disappearance from the board does not remove it from the set. If the same ID later reappears, it is not treated as new again.

The agent must not lose a posting just because Claude is unavailable. If the rule step succeeds but the Claude call fails or returns invalid output, the posting's rule result is saved and the posting ID is added to a pending-judgment list. On later runs, pending judgments are retried even though the posting ID is no longer new. A pending ID is removed only after a valid Claude result is stored or after an explicit, documented decision to stop retrying it.

If a fetch fails or the response is invalid, the last successful seen-ID state is preserved. State is updated only after a successful, validated fetch. State writes must be done safely so an interrupted write does not silently destroy the previous valid state.

A model error makes the run `PARTIAL_FAILURE`, not `SUCCESS_NO_NEW`. If there are no new postings but a pending judgment is retried and fails, the run is also `PARTIAL_FAILURE`.

## 11. Host allow-list and subscription boundary

The agent's own network requests may contact:

- `boards-api.greenhouse.io` — fetch public Greenhouse data.
- Any additional host explicitly documented as required by the approved Claude-subscription interface used by the project.

The implementation must document the actual Claude Code/subscription hosts it relies on before the build is considered complete. The agent's code can enforce the allow-list for requests it makes itself. It cannot guarantee or enforce the network destinations used internally by a separate `claude` executable that it launches; that limitation must be recorded rather than hidden.

The agent must not follow arbitrary links embedded in job descriptions. Requests it makes must use HTTPS. Redirects to undocumented hosts must be rejected. Subscription credentials and session tokens must never be written to the resume, state file, output records, or logs.

If subscription-authenticated use is unavailable, the agent must leave model judgments unavailable or deferred. It must not quietly switch to an Anthropic API key or claim that a subscription-authenticated judgment was completed when it was not.

## 12. Refusals and resume privacy

The agent accepts only the approved fictional resume fixture. It checks all of the following:

1. `$.fictional` is exactly `true`.
2. The email's domain, after the single `@`, is exactly `example.com` (a suffix test is not enough: `notexample.com` fails).
3. The phone number uses the reserved fictional `555-01xx` pattern.
4. The required Kiran persona and resume fields are present.
5. The SHA-256 digest of the fixture matches a pinned expected digest in the test/configuration.

The expected digest must be calculated from the exact committed bytes of `persona/kiran-joshi.resume.example.json` and pinned before the first implementation run. The implementation must not calculate an expected hash from the file at runtime and then compare the file to that same newly calculated value, because that would prove nothing. If the pinned digest is not set, does not match, or any other check fails, the agent refuses to process the resume and must not send its contents to Claude.

The agent must never print a real resume, show its contents in a report, or commit a real resume to GitHub. The only resume details allowed in output are the specific matched skill terms and their JSON paths, plus the fictional persona label needed to identify the fixture. It must not dump resume bullets, personal contact details, or unrelated fields to the terminal or logs. A real resume must stay outside the repository; the existing ignore rules for `private/` and `*.resume.json` should be checked as part of implementation.

The agent also refuses to apply for jobs, email recruiters, log in, bypass access controls, ignore rate limits, follow arbitrary links, contact undocumented hosts, expose credentials, or write outside configured project data/output directories. It must never present Claude's judgment as a fact or as an employer's decision.

## 13. Real-posting hand checks

These hand checks use the Stripe Greenhouse API response fetched on October 29, 2026 at 22:41:31 UTC, committed as `evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json`. Its SHA-256 (`74e20e05ef226186…`, full value in the accompanying `.meta.json`) and HTTP status are recorded in `evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.meta.json`. Posting URLs are the raw `absolute_url` values. These are evaluations of the contract's rule, not claims that the jobs are a good personal fit.

### Case 1 — US-based positive example: MATCH

- Posting: `$.jobs[566]`, ID `8249901`, “Software Engineer”
- Location: `Seattle, WA` (`$.location.name`)
- URL: https://stripe.com/jobs/search?gh_jid=8249901
- Title check: Pass — contains `software engineer` and no excluded title marker.
- Skill evidence (3 distinct, all in `$.content`): Java (`$.skills.languages[2]`), Python (`$.skills.languages[3]`), AWS (`$.skills.cloud_devops[0]`).
- Explicit exclusion check: Pass — none of the §6.3 phrases appears in the full cleaned content.
- US location check: `US_BASED` — `, WA` is a US state code.
- Final verdict: `MATCH`.
- Qualification caveat: the description requires three years of experience and lists several infrastructure requirements. The current rule does not separately gate on years of experience, so the verdict means only that the written deterministic checks pass.

### Case 2 — Non-US location: NO_MATCH

- Posting: `$.jobs[575]`, ID `7543868`, “Software Engineer, Financial Business Insights”
- Location: `Bengaluru, India` (`$.location.name`)
- URL: https://stripe.com/jobs/search?gh_jid=7543868
- Title check: Pass — contains `software engineer` and no excluded title marker.
- Skill evidence (4 distinct, all in `$.content`): GraphQL (`$.skills.backend[4]`), AWS (`$.skills.cloud_devops[0]`), Docker (`$.skills.cloud_devops[2]`), Kubernetes (`$.skills.cloud_devops[3]`).
- Explicit exclusion check: Pass.
- US location check: `NON_US` — `Bengaluru` and `India` are non-US signals and there is no US signal.
- Final verdict: `NO_MATCH` because the location condition fails, despite the title and skill matches.
- Qualification caveat: the description requires 8+ years of experience; the current deterministic rule does not separately gate on years of experience.

### Case 3 — Excluded seniority title: NO_MATCH

- Posting: `$.jobs[556]`, ID `8175099`, “Senior Software Engineer”
- Location: `South San Francisco, CA` (`$.location.name`)
- URL: https://stripe.com/jobs/search?gh_jid=8175099
- Title check: Fail — the title contains the excluded whole-word marker `senior`.
- Skill evidence (4 distinct, all in `$.content`): Java (`$.skills.languages[2]`), AWS (`$.skills.cloud_devops[0]`), GCP (`$.skills.cloud_devops[1]`), Kubernetes (`$.skills.cloud_devops[3]`). They do not override the title exclusion.
- Explicit exclusion check: Pass.
- US location check: `US_BASED`.
- Final verdict: `NO_MATCH` because the title fails the seniority check.

### Case 4 — Eligible title, US location, fewer than two skills: NO_MATCH

- Posting: `$.jobs[604]`, ID `8127182`, “Software Engineer, Revenue and Financial Automation”
- Location: `San Francisco, New York City, Seattle, Chicago, US-Remote` (`$.location.name`)
- URL: https://stripe.com/jobs/search?gh_jid=8127182
- Title check: Pass — contains `software engineer` and no excluded title marker.
- Skill evidence (1 distinct): Java (`$.skills.languages[2]`) in `$.content`. No other eligible resume skill appears in the title, cleaned content, or department names.
- Explicit exclusion check: Pass.
- US location check: `US_BASED` — US city names and the `US` token, no non-US signal.
- Final verdict: `NO_MATCH` because only one distinct skill matches and the threshold is two. This is the case that catches wrong implementation A (§14).

### Additional observed case — location not established: NO_MATCH

- Posting: `$.jobs[273]`, ID `8234357`, “Full Stack Engineer, Revenue”
- Location: `N/A` (`$.location.name`)
- URL: https://stripe.com/jobs/search?gh_jid=8234357
- Title check: Pass — `full stack` plus `engineer` matches the Full-Stack Software Engineer family.
- Skill evidence (4 distinct, all in `$.content`): TypeScript (`$.skills.languages[0]`), React (`$.skills.frontend[0]`), HTML (`$.skills.frontend[2]`), CSS (`$.skills.frontend[3]`).
- Explicit exclusion check: Pass.
- US location check: `NOT_ESTABLISHED` — `N/A` has no signal, and none of the §6.4 rescue phrases appears in the cleaned content.
- Final verdict: `NO_MATCH` under the US-only rule.

Together these cover a positive US match, a non-US rejection, a title-exclusion rejection, a skill-threshold rejection, and an unknown-location rejection. The raw response must stay committed so the IDs, locations, and skill evidence can be checked independently.

## 14. Two wrong implementations the tests must catch

**Wrong implementation A: title-only matching.** It returns `MATCH` for every title that looks like a software engineering role. This is wrong because the skill threshold, explicit exclusion check, and US-based location check also apply. A test with an eligible title and zero or one distinct matching skill (as in §13 case 4), a non-US location (case 2), or an unestablished location (the `N/A` case) must return `NO_MATCH`.

**Wrong implementation B: raw substring counting.** It searches for skill strings after stripping punctuation and counts repeated appearances as separate skills. This is wrong because special skills such as `C#` need their own matching rule, common English words like “rest” must not count as `REST`, and repeated mentions of one skill count only once. Tests must cover `C#` versus plain `c`, plain-English “the rest of the team,” repeated mentions of a single skill, and a missing evidence path. Tests must also reject an evidence entry that cites the wrong resume path for a term, for example GraphQL with `$.skills.backend[3]` (that value is `REST`).

## 15. Failure statement

**October 29, 2026:** If a fetch fails or returns an invalid or empty response and the agent reports `SUCCESS_NO_NEW`, it has hidden a failed or unusable run by describing it as a successful run.

## 16. Hand-labeling for the prompt experiment

My hand labels will use the same deterministic rule as the agent, not my personal opinion about whether I would spend a day applying. I will apply the title check, skill threshold, explicit exclusion phrases, and US-based location check exactly as written, then record the evidence paths. Claude uses `RELEVANT` and `NOT_RELEVANT`, so its label can be compared directly with the human `MATCH`/`NO_MATCH` label using this mapping:

- `RELEVANT` corresponds to `MATCH`
- `NOT_RELEVANT` corresponds to `NO_MATCH`

This comparison measures agreement with the written rule, not whether a recruiter would interview Kiran or whether a job is objectively desirable.

## 17. Acceptance checks

The implementation is consistent with this contract only if:

- It reads the Kiran fixture from `persona/kiran-joshi.resume.example.json`.
- It validates the fixture flag, reserved contact patterns, required structure, and pinned SHA-256 digest.
- It fetches Stripe Greenhouse postings and validates the response shape.
- It decodes escaped HTML and strips tags before matching.
- The title, skill, explicit exclusion, and US-based location checks follow this contract exactly; unknown or non-US locations cannot receive `MATCH`.
- Each rule result cites the resume and posting paths that support it.
- Claude's output is validated against the exact JSON schema and allowed labels.
- Invalid Claude replies are rejected rather than silently repaired.
- The model judgment includes evidence paths that are checked against the actual input objects.
- Baseline, no-new, empty, invalid, fetch-failure, and partial-failure outcomes remain distinct.
- Failed model judgments stay pending and can be retried.
- A failed fetch never overwrites the last successful state.
- The agent's own requests stay within the documented allow-list, and the separate Claude executable limitation is documented.
- A real or unverified resume is refused and never printed or committed.
- The two wrong implementations above are caught by tests.
- Applied to the committed raw response, the implementation reproduces every §13 verdict: 8249901 `MATCH`; 7543868, 8175099, 8127182, and 8234357 `NO_MATCH`, with the same skill evidence and location labels.



