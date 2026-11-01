# CONTRACT — Job-Search Agent 1 (Anisha Gaikar)

Committed (`509e6ca`) before any run, test or label, but drafted together with the code, not before it (see FRICTIONAL.md). Claude drafted the wording from my decisions; I reviewed and own every line. Date: 2026-10-31.

## In
- A board name: one Greenhouse board slug (default `klaviyo`), fetched from `boards-api.greenhouse.io` only.
- A résumé as JSON: `persona/resume.json` (fictional persona "Nadia Okafor"; `@example.com`, 555 phone). Needs `target_titles`, `skills.core`, `max_years_experience`.
- The state file `state/seen.json` from the last run (absent on the first run).

## Out (for each posting that is NEW since the last run)
1. **RECORD (rule):** `relevant` / `not_relevant` + a justification naming the résumé fields (`target_titles`, `skills.core`, `max_years_experience`) and posting fields (`title`, `text`) behind it. Anyone can recompute it.
2. **JUDGMENT (Claude):** the same verdict question answered by Claude under `prompts/revised.txt`, as one JSON object `{verdict, resume_fields, posting_quotes, reason}`. Labelled as a judgment, never as a fact. Anything else is rejected by the validator and shown as `INVALID`.

## Refuses
- Fetching any host not on the allow-list (`boards-api.greenhouse.io`), or a malformed board slug (refused before any network call).
- Showing a real résumé on screen or on GitHub: only the fictional persona is ever loaded.
- Presenting Claude's judgment as a fact: every Claude verdict carries `"kind": "JUDGMENT (Claude)"`.
- Applying, emailing, messaging, or logging in anywhere.

## The rule (predictable by hand)
A posting is **relevant** only if all three hold, otherwise **not_relevant**:
1. Its **title** contains *analyst*, *analytics* or *business intelligence*.
2. Its title + text name **at least 2** of `skills.core` (SQL, Python, Tableau, Power BI, Excel, dbt, Looker, Snowflake, A/B testing, ETL), whole-word, case-insensitive.
3. The **largest "N years"** number in the text is **≤ 3** (`max_years_experience`), or no years are stated.

## Labeling rule (for my 20 hand labels — I apply this myself, by reading)
I mark a posting `relevant` if I, as this persona (MSIS student, entry-level BI/data analyst), would spend time applying: the job is an analyst role I could do with these skills and it is open to someone with ≤ 3 years' experience. I read the whole posting, not keywords.

## Wrong versions my tests must catch
1. **Labels paired with the wrong postings** (verdict list shifted by one) — `tests/test_agent.py::RuleJudge.test_wrong_version_1…`.
2. **A justification that cites nothing** (empty `posting_quotes`), or a quote not in the posting — `ClaudeContract.test_rejects`.

## What a failure looks like (written before running anything)
> 2026-10-31: A failure is a posting reported as new that was already seen, a posting that is new but not reported, or a Claude verdict shown without its JUDGMENT label or accepted without passing the validator.

## Appendix: worked examples (added 2026-10-31, ~6:35 pm, AFTER the runs; the rule above is unchanged)
These show how to apply the rule by hand. The first three are real Klaviyo postings from run 1; the fourth is the constructed posting used in `tests/test_agent.py`.
| posting | (1) title | (2) skills.core named | (3) max years | verdict |
|---|---|---|---|---|
| 7989990003 Senior CS Compensation Analyst (real) | analyst ✔ | 6: SQL, Python, Tableau, Excel, Looker, ETL ✔ | 5 ("3-5 years") > 3 ✘ | not_relevant |
| 7986841003 Lead Treasury Analyst (real) | analyst ✔ | 1: Excel ✘ | 8 > 3 ✘ | not_relevant |
| 8013125003 Account Executive, Large Enterprise (real) | ✘ | 0 ✘ | 10 > 3 ✘ | not_relevant |
| "Data Analyst" (CONSTRUCTED test posting: "You will use SQL and Tableau daily. 1-2 years of experience.") | analyst ✔ | 2: SQL, Tableau ✔ | 2 ≤ 3 ✔ | relevant |
