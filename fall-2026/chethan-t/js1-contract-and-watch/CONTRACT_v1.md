# CONTRACT — Job-Search Agent 1

Written 2026-10-31, before any code was written or run.

## In
- **Board token** (e.g. `Klaviyo`) and **résumé path**: read from `config.json`;
  either can be overridden on the command line.
- **Résumé**: a JSON file with `personal`, `education`, `experience`,
  `skills`, and `target`. The agent rejects a résumé missing any of these.
- **Fetched data**: the board's postings from
  `https://boards-api.greenhouse.io/v1/boards/<token>/jobs?content=true`,
  including descriptions.
- **Needs**: network access to `boards-api.greenhouse.io` only, and a
  writable state file listing previously seen posting ids.
- Each posting `id` is treated as a separate posting, even when several
  share a `requisition_id`.

## Out
For each posting new since the last run, the agent returns two verdicts:

1. **Rule verdict** (labeled `record`): from the written rule below.
2. **Claude verdict** (labeled `judgment`): Claude's judgment, not fact.

Each verdict has:
- `posting_id`, `title`
- `verdict`: one of `relevant`, `not_relevant`
- `resume_fields`: every résumé field checked (e.g. `target.roles`)
- `posting_fields`: every posting field checked (e.g. `title`, `location.name`)
- `reason`: one or two sentences connecting those fields

Results are printed to the terminal and written to `results/<run_date>.json`.
On a baseline run, no postings are reported as new.

## Refuses
The agent will not:
1. **Fetch any host not on the allow-list.** The allow-list is
   `boards-api.greenhouse.io`; any other host raises an error before a
   request is made.
2. **Use or show a real résumé.** It refuses to run unless the résumé's
   email ends in `@example.com` and its phone contains `555`.
3. **Present Claude's judgment as fact.** Every Claude verdict is labeled
   `judgment`; every rule verdict is labeled `record`.
4. **Accept malformed Claude output.** If a response fails the validator,
   the agent retries once; if the retry also fails, it records
   "no Claude verdict" for that posting rather than guessing.
5. **Apply, email, message anyone, or log in anywhere.**

## The rule
A posting is `relevant` only if ALL checks pass; otherwise `not_relevant`.

1. **Role**: `title` contains (case-insensitive) one of: "software engineer",
   "software developer", "full stack engineer", "full stack developer",
   "frontend engineer", "frontend developer", or the whole words "SDE" or "SWE".
2. **Seniority**: `title` contains none of (whole words, case-insensitive):
   "Staff", "Principal", "Manager", "Director".
3. **Experience** (only if `title` contains "Senior" or "Lead"):
   - Find every phrase in `content` where a number (digits, e.g. "4",
     "3+", "3-5") is followed by "year" or "years" and the word
     "experience" appears in the same sentence.
   - For a range, use the smaller number.
   - Take the smallest number across all such phrases.
   - Relevant only if that number is 3 or fewer.
   - If no such phrase exists, the posting is `not_relevant`.
4. **Location**: at least one location in `location.name` (split on ";")
   is in the US: it ends in a two-letter US state code, or contains
   "United States", "USA", or "US" as a whole word.

### Fields each check uses

| Check      | Posting field   | Résumé field                       |
|------------|-----------------|------------------------------------|
| Role       | `title`         | `target.roles`                     |
| Seniority  | `title`         | —                                  |
| Experience | `content`       | `experience` (dates total ~3 years)|
| Location   | `location.name` | `target.locations`                 |

## Wrong versions
1. **"US" matched as a substring.** A version that checks whether
   `location.name` contains "us" (case-insensitive) would mark
   "Brussels, Belgium" as a US location. Test: a posting with title
   "Software Engineer" and location "Brussels, Belgium" must be
   `not_relevant`.
2. **Justification cites no fields, or fields the rule never checked.**
   A version that returns `"reason": "Good match"` with empty
   `resume_fields`/`posting_fields`, or cites a field like `department`
   that no check uses. Test: for every verdict, `posting_fields` must
   equal exactly the posting fields the rule evaluated, and
   `resume_fields` must equal exactly the résumé fields it used.

## What a failure looks like
2026-10-31: Failure = any posting I hand-labeled `relevant` before running
the agent is marked `not_relevant` by the agent's rule verdict.
