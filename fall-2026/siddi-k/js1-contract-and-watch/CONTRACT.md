# CONTRACT.md — Job-Search Agent 1

Author: Siddi Kommuri · Written: 2026-10-31 (before any implementation) · Contract version: v1

## In

* Board: Greenhouse public Job Board API
   * Host: `boards-api.greenhouse.io`
   * Company slug: `databricks`
   * Endpoint: `GET https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true`
* Run modes:
   * `live` fetches the board.
   * `seeded` reads a saved board file passed as `--seeded-from <path>`, makes no network call, and labels every output it writes as seeded (see State and Out).
* Résumé: `data/persona_resume.json`, fictional persona "Jordan Lee" (Appendix A). It must pass the persona validator below before anything else runs.
* Frozen config: committed together with this contract; each file has a `version` field.
   * `config/skill_vocab.json` (Appendix B)
   * `config/boilerplate.json` (Appendix C)
   * `prompts/judge_v1.md`: the Claude prompt
   * `config/claude_cmd.txt`: the exact `claude` invocation, including the pinned model
   * Changing any of these means a new version string and a re-run over stored `raw/` boards into a new output file. Past verdict lines are never edited. Every verdict line records the versions it used.

### Persona validator

The agent exits with an error, before fetching anything, if any rule fails:

* Required fields and types:
   * `name`: non-empty string
   * `email`: string ending in `@example.com`
   * `phone`: string matching `^\(555\) \d{3}-\d{4}$`
   * `education`: string
   * `highest_degree`: one of `bachelors`, `masters`, `phd`
   * `target_title_keywords`, `title_exclusions`, `skills`, `preferred_cities`: non-empty lists of lowercase strings
   * `years_experience`: integer from 0 to 40
   * `remote_ok`: boolean
* No extra fields. Any field not listed above fails validation.
* Vocab membership: every entry in `skills` is a canonical key in `skill_vocab.json`.

## State

* Files: `live` runs use `state/state.json`. `seeded` runs use `state/state.seeded.json`, which starts empty, so the first seeded run is its own baseline. A seeded run never reads from or writes to `state/state.json`.
* Seeded sequence: the README gives exactly these two commands. The first is the seeded baseline and reports 0 new postings. The second reports the postings in the later board that weren't in the earlier one.

```
python -m agent run --mode seeded --seeded-from raw/<earlier_run_id>/board.json
python -m agent run --mode seeded --seeded-from raw/<later_run_id>/board.json
```

* Fields:
   * `seen_ids`: Greenhouse job IDs observed by completed runs
   * `baseline_run_id`
   * `runs`: a list of `{run_id, run_mode, seeded_from, started_at, completed_at}`
* Baseline: if the state file is missing, the run saves the raw board, records all fetched IDs in `seen_ids`, reports 0 new postings, writes no verdicts, and marks itself complete.
* Later runs: a posting is new only if its ID is not in `seen_ids`.
* Crash safety:
   * A run is added to `runs` with `completed_at: null` when it starts.
   * Only after every new posting has been handled (a verdict line written, skipped, or logged as a Claude failure) does it add all new IDs to `seen_ids`, set `completed_at`, and rewrite the state file atomically (write to a temp file, then rename).
   * If a run crashes, it never completes, so its postings are still new on the next run. Every reader (validators, reports, experiments) ignores lines whose `run_id` has no `completed_at`, so a re-run can't create counted duplicates.
* Retries: none are automatic. Skipped and Claude-failed postings get `seen_ids` like any other posting; their logs are the record.

## Out (per new posting)

Each posting gets two verdicts with separate labels: the rule's verdict is a record, and Claude's verdict is a judgment. Both go in one JSON line in `output/verdicts.jsonl`:

```json
{
  "run_id": "2026-11-02T14-00-00Z",
  "run_mode": "live",
  "seeded_from": null,
  "contract_version": "v1", "vocab_version": "v1", "boilerplate_version": "v1", "prompt_version": "judge_v1",
  "claude_model": "<model id pinned in config/claude_cmd.txt>",
  "posting_id": 1234567,
  "posting_title": "Software Engineer - Data Platform",
  "posting_location": "San Francisco, California",

  "rule_verdict": "relevant",
  "rule_label": "record",
  "rule_checks": {
    "title_match": { "passed": true, "matched_keyword": "data platform", "exclusion_hit": null },
    "seniority_ok": { "passed": true, "seniority_token": null, "years_required": 3 },
    "location_ok": { "passed": true, "matched": "san francisco" },
    "skill_overlap": {
      "passed": true,
      "posting_skills": ["python", "spark", "kafka", "java", "kubernetes"],
      "matched": ["python", "spark", "kafka"],
      "matched_count": 3,
      "ratio": 0.6
    }
  },
  "rule_justification": "Title contains 'data platform' with no exclusion; no seniority token; years_required 3 ≤ 2 + 2; location contains 'san francisco'; 3 of 5 posting skills match (0.60).",

  "claude_status": "ok",
  "claude_verdict": "relevant",
  "claude_label": "judgment",
  "claude_justification": "Requirements ask for Spark and Kafka pipelines, which are in résumé skills; '3+ years' is slightly above years_experience 2.",
  "claude_cited_resume_fields": ["skills", "years_experience"],
  "claude_cited_posting_fields": ["content"],
  "claude_raw_paths": ["raw/2026-11-02T14-00-00Z/claude_1234567.json"],

  "disclaimer": "rule_verdict is a deterministic record of CONTRACT.md's rule. claude_verdict is a model judgment, not fact. Neither is a hiring decision."
}
```

A seeded line has `"run_mode": "seeded"` and `"seeded_from": "<path to the saved board file>"`.

Line validator, in two stages. A line is rejected if any check in its stage fails.

* Write-time (applied as each line is written, before the run completes): every check in the list below.
* Read-time (applied by reports, experiments, and TA checks): all the write-time checks, plus `run_id` belongs to a run with `completed_at` set in the matching state file. Lines from incomplete runs are ignored.

The checks:

* `run_mode` is `live` or `seeded`, and `seeded_from` is non-null if and only if `run_mode == "seeded"`
* `rule_verdict` is exactly `relevant` or `not_relevant`, and `rule_label == "record"`
* `rule_verdict == "relevant"` if and only if all four `rule_checks.*.passed` are true
* `skill_overlap.passed` if and only if `matched_count ≥ 3` and `ratio ≥ 0.40`; `matched ⊆ posting_skills ⊆ vocab`, and `matched ⊆ persona skills`
* `posting_id` and `posting_title` equal the id and title of that same posting in `raw/<run_id>/board.json`
* `claude_model` equals the model pinned in `config/claude_cmd.txt`
* `claude_status` is `ok` or `invalid_output`, and `claude_label == "judgment"`
   * If `ok`: `claude_verdict` is in the enum, the justification is non-empty, and both cited-field lists are non-empty and use only allowed names (résumé: `target_title_keywords`, `skills`, `years_experience`, `preferred_cities`, `remote_ok`, `highest_degree`; posting: `title`, `location`, `content`)
   * If `invalid_output`: `claude_verdict`, `claude_justification`, and both cited lists are `null`
* every path in `claude_raw_paths` exists, and so does `raw/<run_id>/board.json`. For seeded runs, `board.json` is a byte-for-byte copy of `seeded_from`.

## Claude judgment (Step 3)

* How it runs: the agent never calls an API. It runs the `claude` CLI as a subprocess with the exact command in `config/claude_cmd.txt`:
   * non-interactive with JSON output (`claude -p --output-format json`)
   * `--model <pinned model id>`
   * tool use disabled by an explicit flag, with the exact flag taken from `claude --help` for the installed version and recorded in the file
   * Isolation: the working directory is a new, empty temp directory outside the repo, created for each call, so no project `CLAUDE.md`, settings, or `output/` files are reachable. Before committing, confirm that no user-level `CLAUDE.md` in the home directory is loaded, or that it's empty, and note which in `claude_cmd.txt`.
   * stdin and stdout use `encoding="utf-8"` explicitly, so ™, –, and é survive on every OS.
* What Claude receives: the `prompts/judge_v1.md` template, filled with:
   * persona fields `target_title_keywords`, `skills`, `years_experience`, `highest_degree`, `preferred_cities`, `remote_ok`
   * posting `title`, `location.name`, and the requirements text (see Text preparation), truncated to its first 6,000 characters
   * Claude never sees `rule_verdict` or `rule_checks`, so the two judges stay independent.
* Evidence: the CLI's stdout is saved unmodified to `raw/<run_id>/claude_<posting_id>.json`, and a retry goes to `claude_<posting_id>_retry1.json`.
* Claude output validator:
   * stdout parses as JSON and is not an error envelope (`is_error` is false)
   * its `result` string parses, as-is, as exactly one JSON object with exactly these keys: `{"verdict": "relevant"|"not_relevant", "justification": string (1–400 chars), "cited_resume_fields": [non-empty], "cited_posting_fields": [non-empty]}`
   * cited names come from the allowed lists
   * No repair is allowed: code fences, extra prose, extra keys, or wrong casing all fail.
* On failure: retry once with the identical prompt. If the retry also fails, set `claude_status: "invalid_output"`, still write the rule verdict, and append `{posting_id, run_id, reason, raw_paths}` to `output/claude_failures.jsonl`. Claude's output is never edited, guessed, or filled in.

## Experiment runner

* The prompt experiment and sampling report (`experiments/`) run Claude on stored postings from `raw/` boards and on `labels/`, using the same isolated invocation.
* The runner never reads or writes `state/` or `output/`, and writes only to `experiments/output/`.

## Refuses

* Any network fetch by the agent's own code to a host not on the allow-list: [`boards-api.greenhouse.io`]
   * This includes each posting's `absolute_url`, which is recorded but never fetched
   * Seeded runs make no network fetch at all
   * The only other outside process is the `claude` CLI exactly as in `config/claude_cmd.txt`: isolated, tools disabled, and with no URLs passed
* Show a real résumé on screen or on GitHub: only the validated fictional persona is committed, and a real email or phone fails the persona validator
* Present the model's judgment as fact: Claude's verdict is always labeled `judgment`, and it is never merged into, substituted for, or used to repair `rule_verdict`
* Anything else:
   * Submit, apply to, or contact anyone about a posting
   * Emit verdicts for a posting whose requirements text is empty; it logs the ID and reason to `output/skipped.jsonl` instead
   * Commit API keys, tokens, or `.env`
   * Write anywhere except `output/`, `state/`, `raw/`, and `experiments/output/`

## The rule

`rule_verdict` is `relevant` only if all four checks pass. Every step uses frozen config and stated regexes, so a TA can recompute any verdict by hand from `raw/<run_id>/board.json`, the persona file, and the config files. Claude is not involved in the rule.

Text preparation:

1. HTML-unescape `content`.
2. Normalize quotes: replace ’ and ‘ with a straight `'`, and “ and ” with a straight `"`, so "Master’s" matches `master's`.
3. Cut boilerplate: find the first block element (`h1`–`h6`, `p`, `strong`, `b`, `div`) whose whole text, after lowercasing, trimming, and stripping trailing `:`, `.`, `-`, `–`, or `—`, equals a `cut_headings` entry in `boilerplate.json`. Drop that element and everything after it. So "Benefits:" matches "benefits".
4. Strip tags while keeping line structure:
   * Each block tag (`li`, `p`, `br`, `div`, `h1`–`h6`, `ul`, `ol`, `tr`) becomes a newline.
   * Collapse only runs of spaces and tabs into one space, trim each line, drop empty lines, and lowercase.
   * Each `<li>` bullet is therefore its own line.
5. Sentences: a sentence is a line, further split after `. `, `! `, or `? `. Delete every sentence containing a `drop_sentence_phrases` entry, such as "original creators of". Only that sentence is removed, never a whole bullet list.

The result is the requirements text, and the skills and years checks use only it. The Databricks company blurb names Apache Spark™, Delta Lake, and MLflow, so without step 3 and step 5, "spark" would match every posting.

A "whole-word match" of a term means the regex `(?<![a-z0-9])TERM(?![a-z0-9])`, with TERM regex-escaped, applied to lowercased text.

1. Title:
   * The title whole-word matches at least one `target_title_keywords` phrase.
   * It whole-word matches no `title_exclusions` phrase, such as account, sales, solutions, architect, or recruiter (full list in Appendix A).
   * Keywords are domain phrases, not full titles, so "Software Engineer - Machine Learning" passes, while "Account Executive, AI/ML" and "Solutions Architect - Data Engineering" fail.
2. Seniority: both parts must pass.
   * The title has no match for `\b(senior|sr|staff|principal|lead|manager|director|head|vp)\b`. Because `\b` falls between "r" and ".", "Sr." is caught.
   * `years_required` ≤ `years_experience` + 2, where `years_required` is the smallest first-group capture of the regex below, over every sentence of the requirements text that whole-word contains "experience": `(?<!\d)(\d{1,2})\s*(?:\+|(?:-|–|to)\s*\d{1,2}\+?)?\s*years?(?![a-z0-9])`
      * Only sentences that mention experience count, so boilerplate like "founded 10 years ago" doesn't.
      * Degree filter: a match is ignored if the 25 characters before it whole-word match `ms|m\.s\.|master's|masters|phd|ph\.d\.?|doctorate`. The persona's highest degree is a bachelor's, so "BS + 6 years, MS + 4 years, PhD + 2 years of experience" gives 6.
      * For a range like "2–4 years", the lower bound counts. `(?<!\d)` keeps "100+ years" from being read as "00".
      * If nothing matches, this part passes.
      * Known limits (accepted deliberately):
         * "MS + 1" with no word "years" isn't captured, so the BS figure counts.
         * The degree filter only looks before the number. In "5+ years of experience (or 3+ years with a Master's)", the 3 is kept, giving 3. In "5+ years (or 3+ with a Master's)", the 3 has no "years", so the result is 5.
         * Tool-specific minimums like "1+ years of experience with Terraform" count like any other match, so they can lower `years_required`.
         * A "5+ years" under preferred qualifications counts the same as one under required.
3. Location:
   * Split `location.name` on `;`, `|`, `/`, and the whole word `or`.
   * The check passes if any segment whole-word matches a `preferred_cities` name. Only the city is compared, so "San Francisco, California" and "San Francisco, CA" both pass.
   * A segment containing "remote" passes only if `remote_ok` is true and the segment is exactly "remote" or whole-word matches `us|usa|united states|north america`. "Remote - Australia" fails.
   * A bare "United States" (no city, no "remote") fails. This is intended: the persona wants specific cities or remote.
4. Skills:
   * `posting_skills` is every canonical vocab skill whose name or any alias whole-word matches the requirements text.
   * `matched` is `posting_skills` ∩ persona `skills`.
   * The check passes if `matched_count ≥ 3` and `matched_count / len(posting_skills) ≥ 0.40`. It fails if `posting_skills` is empty.
   * Excluded from the vocab on purpose: "r" (it matches "R&D"), "go" (an ordinary English word; use "golang"), "c", and "databricks" (the company name).
   * The ratio depends on the vocab, which is why the vocab is frozen and versioned.

## Hand-label set (20 postings)

* Source: the baseline run's `raw/<baseline_run_id>/board.json`. The baseline reports no new postings, but its fetched board is the labeling pool.
* Selection (Python 3, reproducible):

```python
rng = random.Random(42)
all_ids = sorted(int(j["id"]) for j in board["jobs"])            # ascending
candidates = [i for i in all_ids if passes_title(i) and passes_seniority(i)]
A = rng.sample(candidates, k=min(10, len(candidates)))
B = rng.sample(sorted(set(all_ids) - set(A)), k=20 - len(A))
labels = A + B                                                    # in sample order
dev, held_out = labels[0::2], labels[1::2]                        # 10 and 10
```

* Development and held-out split: prompt iterations may look only at `dev`. `held_out` is scored once, after the final prompt version is frozen.
* Labeling rule: written in `LABELING.md`, dated and committed before any posting is labeled. Hand labels go in `labels/hand_labels.jsonl`.
* Base-rate check: if fewer than 3 of the 20 are rule-relevant, change the slug before labeling and record the change here, dated, as contract v2. The check prints only the count, never per-posting verdicts, so hand labels stay independent of the rule.

## Wrong versions (tests must catch these)

Each item has exactly one test, `tests/test_wrong_versions.py::test_wv_NN`, built on a fixture. Any item that loses its test is removed from this list.

Tests never call the real `claude`. The harness puts a stub `claude` (`tests/stubs/claude`, which returns fixed fixture outputs or echoes stdin) first on `PATH`, and only inside tests. The README states that tests run without Claude, and that live runs need `claude` to be installed and logged in.

### Title and seniority

1. Marks "Senior Machine Learning Engineer" relevant because its skills match (seniority check skipped)
2. Misses "Sr. Software Engineer - ML" because the period breaks the seniority regex
3. Matches "ML" inside "HTML" (substring match instead of whole-word)
4. Rejects "Software Engineer - Machine Learning" because it matches whole titles instead of keywords
5. Passes "Account Executive, AI/ML" or "Solutions Architect - Data Engineering" (title exclusions ignored)

### Location

6. Fails "San Francisco, California" against "san francisco" (exact string match instead of the city rule)
7. Passes "Remote - Australia" because "us" matched as a substring
8. Passes a bare "United States" location

### Years

9. Takes `years_required` from "founded 10 years ago" or from the upper bound of "2–4 years"
10. Reads "100+ years of combined experience" as `00` (no left digit boundary)
11. Takes 2 from "BS + 6 years, MS + 4 years, PhD + 2 years of experience" (degree filter ignored)
12. Misses "Master’s" with a curly apostrophe in the degree filter (quotes not normalized)

### Text preparation and skills

13. Collapses an `<li>` requirements list into one sentence, so a blurb phrase in one bullet deletes the whole list, or a non-experience bullet's years get counted
14. Fails to cut at a "Benefits:" heading because of the trailing colon
15. Counts "spark" from the "original creators of Apache Spark™" blurb, or matches skills in content after a cut heading
16. Counts an "R" skill hit from "R&D", or counts "databricks" as a posting skill
17. `skill_overlap.matched` contains a skill that isn't in persona `skills`
18. `rule_verdict` is "relevant" while one check shows `passed: false`
19. Verdicts are paired with the wrong posting: `posting_id` or `posting_title` doesn't match `raw/<run_id>/board.json`, for example from an off-by-one error after sorting

### Claude step

20. Claude's justification cites nothing (a cited-field list is empty) but the line still has `claude_status: "ok"`
21. Claude's output is silently repaired (code fences stripped, casing fixed) instead of failing validation
22. Claude's output fails twice, and the line is dropped or filled in instead of written with `claude_status: "invalid_output"` and logged
23. Labels are swapped or missing: Claude's output is labeled "record", or `claude_verdict` overwrites `rule_verdict`
24. `claude` is invoked from the repo directory, without the pinned `--model`, or with tools enabled; or `claude_model` is missing from the line
25. A prompt containing ™, –, or é reaches Claude mangled (no explicit UTF-8)

### State and runs

26. The baseline run reports any posting as new or writes verdicts
27. Re-evaluates a posting whose ID is already in `seen_ids`, including one that was skipped or failed
28. After a simulated crash mid-run, the re-run's lines and the crashed run's lines are both counted (incomplete runs not ignored)
29. A seeded run makes a network call, writes to `state/state.json`, starts from a copy of the live state instead of empty, or writes a line without `run_mode: "seeded"` and `seeded_from`
30. A raw file in `claude_raw_paths` or `raw/<run_id>/board.json` is missing, or a seeded run's `board.json` differs from `seeded_from`

### Safety and persona

31. The agent's own code fetches `absolute_url` or any host other than `boards-api.greenhouse.io`
32. Emits verdicts for a posting whose requirements text is empty instead of skipping it
33. A persona with a real-looking email (`jordan.lee@gmail.com`) or a non-555 phone passes the persona validator
34. A persona with a skill not in the vocab, a missing field, or an extra field passes the persona validator

### Experiments

35. The hand-label selection, run twice on the same board, produces different `dev` or `held_out` sets
36. The experiment runner reads or writes `state/` or `output/`

## What a failure looks like

2026-10-31: `rule_verdict` marks "Sr. Data Engineer" in Austin, Texas as relevant because Python, SQL, and Spark matched, ignoring both the seniority and location checks.

## Appendix A: `data/persona_resume.json` (fictional)

```json
{
  "name": "Jordan Lee",
  "email": "jordan.lee@example.com",
  "phone": "(555) 010-0142",
  "education": "B.S. Computer Engineering, Example State University (2024)",
  "highest_degree": "bachelors",
  "target_title_keywords": ["machine learning", "ml", "data engineer", "data engineering", "data platform", "data scientist", "ai"],
  "title_exclusions": ["account", "sales", "solutions", "architect", "recruiter", "recruiting", "marketing", "consultant", "customer", "support", "field", "partner", "evangelist", "advocate", "product"],
  "skills": ["python", "sql", "scala", "spark", "airflow", "kafka", "dbt", "bigquery", "gcp", "docker", "kubernetes", "tableau"],
  "years_experience": 2,
  "preferred_cities": ["san francisco", "mountain view", "seattle", "new york", "boston"],
  "remote_ok": true
}
```

## Appendix B: `config/skill_vocab.json` (excerpt; the full file is frozen with this commit)

```json
{
  "version": "v1",
  "skills": {
    "python": ["python"], "sql": ["sql"], "scala": ["scala"], "java": ["java"],
    "spark": ["spark", "apache spark", "pyspark"], "airflow": ["airflow", "apache airflow"],
    "kafka": ["kafka", "apache kafka"], "dbt": ["dbt"], "bigquery": ["bigquery"],
    "gcp": ["gcp", "google cloud"], "aws": ["aws", "amazon web services"],
    "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"], "terraform": ["terraform"],
    "tableau": ["tableau"], "pytorch": ["pytorch"], "tensorflow": ["tensorflow"],
    "golang": ["golang"], "rust": ["rust"], "c++": ["c++"]
  }
}
```

## Appendix C: `config/boilerplate.json` (verify every string against a real `board.json` before committing)

```json
{
  "version": "v1",
  "cut_headings": ["benefits", "pay range transparency", "our commitment to diversity and inclusion", "compliance"],
  "drop_sentence_phrases": ["original creators of", "founded by the original", "databricks is the data and ai company"]
}
```
