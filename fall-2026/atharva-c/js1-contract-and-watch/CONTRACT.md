# CONTRACT — Job-Search Agent 1

Written by Atharva C on 2026-10-30, before any code. (Recorded from my answers
in an interview with Claude Code, which asked the questions and did the
formatting; the decisions and wording are mine.)

## In

- The board: Stripe's official Greenhouse board
  (`boards-api.greenhouse.io/v1/boards/stripe/jobs`).
- A résumé as JSON for a fictional persona (Rohan Desai). The agent needs
  personal details (`personal.location`) and `skills`.
- If `skills` is missing or empty, every posting is marked "not relevant".

## Out

For each new posting: a verdict (relevant / not relevant) and a justification.

- The justification shows which title word matched, which location matched,
  and which of Rohan's skills were found in the posting.
- If the verdict is "not relevant", the justification also says which check
  failed (title, location, or skills).

## Refuses

- The agent never emails anyone.
- The agent will only fetch from `boards-api.greenhouse.io` and refuses
  LinkedIn. Postings come only from Stripe's official Greenhouse board, not
  from aggregators like LinkedIn. The agent never fetches stripe.com.
- The agent never shows a real résumé; it only uses a persona.
- When Claude gives a verdict, the agent labels it as "a model judgment, not a
  fact".

## The rule

A posting is relevant only if all three checks pass:

1. **Title:** contains "engineer" or "developer", and does not contain senior,
   staff, principal, lead, manager, or director.
2. **Location:** anywhere in the US.
   - If the location lists several places, all of them must be in the US
     ("US, Canada" fails).
   - Plain "Remote" counts as US (Stripe's remote roles are US-based).
   - "N/A" or "na" fails.
3. **Skills:** at least 3 of Rohan's skills appear in the posting.
   - Counted as whole words, any case ("Go" does not match "good"; "Java"
     does not match "JavaScript").
   - All skill lists count except `familiar_with_not_shipped`.

## Wrong versions

My tests must catch these:

1. A posting seen in an earlier run is reported as new again.
2. Substring matching sneaks back in ("Go" matching "good").
3. Verdicts attached to the wrong posting.

## What a failure looks like

2026-10-30: the agent has failed if a relevant Stripe posting is marked
"not relevant", a non-US job is marked relevant, or an old posting is reported
as new.
