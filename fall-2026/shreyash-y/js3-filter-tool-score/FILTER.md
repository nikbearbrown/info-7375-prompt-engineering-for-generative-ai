<!--
Shreyash's answers below were written by Shreyash Yadav and pasted into the Claude Code session on
2026-11-25 at about 16:58 EST, before any JS3 code, test or run existed. Claude Code changed formatting
only (headings, bullets, code spans). The lines marked "Shreyash" are as pasted. The numbers 1-13 are
Shreyash's answer numbers.

So that every rule's exact word list is in this file, Claude Code added two kinds of labeled blocks:
"From CONTRACT.md" / "From GATE.md" / "From review/19" quote Shreyash's own earlier documents unchanged
(JS1 2026-10-28, JS2 2026-11-09 and 2026-11-10); "Accepted text" is Claude Code's suggestion from this
session, which Shreyash accepted in answer 11. How each phrase became code goes in FILTER-NOTES.md,
a separate file, so this one stays as written. Changes after measuring go only in the version log at
the end, each dated, with what was measured and who decided.

Follow-up: at 17:03 EST Claude Code asked for a one-line reason for six rules and three decisions
(A, B, C). Shreyash's follow-up answers were pasted at about 17:05 EST, also before any JS3 code, and
are placed under the rule each one answers, marked "follow-up". Claude Code's questions are shown in
italics above answers A, B and C, so the answers can be read on their own.
-->

# FILTER — Job-Search Agent 3

**Version: v1, 2026-11-25.** Persona: Alex Morgan (fictional, `persona/alex_morgan.json` from JS1).

## Starting point and sources

**1. Start from my JS2 agent and borrow Lectern's reject-audit method.**

> **Shreyash:** Yes. I want to use my JS2 agent instead of building everything again. I also want to check rejected jobs to see if the agent is making any mistakes.

**2. Boards.**

> **Shreyash:** Yes, keep the same six boards. This will also help me compare the results with JS2.

*From GATE.md section 1 (JS2, 2026-11-09):* Greenhouse `oscar` and `klaviyo`, Ashby `linear`, Lever `palantir`; `oscarhealth-doesnotexist` as a deliberate failure and `whoop` as an empty board.

**3. When a board fails or a field is missing.**

> **Shreyash:** The agent should clearly say what failed or what is missing. It should not guess or make up any data.

*From CONTRACT.md section 2 (JS1, 2026-10-28):* "Posting fields used: Posting ID, company board token, title, department, location, job description, required skills, and minimum experience."

## The filter, v1

### Rule 1 — Title (answer 4: keep)

*From CONTRACT.md section 5, Condition 1:* "The posting title must contain at least one of these phrases (case-insensitive): `Software Engineer`, `Software Developer`, `Backend Engineer`, `Full Stack Engineer`, `Full Stack Developer`, `AI Engineer`, `ML Engineer`, `Machine Learning Engineer`, or `LLM Engineer`."

> **Shreyash:** The title should contain a role phrase like Software Engineer, AI Engineer or ML Engineer because these are the roles Alex is looking for.

### Rule 2 — Department (answer 5: keep)

*From CONTRACT.md section 5, Condition 2:* "The department must be one of: `Engineering`, `Software Engineering`, `Machine Learning`, `AI`, `Artificial Intelligence`, or `Data Science`."

> **Shreyash:** Yes, Palantir's "Dev" should count as engineering. I don't want to miss a job just because the company uses a different department name.

> **Shreyash (follow-up, why this rule exists):** To make sure the job is related to engineering.

*From review/19 (JS2, 2026-11-10):* "This interpretation applies specifically to Palantir, not automatically to other companies using the same department name."

### Rule 3 — Location (answer 6: keep)

*From CONTRACT.md section 5, Condition 3:* "The posting must be located in Boston, MA, or explicitly support remote employment within the United States."

*From GATE.md section 8 (JS2, 2026-11-09):* "I'll focus on counting experience only from mandatory qualifications, rejecting hybrid jobs even when they have a Remote tag, and making sure remote jobs can actually be worked from Massachusetts."

> **Shreyash:** The job should be in Boston or allow Alex to work remotely from Massachusetts.
>
> - **6a.** If the office tag and ad text disagree, the agent should say "I cannot tell" instead of guessing.
> - **6b.** If the location field and office list disagree, the agent should check the job description. If it is still unclear, say "I cannot tell."

> **Shreyash (follow-up, why this rule exists):** Alex lives in Boston and does not want to relocate.

*Question A (Claude Code, 17:03): A job has a "Remote" tag, but the ad says hybrid or on-site. In JS2 (GATE.md section 8) you said reject these. Your answer 6a would now make them "I cannot tell". Which one do you want?*

> **Shreyash (follow-up A):** Reject the job. I want to keep the same rule from JS2. If the remote tag says remote but the job description clearly says hybrid or on-site, the job description wins. If it is still unclear, say "I cannot tell."

### Rule 4 — Skills (answer 7: keep)

*From CONTRACT.md section 5, Condition 4:* "The posting description must mention at least TWO of the fictional applicant's ten listed skills. Skill matching is case-insensitive and uses complete terms or phrases." *Section 1, the ten skills:* Python, Java, TypeScript, FastAPI, React, LangGraph, RAG, PyTorch, SQL, Docker.

> **Shreyash:** At least 2 of Alex's 10 skills should be mentioned in the job description.

> **Shreyash (follow-up, why this rule exists):** At least 2 skills should match what Alex already knows.

### Rule 5 — Experience (answer 8: keep)

*From CONTRACT.md section 5, Condition 5:* "The minimum required experience must be 3 years or fewer. If no experience requirement is stated, this condition passes without assuming an experience match."

> **Shreyash:** The required experience should be 3 years or less. If experience is not mentioned, it passes this rule.

> **Shreyash (follow-up, why this rule exists):** Alex has 3 years of experience, so I don't want jobs that require more.

*Question B (Claude Code, 17:03): A job states no experience requirement. Answer 8 says it passes, but your evidence rules say a must-have with no information means "I cannot tell". For these jobs: keep them with experience marked "not stated", or move them to "I cannot tell"?*

> **Shreyash (follow-up B):** Keep the job and mark experience as "not stated." Just because the company does not mention experience does not mean Alex is not eligible. I want this to be an exception to the evidence rule.

### Rule 6 — Exclusions (answer 9: keep)

*From CONTRACT.md section 5, Condition 6:* "Reject postings with `Director`, `Staff`, `Principal`, `Manager`, or `Lead` as whole words in the title. Also reject unpaid internships, contract-only positions, and jobs explicitly requiring relocation outside Boston."

> **Shreyash:** Exclude Director, Staff, Principal, Manager, Lead, unpaid jobs, contract-only jobs and jobs that require relocation. Paid internships are out because Alex is looking for full-time jobs.

> **Shreyash (follow-up, why this rule exists):** I want to avoid jobs that do not match Alex's experience or work preferences.

*Question C (Claude Code, 17:03): You ruled out internships because Alex wants full-time work. Are part-time and temporary jobs out too?*

> **Shreyash (follow-up C):** Yes, exclude part-time and temporary jobs too. Alex is only looking for full-time permanent jobs.

### Final decision (answer 10: keep)

*From CONTRACT.md section 5:* "If any mandatory title, department, location, or skills information is missing, the condition fails with an explanation rather than being guessed." "Return `Relevant` only when all six conditions pass. Otherwise, return `Not Relevant` and identify the failed conditions."

> **Shreyash:** A job should only be kept if it passes all the rules. If it fails exactly one rule and passes the rest, it should be marked as a closest call.

> **Shreyash (follow-up, why this rule exists):** Every rule must pass because even one failed rule can make the job unsuitable for Alex.

## Evidence rules (answer 11: keep)

*Accepted text: Claude Code's suggestion from this session, which Shreyash accepted in answer 11:*

- A claim is **supported** when a quote copied exactly from the posting states it. Code checks that the quote is really there.
- It is **contradicted** when a quote says the opposite, like "5+ years required" against "3 years or less".
- It is **insufficient** when the posting says neither.
- The agent says **"I cannot tell"** when a must-have claim (role, location, experience, exclusions) is insufficient, when one quote supports it and another contradicts it, or when the posting text is empty.

> **Shreyash:** I agree with these rules. The agent should use exact quotes from the job posting. If there is not enough information or the posting says two different things, the agent should say "I cannot tell."

*Cross-reference added by Claude Code: follow-up B, under Rule 5, makes "experience not stated" an exception to these rules.*

## Wrong versions my tests must catch (answer 12)

> **Shreyash:**
>
> - The agent accepts a remote job that does not allow someone to work from Massachusetts.
> - The agent counts skills mentioned in employee benefits as required job skills.
> - The agent accepts a job that requires more than 3 years of experience.
> - The agent makes up a quote when information is missing.
> - The agent treats a failed board as a board with zero jobs.

## The tool (answer 13)

> **Shreyash:** Yes. I want to use `score_posting` to check each job against my rules. I also want to test `chrome-devtools-mcp` to see if it is useful for checking job postings before deciding whether to use it.

## Version log

| Version | Date | Change | Measured on | Decided by |
|---|---|---|---|---|
| v1 | 2026-11-25 | First version: answers 1-13 (16:58 EST) and the follow-up reasons and decisions A-C (17:05 EST) | nothing yet; written before any JS3 code or run | Shreyash |
