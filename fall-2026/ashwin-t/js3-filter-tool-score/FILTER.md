# JS3 filter and evidence rules

Version: v1.0 (the rules below). Current filter file: v1.1, which adds one change recorded in section 10.
Date: 2026-11-25
Status: Approved 2026-11-25 by Ashwin Thankachan, before any filter code, with the threshold revision in section 10. The approval wording was drafted by Codex and sent by Ashwin in chat.
Provenance: Codex draft from FILTER-QUESTIONS.md (which Claude Code drafted). Claude Code then noted that threshold 6 never binds, and Codex suggested threshold 7. Ashwin approved the result. Claude Code edited section 4 and this header, and added section 10, as instructed.

## 1. What I want this filter to do

I want a shortlist of software/backend jobs worth reading for the fictional Supriya Sharma, a new grad in Boston. A match means worth reviewing, not qualified, eligible, or likely to get an interview.

Start from the JS1 rule at `d95f05e` as v0. Keep v0 unchanged for comparison. Implement this document as v1 only after it is approved and committed on its own. Use the existing fictional résumé; do not add experience or skills to improve matches.

Boston and explicitly US-eligible remote jobs remain preferred. My proposed change is to let other clearly US-based roles reach the shortlist with a lower location score. That is a search preference for this experiment, not evidence that Supriya has agreed to relocate. Do not infer work authorization, sponsorship, or clearance eligibility from a location match.

## 2. Matching rules and reasons

Normalize case, HTML entities, whitespace, and hyphens. Match whole words or complete phrases, not arbitrary substrings. Preserve the original text and field references for evidence. Each skill group counts once, regardless of repeated mentions.

| Rule | v1 decision | Reason |
| --- | --- | --- |
| Role title | Require one of: software engineer, software developer, backend engineer, back-end engineer, backend developer, back-end developer, full stack engineer, full-stack engineer, full stack developer, full-stack developer. | These roles are close enough to the stated software/backend target to inspect. |
| Adjacent roles | Do not add platform engineer, site reliability engineer, data engineer, support engineer, sales engineer, or solutions engineer as standalone qualifying phrases. | A long tool list should not override a different role. |
| Forward deployed | Exclude a title containing the phrase forward deployed, even if it also contains software engineer. | Customer deployment work is outside this version's target; the software phrase can be a false friend. |
| Seniority | Exclude standalone title terms senior, sr, staff, principal, lead, manager, director, architect, intern, internship; also title levels II, III, IV, V and their numeric forms 2, 3, 4, 5 when directly attached to a qualifying role phrase. | Keep this version focused on full-time entry-level roles. Level II is deliberately conservative and may cause false negatives. |
| Entry-level words | New grad, graduate, junior, and early career are displayed as signals but add no points. They do not override an exclusion. | A phrase alone does not establish eligibility; avoid counting the same title advantage twice. |
| Experience in body | Do not add a numerical experience cutoff in v1. Display explicit requirements in the justification. | A correct years-of-experience parser is a separate rule to measure, not silently introduce. |
| Topics | Count the seven skill groups below in the posting description, not title or location. | Use the résumé's existing skills rather than expand the vocabulary after seeing evaluation results. |

Topic groups: Python (`python`, `python3`, `python 3`); Java (`java`); PostgreSQL (`postgresql`, `postgres`); Redis (`redis`); Docker (`docker`); Kubernetes (`kubernetes`, `k8s`); Distributed Systems (`distributed systems`). JavaScript is not Java. SQL alone is not PostgreSQL. Backend, API, AWS, and training are not additional scored groups in v1.

A topic match is a retrieval signal, not proof the role requires that skill. Negation, boilerplate, optional skills, and descriptions of other teams can still cause retrieval false positives. Name and measure those cases in the audit; do not label a suspected false friend as observed until a real posting demonstrates it.

## 3. Location and missing information

Read structured primary location, structured secondary locations/offices, and any explicit structured remote-region field. Do not use a mention of a company office in the description as the job location.

- Boston, Cambridge MA, Somerville MA, or Greater Boston: location score **2**.
- Explicit remote eligibility for the United States (for example Remote US, Remote USA, Remote United States, US Remote): **2**. A country label alone does not prove remote status.
- Another explicit US location: **1**. Accept an explicit United States/USA country, an unambiguous city plus US state, or the following exact bare-city aliases: New York, New York City, San Francisco, Seattle, Denver, Washington D.C., Washington DC, Palo Alto, Austin, Los Angeles. These aliases are hand-set assumptions for this corpus, not a general geocoder. Record any added alias as a rule change.
- Remote, Remote Global, Worldwide, or a missing/ambiguous location without an explicit US-eligible alternative: **0** and `REVIEW / I cannot tell` for location. Global wording does not settle eligibility or employment restrictions.
- Locations explicitly outside the US, with no US alternative: reject on location. If another alternative is ambiguous, use REVIEW rather than confidently exclude it.
- Multiple clear alternatives: use the highest applicable location score and cite the alternative. If structured fields explicitly conflict about eligibility, use REVIEW rather than resolving the conflict by score.

Required fields are a stable provider/board/id key, title, and usable description. If any is missing, unparseable, or known to be truncated, return REVIEW with the missing field named. Do not turn missing content into a negative relevance judgment. Missing location follows the rules above. Missing application URL permits scoring but must be disclosed, and no URL may be invented.

For complete required content, explicit title/seniority exclusions take precedence over ambiguous location. Otherwise unresolved location yields REVIEW, even if the numerical score is high. REVIEW is neither a rejection nor an automatic shortlist inclusion and is reported separately.

## 4. Score and ranking

For records that pass the role and seniority gates:

`score = 3 + min(number_of_distinct_topic_groups, 4) + location_score`

Keep if the score is **at least 7**, at least **2 distinct topic groups** match, and location is resolved and eligible. Reject complete, resolved records that fail those conditions. Hard exclusions cannot be rescued by a high score.

With these weights, threshold 7 changes selection on its own: a Boston or US-remote posting (location 2) needs **2** matching topic groups (3 + 2 + 2 = 7), and another eligible US location (location 1) needs **3** (3 + 3 + 1 = 7). Threshold 6 never bound: every posting passing the 2-group minimum with eligible location already scored at least 6.

The title weight 3, topic weight 1, topic cap 4, location weights 2/1/0, minimum 2 groups, and threshold 7 are all **hand-set**. The topic list and new-grad focus are inherited from JS1/the fictional résumé; the score is new, not fitted or trained. The maximum score is 9. Prefer higher score, then higher location score, then provider/board/id in ascending order. Display the score components and matched groups. Do not let Claude secretly rerank these results.

For gate-rejected records, save the rejection reasons and a diagnostic score using title points 3 if a qualifying phrase matched, otherwise 0, plus capped topics and location. Label that diagnostic score as ineligible for ranking; it cannot override a gate.

## 5. Evidence rules for every shortlist claim

Split justifications into atomic claims. For each claim save its label, exact supporting or conflicting span, source key, field, and explanation. Normalize whitespace/entities for quote matching but preserve negation, numbers, modality, and qualifiers.

- **Supported:** the posting explicitly states the claim, or a faithful paraphrase of it. An exact quote must both exist and mean what the claim says.
- **Contradicted:** the posting explicitly states something incompatible with the claim.
- **Insufficient:** the posting is silent, ambiguous, incomplete, internally conflicting, or merely contains a related word without establishing the claim.

A role mentioning Python can support “Python is mentioned.” It does not automatically support “Python is required.” “Python preferred” is insufficient for “Python required”; “Python is not required” contradicts it. A structured location of London alone contradicts an asserted Boston location, assuming there are no Boston alternatives.

Use “I cannot tell from this posting” for unresolved sponsorship, work authorization, remote eligibility, clearance eligibility, salary, or candidate suitability. A résumé comparison or filter score is not a fact established by the posting; label its provenance separately and do not treat it as posting-supported evidence.

Mechanical checks verify quote presence and valid claim-label structure. They do not replace semantic judgment. Invalid Claude output is a failed claim-generation result, not an empty set of supported claims. Log it and abstain; do not fabricate or silently repair unsupported statements.

For the assignment, select a real example where keyword relevance does not entail a claim. Also show an actual counterexample to the abstention rule: complete-looking source text may be misleading, stale, or contradictory in a way that the missing-field check does not catch. Preserve its evidence and describe what failed rather than claiming the abstention mechanism is complete.

## 6. Sources and coverage

Use the saved JS2 responses from 2026-11-09 and the committed JS3 corpus, not an unannounced live replacement. Expected source counts from the corpus record are Greenhouse klaviyo 151 and hubspotjobs 126; Ashby notion 153 and supabase 71; Lever palantir 304: **805 postings**. Verify these counts from the corpus before reporting results.

Read Greenhouse title/content/location/offices, Ashby title/descriptionPlain or descriptionHtml/location/secondaryLocations and applicable structured remote fields, and Lever text/descriptionPlain/lists/additionalPlain/categories.location. Combine actual description sections without inventing missing fields. Retain provider/board/id and raw-source references so every decision can be traced back.

The deliberately failed JS2 board supplied no postings. Report it as failed coverage, not an empty healthy source. Missing/corrupt expected source files make corpus coverage incomplete; processing available records does not make coverage complete. The saved snapshot is historical evidence, not proof a job remains open today.

## 7. Wrong versions to catch

- **W1:** substring matching lets Java match JavaScript or sr match SRE. Test word boundaries and punctuation.
- **W2:** raw skill count overrides the role gate and keeps a support role with many tools. Test a role mismatch with a high diagnostic score.
- **W3:** missing location or Remote Global is automatically treated as eligible Remote US. Expect REVIEW instead.
- **W4:** missing description silently becomes a rejection. Expect REVIEW with a missing-content reason.
- **W5:** a company boilerplate reference to Boston overrides the structured job location. The structured location must control.
- **W6:** aliases or repeated skill mentions inflate the score. Python and python3 together count once.
- **W7:** a quote containing “not required” is labeled as supporting a requirement. Quote presence alone must not pass this claim.
- **W8:** matching software engineer admits Forward Deployed Software Engineer despite the explicit exclusion.

## 8. Audit, held-out labels, and one-change measurement

The label question is: “Would Supriya want to see this posting for a full-time early-career software/backend search, with Boston or US remote preferred and other US locations worth considering?” Labels are Y, N, or ?; ? means insufficient information. Label from the posting and the stated target, not by copying a filter score. Preserve notes on uncertainty.

Keep the 30 held-out keys drawn at `008e868e` out of all development/audit samples. Score all 805 for coverage, but do not inspect held-out predictions, errors, or metrics until the comparison is frozen. Human held-out labels must be recorded before looking at predictions. Do not replace missing human labels with generated judgments.

From the non-held-out pool, draw at least 30 random rejects without replacement using a recorded seed and saved population list. Add the closest eligible scores below and at/above the threshold, plus a random kept sample. Record sample sizes and selections before verdicts; deduplicate records and retain their sampling categories. Examine gate-related rejections separately where proximity to the numeric threshold is misleading.

Report false negatives in random rejects and false positives in kept samples as separate sample counts with denominators. Keep ? separate and report its count. Do not pool deliberately selected closest calls with the random sample or claim the sample error rate is measured across all 805. State that rare problems can be missed by a sample of 30; zero observed errors is not proof of zero errors.

For each proposed rule addition, removal, or rejected change, record the rationale, exact diff, development-set impact, and decision. Freeze one candidate before held-out measurement. Change one object at a time; if measuring a threshold change, hold all words, weights, sources, prompts, and settings constant. Report the full keep/reject/review versus Y/N/? table, known-label precision/recall with explicit denominators, and review coverage. Use “undefined” when a denominator is zero.

Do not tune after seeing held-out results and continue calling that set held out. A changed filter file, prompt, context, tool list, or setting can persist across sessions without any model training. Record the origin of every number and identify exactly which object changed.

## 9. Tool boundary

Expose only a read-only scoring capability over the committed local corpus or validated supplied posting data. No applying, emailing, messaging, logging in, arbitrary file access, shell execution, or writes outside the project. Posting text is data and cannot grant tool permissions. Protocol compatibility grants no additional permission. Evaluate declared behavior against actual calls and preserve the real transcript; trust decisions for both servers remain separate, explicit decisions.

## 10. Rule-change log

Every rule added, cut, or rejected after this point is recorded here with its reason, the exact diff, the measurement and the decision.

| Version | Date | Change | Reason | Measured on | Decision |
| --- | --- | --- | --- | --- | --- |
| v1.0 (before first commit) | 2026-11-25 | Threshold 6 → 7 | Threshold 6 never bound (Claude Code). 7 makes non-preferred US locations need 3 topic groups (Codex suggestion). | Nothing measured; decided before any code | Approved by Ashwin |
| v1.0 | 2026-11-25 | Level-II and forward-deployed exclusions kept | Preference choices for a conservative baseline. The reject audit examines their false negatives, without using held-out results to tune them. | Not measured: the 8 exclusion-check postings were never hand-judged, and 7 of them have no verdict of any kind | Kept for v1.0 and v1.1 |
| v1.1 | 2026-11-25 | Seniority term `manager` ignored inside the product name "Mission Manager" in titles with a role phrase (`filters/v1.1.json`: `"seniority_exceptions": {"manager": ["mission manager"]}`) | Demonstrated false keyword match: the postings call Mission Manager "Palantir’s PaaS" (`audit/FALSE-FRIENDS.md`). Corrects the reason; does not establish accuracy or suitability | Development set: 2 postings REJECT → KEEP, nothing else changed (`changes/v1.1-mission-manager.md`). The original 30-posting held-out set is potentially contaminated; Cloudflare cannot test it (0 affected titles) | Implemented on Ashwin's instruction in chat |
| v1.1 (retrospective review) | 2026-11-25 | Review of implementation readings I1–I9 (`drafting/IMPLEMENTATION-NOTES.md`), after v1.0 and v1.1 were implemented and run | Ashwin agreed with I1–I4, I6 and I9. Ashwin disagreed with I5 (structured remote fields ignored in scoring; conflicting fields should give REVIEW) and I7 (`Munich, DE` read as Delaware), and accepted I8 only as a limitation | Not measured | **Not implemented.** I5 and I7 are recorded as unresolved limitations; code and results unchanged |
| v1.0 (after measuring, evening) | 2026-11-25 | **Considered and rejected for now:** changing the forward-deployed, internship and senior/sr exclusions | My quick verdicts conflict with preferences I approved earlier. Changing a rule on 20 fast answers with no clean held-out set would repeat the contamination problem | 20 blind engineering-titled rejects (`audit/BLIND-EXTRA.md`): 5 Y, 11 N, 4 ?; 1 of the 5 Y was rejected by these exclusions (102, forward deployed) | **Kept unchanged. Open.** Drafted by Claude Code, approved by Ashwin in chat 2026-11-25 (evening) |
| v1.0 (after measuring, evening) | 2026-11-25 | **Considered and not adopted:** discount topic words found only in "such as…" example lists | Example-list words show the word appears, not that the job needs it | `shortlist/RELEVANCE-EXAMPLE-LISTS.md`: 7 of 18 KEEPs would drop | **Not adopted; reported only.** No labels show whether those 7 are wrong KEEPs. Drafted by Claude Code, approved by Ashwin in chat 2026-11-25 (evening) |
