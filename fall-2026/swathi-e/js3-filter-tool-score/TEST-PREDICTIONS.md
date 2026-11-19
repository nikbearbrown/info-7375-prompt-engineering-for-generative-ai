# TEST-PREDICTIONS.md — JS3 filter tests, expected outcomes before any filter code

Written by Claude Code on 2026-11-17 from the test design Swathi approved
(2026-11-17) and FILTER.md as committed at `8c7c9b8` (v1 plus the R5 ranges,
R2 sections and D1-D7 revisions). These are **predictions**, recorded before
`descriptions.py`, `job_filter.py` or the parser change exist. They are not
results.

Data: **SIM** = a SIMULATED posting or body built in the test; **REAL** = the
saved Nov 5 Plaid response, `runs/2026-11-05T23-11-48-228373-0500/005-plaid-request.json`,
read-only. No test uses the network.

Verdicts: `shortlisted`, `not shortlisted`, `rejected`, `I cannot tell`.
Score = role 3 + early-career 2 + topic words 1 each (at most 3); `None` when
rejected or "I cannot tell".

## tests/test_descriptions.py

| Test | Data | Expected outcome | FILTER.md item |
|---|---|---|---|
| S1 | SIM + REAL | "Responsibilities:", "What you’ll do&nbsp;" (bold paragraph) and "Minimum Requirements" are "counts" sections with their text; real posting 1bcfe93d has "counts" sections "responsibilities" and "qualifications" | Revision: R2 sections |
| S2 | SIM | Text in content-intro and content-conclusion (even under "Responsibilities" or "About Databricks"/"Benefits") is boilerplate; "The impact you will have:" text counts | Revision: R2 sections |
| S3 | SIM | Text before any heading, "About the team" and "Our Culture" never count; "About Stripe", diversity, "Pay Range Transparency" and "Compliance" are boilerplate | Revision: R2 sections |
| S4 | FILTER.md | `COUNTS_HEADINGS` and `BOILERPLATE_HEADINGS` equal the two lists in the revision | Revision: R2 sections |
| G7 | SIM | `html_to_text` gives the lines "SQL & Python skills", "One", "Two words", "A", "B" | Expected sources |

## tests/test_js3_sources.py (change to copied parsers.py; loop.py unchanged)

| Test | Data | Expected outcome | FILTER.md item |
|---|---|---|---|
| G1 | SIM | Greenhouse `content` escaped once comes back as the original HTML (inner `&amp;` kept) in `description_html` | Expected sources (Greenhouse) |
| G2 | SIM | Without `include_description`, both parsers return exactly id, title, location, url, as in JS2. **Passes before any change** (existing behavior) | JS2 parser kept |
| G3 | SIM | Ashby `descriptionHtml` is returned unchanged as `description_html` | Expected sources (Ashby) |
| G4 | SIM | Missing or empty content/descriptionHtml becomes `""` (4 postings) | Expected sources (missing description) |
| G5 | — | `job_filter.JS3_URLS["greenhouse"]` = JS2 URL + `?content=true`, allowed by the policy; Ashby URL unchanged | Expected sources |
| G6 | SIM | `run_loop` with `JS3_URLS`: exactly 3 requests (one per board, the `?content=true` URLs), exit `finished` | Expected sources + JS2 budgets |

## tests/test_job_filter.py

| Test | Data | Expected outcome | FILTER.md item |
|---|---|---|---|
| R1a | SIM | 9 role titles: R1 pass; "Maintenance Technician", "Email Marketing Associate": R1 fail | R1 |
| R1b | SIM | Software Engineer + New Grad / Early Career / Entry / University: R1 pass; "Software Engineer" alone: R1 fail | R1 |
| R2a | SIM | "Fraud Analyst", SQL/data in Responsibilities, 0-1 years: R2 pass, `shortlisted` (score 6) | R2 |
| R2b | SIM | Data/AI words only in intro, About, Benefits: R2 fail, `not shortlisted` | R2, Revision: R2 sections |
| R2c | SIM | Data/AI words only under "About the team": R2 fail, `not shortlisted` | Revision: R2 sections |
| R2d | SIM | No recognized responsibilities/skills section: R2 cannot tell, `I cannot tell` | Revision: R2 sections |
| R2e | REAL | Fraud Intelligence Analyst 1bcfe93d: R2 pass with a quote from a counts section; `rejected` (R5: 5+ years) | R2 |
| R3a | SIM | Senior, Staff, Principal, Lead, Leader, Manager, Director, Head, Intern, Internship: R3 fail, `rejected` | R3 |
| R3b | SIM | "Sr" and "Sr.": `rejected`; "Srinivasan": R3 pass | R3 |
| R4a | SIM | "Boston, Massachusetts", "United States", "Remote - US": R4 pass | R4 |
| R4b | SIM | "Remote - Germany", "London, United Kingdom": R4 fail, `rejected` | R4 |
| R4c | REAL | 1bcfe93d location "San Francisco HQ (United States)": R4 pass | R4 |
| R5a | SIM | "0-1 years", "new grad", "entry level" in a counts section: R5 pass, early 2 | R5 |
| R5b | SIM | "2+ years", "3-5 years": R5 fail, `rejected` | R5 |
| R5c | SIM | "0-2 years": R5 fail, `rejected` | Revision: R5 ranges; wrong version 4 |
| R5d | SIM + REAL | "2–4 years" (en dash): `rejected`; real d2c9d8b1 rejected by R5, quote contains "4–6 years" | R5 |
| R5e | SIM | "not for new graduates": `rejected` | R5 |
| R5f | SIM + REAL | Added 2026-11-18 after the JS3 audit, against the existing filter code. "7 or more years", "1 or more years": R5 fail, `rejected`, quote contains the phrase; real Stripe 8248088 (Nov 17 run) R5 fail, `rejected`, quote contains "7 or more years". Predicted against the current code: **fails** (R5 "cannot tell") until R5 reads "N or more years" | R5, D4 |
| R6a | SIM | Citizenship required, security clearance required, will not / unable to sponsor, without sponsorship: R6 fail, `rejected` | R6, D5 |
| R6b | SIM | Export-control "Compliance" paragraph: R6 pass, `shortlisted` | R6; wrong version 2 |
| R6c | REAL | Posting 7072d96d ("sponsorship assets"): R6 not fail | R6, D5 |
| R7a | SIM | 5 distinct topic words (one repeated): 3 topic points | R7, score |
| R7b | SIM | "sparked", "Pythonic": 0 topic points | R7 |
| SC1 | SIM | Role + 0-1 years, no topic words: score 5, `shortlisted` | Score |
| SC2 | function | `score_points(role, no early, 2 topics)` = 5; shortlisted | Score |
| SC3 | function | `score_points(role, no early, 1 topic)` = 4; not shortlisted | Score |
| SC4 | function | role + 5 topics = 6 (cap 3) | Score |
| SC5 | function + SIM | no role + early + 3 topics = 5, not shortlisted; SIM "Platform Engineer, New Grad": score 5, `not shortlisted` | Score (R1/R2 required) |
| SC6 | SIM | "Senior Machine Learning Engineer": `rejected`, score `None` | Score |
| SC7 | FILTER.md | Weights 3/2/1, cap 3, threshold 5, R7 topic words and R3 seniority words equal FILTER.md | Score, R3, R7 |
| E1 | REAL | All 144 Plaid postings: one of the 4 verdicts; every quote is an exact substring of title, location or description text | Evidence rules |
| E2 | SIM | "5+ years": claim "asks 0-1 years" contradicted, quote contains "5+ years" | Evidence rules |
| E3 | SIM | No sponsorship sentence: "no sponsorship restriction" insufficient, quote `None` | Evidence rules; wrong version 6 |
| E4 | SIM | Empty, blank or missing description (also with a "Senior" title): `I cannot tell`, score `None` | Expected sources; wrong version 5 |
| E5 | SIM | No experience statement, no early-career words: R5 cannot tell, `I cannot tell` | Evidence rules, R5 |
| W1 | SIM | Sales posting ("sales training", "model", "data-driven"): 0 topic points | Wrong version 1 |
| W3 | REAL | Exactly 8 Plaid postings are relevant under the JS1 title-only rule (incl. 1bcfe93d); the filter rejects all 8 by R5 with a "years" quote | Wrong version 3 |
| D1 | SIM | Topic words only in the Databricks intro / "About Databricks": 0 topic points | D1 |
| D2 | SIM | Location "Remote": R4 cannot tell, `I cannot tell` | D2 |
| D3 | SIM | "new grad" only in About or an unrelated program: R5 cannot tell, `I cannot tell`; "New Grad" in the title or a counts section: R5 pass, early 2 | D3 |
| D4 | SIM | "1+ years": R5 fail, `rejected` | D4 |
| D5 | SIM | EEO "citizenship status", export-control paragraph: not rejected (`shortlisted`); "must be a U.S. citizen", "will not sponsor": `rejected` | D5 |
| D6 | SIM | Japanese description: `I cannot tell` | D6 |
| O1 | SIM | `order_shortlist` keeps only shortlisted entries, in the order plaid p-1 (8), databricks 100 (6), databricks 300 (6), stripe 200 (6), databricks 050 (5), for either input order | Revision: shortlist order |

Wrong versions 2, 4, 5 and 6 are checked by R6b, R5c, E4 and E3.

## Expected result before implementation

Every test above except G2 should error with `ModuleNotFoundError`
(`descriptions`, `job_filter`) or `TypeError` (the parser's missing
`include_description` argument). G2 should pass, because it checks behavior
the copied parser already has. The 48 copied JS2 tests should still pass.

## Found while writing the tests (for Swathi to decide)

Under R5 plus D3, a posting is scored only when R5 passes, and R5 passes only
with early-career evidence (0-1 years, or an early-career word describing the
job). So every scored posting already has early 2. With a role match, that is
3 + 2 = 5, already the threshold. Without one, it is never shortlisted. Topic
words therefore cannot change any verdict, and the "role + 2 topic words"
path (SC2) cannot happen in a real evaluation. SC2 and SC3 check the score
arithmetic directly instead.

## Added 2026-11-19: version 1.1 regression tests (FILTER.md change log 2026-11-19)

Written by Claude Code on 2026-11-19 from the decisions recorded in FILTER.md
("Change log: Rules changed after measuring — 2026-11-19", commit `4a6dcfb`).
These are **predictions** against the unchanged version 1 code (`job_filter.py`
as committed at `6e6b4bf`), recorded before the tests were run. They are not
results. R5f is listed above. Data: SIM = built in the test; REAL = the saved
Nov 17 LIVE run, `runs/2026-11-17T21-47-06-167440-0500/`, read-only.

| Test | Data | Expected after the change | Predicted against version 1 | FILTER.md item |
|---|---|---|---|---|
| R5g | SIM | "7 years or more", "At least seven years", "Minimum of 5 years", "Minimum 5 years", "Five (5) years", "5 years+", "4 years' experience", "4 years’ experience": R5 fail, `rejected`, quote contains the phrase | **fails** on "At least seven years", "Five (5) years", "5 years+", "4 years'", "4 years’" (R5 "cannot tell"); **passes** on "7 years or more", "Minimum of 5 years", "Minimum 5 years" (version 1's "N years … experience" and "minimum of" patterns already match them) | change log: R5 parsing |
| R5h | SIM | "Two years of university education…", "At least two years of university study…" next to "0-1 years of experience": R5 pass, `shortlisted` | **passes** (a guard: version 1 reads neither as years) | change log: R5, education is not experience |
| R5i | SIM | "one (1) year" + "five (5) years", both mandatory: R5 fail, quote contains "five (5) years"; "one (1) year" alone: R5 pass | **fails** (R5 "cannot tell": version 1 reads neither) | change log: R5, largest minimum decides |
| R5j | SIM | "3+ years … is a plus", "8+ years … preferred", "Recommended: 2+ years…", "5+ years…" under "Preferred qualifications", each next to "0-1 years": R5 pass, `shortlisted` | **fails** (version 1 rejects every stated "N+ years") | change log: R5, optional statements |
| R5k | SIM | "MS plus 2 years…, or BS plus 3 years…": R5 fail; "PhD with 0-1 years…, or MS with 2+ years…": R5 pass | **fails** on the second line (version 1 rejects the "2+ years" alternative) | change log: R5, alternatives |
| R6d | SIM + REAL | "U.S. citizenship and eligibility for a U.S. government secret clearance are required…", "requires U.S. citizenship", "Must have an active Secret clearance", "requires an active Top Secret Clearance", "Required: … TS/SCI clearance": R6 fail, `rejected`; real databricks 8760167002: R6 fail, `rejected`, quote contains "U.S. citizenship" | **fails** (version 1 matches only "security clearance" and "U.S. citizenship is required") | change log: R6 wording |
| R6e | SIM + REAL | Government customers, regulatory clearance, equal-opportunity "citizenship status", clearance as an advantage or preferred: R6 pass, `shortlisted`; real databricks 8206138002 (audit row 33): R6 pass | **passes** (a guard against over-matching) | change log: R6, not counted |
| U1 | SIM + REAL | "university" only in description text, no experience stated: R5 cannot tell, `I cannot tell`; real Stripe 8186445: R5 not pass | **fails** (version 1 counts "university" in a counts section) | change log: university false friend |
| U2 | SIM | "University Graduate" in the title, no experience stated: R5 pass, early 2 | **passes** (version 1 already counts the title) | change log: university in the title |

Every other existing test should still pass against version 1.
