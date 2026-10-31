# CONTRACT — Job-Search Agent 1 (v2)

Written: 2026-10-31, before any code was written or run.
Previous version: CONTRACT_v1.md (kept for reference).

## In
- **Board name**: the Greenhouse board to watch (e.g. `klaviyo`).
- **Résumé**: a JSON file of a fictional persona (Arjun Mehta).
  Target roles and locations are read from it.
- **Seen-postings file**: the list of posting ids from the last run,
  so the agent can tell what's new. Empty on the first run.
- **Internet access**: only to `boards-api.greenhouse.io`.
- **Claude access**: Claude Code CLI (`claude -p`), using my existing login.
  Optional: without it, only the rule verdict is produced.

## Out
For each posting new since the last run (none on the first, baseline run):

- **Which job**: `posting_id`, `title`, `location`, `url`.
- **Work-authorization flags** (from the description text):
  - `sponsorship`: `no_sponsorship` / `mentioned` / `not_mentioned`
  - `e_verify`: `mentioned` / `not_mentioned`
  - `citizenship_or_clearance_required`: `yes` / `no`
  These are text matches, not legal facts.
- **Rule verdict** (labeled `record`) and **Claude verdict** (labeled
  `judgment`), each with:
  - `verdict`: `relevant` / `not_relevant`
  - `resume_fields`: the résumé fields used
  - `posting_fields`: the posting fields used
  - `reason`: one or two sentences connecting them

Printed to the screen and saved to `results/<date>.json`.

## Refuses
The agent will not:
1. **Fetch any other website.** Only `boards-api.greenhouse.io` is allowed;
   any other host stops with an error before a request is made.
2. **Use a real résumé.** It refuses to run unless the résumé's email ends
   in `@example.com` and its phone contains `555`.
3. **Present Claude's opinion as fact.** Claude's verdict is always labeled
   `judgment`; the rule's verdict is labeled `record`.
4. **Apply, email, message anyone, or log in anywhere.**
5. **Write outside its own files.** It writes only the seen-postings file,
   raw responses, and results inside the project folder.

## The rule
A posting is `relevant` only if ALL checks pass; otherwise `not_relevant`.
All text matches are case-insensitive. `content` is read after removing HTML tags.

1. **Role** (posting `title` vs résumé `target.roles`): pass if `title`
   contains one of "software engineer", "software developer",
   "full stack engineer", "full stack developer", "frontend engineer",
   "frontend developer", or the whole words "SDE" or "SWE".
2. **Seniority** (posting `title`): fail if `title` contains any of the
   whole words "Staff", "Principal", "Manager", "Director".
3. **Experience** (posting `content` vs résumé `experience`, about 3 years);
   applies only if `title` contains "Senior" or "Lead":
   - Find every sentence in `content` with a number in digits ("4", "3+",
     "3-5") followed by "year" or "years", and the word "experience".
   - For a range, use the smaller number. Take the smallest number found.
   - Pass if that number is 3 or less. Fail if it's more than 3, or if no
     such sentence exists.
4. **Location** (posting `location.name` vs résumé `target.locations`):
   pass if at least one location (split on ";") ends in a two-letter US
   state code, or contains "United States", "USA", or "US" as a whole word.
5. **Work authorization** (posting `content` vs résumé `work_authorization`):
   fail if `content` contains any of: "unable to sponsor", "will not sponsor",
   "not able to sponsor", "do not sponsor", "does not sponsor",
   "without sponsorship", "security clearance", or any citizenship
   requirement: "must be a U.S. citizen", "U.S. citizens only",
   "U.S. citizenship is required", "U.S. citizenship required",
   "requires U.S. citizenship", "must be a U.S. person". Otherwise pass.
   - "U.S." and "US" are treated the same (periods ignored).
   - The word "citizenship" alone does NOT fail a posting, because
     equal-opportunity footers mention "citizenship status".
   - Output flags: `sponsorship` = `no_sponsorship` if a fail phrase above
     about sponsorship matched; `mentioned` if "sponsor" appears otherwise;
     else `not_mentioned`. `e_verify` = `mentioned` if "E-Verify" appears.

## Wrong versions
Each is a plausible-but-wrong implementation that my tests must catch.

1. **"Citizenship" matched as a single word.**
   - What it does wrong: fails any posting whose equal-opportunity footer
     mentions "citizenship status".
   - Why it's plausible: "citizenship" looks like the obvious keyword.
   - Test: a posting titled "Software Engineer", location "Boston, MA",
     whose content says "regardless of citizenship status" → `relevant`.

2. **"US" matched as a substring.**
   - What it does wrong: "Brussels, Belgium" contains "us", so it passes
     the location check.
   - Why it's plausible: a simple `"us" in location` check looks correct.
   - Test: a posting titled "Software Engineer", location
     "Brussels, Belgium" → `not_relevant`.

3. **Justification cites nothing, or the wrong fields.**
   - What it does wrong: returns `"reason": "Good match"` with empty
     `resume_fields` / `posting_fields`, or cites a field no check used.
   - Why it's plausible: the verdict itself can still be correct.
   - Test: for every rule verdict, `posting_fields` and `resume_fields`
     equal exactly the fields of the checks that were applied:
     Role → `title` / `target.roles`; Seniority → `title`;
     Experience (Senior/Lead only) → `content` / `experience`;
     Location → `location.name` / `target.locations`;
     Work authorization → `content` / `work_authorization`.

4. **Baseline run reports everything as new.**
   - What it does wrong: on the first run, every posting is reported as new.
   - Why it's plausible: with an empty seen-postings file, every id is
     technically unseen.
   - Test: empty seen-postings file + one fetch of 3 postings → 0 new
     postings reported, and all 3 ids saved to the seen-postings file.

## What a failure looks like
2026-10-31: Failure = the agent's rule verdict disagrees with my hand label
on any posting, either a posting I labeled `relevant` marked `not_relevant`
(a missed opportunity, the worse error) or a posting I labeled
`not_relevant` marked `relevant`.
