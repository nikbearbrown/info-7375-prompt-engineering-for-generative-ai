# CONTRACT.md — Job-Search Agent 1

**Author:** Revan Somshekhar Chonnad · **v1 written:** 2026-10-31 · **v2 revised:** 2026-10-31 after checking the live Klaviyo board · **Status:** review before agent implementation and runs

## In

- `--board <slug>`: one Greenhouse board slug. This project uses `klaviyo`; reject any other slug. The only permitted live request is `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`.
- `--resume <path>`: fictional résumé JSON validated by `resume.schema.json`. The supplied example is `resumes/aarav-patel.json`. Scoring reads `personal.location`, `target_titles[]`, and the listed `skills` categories; it does not count `familiar_with_not_shipped`. The file also contains `personal.name`, `personal.email` ending in `@example.com`, `personal.phone` containing `555`, `years_experience` (integer), and `visa` for a separate authorization flag. The example's `years_experience: 2` is a rounded-down derivation from the supplied dates, not a separately supplied fact.
- `state/seen_ids.json`: posting IDs from prior successful runs, created on the first run.
- `--seeded-response <path>` (optional): a saved, explicitly labeled Greenhouse JSON response used instead of a network request. This is only for the seeded two-run demonstration.
- `resume.schema.json`: validates the input JSON. The implementation may be written from this contract, but I review the schema and run its validation checks before using it.
- For the Claude judge only: `ANTHROPIC_API_KEY` in the environment, never in output or committed files.

## Out

For each posting whose `id` is absent from `seen_ids.json`, emit one record with `posting_id`, `title`, `rule_verdict` (`relevant` or `not_relevant`), and `rule_justification`: an array of objects with `condition`, `passed`, `resume_field`, `resume_value`, `posting_field`, and `posting_value`. Include evidence for each of the title, location, skills, seniority, and role-type conditions, including failures. The posting values must come from that posting's `title`, `location.name`, or stripped `content`.

Emit a **separate** `claude_verdict`, `claude_justification` array, and the exact label `JUDGMENT — model output, not a fact`. A Claude failure is reported as `invalid` or `unavailable`, with a reason. The model's answer never changes the rule verdict.

Also emit `authorization_flag` and `e_verify: "unknown"` in each record. Set `authorization_flag` to `NEEDS_SPONSORSHIP` whenever `visa.type` is `F-1`, including any OPT status and any status string containing “work authorized.” Set it to `UNKNOWN` for another visa type; a missing `visa` object is a résumé validation error. This is a project classification, not a determination that a particular job or employer is eligible. The agent does not infer E-Verify participation from a posting; `e_verify` stays `unknown` unless a separately defined, verifiable source is added in a later version.

Save the exact live raw board response to `evidence/<slug>_<UTC timestamp>.json` before parsing. Write records to stdout and `runs/<UTC timestamp>.json`, with the run mode and source path. The first successful run is a baseline: save its IDs and report **zero** new postings. Later runs report only previously unseen IDs. A changed posting with the same ID is not new. Different IDs for similar titles or offices are separate postings and each receives its own record. Do not advance state if fetch, validation, output, or state writing fails.

**Planned seeded demonstration, not yet run:** Make a copy of `evidence/klaviyo_2026-10-31_preimplementation_live.json`, the real response saved during contract review. I will manually remove **N = 2** posting objects, IDs `8041054003` (Software Engineer, Conversational Products & Agent Workflows) and `7792539003` (Software Engineer II, Mobile Developer), and save that copy as `evidence/klaviyo_2026-10-31_seeded.json`. In a fresh run directory with no state file, run 1 uses that seeded response as the baseline. Run 2 fetches the live board. If both IDs are still live and no other postings have appeared, those two IDs are the expected new set. I will record any other live changes rather than claiming exactly two if the board has changed. The removal, source snapshot, and commands belong in the run log.

## Refuses

- Fetching a host outside `ALLOWED_HOSTS = {"boards-api.greenhouse.io"}`, following a redirect to another host, using a slug other than `klaviyo`, or using any endpoint besides the public jobs GET endpoint. Exit nonzero.
- Loading a résumé whose email does not end in `@example.com` or whose phone lacks `555`; displaying, uploading, logging, or committing a real résumé.
- Presenting a Claude verdict without the JUDGMENT label or in the rule verdict field.
- Accepting Claude output with wrong keys, a verdict outside `relevant`/`not_relevant`, an empty justification, a résumé field or value absent from the input, or a posting value absent from that posting. Record it as `invalid`; do not silently retry or fabricate a result.
- Treating “work authorized” as proof that F-1 STEM OPT needs no future sponsorship, or treating a posting as E-Verify eligible without evidence.
- Applying, emailing, messaging, logging in, or submitting a form anywhere.

## The rule

A posting is **relevant if and only if all five conditions pass**:

1. **Title:** Lowercase the posting `title` and each `target_titles[]` phrase. The title must contain at least one target phrase as a substring. Aarav's exact JSON list is `software engineer`, `backend engineer`, `platform engineer`, `devops engineer`, and `site reliability engineer`. Backend and platform were included because the supplied primary target is Backend / Platform. The list is not expanded at runtime.
2. **Location:** Lowercase `posting.location.name` and the city before the comma in `personal.location`. The posting location must contain `boston` as a complete word or contain `remote` as a complete word. A multi-location string such as `Boston, MA; Denver, CO` passes. `Anywhere in the United States` and `Eastern Timezone` do not count as remote under this rule.
3. **Skills:** Strip HTML and decode entities in `posting.content`. Apply the **same normalization** to each skill and the stripped content: lowercase, replace every non-alphanumeric character with a space, and collapse runs of spaces. A normalized skill must appear as a complete word sequence with a space or string boundary on each side. Thus `Node.js` becomes `node js`, and `Fluent Bit` becomes `fluent bit`; `SQL` does not match inside `PostgreSQL` or `MSSQL`, and `Java` does not match `JavaScript`. At least two **distinct** skills from `skills.languages`, `skills.backend_automation`, `skills.database_cloud`, or `skills.devops_cicd` must match. Repeated mentions count once. `skills.familiar_with_not_shipped` does not count.
4. **Seniority:** Normalize the title the same way as skills. It must contain none of these complete words: `senior`, `sr`, `principal`, `staff`, `lead`, `director`, `manager`. This conservative cutoff reflects the example's two years of experience; the rule may reject some plausible stretch roles.
5. **Role type:** The normalized title must contain none of these complete words or sequences: `frontend`, `front end`, `mobile`, `ios`, `android`. `Full Stack` alone is not excluded. This implements the supplied pure-frontend exclusion and the added mobile exclusion in `target_role.excluded`; it does not attempt to detect third-party staffing or unpaid roles from the title.

Otherwise the rule verdict is **not_relevant**. Missing `id`, `title`, `location.name`, or `content` makes the board response invalid and stops the run without changing state; it is not silently scored. The visa flag is reported separately and does not change this five-condition relevance verdict. In the live Klaviyo response checked on 2026-10-31, 156 postings were present and none of their `location.name` values contained `remote`; the remote branch therefore did not fire in that snapshot.

**Constructed hand-check examples, not board results:** For Aarav, “Software Engineer - Platform Tools” in “Boston, MA” with content mentioning “TypeScript” and “Kubernetes” passes all five conditions. The same title and location with only “TypeScript” fails skills. “Senior Software Engineer - Platform Tools” fails seniority even with both skills. “Software Engineer II - Mobile Android” fails role type even with both skills.

## Claude prompt contract

Give Claude the fictional résumé and one new posting at a time. Require one JSON object, with no surrounding prose, containing exactly `verdict` (`relevant` or `not_relevant`) and `justification` (a nonempty array). Every justification entry must contain exactly `resume_field`, `resume_value`, `posting_field`, and `posting_value`. Allowed résumé paths are exactly `target_titles`, `personal.location`, `years_experience`, `target_role.excluded`, `skills.languages`, `skills.backend_automation`, `skills.database_cloud`, and `skills.devops_cicd`. A `resume_value` must be an actual value at the cited path. Allowed posting fields are exactly `title`, `location.name`, and `content`. A `posting_value` must appear in that field after the same normalization used by the rule; `Node.js` and `node.js` therefore match, but fabricated text does not. The validator checks types, keys, paths, and values against the supplied résumé and the same posting. Record the exact Claude model ID, temperature, prompt, and date for each experiment. Format validity is not correctness; hand labels remain the comparison point.

## Wrong versions my tests must catch

1. **Shifted labels — `test_verdicts_keyed_by_id`:** Correct verdicts are paired with the wrong posting IDs after sorting or zipping. Use one clearly relevant and one clearly irrelevant fixture and assert the verdict and evidence by `posting_id`.
2. **Empty or fake justification — `test_validator_rejects_empty_or_fake_evidence`:** The model returns `[]`, cites `resume.certifications`, or cites a `posting_value` absent from that posting. Reject each case.
3. **Baseline leak — `test_baseline_reports_zero`:** With no prior state, the first run reports jobs as new. Assert zero new and that the observed IDs were saved.
4. **Authorization trap — `test_work_authorized_still_needs_sponsorship`:** The fictional status string contains “work authorized,” but the output must still show `NEEDS_SPONSORSHIP` and `e_verify: "unknown"`.
5. **Ignored exclusions — `test_seniority_and_mobile_exclusions`:** A Senior or Mobile title passes title, location, and skills but is still `not_relevant`.

## What a failure looks like

**Drafted 2026-10-31, before agent runs:** This agent has failed if a TA applies the five conditions above by hand to a reported posting and obtains a different rule verdict from the one the agent printed.

## Source notes

The public jobs endpoint, `content=true`, and posting IDs follow [Greenhouse's Job Board API documentation](https://docs.greenhouse.io/job-board). The E-Verify requirement for STEM OPT employers is described by the [U.S. Student and Exchange Visitor Program](https://studyinthestates.dhs.gov/assets/SEVP_PracticalTrainingOverview_1-pager.pdf). The Aarav persona and mention of a Summer 2026 authorization fix (PR #37) came from the user's supplied Reallocation Engine example; this document does not claim independent verification of that repository or PR. The rule, output fields, and `NEEDS_SPONSORSHIP` operational label are project choices.
