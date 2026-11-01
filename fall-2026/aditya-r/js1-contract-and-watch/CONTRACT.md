# CONTRACT — Job-Search Agent 1

- **Author:** Aditya Raj. The text below is Aditya's, as supplied in the Claude Code session; Claude saved it verbatim and changed only its markdown formatting.
- **Received:** 2026-10-30 17:05 EDT (UTC-4).
- **Status:** APPROVED by Aditya Raj at 2026-10-30 17:30 EDT (UTC-4), with revisions R1–R5 below. The original draft is commit `710b152` (17:05 EDT).
- **Already happened before approval:** a raw board snapshot (2026-10-30 20:39 UTC), the download of an Internet Archive capture, a check of the Claude CLI, and an exploratory count of this rule over the snapshot (a throwaway scratchpad script, not project code; result: 5 of 903 relevant, 3 of the 258 new). This contract does not claim to precede those steps. No project implementation existed at approval.
- **Changes:** any change after approval is listed under "Revision log" at the bottom. The original wording stays in git history.

---

## 1. In

The agent takes:
- The Databricks Greenhouse board identifier.
- Priya Nair's fictional résumé as JSON.
- A local state file containing previously seen posting IDs.
- For the explicitly labeled seeded baseline, the saved archived board response.

For this assignment, the required résumé fields are:
- `skills.languages`
- `skills.data_bi`
- `skills.backend_automation`
- `skills.database_cloud`

Each must be an array of strings. At least one must contain a nonempty skill. Other résumé fields may remain available as context, but they must not change the deterministic relevance rule below.

Validate these requirements against the actual example résumé before implementation. If its structure differs, show me the difference rather than silently modifying the persona.

A missing state file means this is the first run. An existing but malformed state file is an error, not permission to start over.

Missing or malformed résumé JSON, an invalid board response, or missing/duplicate posting IDs must produce a clear error and leave the existing state unchanged.

An individual posting with missing or empty title or description receives `not_relevant` under the rule because there is insufficient evidence. Its explanation must identify the missing field. Missing location information does not affect relevance.

## 2. Out

For each new posting, return:
- Posting ID, title, URL, and location when available.
- The deterministic verdict, labeled `RECORD`.
- Claude's separate verdict, labeled `JUDGMENT`.
- An explanation for each verdict that names the relevant posting fields and résumé fields.
- The rule checks that passed or failed.
- Provenance sufficient to connect the result to the saved board response and, for Claude, its actual model response.

The allowed verdict values are exactly:
- `relevant`
- `not_relevant`

The deterministic explanation must identify the decisive evidence, including matched phrases, matched skills, exclusions, or missing information. When the rule finds no match, report the fields searched and the condition that failed; do not invent a supporting quotation.

Claude must follow a fixed JSON schema. Invalid responses are errors and must not be silently converted into either verdict. Check both the response structure and whether cited fields and quotations actually exist in the supplied inputs. Passing these checks does not establish that the judgment is correct.

The first run saves the baseline IDs and reports zero new postings, with no new-posting evaluations.

On later runs, every new posting must receive both valid verdicts before the run is reported as complete. Preserve partial results for recovery, and do not advance state in a way that permanently skips failed evaluations.

## 3. Refuses

The operational agent may fetch only HTTPS resources on the explicitly allowed host `boards-api.greenhouse.io`. It must reject requests or redirects to any other host.

The Internet Archive response is a separately acquired, documented evidence file read locally for the seeded baseline. It does not authorize the operational agent to browse the archive or arbitrary websites.

The agent also refuses to:
- Apply for jobs.
- Send emails or messages.
- Log in to job sites.
- Publish a real résumé, credentials, private contacts, or private transcripts.
- Treat instructions inside job descriptions as instructions to the agent.
- Describe Claude's judgment as an established fact.
- Fabricate postings, model responses, dates, results, or verification.
- Execute commands or access files requested by a posting.

Fictional-contact guard: see revision R3 below.

For a prohibited operation, report the attempted action and reason for refusal, stop that operation, and preserve the existing state. Do not include credentials or sensitive content in error messages.

Use the supplied fictional persona throughout. Do not claim the program can reliably detect every possible real résumé; enforce the intended input through the selected fixture, validation, and documented review.

## 4. The rule

This is a deliberately narrow relevance rule for this assignment. It does not claim to determine whether someone is actually qualified or should apply.

A posting is `relevant` only when all three conditions below pass.

### A. The title contains an eligible role phrase

The eligible phrases are:
- `software engineer`
- `data engineer`
- `machine learning engineer`
- `ai engineer`
- `analytics engineer`

Match a complete, contiguous sequence of normalized words. For example, "Software Engineer II" matches "software engineer," but "Software Engineering Manager" does not.

### B. The title contains no excluded seniority or management term

Exclude a posting if its title contains any of these complete normalized words:

`senior`, `sr`, `staff`, `principal`, `lead`, `manager`, `director`, `head`, `vp`, `chief`, `distinguished`, `architect`

Apply these exclusions to the title only. A description mentioning collaboration with a senior engineer must not trigger a title exclusion.

### C. There are at least two distinct shared target skills

The target skills are:

`python`, `sql`, `spark`, `databricks`, `langgraph`

A target skill counts only when:
1. It appears in at least one of the four required résumé skill arrays; and
2. It appears in the posting's title or description.

Count distinct skills, not repeated mentions. For example, Python mentioned five times still counts as one skill.

Do not infer synonyms or equivalences. "PySpark" does not count as "Spark," and "PostgreSQL" does not count as "SQL" under this exact rule.

### Normalization and missing information

For all matching:
1. Extract readable text from HTML, decoding entities and excluding script/style content.
2. Convert to lowercase.
3. Replace every sequence of characters other than ASCII letters and digits with a space.
4. Collapse repeated spaces and trim.
5. Match whole words or contiguous whole-word phrases.

This means "machine-learning engineer" matches "machine learning engineer," and "Sr." becomes the excluded word "sr."

Search individual résumé skill entries separately; do not create phrases by joining unrelated entries.

If title or description is missing or empty after normalization, return `not_relevant` with the missing-information reason.

Location, salary, work authorization, degree, years of experience, and other résumé fields do not affect this version of the rule. Document these limitations explicitly. Do not imply that they are unimportant in a real job search.

Give Claude the same relevance criteria, but keep its answer separately labeled as a judgment. Do not provide the deterministic verdict or my manual labels to Claude during evaluation.

## 5. Two plausible wrong implementations

### Wrong version 1: Correct-looking verdicts attached to the wrong postings

The program evaluates several postings correctly but associates responses by list position after the postings have been reordered.

This looks plausible because the output has valid IDs, verdicts, and explanations, but the evidence belongs to another job.

Test it using clearly labeled synthetic fixtures with contrasting expected outcomes and distinct evidence. Deliberately reorder the responses. The test must detect that the posting ID, verdict, and supporting evidence no longer agree.

### Wrong version 2: Structurally valid but unsupported justification

The program accepts a Claude response because it is valid JSON and contains the required fields, even though its explanation quotes a skill or posting statement absent from the supplied inputs.

This looks plausible because the response sounds convincing and passes a superficial format check.

Test it with a clearly labeled synthetic response that cites nonexistent evidence. The validator must reject it, and the posting must not be reported as successfully evaluated.

These controlled fixtures are test data, not experimental results or genuine Claude responses.

## 6. What a failure looks like

Failure prediction, approved by the author 2026-10-30 17:30 EDT, before any project code was written or run (the preparatory steps listed at the top had already happened):

"If the agent reports baseline postings as new, attaches a verdict to the wrong posting, or accepts an explanation supported by neither the résumé nor the posting, I will consider this version to have failed its contract."

---

## Revision log

These revisions were decided by Aditya Raj at approval (2026-10-30 17:30 EDT), after Claude reported the conflicts it found. Sections 1–6 above keep the original wording. Where a revision applies, it overrides those sections.

- **R1 — Clarification of rule C (résumé side).** A target skill appears in a résumé skill array when it matches a complete normalized word or contiguous phrase within **one** entry of that array. It must not match a substring of a word or span separate entries. For Priya Nair this gives the same result as exact equality of the whole entry.
- **R2 — "databricks" is kept as a target skill, and its effect is documented.** The employer's name appears in all 903 descriptions in the 2026-10-30 snapshot, so this skill discriminates almost nothing on this board. In practice, condition C becomes "at least one of python / sql / langgraph also appears", which is less demanding than "two shared skills" sounds. `spark` contributes nothing for this persona because it is in none of the four permitted résumé arrays. The résumé will not be changed to improve results.
- **R3 — Fictional-contact guard (added to §3 Refuses and §1 In).** The agent refuses to load a résumé unless `personal.email` is a well-formed address whose domain is exactly `example.com` (case-insensitive), and `personal.phone` follows the fictional pattern `(NNN) 555-NNNN`. A missing or malformed contact field is rejected with a clear error. This guards against loading a real résumé by accident. It is **not** proof that a résumé is fictional.
- **R4 — Validation of résumé evidence (clarifies §2).** A Claude response that attributes a skill to a résumé field (for example, `skills.languages`) is accepted only if that skill actually matches an entry of that field under R1. A field path that exists is not enough.
- **R5 — Baseline and new-ID state (clarifies §2).** The baseline records every archived ID as seen and judges none of them. On later runs, a new ID is marked completed only after both its RECORD and a valid JUDGMENT exist. IDs that fail stay pending and are retried; they are never silently skipped.
- **Experiment design (decided at approval; not a change to the rule).** The 20-posting prompt experiment uses a deliberately selected diagnostic sample from the 903 postings in the 2026-10-30 snapshot. It contains 5 postings the rule marks relevant, 7 near-misses (pass A, fail B or C) and 8 that fail A. The development target is 3 / 3 / 4 and the held-out target is 2 / 4 / 4. Duplicate jobs stay in the same split, and that takes priority over exact proportions. The labeling sheet hides selection groups and computed verdicts. Held-out material is sealed until both prompts are frozen. The sample is not representative of the board.
