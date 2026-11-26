# FRICTIONAL — Job-Search Agent 3 (honest log, my own words)

Written on 2026-11-25, the day of the work, and typed by me in chat. Claude Code only pasted it into this file,
without editing. The facts and numbers I mention come from the files each pointer names.

## Entry 1 — writing the filter (commit `a725b4a4`)

I started by deciding which job titles and technical skills were relevant to the roles I wanted. I chose titles like Backend Engineer, Java Developer, Software Engineer, Full Stack Engineer, Software Developer, and Platform Engineer. For the technical topics, I chose Java, Spring Boot, REST APIs, microservices, SQL, AWS, PostgreSQL, and distributed systems.

One thing I found difficult was deciding how strict the filter should be. Claude suggested using at least two topic words, treating "Sr." as Senior, and rejecting jobs that explicitly require 3+ years of experience. I accepted those suggestions, with some clarification. For example, I wanted the two topic words to appear in relevant job-description context, not just anywhere in the posting. I also decided that 3+ years being preferred should not automatically reject a job; it has to be explicitly required.

I also included "training" as a false friend because it could refer to machine-learning training rather than employee training. It never actually caused a problem in the results. That made me realize that I cannot predict every misleading keyword in advance. I need to look at what the filter gets wrong and improve it based on real examples.

**Pointer:** `FILTER.md`, commit `a725b4a4`.

## Entry 2 — judging the 54 postings (commit `9ee00800`)

I reviewed 54 postings without seeing the filter's decisions. They were mixed together from 32 random rejects, 12 close calls, and 10 postings the filter had kept. Each entry showed the title, location, link, and up to four requirement lines. I gave my own Y or N verdict with a short reason. I agreed with all 32 random rejects, but only 2 of the 10 postings the filter kept were jobs I would consider.

When I looked at the 8 kept postings I had marked N, I noticed that I was applying requirements I had not clearly written into FILTER.md. I rejected jobs because the location was Bengaluru or unclear, because they required more experience than I wanted, or because the stack was Ruby-focused. US location was only a preference in my written filter, but in my own judgment I was treating it more like a requirement. I also realized that topic words could appear in a team's description without actually being required for the job. "Distributed systems" appeared in 12 of the 13 kept postings, which showed how easily a keyword match could make an irrelevant job look relevant.

The audit made me see that matching keywords is not the same as checking whether a job fits what I am looking for. The filter agreed with me on the obvious rejects, but its keep list had too many jobs I would skip. Also, 32 correct random rejects do not prove that all the rejects are correct; with this sample size, some mistakes could still exist in the remaining postings.

**Pointer:** `audit/my-verdicts-2026-11-25.txt`, commit `9ee00800`.

## Entry 3 — deciding which rule changes to accept (commit `8a6b77e4`)

After reviewing the audit, I considered four changes suggested or discussed with Claude. I rejected making US location a hard requirement because I still wanted it to be a preference, not an automatic rejection. I also rejected lowering the topic-word threshold from two words to one because I felt that would let too many loosely related jobs through.

I accepted the experience rule: if a job explicitly requires 3+ years, it should be rejected, but preferred experience should not automatically disqualify it. I also accepted counting topic words only in actual requirements sections instead of anywhere in the posting. This was important because I noticed that some matches came from team descriptions rather than job requirements.

I changed posting #26 from Y to N after reviewing its 5+ years requirement. I understand that this decision was made after seeing the audit results, so the audit was being used to refine the filter rather than as a final independent measurement. I kept the held-out set separate for the final comparison. The changes I accepted became rules B and D in the updated filter.

**Pointer:** `SCORE-CHANGES.md` and the rule-change work, commit `8a6b77e4`.

## Entry 4 — held-out results: my labels vs my rules (commit `81e4bcf1`)

I expected v1.1 to improve the results after the changes I made using the 54-posting audit. But on the held-out set, v1.1 agreed with 18 out of 20 labels and found none of my two Y postings. It kept only 4 out of 1,088 jobs. It also tied with the simple approach of rejecting everything, which made me question whether the improvements I saw on the audit actually carried over.

After looking at the results, I realized that both my Y labels conflicted with my own rules. For #14, the posting explicitly requires 4+ years of experience, so rule B should reject it. For #4, AWS and PostgreSQL appear under NICE TO HAVES, so rule D should not count them as required skills.

I had judged these jobs based on their general engineering relevance instead of checking whether they actually met my written requirements. I decided not to change my held-out labels after seeing the results because that would make the set no longer held out.

I also noticed that the prompt changes and context changes made no difference to the final verdicts. All three Claude runs gave the same answers, but their explanations were different. This showed me that getting the same answer does not necessarily mean the reasoning behind it is consistent.

One result I still need to think about is rule D. It removed my only true positive, #4, because its matching skills were preferred rather than required. However, I accepted that this was consistent with the rule I had written. I do not want to weaken the rule just to improve the score without understanding the trade-off.

Another issue was #18, a mobile internship. Claude marked it as a match because it passed my written rules, but I marked it N because I was looking for backend-focused roles. I realized that I had not actually written backend focus as a filter rule.

My conclusion was that my labels were wrong, not the rules. I still need to decide whether backend focus should become an explicit rule and whether the current requirements-only approach is too restrictive. I also understand that 20 postings, with only two positive labels, are too few to make strong conclusions from a one-posting difference.

**Pointer:** `SCORE-CHANGES.md`, commit `81e4bcf1`.

## Entry 5 — the tool servers and my trust decisions (TOOL-EVALUATIONS.md, commit `ab371658`)

[ ]
