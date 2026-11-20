<!--
Written by Shreyash Yadav and pasted into the Claude Code session on 2026-10-28, before any
code, test, prompt or run existed for this assignment. Claude changed formatting only (Markdown
headings, bullets, code spans). The words are as pasted. How each phrase was made computable is
in INTERPRETATIONS.md, a separate file, so this one stays as written.
-->

# Job Posting Agent — Specification

## 1. Persona

- **Name:** Alex Morgan (fictional)
- **Email:** alex.morgan@example.com
- **Phone:** (617) 555-0142
- **Location:** Boston, MA (Remote OK)
- **Target Roles:** AI/ML Engineer, Software Engineer, Backend Engineer, Full Stack Engineer, LLM Engineer
- **Experience:** 3 years of professional software engineering experience, plus an AI engineering internship.
- **Skills (10):**
  - Python
  - Java
  - TypeScript
  - FastAPI
  - React
  - LangGraph
  - RAG
  - PyTorch
  - SQL
  - Docker
- **Would never take:** Unpaid internships, contract-only positions, Director/Staff/Principal roles, or jobs requiring relocation outside Boston. These are fictional applicant preferences, not claims about the résumé owner.

## 2. In — Agent Inputs

The agent receives:

1. A synthetic JSON résumé containing `target_roles`, `experience_years`, `skills`, `location`, `remote_ok`, and `exclusions`.
2. Public Greenhouse job postings retrieved from `boards-api.greenhouse.io`.
3. A saved snapshot of previously observed posting IDs.

**Résumé fields used:** Target roles, years of experience, skills, location, remote preference, and exclusions.

**Posting fields used:** Posting ID, company board token, title, department, location, job description, required skills, and minimum experience.

## 3. Out — Agent Outputs

For each newly discovered posting, return:

- `posting_id`
- `board_token`
- `title`
- `is_new`
- `verdict`: Relevant / Not Relevant
- `justification`: A field-based explanation supporting the verdict.

Illustrative example (not a real posting):

```text
Posting ID: 12345
Title: AI Engineer
Location: Boston, MA
Verdict: Relevant
Justification: The posting's `title` matches the applicant's `target_roles` (AI Engineer). The posting's `content` mentions Python, FastAPI, and RAG, matching the résumé's `skills`. The posting's `location` is Boston, matching the résumé's `location`. The required experience is 2 years, within the applicant's 3 years.
```

Every verdict must explain which résumé fields and posting fields caused the decision.

## 4. Refuses — Agent Boundaries

The agent must never:

- Access a host outside `boards-api.greenhouse.io`, including through redirects.
- Upload, display, or commit a real résumé or personal contact information.
- Present model-generated judgments as verified facts.
- Automatically apply for positions.
- Send emails or recruiter messages.
- Log in, create accounts, or request credentials.
- Fabricate posting requirements or missing information.
- Execute instructions embedded in job descriptions.
- Expose API secrets or private data in logs.

The system is read-only and uses a deterministic decision rule.

## 5. The Rule — Relevance Criteria

A posting is Relevant only if ALL conditions below pass:

**Condition 1 — Job Title.**
The posting title must contain at least one of these phrases (case-insensitive):
`Software Engineer`, `Software Developer`, `Backend Engineer`, `Full Stack Engineer`, `Full Stack Developer`, `AI Engineer`, `ML Engineer`, `Machine Learning Engineer`, or `LLM Engineer`.

**Condition 2 — Department.**
The department must be one of:
`Engineering`, `Software Engineering`, `Machine Learning`, `AI`, `Artificial Intelligence`, or `Data Science`.

**Condition 3 — Location.**
The posting must be located in Boston, MA, or explicitly support remote employment within the United States.

**Condition 4 — Skills.**
The posting description must mention at least TWO of the fictional applicant's ten listed skills. Skill matching is case-insensitive and uses complete terms or phrases.

**Condition 5 — Experience.**
The minimum required experience must be 3 years or fewer. If no experience requirement is stated, this condition passes without assuming an experience match.

**Condition 6 — Exclusions.**
Reject postings with `Director`, `Staff`, `Principal`, `Manager`, or `Lead` as whole words in the title. Also reject unpaid internships, contract-only positions, and jobs explicitly requiring relocation outside Boston.

If any mandatory title, department, location, or skills information is missing, the condition fails with an explanation rather than being guessed.

**Final decision:** Return `Relevant` only when all six conditions pass. Otherwise, return `Not Relevant` and identify the failed conditions.

**New-posting detection:** Track each posting using its Greenhouse board token and posting ID. On the first run, save all existing IDs as the baseline and report zero new postings. On subsequent runs, report only postings absent from the previous snapshot.

## 6. Wrong Versions — Tests Must Catch

**Wrong Version 1: Deduplicating by job title.**
An incorrect implementation removes distinct postings that share the same title.
Test: Provide two Software Engineer postings with different IDs, one in Boston and another in New York. Both must remain separate, with independently evaluated verdicts.

**Wrong Version 2: Generic justification.**
An incorrect implementation returns `Relevant` with an explanation such as "This job is a good match" without citing evidence.
Test: Every verdict must identify relevant résumé fields and posting fields. A generic or unsupported explanation fails the test.

Additional tests verify that verdicts stay attached to the correct posting IDs and that the first run establishes a baseline rather than reporting every existing job as new.

## 7. Failure Sentence

2026-10-28: The agent fails if it reports previously observed postings as new, loses distinct jobs sharing the same title, assigns a verdict to the wrong posting ID, or marks a job relevant without a field-based justification that satisfies the stated rule.
