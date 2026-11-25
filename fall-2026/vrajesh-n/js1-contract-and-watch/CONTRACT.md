# CONTRACT — Early Bird, JS1 slice

**Written by:** Vrajesh N. · **First written:** 2026-10-24 · **OPEN items closed:** 2026-10-31, before any code existed
**Scope of this slice:** one public board, one fictional resume (`data/resume/rohan-desai.example.json`), new postings only, every verdict justified.

> How this was written: the 2026-10-24 lines are my own words from chat; Claude placed them under the headings and fixed spelling only.
> On 2026-10-31, Claude listed the OPEN items as multiple-choice questions with options drawn from my saved snapshots, and I picked one answer for each. The picked option is written below and marked *(chosen 10-31)*. The third refusal uses the assignment's own wording.

## In
- Board: Ashby. *(chosen 10-31)* Commure, `https://api.ashbyhq.com/posting-api/job-board/commure`.
- Allow-list: `api.ashbyhq.com` only.
- Resume: one JSON file, fictional persona only (see Refuses #2).
- State: `data/state/seen.json`, holding the posting ids already seen.
- Relevant means: Role type: Software Engineer, United States, Entry Level.

## Out
For each **new** posting (id not in `seen.json`), two verdicts:
- `verdict`: `relevant` or `not_relevant` *(chosen 10-31)*
- `justification`: a sentence, plus `resume_fields` (at least one, e.g. `education[0].degree`) and `posting_fields` (at least one, e.g. `title`). Every cited field must actually exist in the resume or the posting. Otherwise the verdict is rejected.
- `kind`: `record` for the written rule (anyone can recompute it) and `judgment` for Claude (labeled with the model and date).

My words, 10-24: "The verdict is whether the job is actually a software job and the resume is a good match to the job."

## Refuses
1. Off-allow-list hosts: if asked to fetch a website not on the allow-list, it says it is not able to fetch the website.
2. Real resume: if someone tries to use a real resume, it says the system does not accept a real resume. *(chosen 10-31)* A resume counts as fictional only if all three hold: `personal.email` ends in `@example.com`, `personal.phone` contains `555`, and `_comment` contains `FICTIONAL`. Otherwise it is refused.
3. Model judgment as fact *(assignment wording)*: Claude's verdict is never written as the record and is never shown without the label `judgment`. If Claude's output does not match the fixed format, it is rejected and not shown at all.
4. It never applies, emails, messages, or logs in anywhere.

## Rule (hand-predictable relevance)
My words, 10-24: Jobs that contain frontend engineer, backend engineer, full stack engineer, software engineer, software developer are the ones. Sales, business, health are not the type. If location is missing, or if it requires sponsorship, or if it is outside the US, it is a blocker.

Made exact *(chosen 10-31)*. A posting is `relevant` only if **all** of R1–R4 pass. Otherwise it is `not_relevant`, and the justification names the first check that failed.

| # | Check | Posting field | Resume field |
|---|---|---|---|
| R1 role | `title` contains (case-insensitive) one of: software engineer, software developer, full stack / fullstack / full-stack engineer, backend / back-end engineer, frontend / front-end engineer | `title` | `education[0].degree` |
| R2 level | `title` contains none of: senior, sr, staff, principal, lead, manager, head, director; **and** `descriptionPlain` does not ask for 3 or more years ("3+ years", "5 years", "4-6 years" count, using the smallest number) | `title`, `descriptionPlain` | `experience` (empty = new grad) |
| R3 location | `address.postalAddress.addressCountry` is USA / United States / US. Missing or any other country = blocker | `address.postalAddress.addressCountry` | `personal.location` |
| R4 sponsorship | blocker only if the resume says `work_authorization.needs_sponsorship: true` **and** `descriptionPlain` says the company will not sponsor ("unable to sponsor", "no sponsorship", "not sponsor", "without sponsorship") | `descriptionPlain` | `work_authorization.needs_sponsorship` |

*(chosen 10-31)* Rohan's resume gets `work_authorization.needs_sponsorship: true`, since he is an MS student from Mumbai.

## Wrong versions the tests must catch *(chosen 10-31)*
1. **Baseline reports all as new:** the first run, with no state, calls every posting new instead of reporting 0. Caught by `test_baseline_reports_zero_new`.
2. **Seen-state never saved:** the state file is not written, so every run behaves like a first run, and a repeat run on the same snapshot reports postings as new again. Caught by `test_state_is_saved_and_repeat_run_is_zero`.

My 10-24 note: "That there is no mention of H1B sponsorship." This became check R4.

## Failure (dated, written before the first run)
- 2026-10-24: Failure would look like no jobs found.
- Clarified 2026-10-31, still before the first run: either one counts. (a) The fetch or parse returns zero postings, or (b) the second run (10-23 snapshot) reports zero new even though the board changed between the two days.

## Not in this slice
- Connection reach-out and stuff.
