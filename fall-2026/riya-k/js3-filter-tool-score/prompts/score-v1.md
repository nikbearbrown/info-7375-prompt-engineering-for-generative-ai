You are screening one job posting for a job seeker. Decide whether she should see it.

The job seeker (fictional): {{PERSONA}}

She wants: a US-based (or US-remote), full-time, non-senior role in AI, machine learning or data.

The posting:
- Board: {{BOARD}}
- Title: {{TITLE}}
- Location: {{LOCATION}}
- Employment type field: {{EMPLOYMENT}}
- Text:
{{TEXT}}

Answer with ONLY a JSON object, no other text:
{"verdict": "show" | "not" | "cannot_tell", "score": <integer 0-10>, "reasons": ["<short reason quoting the posting>", ...]}
Use "cannot_tell" when the posting does not give enough to decide.
