---
version: judge_v1
---
You are screening one job posting for one job seeker. Decide whether this posting is worth the candidate's time to apply to.

Candidate (a fictional persona; these fields are everything you know about the candidate):
- target_title_keywords: {{target_title_keywords}}
- skills: {{skills}}
- years_experience: {{years_experience}}
- highest_degree: {{highest_degree}}
- preferred_cities: {{preferred_cities}}
- remote_ok: {{remote_ok}}

Posting:
- title: {{title}}
- location: {{location}}
- content (the posting's requirements text: lowercased, company boilerplate removed, possibly truncated):
<<<
{{content}}
>>>

Reply with exactly one JSON object and nothing else: no code fences, and no text before or after it. The object has exactly these four keys:

{"verdict": "relevant", "justification": "...", "cited_resume_fields": ["..."], "cited_posting_fields": ["..."]}

- verdict: "relevant" if the posting is worth this candidate's time, otherwise "not_relevant". Use one of those two lowercase strings exactly.
- justification: 1 to 400 characters. Say which candidate fields and which posting fields your verdict rests on.
- cited_resume_fields: the candidate fields you relied on, at least one, chosen only from: target_title_keywords, skills, years_experience, highest_degree, preferred_cities, remote_ok.
- cited_posting_fields: the posting fields you relied on, at least one, chosen only from: title, location, content.
