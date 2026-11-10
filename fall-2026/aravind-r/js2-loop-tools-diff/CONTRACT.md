# CONTRACT

Written 2026-10-31, before any code. Decisions mine; wording drafted with Claude and edited by me.

## In
- `board`: a Greenhouse board token. This layer: `stripe`. Fetched only from
  `https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true`.
- `resume`: path to a JSON résumé for a fictional persona (Maya Sehgal, the shipped file, untouched). It must validate before anything runs: every email ends `@example.com`, every phone uses a 555 exchange.
- `prefs`: `persona-prefs.json`, labeled as preferences I added for the persona; they are not part of the shipped résumé. The rule reads its fields from this file:
  - `years_pm`: 2
  - `locations`: "San Francisco", "Los Angeles", "San Jose", "Remote"
  - `needs_sponsorship`: true
  - `domains`: "payments", "fintech", "data", "e-commerce", "mobile"
- `state`: the state file of posting ids seen on previous runs. Absent means first run.
- Needs: network access to the one allow-listed host; the `claude` CLI for the judgment step.

## Out
For each posting whose id is not in `state`:
- `id`, `title`, `absolute_url`
- `rule_verdict`: `relevant` | `not_relevant`, labeled **RECORD** (anyone can recompute it from the cited fields).
- `rule_justification`: every gate's result, each naming the posting field and value and the `persona-prefs.json` field and value it was compared with, with the first failed gate flagged. Domain overlap is listed as a citation (`domains` terms found in the posting, or "none"); it is not a gate.
- `claude_verdict` and `claude_justification`, labeled **JUDGMENT**. They must pass a validator against a fixed JSON schema. Output that fails is recorded as `invalid` and never replaced, repaired, or silently retried into a pass.

Every run saves the raw response with a UTC timestamp. The first run is a baseline: it saves state and reports zero postings as new.

## Refuses
- Fetching any host other than `boards-api.greenhouse.io`, including via redirects.
- Applying, emailing, messaging anyone, or logging in anywhere.
- Running on a résumé that fails persona validation, or displaying or committing a real résumé.
- Presenting Claude's verdict as fact, unlabeled, or as overriding the rule.
- Reporting a posting as new when its id is already in `state`.
- Emitting a verdict whose justification does not cite the fields behind it. It fails closed.

## The rule
All text checks run on the posting's `content` with HTML decoded, tags stripped, and case lowered. All six gates are always evaluated, in order. A posting is **relevant only if all six pass**. The justification lists every gate's result and flags the first gate that failed.

1. **Title.** Take the title up to the first `,` ` - ` or `(`. It must exactly match one of: Product Manager, Senior Product Manager, Sr. Product Manager, AI Product Manager, Technical Product Manager, Web3 Product Manager, Technical Program Manager, Senior Technical Program Manager. Anything else fails, for example Product Marketing Manager, Group/Principal/Staff/Lead PM, Director or Head of Product, Product Operations, or Program Manager without "Technical".
2. **Not junior.** Fails if the title contains Associate, APM, Intern, or New Grad, or if the content states an experience range whose upper bound is 2 or less (e.g. "0–2 years", "1-2 years").
   Revision 2026-10-31: title terms match whole words only (on baseline, 'Intern' matched 'International' in 8 titles; all already failed Gate 1, no verdict changed).
3. **Experience ceiling.** Take the first "N+ years" / "N-M years" / "N or more years" phrase that appears in a sentence containing "experience", and its lower bound N. It passes if N ≤ `years_pm` + 1. If no such phrase exists, it passes and the justification says "not stated".
4. **Location.** Passes if any entry in `locations` appears as a substring of the posting's `location.name`, ignoring case (so "Remote" also matches "remote").
5. **Sponsorship.** If `needs_sponsorship` is true, it fails when the content contains any of: "unable to sponsor", "not able to sponsor", "will not sponsor", "does not sponsor", "cannot sponsor", "without sponsorship", "sponsorship is not available". If `needs_sponsorship` is false, it passes and the justification says so.
6. **Citizenship / clearance.** Fails if the content contains "security clearance", "u.s. citizen", "us citizenship", or "citizenship is required".

Domain citation (not a gate; never changes the verdict): for each term in `domains`, whole-word, case-insensitive match against the posting's `departments[].name` first, then `content`. The justification lists each matched term and where it matched, or "none".

## Wrong versions
Each of these must make at least one test fail:
1. **Misaligned verdicts.** Verdicts attach to the wrong posting ids (e.g. off-by-one after a sort or filter). Test: a seeded fixture where adjacent postings have opposite correct verdicts; assert each verdict by id.
2. **Uncited justification.** A verdict whose justification omits a gate's posting field or persona-prefs.json field. Test: the validator rejects it.
3. **Constant judge.** Everything comes back `relevant`. Test: the fixture includes known not-relevant postings (Product Marketing Manager, a Director role, a "10+ years" role, a no-sponsorship role); each must be `not_relevant`.
4. **Seen-id bug.** The baseline reports postings as new, or the second run re-reports a baseline id. Test: run the baseline then the seeded run against the fixtures; assert the exact new-id set.

## What a failure looks like
2026-10-31: a posting marked relevant fails at least one gate when I recompute it by hand from the fields its justification cites.
