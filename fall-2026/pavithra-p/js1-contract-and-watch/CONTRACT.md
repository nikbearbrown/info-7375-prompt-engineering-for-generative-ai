# CONTRACT — Job-Search Agent 1

Pavithra Prasad · INFO 7375 · JS1 · 2026-10-29

## In

The agent takes a Greenhouse job board name (`pinterest`, at `boards-api.greenhouse.io`) and a fictional résumé in JSON format (Rohan Mehta, adapted from an example persona in the Reallocation Engine, with only the name and contact details changed). It uses the résumé's skills and experience to check job openings.

It needs network access to `boards-api.greenhouse.io` only, a folder to save each raw response, and a file of the job IDs it has already seen.

## Out

For every new job, the agent shows:

* Job ID, title, company, and location.
* Whether the job is Relevant or Not Relevant, by the rule below.
* A short reason that names the posting fields (title, location, description) and the résumé fields (skills, experience) behind the verdict, including the matched skills.
* Claude's separate opinion, clearly marked as an AI judgment. Claude must reply in a fixed format (verdict, the posting fields and résumé fields it used, a one-line reason). A validator rejects any other reply; a rejected reply is saved and shown as invalid, never fixed.

The first run saves existing jobs and shows zero new jobs. Later runs show only newly found jobs, meaning job IDs not seen in an earlier run. Every run saves the board's raw response first; if the fetch fails, nothing else changes. A run against a saved earlier response is labelled SEEDED.

## Refuses

The agent will not:

1. Visit websites outside the approved Greenhouse host.
2. Show or upload anyone's real résumé.
3. Apply for jobs, send messages, or log in.
4. Treat Claude's opinion as a confirmed fact.
5. Make up jobs or missing details.
6. Run on a résumé that is not clearly fictional (email not at `example.com`, or phone not a 555 number).

## The rule

A job is Relevant if all four are true:

1. **Role:** the title contains the word "Engineer" and one of: Software, Backend, Back-end, Full-stack, Full Stack, Fullstack, Cloud, AI.
2. **Skills:** at least two of the résumé's skills appear in the job description (the skills listed under languages, backend_automation, database_cloud and devops_cicd).
3. **Experience:** the title does not contain Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished or Intern, and the description does not ask for 3 or more years (as in "3+ years" or "5 years").
4. **Location:** the location field contains "United States", "USA" or "US". State codes don't count, because Pinterest writes "CA" for both California and Canada.

Words are matched as whole words, ignoring case, so "Java" does not match "JavaScript".

If any condition is not met, the job is Not Relevant. I use this same rule to hand-label the 20 postings for the prompt experiment.

## Wrong versions

The tests should catch:

1. **Wrong job:** a result is matched with the wrong job ID. A test shuffles the results and checks that each verdict still matches the rule applied to its own job.
2. **Missing reason:** the agent gives a verdict without mentioning which job requirements and résumé details support it. A test rejects any reason that does not name at least one posting field, one résumé field and the matched skills.

## What a failure looks like

2026-10-29: The agent fails if it shows old jobs as new, gives wrong results based on my rule, or gives reasons without evidence from the job posting and résumé.

## Note added 2026-10-31, after the experiment

My 20 hand labels in experiment 1 did not follow this rule: they agree with it on 7 of 20 (`experiment/label-audit.md`). In experiment 2 my labels agree with it on 16 of 20 (`PROMPT-EXPERIMENT.md`). The rule above is unchanged, and the agent's rule judge still applies it as written.
