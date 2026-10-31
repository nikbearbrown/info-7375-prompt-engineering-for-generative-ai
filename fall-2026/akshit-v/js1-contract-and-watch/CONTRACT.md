# CONTRACT — Job-Search Agent 1

Started 2026-10-31, before any code was written.
The decisions in this file are mine. Claude Code asked the guiding questions, offered suggestions (each one I accepted is marked where it appears), and wrote up my answers (see SOURCES.md).

## In

**Board:** Greenhouse, company board `figma`.
- Host: `boards-api.greenhouse.io` (the only host on the allow-list)
- Endpoint: `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true`

**Résumé:** one JSON file for a fictional persona, **Jack Spencer**. He has a master's degree (already graduated) and 5 years of work experience in data engineering. He is looking for a full-time job in NYC, California, Chicago, or Boston, and remote US roles are fine too. He needs visa sponsorship.

Résumé fields:

| Field | What it holds | Used by the rule? |
|---|---|---|
| `name` | Jack Spencer | No (identity only) |
| `email` | an `@example.com` address | No (proves the persona is fictional) |
| `phone` | a 555 number | No (proves the persona is fictional) |
| `target_titles` | job titles Jack wants | Yes (matched against posting `title`) |
| `skills` | Jack's technical skills | Yes (matched against posting `content`) |
| `seniority` | Jack's level | Yes (see The rule) |
| `locations` | NYC, California, Chicago, Boston, Remote (US) | No (recorded only; location was dropped from the rule) |
| `education` | master's degree, completed | Recorded for justifications |
| `experience` | 5 years of data engineering roles | Recorded for justifications |
| `needs_sponsorship` | `true` | No (recorded only; the rule leaves sponsorship out) |

**What the agent needs to run:**
- network access to the one allow-listed host
- a folder to save each raw response as evidence
- a state file listing the posting ids it has already seen
- an Anthropic API key, used only for the Claude judge (Step 3)

## Out

For each **new** posting (the first run is a baseline and reports none as new), the agent returns:

**Posting identity:** `id`, `title`, `location.name`, `absolute_url`.

**Two verdicts, side by side.** The values are `relevant` or `not_relevant`, with no third option. Claude suggested two values as the simplest to implement and test, and I agreed.

1. **RULE (record, recomputable).** This is the verdict from The rule below. Its justification names the résumé fields and posting fields that decided it, which are title and skills only: `target_titles` against posting `title`, and `skills` against posting `content`. It names the exact matching words, so anyone can recompute it by hand.
2. **CLAUDE (judgment, model output, not verified).** Claude answers under a prompt contract. The heading also records the model id and the date. Claude must return exactly this JSON shape:
   ```json
   {"verdict": "relevant" | "not_relevant",
    "cited_resume_fields": ["..."],
    "cited_posting_fields": ["..."],
    "reason": "..."}
   ```
   A validator rejects anything else: extra keys, missing keys, a verdict outside the two values, empty citation lists, or field names that don't exist in the résumé or the posting. A rejected answer is shown as `CLAUDE: invalid output (rejected)`. It is never guessed at or repaired.

The rule's verdict is always shown first. If the two verdicts differ, the agent prints `DISAGREE`.

Example layout (format only; this is not a real result):
```
id <id> | <title> | <location.name>
  RULE (record, recomputable):  relevant
    because: target_titles "<x>" ~ title; skills <a>, <b> found in content
  CLAUDE (judgment, model output, not verified; <model id>, <date>):  relevant
    cited: resume.skills, posting.title, posting.content
  url: <absolute_url>
```

The label format above was Claude's suggestion, which I adopted.

## Refuses

The agent will not:

1. **Fetch any host that is not on the allow-list.** The allow-list has one entry: `boards-api.greenhouse.io`. This also covers redirects to any other host.
2. **Show a real résumé on screen or on GitHub.** The résumé validator rejects any résumé whose `email` doesn't end in `@example.com` or whose `phone` isn't a 555 number. The agent then stops before printing anything. Only the fictional persona (Jack Spencer) goes in the repo.
3. **Present a model's judgment as a fact.** Claude's verdict is always labeled `CLAUDE (judgment, model output, not verified; <model id>, <date>)` and is never shown as the record. Only the rule's verdict is the record.
4. **Apply to any job, email or message anyone, or log in anywhere.** The agent only reads one public endpoint and writes local files.

**When a refusal happens:** the agent skips the bad item, says why, and continues with the rest. Examples are a fetch to a non-allow-listed host, or a Claude answer that fails the validator. The one exception is a résumé that fails the check in (2), because there is nothing to continue with. In that case the agent stops.

## The rule

Only the posting `title` and `content` are used. Location and sponsorship are **not** part of the rule. Jack has already graduated and wants full-time roles only.

Jack's résumé values (the title and skill lists were Claude's suggestions, which I accepted):
- `target_titles`: "Data Engineer", "Data Platform", "Data Infrastructure", "Analytics Engineer", "ETL", "Data Integration"
- `skills`: Python, SQL, Spark, Airflow, Kafka, dbt, Snowflake, AWS

**Step 1: Disqualify.** If the title contains any of these words, the verdict is `not_relevant` and the agent stops checking:
Staff, Principal, Director, Manager, Head of, Intern, PhD, Contract, Temporary.
"Senior" and "Lead" are **not** disqualifying. Jack would want those roles. Interns and contract or temporary roles are excluded because Jack wants full-time work, and Greenhouse's job list has no employment-type field.

**Step 2: Title match.** The title matches if it contains any `target_titles` phrase, case-insensitive.

**Step 3: Count skills.** Count how many of Jack's 8 `skills` appear in the posting `content`, case-insensitive, as whole words. Whole-word matching was Claude's choice, which I accepted. It stops "SQL" from counting inside "PostgreSQL" or "NoSQL", which a person reading by hand would not count.

**Step 4: Verdict.** The posting is `relevant` if either:
- (a) the title matches **and** at least **3** skills are found, or
- (b) the title does not match, but at least **4** skills are found (more than 3). This is a strong skills match.

Otherwise it is `not_relevant`.

The justification cites the disqualifying word (if any), the `target_titles` phrase that matched (if any), and the list of skills found with their count.

## Wrong versions

My tests must pass on the correct code and fail on each of these two plausible-but-wrong versions. Claude recommended these two from a list of six candidates, and I chose them.

**W1: Verdicts paired with the wrong postings.** Every verdict and justification looks well-formed, but they are attached to the wrong `id`. For example, the list is sorted or shifted by one, or Claude's answers come back in a different order than the postings went out.
- *Test that catches it:* three or four hand-made postings with known, different verdicts. Check that each `id` gets its own expected rule verdict, and that each Claude verdict is matched to the `id` it was asked about.

**W2: Substring skill matching.** A skill is counted when it appears inside another word, e.g. `"sql" in content`. "SQL" then counts inside "PostgreSQL" or "NoSQL", which can push a posting over 3 or 4 skills and flip it to `relevant`.
- *Test that catches it:* one constructed posting that mentions "PostgreSQL" and "NoSQL" but never "SQL" as its own word. The correct code counts 0 for SQL, and the posting's verdict must not change because of it.

The constructed postings in these tests are labeled as constructed. They are not real postings.

## What a failure looks like

On 2026-10-31, before running anything, I'd call this agent a failure if any of these happens:
1. a rule verdict differs from what I get by applying this rule by hand;
2. the baseline run reports any posting as new, or the second run reports an id already in the state file;
3. Figma's "Data Platform Engineer" posting comes out `not_relevant`;
4. a Claude verdict appears without its judgment label, or an invalid Claude answer is shown instead of rejected;
5. the rule disagrees with my hand labels on more than 4 of the 20 postings I label.

(I chose these five conditions from examples Claude wrote, and Claude combined them into one statement at my request.)
