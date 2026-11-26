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

**Version 1.1, the same day, after the audit:** the changes are in the section "Version 1.1" near the end, and in the version log.

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

*Cross-reference added by Claude Code: v1.1 decision B4 makes "full-time not stated" a second exception (section "Version 1.1").*

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

## Version 1.1: what changed after measuring

*Shreyash's decisions, pasted into the session on 2026-11-25 at about 18:07 EST, after his 70 hand
verdicts were frozen (commit `667a2932`) and compared with filter v1, and before any v1.1 code existed.
Claude Code changed formatting only. The italic "Measured" line before each decision is Claude Code's,
from `results/audit-v1.json` and `results/score-v1.json` (AUDIT.md, SCORE.md).*

*Correction by Claude Code, 2026-11-25 19:00 EST, after the independent review: the "Measured" lines came
from more places than the note above says.*

- *A1's and A5's numbers are in `results/score-v1.json`.*
- *A2's and A3's were measured by an ad-hoc script before 18:07 and saved only at 18:16
  (`js3/whatif.py`, `results/whatif-v1.json`).*
- *B4's number is in `results/shortlist-v1.json`.*
- *A4's "36" was not measured; see the correction under A4.*
- *The hand verdicts behind these decisions are described in `labels/hand-verdicts-provenance.md`:
  item 49 for A1, item 31 for A2 and A5, and item 39 for the false positive that led to A3. The final
  answers for 39 and 49 were given after Claude Code described how the rules read those postings.*

**A1. Add the title phrase "Product Engineer" (Rule 1).** *Measured: fixes the one audit miss it touches
(Linear "Product Engineer", hand label yes); 1 more posting kept of 789; no held-out posting is affected.*

> **Shreyash:** Adopt. Product Engineer should be included because the actual work matches Alex's full-stack skills, even if the job title is different.

**A2. Count MySQL, PostgreSQL and Postgres as SQL (Rule 4).** *Measured: fixes the audit miss
(Klaviyo "Software Engineer II - Recommendations", hand label yes); 1 more posting kept of 789, and it is
closed; no held-out posting is affected.*

> **Shreyash:** Adopt. MySQL, PostgreSQL and Postgres should count as SQL because they use SQL. I don't want Alex to miss a job because of exact word matching.

**A3. Count a skill only where the ad asks for it (Rule 4).** *Measured: removes the audit's one false
positive (the Android/Kotlin job), but drops Growth and Flows, which Shreyash labeled yes in the
held-out set: 2 new misses there.*

> **Shreyash:** Reject. This fixes the Android mistake but creates two new mistakes on the held-out set. I would rather improve how the filter checks the main skills of a job instead of removing all skills from technology lists.

**A4. A residence line that names one state limits the job (Rule 3).** *Measured: 0 verdicts change; 36
location results go from "cannot tell" to "fail" (Oscar: "This is a remote position, open to candidates
who reside in: Dallas, Texas.").*

> **Shreyash:** Adopt. If the company clearly says the person must live in a certain state, the agent should use that information. It should mark the location as failed instead of saying it cannot tell.

*Correction by Claude Code, 2026-11-25 18:12 EST: "36" above was the number of postings with this pattern under v1, given as if it
were the measured effect of the change. Measured: the first v1.1 code moved 12 of them. Of the other 24, 21 write the state
as a two-letter code ("reside in: Dallas, TX."), 2 write "reside:" without "in" (one of them also with a
code), and 1 is the Palantir ad below. [Arithmetic corrected at 19:00 EST, after the review: this line first
said "24 … and 2", which sums to 38.] After two test-first fixes to the
code (tests/test_js3_filter_v11_state_codes.py), the change moves 35 of the 36 to "fail"; the 36th (Palantir, Warsaw) is
not a residence line. 0 verdicts change, as stated. Shreyash's decision is unchanged.*

**A5. Minimum skills 1 instead of 2, the number fitted on the audit labels (Rule 4).** *Measured: 1 beats 2
on the audit set by one posting; they tie on the held-out set.*

> **Shreyash:** Reject. I want to keep at least two matching skills. Reducing it to one just to fix a missed job could allow more unrelated jobs to pass. A2 already fixes the Recommendations mistake.

**B4. Evidence rules: "full-time not stated".** *Measured: all 5 kept postings came out "I cannot tell" only
because none of the five ads says "full-time".*

> **Shreyash:** Yes, make it an exception. If full-time is not stated, I want the job to pass this rule but mark employment type as "not stated." If the ad clearly says part-time, temporary, internship, unpaid or contract-only, reject it.

## Version log

| Version | Date | Change | Measured on | Decided by |
|---|---|---|---|---|
| v1 | 2026-11-25 | First version: answers 1-13 (16:58 EST) and the follow-up reasons and decisions A-C (17:05 EST) | nothing yet; written before any JS3 code or run | Shreyash |
| v1.1 | 2026-11-25 | **Added** the title phrase "Product Engineer" (A1) | audit: fixes 1 miss; corpus: +1 kept; held-out: no posting affected | Shreyash |
| v1.1 | 2026-11-25 | **Added** MySQL, PostgreSQL and Postgres as SQL (A2) | audit: fixes 1 miss; corpus: +1 kept (closed); held-out: no posting affected | Shreyash |
| v1.1 | 2026-11-25 | **Added** a residence line naming one state as a location limit (A4) | corpus: 0 verdicts; 35 of 36 location results cannot tell -> fail (corrected 18:12 EST, see A4) | Shreyash |
| v1.1 | 2026-11-25 | **Added** to the evidence rules: "full-time not stated" passes, marked not stated (B4) | shortlist: all 5 kept were "I cannot tell" only for this | Shreyash |
| v1.1 | 2026-11-25 | **Rejected**: count a skill only where the ad asks for it (A3) | audit: fixes 1 false positive; held-out: creates 2 misses | Shreyash |
| v1.1 | 2026-11-25 | **Rejected**: minimum skills 1, the fitted number (A5) | audit: +1 agreement; held-out: tie | Shreyash |
| v1.1 | 2026-11-25 | **Kept**, with reasons written after the re-grade: minimum skills 2, Boston and eligible remote jobs, Rule 2, and the Android job as a known false positive (next section) | the measurements above and in SCORE.md section 2 | Shreyash |

## Version 1.1: my reasons for what stayed the same

*Shreyash's words, written by him and pasted into the session on 2026-11-25 at 21:04 EST, after the
second re-grade asked for his own reasons. Claude Code changed nothing. No rule changed: v1.1 stands as
decided above. The last three sentences under 3 were sent at 21:11 EST. They replace his first
sentence on the Palantir `Dev` exception, which repeated Claude Code's backwards numbers ("reduces the
closest calls from 44 to 9").*

**1. Skills — Keep the minimum at two.**

I kept the minimum at two because one matching skill is not enough to decide whether a job fits my profile. A posting might mention one familiar technology without having relevant responsibilities. Increasing the minimum to three changes no verdicts, so I don't see a reason to change it.

**2. Location — Keep Boston and eligible remote jobs.**

I selected Boston because I am currently based here. I would also consider Cambridge and nearby towns if commuting is manageable. Since none of the 789 postings tests this situation, I would keep the current rule until I have enough evidence to evaluate a broader location rule.

**3. Rule 2 — Keep the department rule.**

Even though removing this rule changes no verdicts, I prefer keeping it as an additional check against unrelated departments. I would keep the Palantir Dev exception because Dev is a relevant engineering department. Even though it increases the closest calls from 9 to 44, I prefer accurate department classification over reducing the number of postings I need to review. The final verdicts remain unchanged.

**4. Android job — Keep it as a known false positive.**

I would reject this job manually because its main requirements are Android and Kotlin. I would not adopt A3 because it would also remove Growth and Flows, which I consider relevant. I would rather review an occasional false positive than miss suitable opportunities. The filter helps me shortlist jobs, but the final decision remains mine.
