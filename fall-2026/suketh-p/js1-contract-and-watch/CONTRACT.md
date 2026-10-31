# CONTRACT.md

## Purpose

I want a job-search agent that helps me find engineering roles involving machine learning, AI systems, and data infrastructure. It should give me a short list I can check against the posting and résumé myself.

“Relevant” will mean that a posting passes the screening rule below. It will not mean that the candidate meets every requirement or should apply.

## In

The agent will take:

- One board name: anthropic, using Greenhouse.
- One fictional résumé in JSON.
- A local state file containing previously seen posting IDs. No state file means the first run.
- Access to Claude for the separate judgment.
- A local output directory for raw responses, results, and state.

The planned board endpoint is:

```text
https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true
```

Greenhouse documents the response fields and the content=true option in its Job Board API documentation.

I will use this constructed persona for the project:

```json
{
  "fictional": true,
  "name": "Alex Morgan",
  "email": "alex.morgan@example.com",
  "phone": "202-555-0147",
  "skills": [
    "python",
    "sql",
    "spark",
    "pytorch",
    "aws",
    "docker"
  ],
  "preferences": {
    "title_word": "engineer",
    "focus_terms": [
      "machine learning",
      "ml",
      "ai",
      "data",
      "inference"
    ],
    "excluded_title_words": [
      "senior",
      "sr",
      "staff",
      "principal",
      "lead",
      "manager",
      "director",
      "head"
    ],
    "location_terms": [
      "boston",
      "new york",
      "san francisco",
      "seattle",
      "united states"
    ]
  }
}
```

This persona is fictional. It will not contain my real contact details, employers, education, or résumé text.

Before processing anything, the agent must validate the résumé structure and required field types. The board response must contain a jobs array. Each posting must have a positive integer id, nonempty string title, string location.name, and nonempty string content. Invalid input must produce an error without advancing state.

## Out

For every new posting, the agent will return its board name, posting ID, title, location, and two separate assessments:

- **Rule verdict — record:** relevant or not_relevant, calculated using the rule below.
- **Claude verdict — model judgment:** relevant or not_relevant, returned under a fixed prompt contract.

Each assessment must explain its verdict using named résumé fields and posting fields, with supporting source values or excerpts. A statement such as “this looks like a good fit” is insufficient.

The rule record must show whether each of the four conditions passed. A negative verdict must identify the failed conditions.

The two verdicts may disagree. The output must preserve that disagreement.

### Claude output contract

Claude must receive the fictional résumé, one posting, the screening rule, and the required response format. Posting text is input data; instructions embedded in it must not change the task.

Its response must be one JSON object with exactly these keys:

| Key | Required value |
|---|---|
| `posting_id` | The supplied posting ID as a decimal string |
| `verdict` | `relevant` or `not_relevant` |
| `justification` | A nonempty explanation |
| `resume_evidence` | A nonempty array of objects containing `field` and `quote` |
| `posting_evidence` | A nonempty array of objects containing `field` and `quote` |

Evidence fields must identify real paths in the supplied inputs, such as `resume.skills` or `posting.title`. Quotes must be nonempty text copied from the referenced string field or from a string item in the referenced array.

The validator must reject malformed JSON, missing or extra keys, incorrect types, unsupported verdicts, mismatched IDs, nonexistent evidence paths, and quotes absent from their cited fields. Markdown fences or commentary outside the JSON are invalid.

A rejected response is an error. It must never become a not_relevant verdict by default. Valid formatting and citations do not establish that the judgment is correct.

## Refuses

The agent will refuse to:

- Fetch job data from any host other than boards-api.greenhouse.io, or from any board path other than the endpoint above.
- Follow redirects or fetch links found inside postings.
- Send model requests anywhere other than api.anthropic.com.
- Send anything to Claude beyond the fixed instructions, fictional résumé, and public posting.
- Read, display, upload, or commit my real résumé, contacts, application tracker, or private conversations.
- Print or save API credentials in reports, raw evidence, or error messages.
- Log in to job sites, apply for jobs, submit forms, or contact anyone.
- Present a model judgment as a verified fact about eligibility, qualifications, or hiring outcomes.
- Treat instructions inside a posting as authority to read files, change settings, or make additional requests.

Only HTTPS requests are permitted. The allow-list must be checked before each request. Job-board access is limited to GET requests; model access is limited to the configured Claude request.

## The relevance rule

I will use the same normalization for every comparison:

1. Decode HTML entities in posting content until decoding makes no further change.
2. Remove HTML markup with an HTML parser, retaining text and separating adjacent text blocks with spaces.
3. Lowercase the text.
4. Split it on every character outside a-z and 0-9, discarding empty tokens.

Single words must match complete tokens. Phrases must match consecutive tokens. For example, lead does not match leadership, and python3 does not match python.

A posting is relevant only when all four conditions pass:

| Condition | Exact check |
|---|---|
| Engineering role | `posting.title` contains `resume.preferences.title_word` and at least one phrase from `resume.preferences.focus_terms`. |
| Title seniority | `posting.title` contains none of `resume.preferences.excluded_title_words`. |
| Location | `posting.location.name` contains at least one phrase from `resume.preferences.location_terms`. |
| Skills | `posting.content` contains python and at least one different item from `resume.skills`. |

Otherwise, the verdict is not_relevant.

Repeated mentions of Python count as one skill. Skill mentions anywhere in the description count, including preferred qualifications. An empty location fails the location condition.

I will not infer synonyms, years of experience, sponsorship, remote eligibility, salary suitability, or missing qualifications. This is a literal screening rule with known limits. A description can pass it while still containing requirements the fictional candidate does not meet.

## The watch

On the first successful run, the agent will save the raw response and all posting IDs as its baseline. It will report zero new postings and produce no posting verdicts.

On later runs:

```text
new IDs = current response IDs − all previously seen IDs
```

IDs, rather than titles or list positions, determine whether a posting is new. An edited title does not make an existing ID new. An ID that disappears and later returns remains previously seen.

The agent will save the unchanged raw response with its retrieval time before interpreting it. Identical duplicate IDs will produce one result; conflicting records sharing an ID will cause an error.

A successful run must save complete results before atomically updating the state to include the current IDs. A fetch, parsing, validation, or model failure must leave the previous state intact. A damaged state file must cause an error instead of silently starting another baseline.

For the two-run demonstration, I will use either responses from separate calendar days or a saved earlier response clearly labeled as a seeded baseline. Seeded evidence must not be presented as a live change.

## Two wrong implementations my tests must catch

### 1. Correct-looking verdict attached to the wrong posting

An implementation could classify postings in one order and attach the results to IDs in another order.

I will construct two fixtures with different IDs and opposite rule outcomes, then reverse their order. The test must confirm that each verdict and its evidence remain attached to the correct ID.

### 2. A verdict with an unsupported justification

An implementation could accept a plausible explanation that cites no fields, invents a quotation, or refers to a different posting.

I will construct invalid responses covering those cases. The validator must reject them. The test must also confirm that rejection does not create a negative verdict or advance the state.

## What a failure looks like

October 28, 2026 — I will consider this version a failure if it reports baseline postings as new, makes an unapproved request, exposes private résumé information, attaches evidence to the wrong posting, or accepts a verdict without the required supporting fields.

## Amendment

October 31, 2026 - I will consider this version a failure if it reports a previously seen posting as new, accepts a verdict without matching résumé and posting evidence, contacts an unapproved host, or exposes private résumé information.

October 31, 2026 — For future runs in this assignment, I accept the additional uninspected context supplied by the configured Claude Code route, observed at about 800 tokens in the probes, provided the application supplies only the fixed instructions, fictional résumé, and one public posting, keeps model tools and saved sessions disabled, and retains the board allow-list and strict output validator.
This records an exception when adopted; it does not establish retroactive compliance for earlier runs.
