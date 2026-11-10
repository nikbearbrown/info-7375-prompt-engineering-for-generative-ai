You are judging whether one job posting is relevant for a job seeker. Your answer is a judgment, not a fact. Answer only from the résumé and posting below.

## Job seeker's résumé (JSON; contact details removed)

{resume_json}

## Relevance rule

A posting is "relevant" only if ALL of these hold; otherwise it is "not_relevant":

1. The title contains at least one of: AI, Machine Learning, ML, Software Engineer, Intern, New Grad, Early Career.
2. The title contains none of: Senior, Sr, Staff, Principal, Distinguished, Manager, Director, Lead, Sales, PhD, Research Scientist.
3. The location is in the United States.
4. The description mentions at least 2 different skills from the résumé fields skills.languages, skills.data_bi, skills.backend_automation, skills.database_cloud.
5. The job seeker needs visa sponsorship, so the description must not say the employer cannot sponsor visas.

## Posting

posting_id: {posting_id}
title: {title}
location.name: {location}
content:
{description}

## Output format

Reply with ONE JSON object and nothing else: no code fence, no text before or after.

{{"posting_id": {posting_id}, "verdict": "relevant" or "not_relevant", "resume_fields": [...], "posting_fields": [...], "reason": "..."}}

- resume_fields: the résumé fields your verdict rests on, as dotted paths that exist in the résumé JSON above (e.g. "skills.languages").
- posting_fields: the posting fields your verdict rests on, from: "title", "location.name", "content".
- reason: one or two sentences.
