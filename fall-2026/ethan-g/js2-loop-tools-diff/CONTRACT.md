# CONTRACT — Job-Search Agent 1

**DATE** - 31st October 2026

This contract is for a job-search agent that checks one public job board, **Samsara's Greenhouse board**, and finds new **data engineering and data analyst** jobs that
may match a candidate's resume.

---

## 1. In

- **Board:** one public Greenhouse job board, `samsara` (Samsara Inc.), listed in `config/boards.json`. A list of 131 more boards
  (`config/boards_all.json`) was tested as an optional extension, but it is not part of this layer.
- **API URLs:** `https://boards-api.greenhouse.io/v1/boards/<board>/jobs` for each board's job list, and
  `https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<id>` for a single job's full description
- **Résumé:** `persona/evan-gordon.resume.json`

### Sample of the fictional resume

This is a shortened excerpt of `persona/evan-gordon.resume.json`. It shows the parts the refusal checks look at:

```json
{
  "personal": {
    "name": "Evan Gordon",
    "location": "Boston, MA",
    "phone": "(617) 555-0142",
    "email": "evan.gordon@example.com"
  },
  "experience": [
    { "company": "Harborline Logistics (fictional)", "title": "Data Engineer", "start_date": "2021-01", "end_date": "2023-12" }
  ],
  "skills": { "languages": ["Python", "SQL", "Scala", "Bash"], "bi_tools": ["Tableau", "Power BI"] },
  "search": { "years_experience": 4, "max_required_years": 5, "preferred_max_years": 4, "locations": ["Boston, MA"] }
}
```

- **State file:** `state/seen_ids.json`
- **Python:** version 3.10 or later, standard library only
- **Judge:** Claude Code CLI (`claude -p`, model `claude-sonnet-5-5`), used for the separate AI judgment step


## 2. Out

For every new job with a data title, the agent reports:

- Company board
- Job ID
- Job title
- Location
- Job posting URL
- Deterministic verdict: `relevant` or `not_relevant`
- Two preference flags, `preferred_location` (Boston) and `preferred_years` (asks 0–4 years). They never change the verdict.
- A justification of five checks (R1–R5)

New jobs without a data title are counted in the run report but not judged, because Rule 1 already makes them not relevant.

Each check in the justification names the exact resume field and posting field it used, the values compared, and whether it passed. For example, the
skills check names résumé fields such as `skills.languages` and `skills.data_tools`, the posting field `content`, and the matching skills, such as
`["Python", "Airflow"]`.

The agent also produces a separate Claude judgment, labeled **"Claude judgment (claude-sonnet-5-5), not a fact"**. Claude's output must use exactly
this JSON format:

```json
{"posting_id":"8141959","verdict":"relevant","resume_fields":["search.target_titles","skills.data_tools"],"posting_fields":["title","content"],"reason":"Short explanation"}
```

A validator rejects the reply unless all of these hold:

- the whole reply is only this JSON object, with no prose and no code fences
- it has exactly these five keys
- `posting_id` matches the posting
- `verdict` is `relevant` or `not_relevant`
- every `resume_fields` path really exists in the résumé Claude was shown
- `posting_fields` uses only `title`, `location.name`, `departments`, or `content`
- `reason` is non-empty and at most 500 characters

A reply that fails is recorded as `rejected`, never repaired.

The deterministic verdict and Claude's judgment are kept separate. Claude's opinion does not change the deterministic result.

The agent saves every raw API response exactly as received, before processing it: each board's list under `evidence/raw/<run>/boards/`, and each
fetched description under `evidence/raw/<run>/jobs/`. It then updates the state file with the job IDs and boards it has seen, and writes a run report
to `evidence/runs/`.


If fetching a board fails, that board contributes nothing to the run and loses nothing from the state file. If the rule audit fails, the state file
is not updated.

## 3. Refuses

My agent will not:

- Access any host other than `boards-api.greenhouse.io`. This includes non-https URLs and redirects off the allow-list.
- Make more than one list request per board, plus one description request per new data-titled job, per run, or have more than 8 requests in flight
  at once.
- Use a resume that isn't fictional. The agent refuses to load a resume unless the file is marked `FICTIONAL`. No real resume is considered for this.
- Show the candidate's name or contact details on screen, or send them to Claude.
- Apply for jobs, send emails, contact recruiters, or log in anywhere.
- Mark a job relevant without evidence. Every check must cite real résumé and posting values.
- Count skills under `familiar_with_not_shipped` (Flink, Kubernetes) as real skills.
- Present Claude's opinion as a proven fact. Every Claude verdict is printed as "Claude judgment, not a fact"


## 4. The rule

A job must pass all five checks to be **relevant**. Two preferences are reported alongside the verdict but never change it.

### Rule 1: Job title (role)

I read the posting's `title` field. It must contain at least one of these phrases (from `search.target_titles`):

- data engineer
- analytics engineer
- data platform
- data infrastructure
- data analyst

I ignore uppercase and lowercase, and match the phrase anywhere in the title.

### Rule 2: Seniority (level)

I read the posting's `title` field. It must not contain any of these complete words (from `search.excluded_title_terms`), ignoring case:

- Staff, Principal, Lead, Manager, Management, Director, Head, VP, Intern, Distinguished, Architect

**"Senior" is allowed**, because many Senior data roles ask for only 4–5 years. Rule 5 judges the level by years instead. "Internal" doesn't trip
"Intern", because only whole words count.

### Rule 3: Location (place)

I read the posting's `location.name` field. A job passes if either:

- **(a)** it contains "Boston" (the city in `search.locations`), ignoring case. This passes **and is marked preferred**.
- **(b)** it contains a US marker as a complete word, case-sensitive, from `search.us_location_markers`: US, USA, U.S., United States, any US state
  name or two-letter code (including DC), or a listed US metro(New York, Seattle, San Francisco). In addition:
  - if the location says "remote", the candidate must be open to remote (yes), **or**
  - if it doesn't, the candidate must be open to relocating within the US (yes).

A posting listing several places passes if any one of them qualifies.

Examples:

- `Remote - US` passes (remote, in the US)
- `Boston, Massachusetts, United States` passes and is **preferred**
- `San Francisco, CA` passes (relocate, US)
- `Remote - Canada` fails
- `London, UK` fails
- `Remote` with no country fails

### Rule 4: Skills

I read the candidate's skills from every list in `skills` except `familiar_with_not_shipped`:

- `skills.languages`: Python, SQL, Scala, Bash
- `skills.data_tools`: Spark, Airflow, dbt, Kafka, Databricks, Pandas
- `skills.database_cloud`: Snowflake, PostgreSQL, BigQuery, Redshift, AWS, GCP
- `skills.devops_cicd`: Docker, Terraform, Git, GitHub Actions
- `skills.bi_tools`: Tableau, Power BI

At least **two different** skills must appear in the posting's `content`. I match complete terms and **case-sensitively**, so "Scala" doesn't match
"Scalable" and "Spark" doesn't match "spark". I don't count Flink or Kubernetes.

### Rule 5: Experience (years)

I read the posting's `content` field. I find the **first** digit-based phrase of the form `N years`, `N+ years`, or `N-M years` (also `N–M` or
`N to M`) that has the word "experience" within 60 characters before or after it. I use **N**, the first number.

- It passes if **N ≤ 5** (`search.max_required_years`), or if no such phrase exists.
- It's marked **preferred years** if **N ≤ 4** (`search.preferred_max_years`).

Examples:

- `2+ years of experience`: pass, preferred
- `4-5 years of professional experience`: pass (N = 4), preferred
- `5+ years of experience`: pass, not preferred
- `8+ years of experience`: fail
- `Our company is 12 years old` (no "experience" nearby): not counted, so pass
- `three years of experience`: not counted (written as a word)

I chose these limits because Evan has about 4 years of experience. 0–4 years fits comfortably, 5 is a reasonable reach.

**Worked example (made up example):**

title: Senior Analytics Engineer
location.name: Boston, MA
content: asks for 4-5 years of professional experience and uses dbt and SQL daily
It passes all five rules:

The title contains "analytics engineer".
The title has no excluded word. "Senior" is allowed.
The location contains Boston, so it's preferred.
The content contains two skills, dbt and SQL.
The first years phrase is "4-5 years" with N = 4, which is ≤ 5 and ≤ 4, so years are preferred.
I'd mark it relevant, with both preferences, and the justification names each résumé and posting field used.

## 5. Wrong versions

My tests build these incorrect versions on purpose and must catch each one:

**Wrong version 1: verdicts attached to the wrong postings.**
The verdicts are computed correctly but attached to a shifted or re-sorted list, so job A shows job B's verdict.
*Test:* every verdict's job ID must exist in the run, every cited posting value must appear in **that** job's field, and the recomputed verdict must
match. The shifted and re-sorted versions fail the audit.

**Wrong version 2: a justification that cites nothing, or cites things that aren't there.**
Examples: an empty justification, a résumé path that doesn't exist, or a cited value that isn't in the résumé or posting, such as claiming the résumé
lists "Rust".
*Test:* all five checks must be present, each résumé path must resolve to exactly the stated value, and each posting value must appear in the cited field.

 **Wrong version 3:** the first run reports jobs as new. *Test:* the baseline must report zero.

**Wrong version 4:** a board seen for the first time reports all its jobs as new. *Test:* it must be baselined instead.

`scripts/sabotage_check.py` disables the audit and shows the Wrong version 1 and 2 tests go red, proving they can fail.

## 6. Failure

(All on 31st October 2026)
- This layer has failed if any run reports a job as new whose ID was already in the state file, or prints a verdict whose
  justification cites a résumé or posting value that isn't actually in those files.
- It has also failed if Rule 5 passes a job whose first stated experience requirement is more than 5 years.
- It has also failed if a preference flag ever changes a verdict.
- It has also failed if a board's first successful fetch reports any of its jobs as new.
