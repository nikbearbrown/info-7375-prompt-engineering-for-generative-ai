# CONTRACT — Job-Search Agent 1

## Executive summary

This is the contract the job-search agent has to meet. It was written **before** any code
existed. The agent watches one company's public job board, finds the postings that are new
since it last looked, and says for each one whether it fits a fictional candidate's
résumé, citing the résumé lines and posting text that produced the verdict. It also asks
Claude for a second opinion, which is always labelled as a model's judgment and never
counted as a fact. Every rule below is meant to be simple enough that a grader could take
one posting and reach the same verdict by hand.

**Provenance of the decisions.** Smit P. chose the board, the persona, the relevance
rule, the two wrong versions, and the failure sentence on 2026-10-24, in a Claude Code
session where Claude offered options and Smit picked from them. Claude wrote those
choices up as this file. Nothing in `src/` or `tests/` existed when this file was
committed (see the git log: this file is the first commit in the folder).

---

## In

| Input | Form | Required |
|---|---|---|
| Board | a Greenhouse board slug — `airbnb` | yes |
| Résumé | a JSON file with `personal`, `education[]`, `experience[]`, `skills{}` | yes |
| State file | JSON list of posting ids already seen (created on the first run) | created if missing |
| Saved response | an earlier raw board response, for a **seeded** run only | optional, labelled |

The résumé used on GitHub and on screen is the fictional persona **Aarav Patel**
(`aarav.patel@example.com`, `(617) 555-0148`) shipped with *The Reallocation Engine*.

What it needs: network access to one allow-listed host, Python 3.10+ (standard library
only), and — for the Claude judge only — the `claude` CLI signed in.

## Out

For every posting that is **new since the last run**, two verdicts:

1. **Rule verdict (a record).** `relevant` or `not_relevant`, plus a justification that is
   a list of citations. Each citation names a résumé field path (e.g.
   `skills.languages[1]`) and value, and the posting field (`title` or `content`) with
   the exact text it matched. A failing check is cited too (e.g. "title contains excluded
   word «Senior»"). Anyone can recompute it.
2. **Claude verdict (a judgment).** Same two-value verdict, in a fixed JSON format, with
   the résumé fields and posting fields it relied on. It is labelled
   `JUDGMENT (model)` everywhere it appears and never overrides the rule verdict.

Plus, per run: the raw board response saved untouched, the updated state file, a JSON run
record, and a Markdown report.

## Refuses

The agent will not:

- **fetch any host not on the allow-list.** The allow-list is exactly
  `boards-api.greenhouse.io`. Any other host (including redirects to one) stops the run
  with an error before a request is made.
- **show a real résumé on screen or on GitHub.** It refuses any résumé whose
  `personal.email` does not end in `@example.com` or whose `personal.phone` does not
  contain `555`. The real résumé stays on Smit's machine and is never an input here.
- **present a model's judgment as a fact.** Claude's verdict is always labelled a
  judgment, kept in a separate field, and never used to compute the rule verdict or the
  counts. A Claude reply that does not match the fixed format is rejected and recorded as
  `REJECTED`, not repaired or guessed.
- **report a posting as new on the first run.** The first run is a baseline.
- **update the state file when a fetch fails.**
- **apply, email, or contact anyone.** It produces a list; the person decides.

## The rule

A posting is **relevant** if and only if all three checks pass:

1. **Title check.** The posting title contains a résumé role keyword. Role keywords are
   the résumé's `experience[].title` values with any parenthesised part removed
   (Aarav: «Software Engineer (Co-op)» → «Software Engineer»; «Software Engineer»).
   Match is case-insensitive and whole-phrase.
2. **Seniority check.** The posting title contains none of the words
   `senior`, `sr`, `staff`, `principal`, `manager` (case-insensitive, whole word).
   `sr` is included only as the abbreviation of senior.
3. **Skill check.** At least **2 distinct** résumé skills appear in the posting title or
   content. Résumé skills are every string in every list under `skills`, **except**
   `skills.familiar_with_not_shipped` (those are honest "not shipped" skills and do not
   count). Match is case-insensitive and whole-word: the skill must not be preceded or
   followed by a letter or digit. So «Java» does not match «JavaScript», «SQL» does not
   match «PostgreSQL», and «Go» would not match «Google». Content is read after HTML
   entities are decoded and tags removed.

Otherwise the posting is **not_relevant**, and the justification names the first check
that failed (and still lists any skills that did match).

**Worked by hand.** «Software Engineer, Payments» whose description mentions Java,
Kafka, and AWS → title ✓, no excluded word ✓, 3 skills ✓ → relevant.
«Senior Software Engineer, Payments», same description → seniority check fails →
not_relevant.

## Wrong versions the tests must catch

1. **Labels paired with the wrong postings.** An implementation that returns the right
   set of verdicts but attaches them to the wrong posting ids (for example, shifted by one
   after a sort). Caught by a test that checks every citation's quoted posting text
   actually occurs in the posting with that id, and by a test that shuffles the input
   order and requires identical per-id verdicts.
2. **A justification that cites nothing.** An implementation that returns a verdict with
   an empty justification, or one whose citations name a résumé field or posting text
   that does not exist. Caught by a validator, run on every verdict (rule and Claude),
   that rejects a verdict with no résumé-field citation and no posting-field citation,
   and rejects any citation that cannot be found in the résumé or posting.

## What a failure looks like

**2026-10-24:** a failure is a posting added to the board between runs that the agent
does not report as new, or one it reports as new that was already seen.

---

## Errata — added 2026-10-28, after implementation (nothing above was changed)

Everything above this line is the contract as committed in `c29d163` on 2026-10-24,
before any code existed. There is one exception: on 2026-10-28 the author's full name was
shortened to "Smit P.", because the course folder stores no full names. Where the code
differs from the text above, it is listed here rather than silently fixed:

1. **State file shape.** "In" says the state file is a JSON *list* of posting ids. The
   code writes an object, `{"board", "seen_ids": [...], "runs": [...]}`, so that the
   state also records which runs produced it.
2. **Validator is stricter than written.** "Wrong versions" says a verdict is rejected if
   it has "no résumé-field citation and no posting-field citation". The code rejects a
   verdict that lacks *either* one: it needs at least one of each.
3. **Validator additions** (2026-10-28, after a TA-style review). A rule verdict's
   recorded posting title must equal the posting it is checked against. Cited posting
   text must match as a whole word. Claude's résumé fields must name a single value.
   Re-validating all 87 saved Claude replies with these rules changed no outcome.
4. **The worked example** in "The rule" («Software Engineer, Payments» with Java, Kafka,
   AWS) is a **constructed** example, not a real posting.
5. **Known gap, not fixed here:** the rule has no location condition. The hand labels
   and the revised prompt do. See PROMPT-EXPERIMENT.md.
