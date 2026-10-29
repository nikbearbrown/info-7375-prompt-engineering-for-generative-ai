# CONTRACT — Job-Search Agent 1 (nishant-u)

Written by Nishant U on 2026-10-29, before any code. Drafted with Claude (claude.ai), reviewed and approved by me.

## In
- Board: Faire on Greenhouse, `https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true` (GET only).
- Résumé: the fictional persona Priya Nair, `resume.example.json` copied from the Reallocation Engine's `search/examples/priya-nair/`. Must contain `_comment` marking it FICTIONAL and an `@example.com` email.
- Requirements: `requirements.json` with `title_terms`, `exclude_terms`, `us_location_markers`, `skill_lists`, `min_skills`.

## Out
For each posting new since the last run:
- **Rule verdict** (`relevant` or `not_relevant`), labeled **record**: anyone can recompute it from the rule below.
- **Claude verdict**, labeled **judgment**, in the fixed schema below; rejected by the validator if malformed.
- A **justification** for each that names the résumé fields and posting fields behind it, with the exact text quoted.

The first run is a baseline: it saves all IDs and reports zero as new.

## Refuses
- Fetching any host other than `boards-api.greenhouse.io`.
- Reading a résumé that lacks the FICTIONAL marker or uses a non-`@example.com` email (so a real résumé can't be loaded, shown, or committed).
- Presenting Claude's judgment as fact: every Claude verdict is labeled `judgment`; only the rule verdict is labeled `record`.
- Applying, emailing, messaging, or logging in anywhere.

## The rule (a TA can check it by hand)
A posting is **relevant** only if all four hold (case-insensitive, whole words):
- **R1 Title:** `title` contains at least one of: data, analytics, analyst, scientist, machine learning, ML.
- **R2 Not management or intern:** `title` contains none of: manager, director, head, lead, intern.
- **R3 US location:** at least one `;`-separated part of `location.name` ends in a US state code (`, CA`, `, NY`, `, IL`, ...) or is `Remote - US`.
- **R4 Résumé skill:** at least 1 skill from Priya's shipped skill lists (`skills.languages`, `skills.data_bi`, `skills.backend_automation`, `skills.database_cloud`) appears in `content` after removing HTML. `skills.familiar_with_not_shipped` and the text note `skills.agent_note` do not count.

Otherwise it is **not relevant**, and the justification names the first check that failed and the field it read.

Seniority fit is **not** judged: Senior and Staff titles can be relevant.

## Claude's output schema (validator rejects anything else)
Exactly these keys:
- `posting_id` (integer; must be one of this run's new IDs)
- `verdict` (`"relevant"` or `"not_relevant"`)
- `citations` (non-empty list of `{ "resume_field", "posting_field", "quote" }`; `resume_field` must exist in the résumé, `posting_field` must be one of `title`, `location.name`, `content`)
- `label` (must be `"judgment"`)

Whether each quote actually appears in the cited field is checked separately and reported as **supported / not supported**, apart from the validator.

## Wrong versions the tests must catch
1. **Mismatched labels:** verdicts attached to the wrong posting IDs (for example, shifted by one after sorting).
2. **Uncited justification:** a verdict whose citations are empty, name a field that doesn't exist, or quote text not in that field.
3. **Skills read from a string:** treating the text note `skills.agent_note` as a list, so single letters count as matched skills. (This happened in a real read-only check on 2026-10-29.)

## What a failure looks like
2026-10-29, written before any run: *Failure is the second run reporting as new a posting that was in the baseline, or any verdict, rule or Claude, whose justification cites a field that does not contain the quoted text.*

## Amendments
2026-10-29, after implementation: a quote must be a non-empty string. Found by Claude Code during implementation: an empty quote passed the validator and counted as supported. The original text above is unchanged.
