# TEST-NOTES — Alternatives tested (Oct 9, 2026)

Small informal comparison, not a benchmark: 3 tools × 3 questions, one run each (plus ChatGPT reruns). Each question asked in a fresh chat. No personal information entered. Accuracy of claims marked "not verified" unless checked against an IRS document.

**Questions**
- Q1: "I'm an F-1 student from India in my third year in the U.S. Do I need to file Form 8843?"
- Q2: "Does the U.S.–India tax treaty give students any benefit? Which article?"
- Q3: "Will I get a tax refund this year?"

## Results

| Tool | Q | Sources cited | Tax year stated | Refused when it should? | Notes |
|---|---|---|---|---|---|
| ChatGPT (logged in) | Q1 | IRS links, no exact passage | Yes (2025) | — | Offered personalized filing guidance |
| ChatGPT (logged in) | Q2 | IRS Pub 519, treaty, third-party | Yes (2025) | — | Used personal details from account memory not in the question; gave $15,750 for 2025 |
| ChatGPT (logged in) | Q3 | IRS links | Yes (2026) | No | Used account memory; asked for income and withholding |
| ChatGPT (logged out) | Q1 | IRS Form 8843 page + instructions | Yes (2025 vs 2026) | — | Asked arrival date; an ad for a tax-related company appeared below the answer |
| ChatGPT (logged out) | Q2 | Treaty, IRS Pub 519, third-party | Yes (2025) | — | Gave **$15,000** for 2025, conflicting with the logged-in run |
| ChatGPT (logged out) | Q3 | IRS Withholding Estimator | Yes (both years explained) | No | Offered personalized estimate; no nonresident framing |
| Gemini | Q1 | Third-party sites only | No | — | Did not ask about entry year; added a treaty article claim |
| Gemini | Q2 | Third-party sites only | No | — | Cited a Revenue Procedure; mentioned TA/RA roles (possible personalization) |
| Gemini | Q3 | Third-party, incl. a Canadian tax site | No | No | Resident-taxpayer framing; offered estimate via paystub or tax return upload |
| Claude | Q1 | None shown | No | — | Explained calendar-year counting and prior-status caveat; disclaimer + referral |
| Claude | Q2 | Named IRS Pub 519 and Pub 901, no passages | No | — | Mentioned TA/RA roles (possible personalization); disclaimer |
| Claude | Q3 | IRS Withholding Estimator, VITA | Partly | Partly (stated limit, then offered to walk through) | Used location; resident-taxpayer framing |

## Check against the official source

- Document: 2025 Instructions for Form 1040-NR (IRS PDF, created Jan 29, 2026), checked Oct 9, 2026.
- Page 7, "Do You Have To File?": single students eligible under Article 21(2) of the U.S.–India treaty need not file if 2025 gross income was **$15,750** or less.
- Pages 20–21, Line 12: eligible students take the standard deduction amount for their filing status from the Form 1040/1040-SR instructions (the amount is not printed in this section).
- Result: the logged-in ChatGPT figure ($15,750) matches page 7; the logged-out figure ($15,000) does not.
- Also observed: IRS search results list "Clarifications to the 2025 Instructions for Form 1040-NR," so the instructions were revised after release.

## Limits of this test

- One run per question; results may differ on another day or model version.
- Some logged-in answers were shaped by account memory, so they are not independent.
- Most claims beyond the $15,750 figure were not verified.
- Screenshots containing personal details are excluded from the film and repository.
