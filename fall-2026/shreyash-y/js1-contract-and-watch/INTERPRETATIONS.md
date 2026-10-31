# Interpretations of CONTRACT.md

*Drafted by Claude Code on 2026-10-28, after CONTRACT.md was committed (commit `7c8f9e5`) and before any code was written. CONTRACT.md is Shreyash's and is not edited; this file records how each phrase in it was made computable, so a TA can apply the rule by hand and get the same verdict as `jsagent/rule.py`. Where a choice was made that the contract does not force, it is marked **choice**. Shreyash was asked on 2026-10-28 and again on 2026-10-30 to accept or change the two main choices (the experience reading and state-limited remote) and did not answer before submission, so they stand as Claude's choices, unreviewed.*

**Known defects found after run 2 (not fixed in this layer; see FRICTIONAL.md):** the experience pattern misses a requirement whose "experience" word is missing or more than 60 characters away (postings 8083703, 8319419), and condition 3 trusts a "Remote" office tag over an ad that says hybrid (6555819, 8250366) or limits remote to states without Massachusetts (8172223). In every one of these cases the verdict is still Not Relevant, because other conditions fail too.

The words "posting.X" below are the Greenhouse field names the code reads. Greenhouse has no "required skills" or "minimum experience" field: both are read out of `content` (the ad text), as described in conditions 4 and 5.

## Reading a posting

- `posting.id`: Greenhouse `id`. With the board token (`oscar`), it is the key for everything.
- `posting.title`: Greenhouse `title`.
- `posting.departments`: the `name` of every entry in Greenhouse `departments`.
- `posting.location`: Greenhouse `location.name`.
- `posting.offices`: the `name` of every entry in Greenhouse `offices`.
- `posting.content`: Greenhouse `content`. This is HTML that has been escaped once. It is unescaped, its tags are stripped, it is unescaped again, and whitespace is collapsed.

## Condition 1, title

The title passes if it contains one of the nine phrases. Matching is case-insensitive, and the phrase must start and end on a non-letter, non-digit boundary, so "AI Engineer" does not match inside "MAI Engineer", and "ML Engineer" does match "AI/ML Engineer". **Choice:** `Fullstack` (one word, as Oscar writes it) is not treated as `Full Stack`. Oscar's two Fullstack titles also contain "Software Engineer", so this choice changed no verdict on the boards seen.

## Condition 2, department

The posting passes if any `posting.departments` name equals one of the six names. The comparison ignores case and surrounding spaces, and it is not a substring match. Oscar's `Data` department is **not** `Data Science`, so it fails. An empty department list fails as missing.

## Condition 3, location

The posting passes if either of these holds:

- **(a)** `posting.location` contains the word `Boston`; or
- **(b)** `resume.remote_ok` is true, `posting.location` or an office name contains the word `Remote`, and the posting names the United States somewhere: `United States`, `U.S.`, `USA`, the word `US` in the location, an office or the content, or an office written `Remote (<a U.S. state>)`.

**Choice:** a remote job limited to one state (Oscar writes `Remote (Florida)`) still counts as remote within the United States, because the contract says "within the United States" and does not say which state. This is a literal reading. For a Boston applicant, a Florida-only remote job may in practice need a move, and that is not caught. It is listed under "Not checked" in the README.

## Condition 4, skills

At least two of the terms in `resume.skills` must appear in `posting.content`. Matching is case-insensitive and on whole terms, with the same boundary rule as condition 1. So `Java` does not match `JavaScript` and `SQL` does not match `PostgreSQL`. **Known weakness, kept as written:** case-insensitive whole-word matching makes `React` match the verb "react", and `RAG` match the word "rag".

## Condition 5, experience

Every phrase in `posting.content` of the form `N years`, `N+ years`, `N-M years`, or `N to M years` is collected when the word `experience` appears within 60 characters after it. N can be digits or a number word from one to fifteen, and for a range the number taken is N. **Choice:** the posting's minimum required experience is the **largest** N collected, because each stated requirement is one the applicant must meet. Example: a posting that says "5+ years of software experience… 2+ years of experience with LLMs" requires 5. The condition passes if that number is at most `resume.experience_years` (3 for Alex). If no phrase is found, it passes, and the justification says so ("no experience requirement stated"), as the contract requires. **Known weakness:** "preferred" and "required" are not told apart, and a degree offered as an alternative to the years ("a bachelor's degree or 6+ years") still counts the years.

## Condition 6, exclusions

The posting fails if any one of these holds:

- `Director`, `Staff`, `Principal`, `Manager`, or `Lead` appears as a whole word in `posting.title`, ignoring case. `Leader` and `Management` are not whole-word `Lead` or `Manager`.
- **Unpaid internship:** the word `unpaid` appears in the title or content.
- **Contract-only:** the title contains the word `Contract` or `Contractor`, or the content contains `contract-only`, `contract only`, `contract position`, `contract role` or `1099`.
- **Relocation:** the content contains `must relocate`, `required to relocate`, `requires relocation` or `relocation is required` / `relocation required`, and condition 3(a) (Boston) did not pass.

`resume.exclusions` is cited as the résumé field behind this condition.

## Missing information

If the title, department list, location or content is empty, the condition that reads it fails with the word "missing" in its line. Condition 5 is the exception: the contract tells it to pass when no requirement is stated.

## New-posting detection

- **Seen ids.** The state file keeps, for each board token, every posting id ever seen. "The previous snapshot" is read as "every id previously observed", so a posting that disappears for a day and comes back is not reported as new again. **Choice:** the contract could also be read as "the last run's ids only". The union was picked so that a flaky response cannot re-announce old postings.
- **Baseline.** The first run for a board records the ids and reports zero new postings.

## Justification format

Every verdict carries one line per condition. Each line has the condition number, PASS or FAIL, the `resume.<field>` and `posting.<field>` names it read, and the value that decided it. A Not Relevant verdict names the failed conditions first. Wrong version 2 ("a justification that cites nothing") is tested by checking that every line names at least one real `resume.` field and one real `posting.` field.
