# CONTRACT.md

## Job-Search Agent 1 — The Contract and the Watch

Date: October 31, 2026
Language: Python
Company: Stripe
Job Board: Greenhouse
**Fictional Candidate:** Rohan Desai

## 1. Purpose

The Job-Search Agent monitors Stripe's public Greenhouse job board, identifies newly posted software engineering opportunities, and evaluates their relevance against a fictional candidate's résumé.

The agent uses two independent evaluation methods:

1. A deterministic rule-based evaluation that produces a reproducible record.
2. A Claude-based evaluation that produces a model judgment under a fixed prompt contract.

The agent is intended only for job discovery and evaluation. It does not apply for jobs or communicate with employers.

## 2. Input

The agent accepts the following inputs:

* Board name: Stripe
* ATS platform: Greenhouse
- **Résumé:** Rohan Desai's fictional résumé in JSON format.
* Job postings: Public JSON data retrieved from the Greenhouse API.

### Greenhouse API endpoint

`https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`

### Network allow-list

Only the following hostname is permitted:

`boards-api.greenhouse.io`

The agent must use read-only GET requests and reject unapproved hosts and redirects.

### Fictional résumé skills

Rohan Desai's fictional résumé includes:

**Programming Languages:**
- Python
- Go
- Java
- JavaScript
- SQL
- Protobuf

**Frontend:**
- React
- Next.js
- Tailwind CSS
- TypeScript

**Databases and Cloud:**
- PostgreSQL
- MongoDB
- Redis
- AWS
- GCP

**DevOps and CI/CD:**
- Docker
- Kubernetes
- Jenkins
- Terraform

All résumé information is fictional and uses example contact details.

## 3. Output

For each newly discovered posting, the agent produces:

1. Job title.
2. Posting ID.
3. Job location.
4. Department or team, if available.
5. Rule-based verdict: RELEVANT or NOT RELEVANT.
6. Claude's judgment: RELEVANT or NOT RELEVANT.
7. Matching résumé skills and corresponding job requirements.
8. An evidence-based justification referencing actual résumé fields and job-posting fields.

The two verdicts must remain separate.
Claude's judgment must be explicitly labeled as a model-generated judgment, not an objective fact.
Every justification must identify the source fields supporting its conclusion.

## 4. Refusals and boundaries

The agent must refuse to:

1. Fetch any website or hostname outside the explicit allow-list.
2. Display or publish a real person's résumé or personal information.
3. Present Claude's opinion as an established fact.
4. Apply for jobs on behalf of the candidate.
5. Send emails, messages, or contact recruiters.
6. Log in to websites or access private job boards.
7. Make POST, PUT, PATCH, or DELETE requests.
8. Follow redirects to unapproved hosts.
9. Invent job descriptions, résumé skills, or matching evidence.

The agent is limited to read-only monitoring of the approved public endpoint.

## 5. Deterministic relevance rule

A job is relevant if its title identifies a Software Engineer, Software Developer, Backend Engineer, or Full-Stack Engineer position, its employment level is an internship, co-op, or new-graduate opportunity, its location is in the United States, and its description explicitly requires or prefers at least two of the following skills:

* Python
* Go
* Java
* JavaScript
* SQL
* PostgreSQL
* AWS
* Docker
* Kubernetes
* Jenkins

All three conditions must be satisfied:

1. Role condition: The job title matches one of the four eligible engineering roles.
2. Employment and location condition: The opportunity is an internship, co-op, or new-graduate position located in the United States.
3. Technical skill condition: At least two of the ten specified skills appear in the job description.

If any condition is false or cannot be verified from the available posting fields, the verdict is NOT RELEVANT.
The rule-based evaluation must be deterministic and reproducible without Claude.
The implementation must document how it interprets job titles, employment levels, locations, and skill mentions.

## 6. Wrong versions that tests must catch

### Wrong Version 1: Verdicts associated with incorrect postings

The agent retrieves multiple postings but accidentally assigns one posting's verdict or justification to another posting.

Test: Provide multiple postings with unique IDs and different expected verdicts. Verify that every verdict and justification is associated with the correct posting ID.

### Wrong Version 2: Justification without evidence

The agent produces a relevant verdict with a generic explanation but does not identify matching résumé fields and job-posting fields.

Test: Reject justifications that do not identify at least two actual matching skills and their corresponding source fields.

## 7. Failure statement

A failure is 2026-10-31: the agent reports an existing job as new, assigns a verdict to the wrong posting, or produces a relevant verdict without evidence from the résumé and job description.

## 8. Autonomy and permissions

The agent operates with limited autonomy.

It is permitted to:

* Fetch public job postings from the approved Greenhouse endpoint.
* Save raw JSON responses as evidence.
* Read the fictional résumé JSON.
* Maintain a local state file containing previously seen posting IDs.
* Identify newly discovered postings.
* Generate rule-based and Claude-generated verdicts.
* Validate Claude's output against a fixed output schema.

It is not permitted to:

* Apply for jobs.
* Send communications.
* Access private accounts.
* Modify external job-board data.
* Access unapproved websites.

## 9. New-posting identification

The first execution establishes a baseline by saving all currently available posting IDs. It reports zero new postings.

On subsequent executions, the agent compares the current posting IDs against the IDs stored in its local state file.

Only previously unseen posting IDs are reported as new.

The agent saves each raw response as evidence and updates its local state after processing.

A second run must demonstrate a real change using a later calendar-day response or an explicitly labeled seeded response.

## 10. Verification requirements

The implementation must include tests for:

* First-run baseline behavior.
* Identification of newly added postings.
* Prevention of duplicate posting reports.
* Correct association between posting IDs and verdicts.
* Evidence-based justifications.
* Rejection of invalid Claude output.
* Enforcement of the hostname allow-list.
* Rejection of unapproved redirects.
* Separation of deterministic verdicts and model judgments.

All test results, execution evidence, and limitations must be documented in README.md.

End of Contract
