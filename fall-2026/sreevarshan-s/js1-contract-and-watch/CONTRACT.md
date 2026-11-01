# CONTRACT.md: Job-Search Agent 1 — Final (supersedes the drafts below)

## In

- The résumé JSON gives the agent information about Priya's education, experience, projects, and technical skills. (D1§1)
- The profile JSON tells it what roles she's targeting, her preferences, and work authorization requirements. (D1§1)
- The agent should use both to evaluate jobs it fetches from the Databricks job board. (D1§1)
- It should only retrieve public job postings and analyze them using the provided sample persona files. (D2§5)
- The agent should accept `databricks` as the board token, use Priya's fictional résumé JSON and a JSON copy of `profile.yml`, and save the results to a file with the posting IDs, verdicts, evidence, and explanations. (D5§8)

## Out

- Every result should include the posting ID, job title, company, location, URL, sponsorship status, and final verdict. (D2§4)
- Each result should show the job title, company, location, job URL, relevant skills, sponsorship information, and the final verdict with a short explanation. (D1§5)
- The explanation should mention the actual résumé or profile JSON field names used to justify the decision. (D2§4)
- Since we're monitoring only the Databricks job board, the company should be recorded as "Databricks." (D6-C§13)
- Evidence should contain the exact matched phrases and the posting field they came from, along with the relevant résumé or profile field names. (D6-C§13)
- I want only two final verdicts: relevant or not relevant. (D1§4)
- I want the agent to check both the Greenhouse location field and the job description. (D6-C§10)
- It should report whether the position is remote, hybrid, or onsite, along with the location when available. (D6-C§10)
- If neither field specifies the work arrangement, the output should say "not specified." (D6-C§10)
- If the fields contradict each other, the agent should report the conflict instead of guessing. (D6-C§10)
- I also want the rule-based output labeled "record" and Claude's separate assessment labeled "judgment," so we can compare them without confusing an AI opinion with a verified result. (D2§4)
- I want Claude to make its judgment independently without seeing the rule-based verdict. (D4§1)
- Both results should be compared afterward to identify disagreements and understand where either approach might be wrong. (D4§1)
- The agent should save the raw job-board response, maintain a file of previously seen posting IDs, and report only new postings. (D5§1)
- The first run should establish the baseline, save all existing IDs, and report zero new postings. (D5§1)
- Any seeded run should use a separate state file and clearly label its output "SEEDED." (D6-C§12)
- It should never overwrite or modify the real watch history, posting IDs, or saved evidence from live runs. (D6-C§12)

### The Claude judge

- Claude should receive the public posting, Priya's relevant résumé skill fields, target roles, experience requirements, and exclusions. (D6-C§14)
- It should never receive contact information, unnecessary personal details, or the rule-based verdict, because I want its judgment to remain independent. (D6-C§14)
- Claude must return valid JSON containing the posting ID, verdict (relevant or not relevant), skills cited with their résumé field names, and a short explanation referencing the posting fields. (D5§2)
- Any missing fields, extra fields, invalid verdicts, or incorrectly formatted responses should be rejected by the validator. (D5§2)
- If Claude returns an invalid response, the agent should retry exactly once using the same input and output requirements. (D6-C§15)
- If the second response also fails validation, it should record the judgment status as "invalid," save the validation error, and continue processing other postings. (D6-C§15)
- It should never invent a verdict or silently treat an invalid response as relevant. (D6-C§15)
- This is the only permitted exception to the external host allow-list. (D3§3)
- It should never receive personal contact information, private files, or unnecessary sensitive data. (D3§3)

## Refuses

- For this assignment, the only allowed external host should be `boards-api.greenhouse.io`. (D2§5)
- The agent's own code should connect only to `boards-api.greenhouse.io`, while the Claude judge runs separately through the `claude` CLI. (D4§3)
- The agent should never visit unauthorized websites, email anyone, log in to accounts, submit applications, or expose personal information. (D2§5)
- The agent should never access other job boards, log in, email anyone, or submit applications. (D4§3)
- It should never access unrelated websites, upload real personal résumés, publish sensitive information to GitHub, automatically apply to jobs, or present an AI-generated assumption as a verified fact. (D1§5)
- The agent should never assume missing information means yes or no. (D1§4)
- It shouldn't assume the company offers sponsorship or that it doesn't. (D0§6)

## The rule

- The title helps identify the role, but the description gives important information about required skills, experience, sponsorship, and security clearance. (D0§5)
- I don't want the agent making a decision based only on a job title when the description might contain something that changes the result. (D0§5)
- Every eligibility check should be a hard filter, meaning one failed requirement makes the job not relevant, even if the posting calls itself entry-level or new graduate. (D3§4)
- The agent should run every eligibility check instead of stopping at the first failure. (D6-C§11)
- I want all failed checks listed with their explanations so I can understand every reason a job was rejected. (D6-C§11)
- Even one failed mandatory check should make the final verdict "not relevant." (D6-C§11)
- If the same sentence contains "preferred," "nice to have," "nice-to-have," "bonus," or "plus" as a separate word, the experience or clearance requirement in that sentence should be treated as optional and ignored as a hard filter. (D6-B§2)
- Remove "plus" from the preferred words because it can mean "and" rather than an optional requirement. (D7§c)
- However, if the sentence explicitly says "required" or "must have," the mandatory requirement takes priority. (D6-B§2)

1. I want the agent to prioritize AI Engineer, ML Engineer, Machine Learning Engineer, Junior AI Engineer, and Software Engineer, Machine Learning. (D1§2)
   - Data Engineer, Junior Data Engineer, and Associate Data Engineer should also count. (D1§2)
   - A title passes if it contains an approved role phrase and does not contain any prohibited seniority term. (D6-B§7)
   - The title doesn't need to match my list exactly. (D2§2)
   - It can contain one of the approved role phrases, even with additional words before or after it. (D2§2)
   - For example, Junior Machine Learning Engineer and Software Engineer, Machine Learning should count. (D2§2)
   - Matching should be case-insensitive and based on complete words or phrases, not accidental partial matches. (D2§2)
   - "Software Engineer - Machine Learning" and "Software Engineer (Machine Learning)" should match "Software Engineer, Machine Learning." (D6-B§8)
   - The agent should normalize commas, hyphens, and parentheses as separators. (D6-B§8)
   - "ML/AI Engineer" should also match because the slash combines two approved titles, "ML Engineer" and "AI Engineer." (D6-B§8)
   - Seniority restrictions must still apply after normalization. (D6-B§8)
   - Just having the words "Data Engineer" somewhere in a title shouldn't automatically make it relevant. (D1§2)
   - "Data Engineer, Analytics Platform" should count as a role match because it contains the complete approved phrase "Data Engineer." (D5§10)
   - However, it should only receive a relevant verdict if all other eligibility checks pass. (D5§10)
2. However, the agent should check the complete title for seniority restrictions before accepting it. (D2§2)
   - I would reject titles containing Senior, Sr., Lead, Staff, Principal, Manager, Director, or Head of Engineering. (D0§3)
   - Any title containing "Head of" should be rejected, regardless of the department. (D6-C§9)
   - Both "Sr" and "Sr." should count as seniority indicators. (D6-C§9)
   - Words like "Senior," "Lead," "Staff," "Principal," "Manager," and "Director" should match only as complete words, so "Leading" should not be confused with "Lead." (D6-C§9)
3. A job should have at least two matching résumé skills. (D2§1)
   - I want the agent to count only skills that are actually listed in Priya's résumé JSON. (D2§1)
   - Python and SQL should count as two separate skills if both appear in her résumé. (D2§1)
   - Other skills should count only if they're explicitly mentioned in her résumé. (D2§1)
   - I don't want the agent assuming she knows something just because it's related to AI or data engineering. (D2§1)
   - Skills explicitly listed in her skills section still count separately. (D6-B§1)
   - I want only "Databricks Genie API" and "MLflow" to count as additional tools from Priya's experience or projects, and only if those exact names appear in her résumé. (D6-B§1)
   - Terms like "A/B framework" and "drift monitoring" should not count as tools. (D6-B§1)
   - Every matched skill must reference the exact résumé field where it appears. (D6-A§1)
   - Yes, each skill should count only once, even if it appears in multiple résumé fields. (D7§b)
   - Yes, "Databricks Genie API" should count separately from "Databricks" because they are distinct skills. (D7§b)
   - I chose option B, as worded by the chat assistant: "Databricks" counts as a matched skill only when the posting asks for it as a skill (for example "experience with Databricks" or "Databricks platform"), not when it appears only as the company name. (D8§1)
   - Skill matching should be case-insensitive and use complete words or phrases across the title and description. (D5§7)
   - SQL should not match PostgreSQL automatically. (D5§7)
   - AWS should match Amazon Web Services only through an explicitly defined alias, and only if AWS is actually listed in Priya's résumé. (D5§7)
   - For now, AWS = Amazon Web Services should be the only approved alias. (D6-A§2)
   - I don't want the agent assuming other technologies are equivalent unless we explicitly add them later. (D6-A§2)
   - PyTorch, TensorFlow, scikit-learn, and Spark should not count unless they're explicitly present in Priya's résumé JSON. (D3§1)
   - Skills under `familiar_with_not_shipped` should not count toward the two required skills because Priya hasn't demonstrated practical experience with them. (D3§2)
   - They can be reported as additional familiarity, but not used to justify a match. (D3§2)
4. If the required minimum experience exceeds three years, the posting should be marked not relevant. (D4§2)
   - The agent should recognize phrases like "3+ years," "minimum 3 years," "at least 5 years," "5 or more years," "five years," "5+ yrs," and ranges like "2–4 years." (D6-A§3)
   - For something like "3+ years," it should treat 3 as the minimum. (D2§3)
   - For a range like "2–4 years," it should use 2 as the minimum because someone with 2 or 3 years could still qualify. (D2§3)
   - It should use the highest stated minimum when multiple requirements exist. (D6-A§3)
   - Preferred or nice-to-have experience should not count as a mandatory minimum. (D6-A§3)
   - If a posting doesn't mention a minimum experience requirement, it should pass the experience check. (D5§5)
   - The agent should report that the requirement was not specified rather than assuming a number. (D5§5)
   - Even if a posting says "new grad" or "entry-level," it should not override the experience requirement. (D4§2)
   - I want the agent to recognize "entry-level," "entry level," "new grad," "new graduate," "early career," "early-career," and "junior" as entry-level indicators. (D3§4)
   - Entry-level and new-graduate phrases should be reported as additional information, but they should not override the experience requirement or change the final verdict. (D5§6)
5. If the posting explicitly requires security clearance, it should be marked not relevant. (D5§4)
   - The agent should recognize all explicit clearance requirements, including "clearance required," "active security clearance required," "must possess a Secret clearance," "Top Secret/SCI required," and "must be able to obtain a security clearance." (D6-A§4)
   - However, clearance mentioned only as preferred should not automatically cause rejection. (D6-A§4)
   - Simply mentioning clearance without making it a requirement should not automatically cause rejection. (D5§4)
6. Since Priya's profile has `needs_sponsorship: true`, any posting explicitly stating "no visa sponsorship," "sponsorship is not available," or "must not require sponsorship now or in the future" should be marked not relevant. (D6-B§6)
   - Any posting that explicitly denies visa sponsorship should be marked not relevant, even if it uses wording beyond the original three phrases. (D7§a)
   - The agent should use exactly three sponsorship values: "offered," "denied," and "unknown." (D6-B§5)
   - Offered means the posting explicitly confirms sponsorship, denied means it explicitly refuses sponsorship, and unknown means the posting doesn't provide enough information. (D6-B§5)
   - I want "offered" to be used only when the posting explicitly says "visa sponsorship available," "visa sponsorship provided," "we offer visa sponsorship," "we provide visa sponsorship," "H-1B sponsorship available," or "will sponsor work visas." (D6-C§5)
   - Matching should be case-insensitive. (D6-C§5)
   - Use only the six explicitly approved phrases to classify sponsorship as "offered." (D7§d)
   - Any other wording should remain "unknown" unless it explicitly denies sponsorship. (D7§d)
   - If sponsorship isn't mentioned, the job can still be relevant, but the agent must clearly report that sponsorship information is unknown. (D1§4)
7. For this first version, I want location to be reported rather than used to reject a job. (D0§4)

## Wrong versions

- The first bug is the agent accepting a senior-level job just because the title contains a matching term like Data Engineer. (D0§7)
- For example, Senior Data Engineer should not pass the early-career filter. (D0§7)
- The second bug is the agent treating missing sponsorship information as a confirmed yes or no. (D0§7)
- A posting titled "Senior Data Engineer" must be marked not relevant even if its skills match. (D5§9)
- A posting without sponsorship information must report sponsorship as "unknown" rather than assuming yes or no. (D5§9)
- Both tests should automatically fail if the agent produces the wrong result. (D5§9)

## What a failure looks like

- October 29, 2026: I would consider the agent a failure if tomorrow's run marks a job with any of my prohibited seniority terms as relevant, rejects a job that I manually labeled relevant, accesses a host outside the allow-list, or reports unknown sponsorship information as a confirmed fact. (D2§6)

## Draft history (verbatim, as written)

# CONTRACT.md: Job-Search Agent 1

## Draft 0 — my answers, Sreevarshan Sathiyamurthy, 2026-10-29, written before any code

1. What two files should the agent use, and why?
I want the agent to use Priya's résumé or profile and a separate file containing job postings. The résumé tells the agent what kind of roles Priya is looking for and what skills she has. The job postings file gives it something to compare against. Keeping them separate makes it easier to check whether each job actually matches her background.

2. Which title words make a posting a role match?
I would look for titles like Data Engineer, Junior Data Engineer, Associate Data Engineer, Entry-Level Data Engineer, ETL Engineer, and Analytics Engineer. I want the matching to ignore capitalization and small wording differences so that relevant jobs don't get missed.

3. Which title words make a job too senior?
I would reject titles containing Senior, Sr., Lead, Staff, Principal, Manager, Director, or Head of Engineering. Since Priya is looking for early-career opportunities, I don't want the agent recommending positions that clearly require a higher level of experience.

4. Does location decide the verdict, or just get reported?
For this first version, I want location to be reported rather than used to reject a job. The agent should show whether a position is remote, hybrid, or onsite and mention the city if available. That way, Priya can decide whether the location works for her without losing potentially good opportunities.

5. Should the agent read job descriptions or just titles?
I want it to check both. The title helps identify the role, but the description gives important information about required skills, experience, sponsorship, and security clearance. I don't want the agent making a decision based only on a job title when the description might contain something that changes the result.

6. What happens when sponsorship isn't mentioned?
If sponsorship isn't mentioned, the agent should mark it as Unknown or Needs Review. It shouldn't assume the company offers sponsorship or that it doesn't. I would rather have the agent clearly say something is missing than make up an answer. If the posting explicitly conflicts with Priya's work authorization requirements, that should affect the verdict.

7. What are two bugs the tests must catch?
The first bug is the agent accepting a senior-level job just because the title contains a matching term like Data Engineer. For example, Senior Data Engineer should not pass the early-career filter.
The second bug is the agent treating missing sponsorship information as a confirmed yes or no. If the posting doesn't mention sponsorship, the result should remain Unknown or Needs Review.

8. What result would mean the agent failed?
I would consider the agent a failure if it recommends jobs that clearly don't match Priya's target roles or experience level, or if it makes assumptions about important missing information. I want the results to be consistent, explainable, and based on what the job posting actually says.

## Draft 1 — my revisions, Sreevarshan Sathiyamurthy, 2026-10-29, still before any code

1. Files
The résumé JSON gives the agent information about Priya's education, experience, projects, and technical skills. The profile JSON tells it what roles she's targeting, her preferences, and work authorization requirements. The agent should use both to evaluate jobs it fetches from the Databricks job board.

2. Roles
I want the agent to prioritize AI Engineer, ML Engineer, Machine Learning Engineer, Junior AI Engineer, and Software Engineer, Machine Learning. Data Engineer, Junior Data Engineer, and Associate Data Engineer should also count. Just having the words "Data Engineer" somewhere in a title shouldn't automatically make it relevant. The title needs to describe an actual engineering position, and senior-level or management positions should be rejected.

3. Description
I want the agent to check for Python, SQL, PyTorch, TensorFlow, scikit-learn, machine learning, deep learning, data pipelines, Spark, and cloud technologies. Ray and Kubeflow should count because they're relevant to ML engineering. I would require at least two matching skills rather than accepting a job based on one common keyword. It should also check years of experience and reject jobs requiring more than three years, unless the posting explicitly identifies the role as entry-level or new graduate. Phrases like "active security clearance required," "must possess a Secret clearance," or "Top Secret/SCI required" should be treated as clearance requirements.

4. Verdict
I want only two final verdicts: relevant or not relevant. If sponsorship isn't mentioned, the job can still be relevant, but the agent must clearly report that sponsorship information is unknown. If a posting explicitly says "no visa sponsorship," "sponsorship is not available," or "must not require sponsorship now or in the future," it should be marked not relevant when that conflicts with Priya's profile. The agent should never assume missing information means yes or no.

5. Output and Refuses
Each result should show the job title, company, location, job URL, relevant skills, sponsorship information, and the final verdict with a short explanation.
The agent should access only the approved Databricks careers board and its verified job-data endpoint, with their exact hostnames recorded in an allow-list before running. It should never access unrelated websites, upload real personal résumés, publish sensitive information to GitHub, automatically apply to jobs, or present an AI-generated assumption as a verified fact.

6. Failure Sentence
October 29, 2026: I would consider the agent unsuccessful if tomorrow's run accepts a clearly senior-level or unrelated position, rejects a valid entry-level AI/ML opportunity, accesses an unauthorized website, or presents missing sponsorship information as confirmed.

## Draft 2 — my revisions, Sreevarshan Sathiyamurthy, 2026-10-29, still before any code

1. Skills
I want the agent to count only skills that are actually listed in Priya's résumé JSON. Python and SQL should count as two separate skills if both appear in her résumé. Other skills should count only if they're explicitly mentioned in her résumé. I don't want the agent assuming she knows something just because it's related to AI or data engineering. A job should have at least two matching résumé skills.

2. Title Matching
The title doesn't need to match my list exactly. It can contain one of the approved role phrases, even with additional words before or after it. For example, Junior Machine Learning Engineer and Software Engineer, Machine Learning should count. However, the agent should check the complete title for seniority restrictions before accepting it. Matching should be case-insensitive and based on complete words or phrases, not accidental partial matches.

3. Years of Experience
I want the agent to identify experience requirements such as "3+ years," "minimum 3 years," and "2–4 years." For something like "3+ years," it should treat 3 as the minimum. For a range like "2–4 years," it should use 2 as the minimum because someone with 2 or 3 years could still qualify. If the minimum requirement is more than 3 years, the agent should reject it, unless it's explicitly a new-graduate or entry-level opportunity.

4. Output
I agree. Every result should include the posting ID, job title, company, location, URL, sponsorship status, and final verdict. The explanation should mention the actual résumé or profile JSON field names used to justify the decision. I also want the rule-based output labeled "record" and Claude's separate assessment labeled "judgment," so we can compare them without confusing an AI opinion with a verified result.

5. Hosts
I agree. For this assignment, the only allowed external host should be `boards-api.greenhouse.io`. The agent should never visit unauthorized websites, email anyone, log in to accounts, submit applications, or expose personal information. It should only retrieve public job postings and analyze them using the provided sample persona files.

6. Failure Sentence
October 29, 2026: I would consider the agent a failure if tomorrow's run marks a job with any of my prohibited seniority terms as relevant, rejects a job that I manually labeled relevant, accesses a host outside the allow-list, or reports unknown sponsorship information as a confirmed fact.

## Draft 3 — my answers, Sreevarshan Sathiyamurthy, 2026-10-29, still before any code

1. Draft 2 Skills
I agree. Draft 2 should replace Draft 1's skill list. PyTorch, TensorFlow, scikit-learn, and Spark should not count unless they're explicitly present in Priya's résumé JSON.

2. Ray and Kubeflow
No. Skills under `familiar_with_not_shipped` should not count toward the two required skills because Priya hasn't demonstrated practical experience with them. They can be reported as additional familiarity, but not used to justify a match.

3. Claude Judge Call
The Claude judge should receive the public job posting details, posting ID, relevant résumé skills, profile requirements, and the rule-based verdict with its explanation. It should never receive personal contact information, private files, or unnecessary sensitive data. This is the only permitted exception to the external host allow-list.

4. Entry-Level and Years
I want the agent to recognize "entry-level," "entry level," "new grad," "new graduate," "early career," "early-career," and "junior" as entry-level indicators. If a posting contains multiple minimum experience requirements, the agent should use the highest stated minimum. Every eligibility check should be a hard filter, meaning one failed requirement makes the job not relevant, even if the posting calls itself entry-level or new graduate.

## Draft 4 — my answers, Sreevarshan Sathiyamurthy, 2026-10-29, still before any code

1. Claude's Verdict
No. I want Claude to make its judgment independently without seeing the rule-based verdict. Both results should be compared afterward to identify disagreements and understand where either approach might be wrong.

2. Entry-Level Exception
No. Even if a posting says "new grad" or "entry-level," it should not override the experience requirement. These phrases should only help identify early-career opportunities. If the required minimum experience exceeds three years, the posting should be marked not relevant.

3. Claude's Host
Yes, that's how I want it stated. The agent's own code should connect only to `boards-api.greenhouse.io`, while the Claude judge runs separately through the `claude` CLI. The agent should never access other job boards, log in, email anyone, or submit applications.

## Draft 5 — Final Contract Decisions, Sreevarshan Sathiyamurthy, 2026-10-29, still before any code

1. The Watch
Yes. The agent should save the raw job-board response, maintain a file of previously seen posting IDs, and report only new postings. The first run should establish the baseline, save all existing IDs, and report zero new postings.

2. Claude's Output
Claude must return valid JSON containing the posting ID, verdict (relevant or not relevant), skills cited with their résumé field names, and a short explanation referencing the posting fields. Any missing fields, extra fields, invalid verdicts, or incorrectly formatted responses should be rejected by the validator.

3. What Claude Receives
Claude should receive only the public job posting and the relevant parts of Priya's profile, including her verified skills, target roles, experience requirements, and exclusions. It should not receive contact information, private details, or the rule-based verdict.

4. Clearance
Yes. If the posting explicitly requires security clearance, it should be marked not relevant. Simply mentioning clearance without making it a requirement should not automatically cause rejection.

5. No Years Stated
If a posting doesn't mention a minimum experience requirement, it should pass the experience check. The agent should report that the requirement was not specified rather than assuming a number.

6. Entry-Level Phrases
Yes. Entry-level and new-graduate phrases should be reported as additional information, but they should not override the experience requirement or change the final verdict.

7. Skill Matching
Skill matching should be case-insensitive and use complete words or phrases across the title and description. SQL should not match PostgreSQL automatically. AWS should match Amazon Web Services only through an explicitly defined alias, and only if AWS is actually listed in Priya's résumé.

8. Inputs and Output
Yes. The agent should accept `databricks` as the board token, use Priya's fictional résumé JSON and a JSON copy of `profile.yml`, and save the results to a file with the posting IDs, verdicts, evidence, and explanations.

9. Wrong-Version Tests
Yes. A posting titled "Senior Data Engineer" must be marked not relevant even if its skills match. A posting without sponsorship information must report sponsorship as "unknown" rather than assuming yes or no. Both tests should automatically fail if the agent produces the wrong result.

10. Title Conflict
Yes. "Data Engineer, Analytics Platform" should count as a role match because it contains the complete approved phrase "Data Engineer." However, it should only receive a relevant verdict if all other eligibility checks pass.

## Draft 6 — my answers, Sreevarshan Sathiyamurthy, 2026-10-29, still before the rule judge was written

### Batch A

1. Résumé Skills
I want the agent to count skills explicitly listed in Priya's skills section, as well as tools mentioned in her actual work experience or projects, like Databricks Genie API. However, skills under `familiar_with_not_shipped` should not count. Every matched skill must reference the exact résumé field where it appears.

2. Aliases
For now, AWS = Amazon Web Services should be the only approved alias. I don't want the agent assuming other technologies are equivalent unless we explicitly add them later.

3. Years of Experience
The agent should recognize phrases like "3+ years," "minimum 3 years," "at least 5 years," "5 or more years," "five years," "5+ yrs," and ranges like "2–4 years." It should use the highest stated minimum when multiple requirements exist. Preferred or nice-to-have experience should not count as a mandatory minimum.

4. Security Clearance
The agent should recognize all explicit clearance requirements, including "clearance required," "active security clearance required," "must possess a Secret clearance," "Top Secret/SCI required," and "must be able to obtain a security clearance." These should make the posting not relevant. However, clearance mentioned only as preferred should not automatically cause rejection.

### Batch B

1. Experience and Project Tools
I want only "Databricks Genie API" and "MLflow" to count as additional tools from Priya's experience or projects, and only if those exact names appear in her résumé. Terms like "A/B framework" and "drift monitoring" should not count as tools. Skills explicitly listed in her skills section still count separately.

2. Preferred Requirements
If the same sentence contains "preferred," "nice to have," "nice-to-have," "bonus," or "plus" as a separate word, the experience or clearance requirement in that sentence should be treated as optional and ignored as a hard filter. However, if the sentence explicitly says "required" or "must have," the mandatory requirement takes priority.

5. Sponsorship Values
Yes. The agent should use exactly three sponsorship values: "offered," "denied," and "unknown." Offered means the posting explicitly confirms sponsorship, denied means it explicitly refuses sponsorship, and unknown means the posting doesn't provide enough information.

6. Sponsorship Conflict
Yes. Since Priya's profile has `needs_sponsorship: true`, any posting explicitly stating "no visa sponsorship," "sponsorship is not available," or "must not require sponsorship now or in the future" should be marked not relevant.

7. Title Test
Yes. A title passes if it contains an approved role phrase and does not contain any prohibited seniority term. Matching should be case-insensitive and use complete words. I want to remove the vague "actual engineering position" condition because it cannot be evaluated consistently.

8. Punctuation
Yes. "Software Engineer - Machine Learning" and "Software Engineer (Machine Learning)" should match "Software Engineer, Machine Learning." The agent should normalize commas, hyphens, and parentheses as separators. "ML/AI Engineer" should also match because the slash combines two approved titles, "ML Engineer" and "AI Engineer." Seniority restrictions must still apply after normalization.

### Batch C

5. Sponsorship — Offered Phrases
I want "offered" to be used only when the posting explicitly says "visa sponsorship available," "visa sponsorship provided," "we offer visa sponsorship," "we provide visa sponsorship," "H-1B sponsorship available," or "will sponsor work visas." Matching should be case-insensitive. General statements like "we sponsor" should not count unless they specifically refer to employment visa sponsorship.

9. Seniority Words
Yes. Any title containing "Head of" should be rejected, regardless of the department. Both "Sr" and "Sr." should count as seniority indicators. Words like "Senior," "Lead," "Staff," "Principal," "Manager," and "Director" should match only as complete words, so "Leading" should not be confused with "Lead."

10. Remote, Hybrid, or Onsite
I want the agent to check both the Greenhouse location field and the job description. It should report whether the position is remote, hybrid, or onsite, along with the location when available. If neither field specifies the work arrangement, the output should say "not specified." If the fields contradict each other, the agent should report the conflict instead of guessing.

11. Failed Checks
The agent should run every eligibility check instead of stopping at the first failure. I want all failed checks listed with their explanations so I can understand every reason a job was rejected. Even one failed mandatory check should make the final verdict "not relevant."

12. Seeded Runs
Yes. Any seeded run should use a separate state file and clearly label its output "SEEDED." It should never overwrite or modify the real watch history, posting IDs, or saved evidence from live runs.

13. Output Fields
Since we're monitoring only the Databricks job board, the company should be recorded as "Databricks." Evidence should contain the exact matched phrases and the posting field they came from, along with the relevant résumé or profile field names. This should make every verdict easy to verify manually.

14. Claude's Inputs
Yes. Claude should receive the public posting, Priya's relevant résumé skill fields, target roles, experience requirements, and exclusions. This allows it to cite actual résumé fields in its explanation. It should never receive contact information, unnecessary personal details, or the rule-based verdict, because I want its judgment to remain independent.

15. Validator Failure
If Claude returns an invalid response, the agent should retry exactly once using the same input and output requirements. If the second response also fails validation, it should record the judgment status as "invalid," save the validation error, and continue processing other postings. It should never invent a verdict or silently treat an invalid response as relevant.

## Draft 7 — my answers, Sreevarshan Sathiyamurthy, 2026-10-29, before the rule judge was written

a) Sponsorship: Yes. Any posting that explicitly denies visa sponsorship should be marked not relevant, even if it uses wording beyond the original three phrases.

b) Skill Counting: Yes, each skill should count only once, even if it appears in multiple résumé fields. Yes, "Databricks Genie API" should count separately from "Databricks" because they are distinct skills.

c) Preferred Words: Yes. Remove "plus" from the preferred words because it can mean "and" rather than an optional requirement.

d) Sponsorship Offered: Yes. Use only the six explicitly approved phrases to classify sponsorship as "offered." Any other wording should remain "unknown" unless it explicitly denies sponsorship.

## Draft 8 — my decision, Sreevarshan Sathiyamurthy, 2026-10-29, after the rule judge tests

I chose option B, as worded by the chat assistant: "Databricks" counts as a matched skill only when the posting asks for it as a skill (for example "experience with Databricks" or "Databricks platform"), not when it appears only as the company name.
