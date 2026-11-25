# Sign-off and driver's seat: Job-Search Agent 3

## Sign-off

**Sign-off — Job-Search Agent 3**

**Checked:** FILTER.md v1.2, the 60-posting audit, 20 held-out postings, three rule-change experiments, MCP tool behavior, and automated tests. The properties checked, and the tests that check them (in `tests/`, plus `wrong_versions.py`):
- **v1.2 is v1.1 plus exactly the adopted change, and v1.1 is kept byte for byte:**
  - `test_versions.ExactlyOneChange.test_v12_differs_from_v11_only_in_the_adopted_value`
  - `test_versions.Archive.test_v11_rules_are_kept_byte_for_byte`
  - `test_versions.RelatedRoleRule.test_v12_needs_two_topic_categories_for_a_related_title`
- **The FILTER.md section 9 wrong versions are caught:** `wrong_versions.py` (6 of 6), including:
  - `test_wrong_versions.WV1SubstringMatching.test_ai_is_not_found_inside_email`
  - `test_wrong_versions.WV4MissingExperience.test_missing_experience_is_unknown_and_never_confirmed`
- **Experience and decision rules:**
  - `test_experience.ConstructedDegreeDependentOr.test_is_unknown_and_goes_to_review_not_confirmed`
  - `test_decisions.SeniorityAndPrograms.test_seniority_overrides_a_high_score`
- **One change at a time, and tuning postings never drawn into the held-out sample:**
  - `test_experiment.OneChange.test_exactly_one_value_changes_and_the_original_is_untouched`
  - `test_experiment.WhatTheLabelsSay.test_every_flip_labeled_is_a_count_not_an_estimate`
  - `test_sampler.HeldOut.test_tuning_postings_are_never_drawn_and_no_posting_is_drawn_twice`
- **The tool server writes nothing but its transcript and survives malformed input:**
  - `test_mcp_server.WhatItCanTouch.test_a_real_session_changes_nothing_but_its_own_transcript`
  - `test_mcp_server.WhatItCanTouch.test_the_only_file_write_is_the_transcript`
  - `test_mcp_server.ProtocolErrors.test_deeply_nested_json_is_a_parse_error_not_a_crash`
- **The shortlist abstains when experience is unknown:**
  - `test_shortlist.Claims.test_unknown_experience_is_insufficient_and_the_agent_abstains`

**How:**
- **By hand:**
  - I reviewed the posting descriptions and recorded my 60 audit labels and 20 blind held-out labels before measuring rule changes.
  - I compared the three experiments against those labels.
  - I checked all 120 shortlist claims.
  - I made the rule-change decisions and both trust decisions.
- **By recomputation, run by Claude on 2026-11-25:**
  - The final v1.2 run processed 2,418 saved postings: 0 confirmed, 55 in review, and 2,363 rejected.
  - `experiment.py flips` reproduces every field of the v1.1 run, and re-deciding all 2,418 postings reproduces both saved runs.
  - The 112 automated tests passed on Python 3.9 and 3.13, and all 6 planted bugs were caught.
- **With Claude's help:**
  - Claude wrote all the code and all 112 tests, including every test named above. None of them was written by me before reading Claude's code.
  - Claude also fact-checked my labels against the posting texts and generated every report.

**Not checked:** Every posting manually, live job availability, every possible MCP input, or future job postings. I did not independently monitor network activity.

**Not claiming:** That the filter is perfect, that every rejection is correct, or that the results generalize to future postings. X2 improved 7 of 8 affected decisions but incorrectly rejected one posting that I would have kept for review.

Signed: Yash Saraf, November 25, 2026

## Driver's seat

| Area | What Claude should do | What I should do | Why |
|---|---|---|---|
| Filter rules | Help translate requirements into deterministic rules and identify inconsistencies. | Choose the matching criteria, thresholds, and exclusions. | Relevance is ultimately my judgment. |
| Reject audit | Draw reproducible samples, calculate counts, and identify disagreements. | Read postings, decide which rejections were correct, and explain my labels. | Automated rejection can hide relevant jobs. |
| Shortlist claims | Generate claims with source excerpts and flag weak evidence. | Review the claims and decide which statements are supported. | A high score does not prove that a job is suitable. |
| Tool server | Implement the MCP protocol, execute tests, and record transcripts. | Decide which capabilities to trust and what information the tools may access. | Tool permissions and privacy require human oversight. |
| Changing the score | Test one change at a time and calculate improvements and regressions. | Decide whether to adopt changes and document trade-offs. | Better scores do not automatically mean better decisions. |

## Why the judgment that a posting is worth my time stays mine

The filter helps reduce the number of postings I need to read, but it cannot fully understand my priorities or determine whether a job is worth applying to.

My experiments showed this limitation. Lowering the threshold improved some decisions but also increased incorrect review results. Requiring two matching topic categories improved seven of eight affected decisions, but it also rejected a relevant personalization and machine-learning role.

I therefore use the filter as a screening tool, not as a final decision-maker. I remain responsible for interpreting qualifications, reviewing uncertain cases, and deciding which opportunities deserve my time.