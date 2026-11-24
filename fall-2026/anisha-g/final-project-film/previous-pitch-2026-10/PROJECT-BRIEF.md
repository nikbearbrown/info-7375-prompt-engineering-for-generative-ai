# Project Brief — JobPost Contracts (working title)

**Name:** Anisha Gaikar
**Target role:** Junior AI / prompt engineer
**Stack:** Python + Claude

## 1. What is it?
A small Python library of prompt contracts that turns a job posting into a structured summary, with a test set that catches Claude inventing details that are not in the posting.

When it is done, it will be a GitHub repository containing:
- the prompt contracts
- 20 synthetic job postings, with a hand-written expected answer for each
- a test script
- an evaluation log that records what passed, what failed, and why

## 2. Why would anyone care?
The user is anyone who reads many job postings and needs the key facts quickly: a job seeker, or a recruiter comparing roles.

Alternatives I will compare against:
- pasting a posting into a general chatbot and asking for a summary
- copying the fields into a spreadsheet by hand

On 2026-10-13 I tried ChatGPT on a real internship posting (Staples, Financial Analytics Intern, from LinkedIn). It could not open the LinkedIn link. With the text pasted, it gave a good summary and correctly said the salary was not disclosed, but it did not show which line of the posting each fact came from, and under location it added a detail that is not in the posting ("Staples is headquartered near Boston"). Copying fields into a spreadsheet by hand is accurate, but slow. Screenshots are in `evidence/` (personal details cropped out).

The difference: every field my tool extracts must be backed by a quote from the posting, or marked "not stated," and the test script checks for invented fields.

## 3. Who opens it, and what do they do?
A hiring manager or engineer reviewing a candidate for a junior AI engineering role.

In the first 60 seconds they will read the README, run one command (`python run_tests.py`), and see a pass/fail table plus a log of the cases that failed.

## 4. What does it prove about me?
- **Prompt contracts:** each prompt will have defined inputs, a defined output format, and rules for what to do when information is missing.
- **Source grounding:** each extracted field will be tied to a quote from the posting.
- **Verification:** the script will check that each quote actually appears in the posting.
- **Evaluation:** a fixed test set and a log of results, including failures.

The evidence will be the test results and evaluation log in the repository. It will **not** prove the tool works on real postings at scale, because it is only tested on synthetic data.

## 5. What is in, what is out, what comes first?
**In:** five fields: job title, seniority, required skills, location/remote, and salary.

**Out:** no scraping of real job sites, no real postings, and no ranking jobs or giving career advice.

**First:** one contract run on one synthetic posting. I will know it ran when the output matches my hand-written expected answer and the test script prints PASS.

## 6. What could sink it?
**Risk:** my synthetic postings may be too clean, so the tests pass easily and prove nothing.
**What I will do:** write at least 5 deliberately tricky postings, for example one with no salary, one where skills are implied but not listed, and one with conflicting seniority signals.

**Second risk:** checking that a quote exists does not catch a quote assigned to the wrong field.
**What I will do:** hand-check those cases and record them in the log.

## 7. Why this project?
I picked this project because it is small enough for one person to finish and it uses exactly what this course teaches. It is a mix of new learning and skills I already have. New to me: writing prompt contracts, building a test set for AI output, and keeping an evaluation log. Already have: Python, including automated tests and data-quality checks. Evidence: my MBTA Transit Reliability Pipeline (github.com/anishagaikar0420/mbta-reliability-pipeline), a Python ELT pipeline with a test suite and a quality gate.

---

## Exists today
- This brief, the beat sheet, and the pitch film, made for this assignment
- My dated ChatGPT comparison screenshots (`evidence/`, 2026-10-13)
- The toolkit's Gate V report on this film (`reports/`), passed
- No code, contracts, test postings, or results exist yet

## Will exist
- Prompt contracts for the five fields
- 20 synthetic job postings with expected answers
- Test script (`run_tests.py`)
- Evaluation log with passes, failures, and explanations
- README explaining how to run it
