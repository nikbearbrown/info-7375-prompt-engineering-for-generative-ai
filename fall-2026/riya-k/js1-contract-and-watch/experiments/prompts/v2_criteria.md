You are screening one job posting for one candidate. Decide whether the posting is relevant for the candidate.

Candidate résumé (JSON):
{{RESUME_JSON}}

Job posting (JSON):
{{POSTING_JSON}}

Decision rule (use this, not your own taste): the posting is relevant only if the candidate could apply honestly today: the role matches her AI/ML/data target, it is not senior, she has at least 2 of the core skills the posting asks for, and the job is located in the US.

Reply with exactly one JSON object and nothing else (no prose, no code fences), with exactly these keys:
{"id": {{POSTING_ID}}, "verdict": "relevant" or "not_relevant", "resume_fields": [...], "posting_fields": [...], "justification": "..."}

- "id": the posting id, as an integer.
- "resume_fields": the résumé fields your verdict rests on, from: "skills.languages", "skills.data_bi", "skills.backend_automation", "skills.database_cloud", "experience", "projects", "education".
- "posting_fields": the posting fields your verdict rests on, from: "title", "content", "location.name".
- "justification": at most 2 sentences that name those résumé fields and posting fields.
