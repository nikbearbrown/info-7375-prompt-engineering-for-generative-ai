# CONTRACT — Job-Search Agent 1: the contract and the watch

## Executive summary

This contract defines, before any code exists, what my job-search agent takes in, what it must return, what it refuses to do, and the exact rule it uses to call a posting relevant. A TA should be able to apply the rule by hand and predict every verdict. It also names two plausible-but-wrong implementations that my tests must catch, and one dated sentence saying what failure looks like.

- **Written:** 2026-10-30, before any code was written or any fetch was run for this assignment.
- **Authorship:** the relevance rule, its seven refinements, and the failure conditions are mine. Claude integrated and refined the wording into this document.

---

## 1. In

| Input | Form | Notes |
|---|---|---|
| Board | a Greenhouse board token: `pinterest` | Fetched from `https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true` (public, no login) |
| Résumé | a JSON file, `persona/resume.json` | **Fictional persona only.** Required fields: `name`; `email` (must end in `@example.com`); `phone` (must use the `555` exchange); `location`; `target_roles[]`; `experience_years` (number); `education[]` (each with `degree`); `work_authorization` (`country`, `us_citizen`, `needs_sponsorship`); `skills[]` (non-empty list of strings). Every rule check below reads one of these fields. |
| State | `state/seen_ids.json` | Posting ids already seen. If the file is absent, this run is the **baseline**. |
| Allow-list | `config/allowlist.json` | Exactly one host: `boards-api.greenhouse.io` |

The agent needs Python 3 and network access to the allow-listed host. The Claude judge additionally needs the Claude Code CLI, logged in.

## 2. Out

Each run saves the raw board response unchanged as evidence (`evidence/<UTC timestamp>-pinterest.json`) and updates the state file. For **each new posting** it returns one record:

| Field | Meaning |
|---|---|
| `posting_id`, `title`, `location`, `url` | copied from the board response |
| `rule_verdict` | `relevant` or `not_relevant`, labelled **record** (anyone can recompute it from the rule below) |
| `rule_reasons[]` | one entry per check R1–R8: `check`, the **posting field** used, the **résumé field** used (or `—` when the check uses no résumé field), the evidence found, and `pass`/`fail` |
| `claude_verdict` | `relevant` or `not_relevant`, labelled **model-judgment**, never presented as fact |
| `claude_justification` | must name at least one résumé field and one posting field; otherwise the validator rejects it |

**The baseline run reports zero new postings.** Every id in the baseline response is stored as seen.

## 3. Refuses

The agent will not:
1. fetch any host that is not on the allow-list;
2. read, show, or write a real résumé. It validates the persona first, and stops if the email is not `@example.com` or the phone is not a `555` number;
3. present Claude's verdict as a fact. It is always labelled `model-judgment` and kept separate from the rule verdict;
4. report a posting that is not in that run's saved raw response;
5. apply to any job, email or message anyone, or log in anywhere;
6. accept a Claude answer that does not match the fixed output format. It is rejected, not repaired or guessed.

## 4. The rule (how a posting is judged relevant)

A posting is **relevant** only if **all eight checks pass**.

- Text matching is case-insensitive.
- A word match means whole words only, so "Lead" does not match "Leader".
- Phrase lists below are **complete**: only the listed phrases count. A requirement worded any other way is not detected. That is a known limit, not a judgment call.

Each check names the **résumé field** that makes it matter for this person and the **posting field** it reads.

| # | Check | Résumé field | Posting field | Passes when |
|---|---|---|---|---|
| **R1 Title family** | the title is a role this person targets | `target_roles[]` | `title` | the title contains at least one `target_roles` entry. For this persona: `Data Analyst`, `Business Intelligence`, `Analytics`, `Business Analyst`, `Product Analyst` |
| **R2 Not senior** | a 0-year candidate is not senior | `experience_years` | `title` | the title contains none of these words: `Senior`, `Sr.`, `Staff`, `Principal`, `Lead`, `Director`, `Head`, `Manager`, `III` |
| **R3 Work country** | the job is in the country the person can work in | `work_authorization.country` (= `US`) | `location.name` | the location contains `United States`, `USA` or `US` as a word, or a comma followed by a US state code (the 50 states + `DC`). A location with no country, such as plain `Remote`, **fails**. |
| **R4 Experience** | the stated minimum fits a new graduate | `experience_years` (= 0) | `content` | no stated minimum of **3 or more** years. A stated minimum is any of: `N+ years`, `N or more years`, `at least N years`, `minimum of N years`, `minimum N years`, `N-M years` / `N–M years` / `N to M years` (minimum = N), `N years of`. It fails if **any** matched minimum is ≥ 3. No match passes. |
| **R5 No citizenship / clearance** | applies because the person is not a U.S. citizen | `work_authorization.us_citizen` (= false) | `content` | none of these phrases appears: `U.S. citizen`, `US citizen`, `United States citizen`, `U.S. citizenship`, `US citizenship`, `green card`, `permanent resident`, `security clearance`, `ITAR`. A phrase does **not** count if its sentence also contains `regardless of`, `without regard to` or `discriminate` (equal-opportunity boilerplate). |
| **R6 Sponsorship not ruled out** | applies because the person needs sponsorship | `work_authorization.needs_sponsorship` (= true) | `content` | none of these phrases appears: `will not sponsor`, `won't sponsor`, `unable to sponsor`, `not able to sponsor`, `cannot sponsor`, `do not sponsor`, `does not sponsor`, `not offer sponsorship`, `sponsorship is not available`, `sponsorship not available`, `without sponsorship`, `without the need for sponsorship`, `without requiring sponsorship`, `no sponsorship` |
| **R7 Degree** | the person's highest degree is a master's | `education[].degree` | `content` | no sentence contains (`PhD`, `Ph.D.`, `doctorate` or `doctoral`) together with (`required`, `requires` or `must`) unless it also contains `preferred` |
| **R8 Skills** | at least two of the person's skills are asked for | `skills[]` | `content` | at least **2** `skills` entries appear in the description as whole words |

**When a check applies.** Each check applies only when its résumé field makes it relevant, and a check that does not apply passes:
- R2 and R4 apply when `experience_years` < 3.
- R5 applies when `us_citizen` is false.
- R6 applies when `needs_sponsorship` is true.
- R7 applies when no `education[].degree` is a PhD.

For this persona (0 years, not a citizen, needs sponsorship, master's) all eight apply, which is exactly my rule. The same rule gives different verdicts for a different persona, and that is how each justification names both the résumé field and the posting field behind it.

## 5. Wrong versions my tests must catch

Each wrong version could plausibly appear in generated code. A test must fail when I swap it in.

- **W1: verdicts paired with the wrong postings.** Results are joined by list position instead of by `posting_id`, so one posting's verdict and reasons appear under another posting. *Caught by:* a fixture whose postings arrive in a different order from the verdicts; every output record's reasons must quote that same posting's title.
- **W2: a justification that cites nothing.** A rule or Claude justification that names no résumé field or no posting field (e.g. "Seems like a good fit."). *Caught by:* the validator test, which must reject it, and a test that every `rule_reasons` entry names its posting field.

## 6. What a failure looks like

> **2026-10-30:** The agent has failed if any of these happens: (1) the first run reports any posting as new; (2) a later run reports a posting seen in an earlier run as new, or reports the same posting twice; (3) it reports a posting that is not in that run's saved raw response; (4) a posting the rule marks relevant breaks the rule when I recompute it by hand.

## 7. The Claude judge's contract

Claude receives this rule, the persona's `skills[]`, and one posting (`title`, `location.name`, `content`). It must answer with **exactly one JSON object and nothing else**:

```json
{"verdict": "relevant" | "not_relevant",
 "resume_fields": ["skills", "..."],
 "posting_fields": ["title", "..."],
 "justification": "one or two sentences that name the fields above"}
```

The validator rejects any answer that:
- is not valid JSON, or has extra text around it;
- has a `verdict` outside the two values;
- has an empty `resume_fields` or `posting_fields`;
- names a field that does not exist;
- has a `justification` longer than 400 characters.

A rejected answer is recorded as `invalid`, never coerced into a verdict.

---

## Revisions (dated; the text above is unchanged)

### 2026-10-30, after the seeded run: R3 and Canadian locations

- **What happened.** In the seeded run, the posting "Sr. Data Scientist" (Pinterest id 6659114) had the location `Toronto, ON, CA`. R3 as written passed it, because `, CA` is a US state code (California). In this location, CA means Canada. Claude's justification said "Toronto … not the US"; the rule did not. The final verdict was still `not_relevant` because R1, R2 and R4 failed.
- **Decision (mine).** In a location segment (segments are separated by `;`) that also contains a Canadian province code after a comma (`AB`, `BC`, `MB`, `NB`, `NL`, `NS`, `NT`, `NU`, `ON`, `PE`, `QC`, `SK`, `YT`), a trailing `, CA` means Canada and does not count as a US state.
- **Effect.** `Toronto, ON, CA` fails R3. `San Francisco, CA` and `San Francisco, CA, US; Toronto, ON, CA` still pass.

### 2026-10-30, after hand-labeling: a ninth check, R9 graduation window

- **What happened.** While labeling, I saw that some postings restrict graduation dates. Affirm wants a degree completed "by August 2027 or earlier"; Stripe's intern role wants "graduating in December 2027 or spring/summer 2028". The eight checks ignore this.
- **Decision (mine).** Add **R9**.

| # | Check | Résumé field | Posting field | Passes when |
|---|---|---|---|---|
| **R9 Graduation window** | the person can meet the posting's graduation dates | `education[0].graduation` (earliest) and `education[0].graduation_latest` (latest, e.g. a co-op term) | `content` | The posting states no graduation date, or the person's window overlaps the posting's window. In a sentence containing `graduat` or `complete … degree`: dates are `Month YYYY` or `spring/summer/fall/winter YYYY` (spring = May, summer = Aug, fall = Dec, winter = Feb). If the sentence says `or earlier`, `by` or `before`, the posting's window ends at its latest date. Otherwise it runs from its earliest date to its latest date. |

- **This persona.** Graduation runs 2027-05 to 2027-12 (May, or December with a co-op).
  - Affirm (window ends 2027-08): overlaps, so it passes.
  - Stripe intern (window 2027-12 to 2028-08): overlaps at 2027-12, so it passes.
- **Labels.** My hand labels were made before this revision and were not changed by it.
