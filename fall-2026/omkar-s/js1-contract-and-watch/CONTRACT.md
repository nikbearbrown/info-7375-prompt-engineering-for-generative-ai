# CONTRACT — Job-Search Agent 1

**Who wrote what.** The decisions in this file were made by Omkar Salian in a Claude Code chat on **2026-10-25 (about 20:30 UTC)**, before any agent code existed. Claude Code asked them as multiple-choice questions. Omkar picked the options, and Claude Code typed his picks into this file. Lines marked **[Omkar, verbatim]** are his own typed words. Lines marked **[Claude, transcription]** restate a choice he made. Details his choices did not settle are marked as Claude's interpretation; Claude Code filled them in so the rule could be coded, and Omkar confirmed them ("nothing" to change, 2026-10-26 01:51 UTC; "confirm" on the DE detail, 2026-10-26T16:39:54Z).

Board: **Klaviyo** (Greenhouse). Persona: **Aarav Patel**, fictional. Both were chosen by Omkar on 2026-10-25.

---

## In

> [Omkar, verbatim, 2026-10-25 22:58 UTC, replying to the In/Out summary below] "yes"

[Claude's wording, which Omkar approved with that "yes"]
- A board token. Only `klaviyo` is used in this assignment, and it must match `^[a-z0-9-]+$`.
- A résumé as JSON in the shape of the Reallocation Engine example personas. It must be a fictional persona: every e-mail ends in `@example.com`, every phone number contains `555`, and `_comment` contains `FICTIONAL`.
- A state file path. It is created on the first run.
- Needs: Python 3.10+ (standard library only), and HTTPS access to `boards-api.greenhouse.io` only. The Claude judge also needs the `claude` CLI, signed in.

## Out

[Claude's wording, which Omkar approved with the "yes" above] For each posting that is **new since the last run**, the agent returns one record holding:
- `posting_id` and `title`, plus `absolute_url` so the posting can be checked by hand.
- `rule` — a **record**: `verdict` (`relevant` / `not_relevant`), and one justification line per rule clause. Each line names the résumé field and the posting field it compared, and the values it found.
- `claude` — a **judgment**, labelled as one: a `verdict`, the résumé fields and posting fields it cites, and a short reason. If Claude's output fails the validator, this is `rejected` together with the reason; it is never coerced into a verdict.

The first run (no state file) is a baseline: it records every id and reports **zero** new postings.

## Refuses

> [Omkar, verbatim, 2026-10-25 22:58 UTC] "minimum". Nothing is added beyond the assignment minimum.

[Assignment minimum]
1. It never fetches any host that is not on the allow-list (`boards-api.greenhouse.io`). It follows no redirects.
2. It never shows a real résumé on screen or on GitHub. Any résumé that does not pass the fictional-persona check is refused.
3. It never presents a model's judgment as a fact. Every Claude verdict is printed under a "judgment" label, separate from the rule's "record".
4. It never applies, emails, messages anyone, or logs in anywhere. This comes from the assignment's privacy section.

## The rule

[Claude, transcription of Omkar's choices on 2026-10-25] A posting is **relevant** for Aarav if and only if **all three** of these hold. If any one fails, the verdict is `not_relevant`.

| Clause | Résumé field | Posting field | Passes when |
|---|---|---|---|
| A. Role | — (Aarav's `experience[].title` are both "Software Engineer…") | `title` | `title` contains `Software Engineer` |
| B. Location (**v2**) | `personal.location` = "Boston, MA" | `location.name`, `offices[].location` | the posting is in the **US**: `location.name` contains `Boston`; **or** it is a US remote location; **or** it is a "City, ST" US location and `offices[]` has an office in the United States. *(v1, 2026-10-25, was Boston or US remote only. Superseded, see the change log below.)* |
| C. Skills | `skills.languages`, `skills.backend_automation`, `skills.database_cloud`, `skills.devops_cicd` (15 skills) | `content` | **at least 2** distinct skills from those lists appear by name in `content` |

There is **no seniority gate** (Omkar's choice). "Senior Software Engineer…" and "Principal Software Engineer" pass clause A. `skills.familiar_with_not_shipped` (Rust, Terraform) **never counts** for clause C.

> **Why this rule** — [Omkar, verbatim, 2026-10-25 22:58 UTC; typos kept as typed]
> - Why "Software Engineer": "because as a fresher i  want that particular role and also i have worked as a SDE before so want to grow more"
> - Why Boston or remote: "Boston is a very familiar city to me right now, but i am also open to relocate wherever necessary"
> - Why 2 skills: "better to ook for skills i am good at and once i start developing other skills i will add that too"
> - Why no seniority gate: "i already have a 2 years of professional experience in India after that again i started my student life which led to gap in professional experience so i would like to start with basucs again for a smooth start"

**Details his choices did not settle** [Claude's interpretation. Asked to confirm or name one to change, Omkar replied "nothing" at 2026-10-26 01:51 UTC, so all five stand.]
- **Matching:** all matching ignores upper and lower case.
- **Clause B, US remote:** `location.name` contains `Remote` **and** one of `US`, `USA`, or `United States`. On the 2026-10-25 board snapshot, no Klaviyo posting is remote, so this branch is untested on live data.
- **Clause B, several locations:** a posting listing several locations ("Boston, MA; Denver, CO") passes if any one of them passes.
- **Clause B v2, which suffixes count as US** [Claude, 2026-10-26. Omkar replied "confirm" at 2026-10-26T16:39:54Z]: a two-letter suffix alone is ambiguous. Klaviyo writes Munich as "Munich, DE", and DE is also Delaware. So "City, ST" counts as US only when the posting's `offices[].location` includes one ending in "United States". Boston and US remote pass on `location.name` alone.
- **Clause C, cleaning the text:** `content` is HTML-unescaped, stripped of tags, and unescaped again (Klaviyo double-escapes it).
- **Clause C, whole words only:** a skill counts only as a whole word. `Java` does **not** match inside `JavaScript`, and `SQL` does **not** match inside `PostgreSQL` or `MSSQL`. Each distinct skill counts once, however often it appears.

**Predicting a verdict by hand:** read the title (A), read the location (B), then search the posting text for the 15 skill names as whole words (C). Two or more hits, plus A and B, means relevant.

## Change log

**v2 — 2026-10-26 01:51 UTC.** After the whole-board dry run of v1 (`experiments/whole-board-2026-10-25-contract-v1.md`), Claude Code raised three points with Omkar. His answers, verbatim:
- Seniority (13 of the 18 relevant postings under v1 were Senior, Lead or Principal, against his "start with basics" reason). He chose to "keep no seniority gate". **Clause A is unchanged.** He gave no further reason.
- Privacy (his "why" lines describe his own real background, not Aarav's): "i would like to keep my background only". **His reasons stay as written.**
- Relocation (he said "open to relocate wherever necessary", but v1 passed only Boston): "widen it with boston". Asked which locations, he chose "Any US location". **Clause B becomes v2.**

When it changed: the only v1 runs were the live baseline (it reports nothing by design) and the v1 whole-board dry run. No watch verdict was ever issued under v1. The v2 whole-board run has 19 relevant postings out of 160 (`experiments/whole-board-2026-10-25-contract-v2.md`), and 13 of those 19 are still senior, lead or principal titles.

## Wrong versions the tests must catch

[Claude, transcription of Omkar's two picks on 2026-10-25]
1. **Labels shifted to the wrong posting.** The verdicts are computed correctly, but each one is attached to its neighbour's `posting_id` (an off-by-one pairing). A test must fail when a verdict's justification describes a title or location that is not the posting it is paired with.
2. **Baseline reports everything new.** On the first run, with no state file, the agent reports every posting as new instead of none. A variant is a state file that is not updated, so the second run re-reports old postings. A test must fail on either.

Both are built as mutants in `tests/mutants/`. `python3 tests/run_mutants.py` checks that the test suite **fails** against each of them.

## What a failure looks like

> [Omkar, verbatim, 2026-10-25 22:58 UTC — written before any test, fetch or Claude call had run; only a syntax check and the pre-build curl snapshot preceded it]
> "It failed if sometimes it gives job posting not related to field but similar to a particular field"

---

### Status of the gate
- [x] Failure sentence: 2026-10-25 22:58 UTC, before any run.
- [x] Why this rule; In/Out "yes"; Refuses "minimum".
- [x] Interpretation details: "nothing" to change (2026-10-26 01:51 UTC).
- [x] v2 detail (DE/state-code check against `offices[]`): "confirm" (2026-10-26T16:39:54Z).
