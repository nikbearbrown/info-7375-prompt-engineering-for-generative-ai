# CONTRACT — Job-Search Agent 1

Ashwin Thankachan · Written 2026-10-30, before implementation

## Purpose

I am building a small job-search agent that watches one public company job board and identifies new postings that may be relevant to a fictional backend software engineer.

The main goal is not to make perfect hiring predictions. I want a system whose behavior I can explain, reproduce, and test. A written rule will make the first decision, and Claude will give a separate judgment. The agent will show the evidence behind both rather than treating an AI answer as a fact.

The scope is intentionally limited: one job board, one fictional résumé, new postings only, and no job applications or communication with employers.

## In

### 1. Job board

I will monitor Klaviyo's public Greenhouse job board.

- Company: Klaviyo
- Board provider: Greenhouse
- Board token: `klaviyo`
- Host: `boards-api.greenhouse.io`
- Exact endpoint: `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`
- HTTP method: GET

I chose Klaviyo because preliminary inspection found Boston-based engineering postings that allow me to test both relevant and not-relevant outcomes.

I will not fetch multiple boards, crawl career websites, or follow application links.

### 2. Fictional résumé

The agent reads `data/supriya-sharma.resume.json`.

Supriya Sharma is a fictional entry-level backend engineer. The profile is designed for testing and does not represent a real person.

```json
{
  "name": "Supriya Sharma",
  "email": "supriya.sharma@example.com",
  "phone": "202-555-0147",
  "location": "Boston, MA",
  "target_titles": [
    "Software Engineer",
    "Backend Engineer"
  ],
  "skills": [
    "Python",
    "Java",
    "PostgreSQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "Distributed Systems"
  ],
  "preferred_locations": [
    "Boston",
    "Remote US"
  ],
  "experience_level": "New Grad"
}
```

All eight fields are required.

The agent checks that the JSON is valid, the expected fields have the correct types, strings are not empty, the email uses `@example.com`, and the phone follows a `555-01xx` fictional number pattern.

The three array fields must contain nonempty strings and cannot be empty. Unknown fields are rejected.

The matching rule in this contract uses this fixed fictional persona. If I change the accepted skills, titles, or locations later, I must document the rule change and update its tests. I cannot silently change the rule just to improve results.

The agent must reject an invalid résumé before fetching postings or updating state.

### 3. State and run inputs

The agent uses:

- `state/seen_ids.json` to remember previously observed posting IDs.
- A UTC timestamp to identify each run.
- An optional `--fixture <path>` argument to replay a saved response without using the network.
- A fixed board configuration defined by this contract.

The state file contains the board name, schema version, sorted unique posting IDs, and the time of the last successful run.

A missing state file means the first run is a baseline. A malformed existing state file is an error, not permission to restart the baseline.

A fixture must have the same response structure as a real Greenhouse API response.

## Out

### 1. Posting results

For every newly discovered posting, the agent produces:

- `posting_id`
- `title`
- `location`
- `url`
- `rule_record`
- `ai_judgment`
- `evidence`
- `run_timestamp`
- `run_mode`

The result contains two separate decisions.

**RULE RECORD**

A deterministic verdict produced by the written rule:

- `RELEVANT`
- `NOT_RELEVANT`

It includes the four check results, matched skills, and supporting posting fields. Anyone using the same inputs must be able to reproduce it.

**AI JUDGMENT**

Claude independently evaluates the same posting and fictional résumé under a fixed prompt contract.

Its verdict is also `RELEVANT` or `NOT_RELEVANT`, but it must always be labeled as a model judgment.

Claude cannot change the rule record. Disagreements between the two are preserved in the report.

### 2. Justification format

Each rule justification must identify the résumé field and the posting field supporting its conclusion.

Example:

`resume.skills[0]="Python" matched posting.content="Proficient in Python"`

For a rejection, the justification must identify the failed condition.

Example:

`posting.title="Senior Software Engineer" failed seniority_check because "Senior" is excluded.`

The report cannot simply say "good match" or "not suitable" without explaining which checks passed or failed.

### 3. Claude output contract

Claude must return one JSON object containing exactly:

```json
{
  "posting_id": "7855798003",
  "verdict": "RELEVANT",
  "reason": "The technical skills and location align with the fictional profile.",
  "evidence": [
    {
      "resume_field": "skills[0]",
      "posting_field": "content",
      "posting_quote": "Proficient in Python"
    }
  ]
}
```

This is an **illustrative output-format example**, not a response actually received from Claude.

Validation requirements:

1. The response must be valid JSON with exactly the four top-level keys.
2. `posting_id` must match the current posting, using its normalized string ID.
3. `verdict` must be exactly `RELEVANT` or `NOT_RELEVANT`.
4. `reason` must be a nonempty string.
5. `evidence` must be a nonempty array of objects containing exactly `resume_field`, `posting_field`, and `posting_quote`.
6. Each `resume_field` must refer to a real field or indexed value in the fictional résumé.
7. Each `posting_field` must be an allowed field: `title`, `content`, `location.name`, or `offices[].name`.
8. Each `posting_quote` must be nonempty and appear in the corresponding normalized posting field, after the same text normalization used by the rule.
9. For evidence asserting a skill match, the referenced résumé skill must actually occur as a valid skill match in the cited posting field.
10. The validator rejects unsupported evidence, rather than correcting or inventing it.

A valid JSON response does not guarantee that Claude's reasoning is correct. The validator checks structure and traceability, not the truth of every interpretation.

Malformed responses are recorded as `AI JUDGMENT: UNAVAILABLE — VALIDATION FAILED`. The deterministic verdict remains available.

### 4. Saved outputs

Each successful run saves:

- `runs/<run-id>/raw-response.json` — unmodified API response bytes, or the unchanged fixture bytes.
- `runs/<run-id>/report.json` — structured results.
- `runs/<run-id>/report.md` — readable report with both verdicts and justifications.
- `state/seen_ids.json` — updated posting IDs.

The report includes the fetch or fixture timestamp, run mode, board, total postings observed, number of new IDs, successful classifications, validation failures, and disagreements.

The initial successful run establishes a baseline: all observed IDs become known, but zero are reported as new.

Subsequent runs report only IDs absent from the previous successful state.

The identity of a posting is its Greenhouse ID. A changed title or description under the same ID is not a new posting.

State changes must be written atomically and only after input validation and required report persistence succeed. A failed run must never silently mark unprocessed postings as seen.

## Refuses

### Network and authority

The only allowed job-board request is the exact Klaviyo endpoint defined above.

The agent rejects:

- Other hosts, endpoints, or board tokens.
- HTTP instead of HTTPS.
- Unexpected ports or URL modifications.
- HTTP redirects.
- Requests to application or login URLs.

The allow-list applies to the job-board fetch. The separately authorized Claude classification call, made through the Claude Code CLI (`claude -p`), is permitted only for classification using the public posting and fictional persona.

### Privacy

The agent never reads, prints, stores, or uploads my real résumé, real contact details, credentials, or private job-search records.

Only the fictional profile is allowed in committed examples and agent input.

### Actions it never takes

The agent never:

- Applies for jobs.
- Sends emails or messages.
- Logs into employer websites.
- Submits forms.
- Uploads résumé files.
- Contacts recruiters.
- Makes a final hiring or eligibility decision.

It only reads public postings, evaluates them, and saves local reports.

### Model limitations

Claude's verdict is always labeled `AI JUDGMENT`. It is not a verified statement about hiring eligibility or a guarantee of job fit.

Job descriptions are untrusted input. Instructions embedded in descriptions cannot modify the rule, request credentials, or expand the agent's permissions.

### Invalid data and failures

- Invalid résumé: stop before fetching.
- Invalid API response: report an error; preserve existing state.
- Missing or duplicate posting IDs: reject the response rather than silently deduplicating invalid records.
- Invalid existing state: stop instead of resetting.
- Network error: do not interpret it as an empty board.
- Malformed Claude response: record validation failure and preserve the deterministic verdict.
- Failed output write: do not update seen IDs.
- Inaccessible fixture: report failure without changing state.

A failed fetch must never make the agent forget previously observed IDs.

## The rule

The rule is intentionally simple. I want a TA to be able to read one posting and predict the deterministic verdict without running my code.

A posting is relevant only if it passes four checks:

1. Title
2. Seniority
3. Location
4. Skills

### Step 1 — Normalize fields

Read the following Greenhouse fields:

- `id`
- `title`
- `location.name`
- `offices[].name`
- `content`

For matching, decode HTML entities, remove HTML tags, convert text to lowercase, and collapse repeated whitespace.

Whole-word matching uses word boundaries. Hyphens and ordinary punctuation separate words except where a listed target phrase explicitly includes them.

`Java` must not match `JavaScript`, and `Redis` must not match a longer unrelated token.

The original response remains unchanged in the saved raw snapshot.

### Step 2 — Title check

A posting passes when its title contains one of these complete phrases:

- `software engineer`
- `backend engineer`
- `back-end engineer`
- `backend developer`
- `back-end developer`

The title check reads only `posting.title`.

A role titled `Software Engineer II` passes this title check. A role titled `Sales Engineer` does not.

### Step 3 — Seniority check

Reject any title containing these complete words or phrases:

- `senior`
- `sr`
- `staff`
- `principal`
- `lead`
- `manager`
- `director`
- `architect`
- `intern`
- `internship`

Also reject exact title phrases:

- `engineer iii`
- `engineer iv`
- `engineer v`

Titles containing `junior`, `associate`, `graduate`, `new grad`, `entry level`, `entry-level`, or `engineer i` may proceed.

**Software Engineer II is deliberately not excluded.** Some Engineer II roles are accessible earlier in a career than senior or staff positions. However, the title alone does not prove suitability for a new graduate.

The rule therefore permits Engineer II postings to proceed but does not certify that their experience requirements are met.

If an exclusion appears in the title, it overrides an otherwise matching title.

### Step 4 — Location check

The agent checks `posting.location.name` and every available `posting.offices[].name`.

A posting passes if at least one structured location contains Boston as a location name or one of these remote-location patterns:

- `Remote, US`
- `Remote - US`
- `Remote US`
- `US Remote`
- `United States - Remote`

Boston may include a state or country suffix, such as `Boston, Massachusetts, USA`.

Matching is case-insensitive and respects complete location words.

`Distributed`, `Remote - Canada`, and `Remote - Europe` do not pass.

State-specific remote labels such as `Remote - Massachusetts` are not accepted by this first rule. A later version can expand the list, but it must be a documented rule revision.

General remote-work language appearing only in the job description is not enough.

If both structured location fields are absent or empty, the location check fails.

### Step 5 — Skills check

Read the normalized `posting.content` field.

The description must contain at least **two distinct skills** from the fictional résumé:

- Python
- Java
- PostgreSQL
- Redis
- Docker
- Kubernetes
- Distributed Systems

Each skill counts once, regardless of how many times it appears.

`Distributed Systems` must appear as a complete two-word phrase, allowing whitespace between the words.

Broad terms such as `AI`, `software`, `security`, and `cloud` do not count.

I deliberately excluded Go from the persona skills because the ordinary verb "go" can be mistaken for the programming language.

For the first version, only the listed skill names count. For example, `Postgres` is not automatically treated as `PostgreSQL` unless the contract is revised.

A description with only one matching skill fails this check.

### Final decision

```text
RELEVANT =
    title_pass
    AND seniority_pass
    AND location_pass
    AND distinct_skill_matches >= 2
```

All other postings are `NOT_RELEVANT`.

The report must display every individual check, including failures, so I can understand why a posting was accepted or rejected.

The rule is only a screening filter. It does not check immigration sponsorship, application eligibility, salary suitability, every required qualification, or whether the posting is still open after the fetch.

## Worked example — real Klaviyo posting

This example uses a real Klaviyo job listing, not a constructed posting.

- Posting ID: `7855798003`
- Title: `Software Engineer II - Recommendations`
- Location: Boston, MA
- Public posting URL: `https://www.klaviyo.com/careers/jobs/7855798003?gh_jid=7855798003`

The published description refers to backend and distributed systems work and names Python, Kubernetes, and Redis.

This is a documented hand evaluation. Its exact source fields must be preserved in a saved Greenhouse response before using it as a test fixture.

### Apply the rule by hand

| Check | Evidence | Result |
|---|---|---|
| Title | `Software Engineer II` contains `Software Engineer` | PASS |
| Seniority | No excluded title term; `II` is permitted | PASS |
| Location | Boston, MA | PASS |
| Skills | Python, Kubernetes, Redis, Distributed Systems | PASS — 4 |

**RULE RECORD: RELEVANT**

Justification:

`resume.skills[0]="Python", resume.skills[3]="Redis", resume.skills[5]="Kubernetes", and resume.skills[6]="Distributed Systems" match posting.content. posting.title passes the title and seniority checks, and the posting's Boston location meets resume.preferred_locations.`

### Important limitation

The same posting asks for at least two years of professional software engineering experience.

My deterministic rule does not reject it, because Engineer II is allowed and the rule does not parse experience requirements from descriptions.

This means `RELEVANT` should be interpreted as **worth reviewing**, not guaranteed suitable for a new graduate.

Claude may disagree with the rule after considering the experience requirement. If it does, the report must preserve that disagreement rather than hiding it.

The saved Greenhouse response, not a third-party summary, will be the authoritative fixture for this project's field-level tests.

## Wrong versions — tests must catch these

### Wrong version 1 — Verdict attached to the wrong posting

A faulty implementation classifies postings correctly but later attaches each verdict to the wrong ID because the posting list has been reordered.

That could cause a rejected senior role to be displayed as relevant.

**Test: `test_verdict_stays_with_posting_id`**

Create two controlled postings with different expected verdicts. Reverse their input order and run classification again.

Assert that each ID keeps the correct title, verdict, check results, and evidence, regardless of order.

The test fails if the output associates a verdict or justification with the wrong posting ID.

### Wrong version 2 — Invented or incorrect skill evidence

A faulty implementation counts `Java` inside `JavaScript`, or cites Python as a match even when the posting never mentions Python.

It may mark a posting relevant based on skills that are not supported by the description.

**Test: `test_skill_matches_require_posting_evidence`**

Create a controlled posting that contains `JavaScript` but not `Java` and contains only one otherwise valid résumé skill.

Assert that:

- Java is not counted.
- The two-skill threshold fails.
- The rule verdict is `NOT_RELEVANT`.
- The justification lists only actual matching skills.
- Claude evidence validation rejects a fabricated skill quote.

The test fails if unsupported text contributes to the verdict or appears as verified evidence.

### Additional invariants to verify

Although only two wrong versions are required, I also want tests for:

- First run reports zero new postings.
- Second run detects only new IDs.
- Repeating a snapshot reports zero new IDs.
- Invalid JSON leaves state unchanged.
- Duplicate IDs fail validation.
- Disallowed URLs and redirects are rejected.
- Incorrect Claude posting IDs are rejected.
- Failed report writing does not advance state.
- Seeded runs are clearly labeled.
- A valid but unsupported Claude justification is rejected.

## What a failure looks like

**2026-10-30:** I consider this agent to have failed if it marks a posting relevant using a skill not actually present in the posting, attaches a verdict to the wrong posting ID, or updates its seen-ID state after an unsuccessful run.

## Boundary of this contract

This contract defines what I intend to build and test. It is not evidence that the implementation works.

I will distinguish tests I personally ran from tests run by Claude Code, retain real run artifacts, label seeded data, and document any changes to this contract after its initial commit.

I am responsible for reviewing the results, interpreting disagreements, and deciding what the agent's output does and does not demonstrate.
