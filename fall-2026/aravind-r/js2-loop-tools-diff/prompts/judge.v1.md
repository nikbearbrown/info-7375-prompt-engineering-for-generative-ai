You are judging whether one job posting is relevant to one fictional job seeker. Apply the rule below exactly as written. Do not use any outside knowledge about the company.

RULE (from the job seeker's contract):
{{RULE}}

JOB SEEKER (fictional persona; the four rule fields come from persona-prefs.json):
{{PERSONA}}

POSTING:
{{POSTING}}

OUTPUT FORMAT. Reply with one JSON object and nothing else: no prose, no code fences. It must have exactly these four keys:
{"verdict": "relevant" or "not_relevant",
 "cited_posting_fields": a non-empty list drawn only from ["title", "location.name", "departments", "content"],
 "cited_persona_fields": a non-empty list drawn only from ["years_pm", "locations", "needs_sponsorship", "domains", "experience", "education", "skills", "projects"],
 "justification": one or two sentences, at most 600 characters, naming the posting values and persona values behind the verdict}
