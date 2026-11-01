# CONTRACT — Job-Search Agent 1 (the contract and the watch)

Written 2026-11-01, before any agent code existed (see the first commit, `JS1-1`).
Choices made by Saloni on 2026-11-01: the persona (Priya Nair), the rule shape
("title + level"), and the board (Greenhouse, `anthropic`). The keyword lists, the wording of the
wrong versions and the failure sentence were drafted with Claude from those choices; SOURCES.md
records which is which.

## In

| Input | Form | Needed for |
|---|---|---|
| Board | a Greenhouse board token, `anthropic` | the URL `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` |
| Résumé | a JSON file for a **fictional** persona (`personas/priya-nair.resume.json`) | the rule and the Claude judge |
| State | `state/seen_ids.json` (created by the first run) | deciding what is new |

The résumé must have `personal.email` ending in `@example.com`, a `personal.phone` containing
`555`, and a `search` block with non-empty `title_keywords` and `exclude_title_terms` lists. The
agent refuses to run on anything else (`validate_resume`).

## Out

For each posting whose id is **not** in the state file, two verdicts:

1. **Rule verdict (a record).** `relevant` or `not_relevant`, plus a justification that names
   the résumé field and the posting field it used, for example
   `{"resume_fields": ["search.title_keywords[1]"], "posting_fields": ["title"]}`, and the
   matched term. Anyone can recompute it from the two files.
2. **Claude verdict (a judgment).** The same shape, produced by Claude under the prompt
   contract in `prompts/`, labelled `"kind": "judgment"`. It is accepted only if it passes
   `validate_claude_output`: exactly the keys `verdict`, `resume_fields`, `posting_fields`, `reason`;
   `verdict` is one of the two labels; both field lists are non-empty; every résumé field is a real
   path in the résumé; every posting field is one of `title`, `location.name`, `content`,
   `departments`. Anything else is rejected and recorded as `rejected`, never as a verdict.

The first run is a baseline. It records every id it sees and reports **zero** postings as new.

## Refuses

- To fetch any host not on the allow-list. The allow-list is exactly `boards-api.greenhouse.io`.
- To show or commit a real résumé. Only the fictional persona file is read, and it must pass
  the `@example.com` / `555` check.
- To present Claude's verdict as a fact. Every Claude verdict carries `"kind": "judgment"`, and
  reports print it under the heading "Claude (judgment)", separate from "Rule (record)".
- To apply, email, message or log in anywhere. The agent makes one unauthenticated GET per run.

## The rule

Lower-case the posting `title`. Split it into words on anything that is not a letter or digit.

- **Keyword hit:** a keyword in `search.title_keywords` is found in the title. A one-word keyword
  must equal one whole word (so `ml` matches "ML Engineer" but not "HTML"). A multi-word keyword
  must appear as consecutive whole words.
- **Level hit:** a term in `search.exclude_title_terms` equals a whole word of the title.
- **Verdict:** `relevant` if there is at least one keyword hit **and** no level hit. Otherwise
  `not_relevant`.
- **Justification:** the first keyword hit, as `search.title_keywords[i]`, and, if any, the first
  level hit, as `search.exclude_title_terms[j]`, plus posting field `title`. If neither hits, the
  justification cites `search.title_keywords` (the whole list, none matched) and `title`.

Worked examples by hand, for a TA to check:
"Machine Learning Engineer, Inference" → `relevant` (`machine learning`).
"Senior ML Engineer" → `not_relevant` (`senior`).
"Account Executive" → `not_relevant` (no keyword).

The rule reads only the title. Location, sponsorship and years of experience are not part of it.
That gap is deliberate for this first layer and is listed in the README sign-off.

## Wrong versions the tests must catch

1. **Mis-paired labels.** The verdict list is built in one order and the posting ids in another
   (for example, sorted by title against sorted by id), so a correct verdict sits on the wrong
   posting. `test_wrong_version_mispaired_labels` must fail this.
2. **Justification that cites nothing.** The verdict is right but `resume_fields` or
   `posting_fields` is empty, or it names a résumé field that does not exist.
   `test_wrong_version_empty_justification` must fail this, for the rule and for the Claude
   validator.

## What a failure looks like

2026-11-01: The agent has failed if any posting whose title contains senior, staff, lead,
principal or manager gets a `relevant` verdict from the rule, if any verdict's justification
names no résumé field, or if the second run reports a posting id that was already in the state
file after the first run.

## Amendment 2026-11-01 (after seeded run 2, before any Claude call)

Seeded run 2 showed "Contracts Manager, GTM" justified only by `search.exclude_title_terms[5]`,
although what made it `not_relevant` was that no keyword matched. Justification rule, amended:
**when no keyword hits, the justification always cites `search.title_keywords`**, and adds the
first level hit if there is one. Verdicts are unchanged; only the citations changed. Test:
`test_no_keyword_always_cites_the_keyword_list`.
