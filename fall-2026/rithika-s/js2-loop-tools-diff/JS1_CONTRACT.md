# CONTRACT — Job-Search Agent 1

Written 2026-10-31, before any implementation code.

## In
- **Board:** one public Greenhouse board. Host `boards-api.greenhouse.io`,
  board token `scaleai`, endpoint `/v1/boards/scaleai/jobs?content=true`.
- **Résumé:** `data/resume.example.json`, a fictional persona (Priya Nair).
  The agent accepts it only if:
  - it is valid JSON with `personal.name`, `personal.email`, `personal.phone`,
    and a non-empty `skills` object;
  - `personal.email` ends in `@example.com`;
  - `personal.phone` contains `555`.
  If any check fails, the agent stops before fetching anything.
- **Target:** `data/target.example.json`, holding the persona's target title
  keywords and excluded terms, copied from her fictional `profile.yml`.
- **State:** `data/state.json`, the posting ids seen on earlier runs.
  If it does not exist, the run is a **baseline**: all current ids are
  recorded and zero postings are reported as new.
- **Needs:** Python 3.11+, standard library only. Network access only to
  the allow-listed host. All tests run offline against saved responses.

## Out
For every run:
- the raw board response, saved unchanged as `data/raw/<UTC timestamp>_scaleai.json`,
  with its SHA-256 hash recorded in the run report;
- the updated `data/state.json`;
- a run report listing only postings whose ids were not in the state file.

For each new posting, two separately labeled verdicts:
1. **Rule verdict (record):** `relevant` or `not_relevant`, with a
   justification naming the résumé/target fields and posting fields behind it,
   e.g. `skills.languages: Python` matched in `posting.content`.
   Anyone can recompute it by hand.
2. **Claude verdict (judgment):** returned as JSON only:
   `{"posting_id": int, "verdict": "relevant" | "not_relevant",
     "resume_fields": [str, ...], "posting_fields": [str, ...], "reason": str}`.
   A validator rejects any output that is not exactly this shape, has an
   unknown verdict, a mismatched `posting_id`, or empty field lists.
   If Claude was not run, the report says "not run"; it is never filled in.

## Refuses
- Fetching any host other than `boards-api.greenhouse.io`, or any non-HTTPS URL.
- Running with a résumé that fails validation (e.g. a real email address).
- Showing résumé contact fields (email, phone, LinkedIn, GitHub) on screen
  or in any output file. Justifications cite skills fields only.
- Presenting Claude's verdict as fact. It is always labeled as a judgment
  and never overrides the rule verdict.
- Accepting Claude output that fails the validator.
- Applying, emailing, messaging anyone, or logging in anywhere.

## The rule
Text preparation: posting `content` is HTML-escaped. Unescape entities,
remove HTML tags, lowercase. Matching is case-insensitive and whole-word
(`SQL` does not match inside `PostgreSQL`).

A posting is **relevant** only if all three hold:
1. **No exclusion:** neither the title nor the content contains an
   excluded term from `target.example.json` (`clearance`).
2. **Title gate:** the title contains at least one target title keyword:
   `ai engineer`, `ml engineer`, `machine learning`, `data engineer`,
   `ml infrastructure`, `ml platform`.
3. **Skill evidence:** at least **2 distinct** résumé skills appear in the
   content, counting only `skills.languages`, `skills.data_bi`,
   `skills.backend_automation`, `skills.database_cloud`.
   `skills.familiar_with_not_shipped` (Ray, Kubeflow) never counts.

Otherwise it is `not_relevant`, and the justification names the first
condition that failed, checked in the order 1, 2, 3.

## Wrong versions my tests must catch
1. **Misaligned labels:** verdicts paired with the wrong postings, e.g. a
   list of verdicts computed in one order and zipped against postings in
   another. Caught by checking that every skill a justification cites
   actually appears in *that* posting's text.
2. **Empty justification:** a verdict whose justification cites no résumé
   field or no posting field (e.g. "Strong ML fit."). Caught by the
   validator rejecting any justification without at least one of each.

## What a failure looks like
2026-10-31: The agent has failed if any posting reported as new on the
second run was already in the first run's state file, or if any
justification cites a résumé skill that does not appear in that posting.