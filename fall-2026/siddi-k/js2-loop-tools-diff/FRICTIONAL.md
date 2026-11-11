# Experiment Timeline and Evidence

Written by Siddi Kommuri and pasted in chat at about 22:20 ET on 2026-11-10. Claude saved it verbatim, except that Siddi approved removing the word "Example" from two headings. The timeline follows the table of events Claude listed; the wording and the reflection are Siddi's.

**Date:** 10 November 2026  
**Project:** Job Board Collection and Boundary Testing

| Time | What happened | Who | Evidence / Citation |
|---|---|---|---|
| 22:04 | GATE.md was written before any implementation code existed. It established the board selection, exit statuses, budgets, repeat rule, error handling, permissions, and test requirements. | Me | `1793a11` |
| 22:08 | The first real run produced the correct result, but the trace incorrectly logged every successful board as `failed` before recording its outcome. The bug was retained as evidence and fixed before the next run. | Claude — implementation bug | Run `03-08-32Z`; fix `24d6e27` |
| 22:08 | A real run ended with `incomplete`. The misspelled Greenhouse slug `stripee` returned `not_found`, and the system correctly did not report it as zero postings. | System behavior | Run `03-08-59Z` |
| 22:09 | The SmartRecruiters name `Canvaa` returned HTTP 200 with zero postings. The run incorrectly reported `finished`; only a separate identity check detected the problem. | System behavior / test gap | Run `03-09-02Z`; `evidence/checks/` |
| 22:11 | The tests initially reused the same run ID. The overwrite protection correctly refused the second run because it would have overwritten an existing file. | Claude — test implementation bug | `c0eea55` message |
| 22:11 | The repeat rule in §3 and timeout retry policy in §4 appeared to conflict. Retries were interpreted as attempts belonging to one logical action, rather than separate repeated actions, and this interpretation was documented. | Claude — interpretation | `README` |
| 22:12–22:13 | An identity test was written before the implementation patch. It failed before the patch and passed after the patch. | Claude | `c0eea55` → `ef6456a` |
| 22:16 | Fifteen boundary cases were predicted. Fourteen matched the implementation. Case 12 was incorrect: I predicted `refused`, although GATE.md requires approval for configuration changes. | Me | `e769016`; `BOUNDARY-TESTS.md` |
| 22:18 | I ran the tests and the check myself, reviewed the results, and accepted the patch. | Me | `b24d512` |
| Unspecified | The patch catches a typo only when the board is empty. A typo that resolves to another real company's board could still pass undetected. | Outstanding limitation | `REVIEW-PACKET` §6 |

## Reflection

This stage showed that writing a permission policy before implementation gave us a concrete basis for testing the system. The first runs also exposed a difference between receiving a technically successful HTTP response and retrieving the intended company's postings.

The `Canvaa` case was especially important. A 200 response with zero postings looked like a valid empty result, but the board identity was wrong. The system therefore needed to validate not only the response status and structure but also whether the returned board actually belonged to the requested company.

I also made a mistake in boundary case 12. I classified a configuration write as refused, even though my own policy said configuration changes require approval. This showed that I had not applied my written policy consistently when predicting the boundary tests.

The identity test was useful because it was written before the patch and demonstrated a red-before, green-after result. However, the remaining limitation is significant: checking identity only when a board is empty does not catch a typo that points to another real company's board. That case still needs to be addressed.

**Current unresolved issue:** Board identity must be validated even when the returned board contains postings. A successful HTTP response alone must never establish that the correct company was queried.
