You are screening one job posting for a job seeker. Decide whether she should see it.

The job seeker (fictional): {{PERSONA}}

She wants: a US-based (or US-remote), full-time, non-senior role in AI, machine learning or data.

Rules (apply in order; quote the posting for each one you use):
1. If the location is only outside the US, the answer is "not".
2. If the smallest number of years of experience the posting asks for is more than 3, the answer is "not". "Preferred" years count the same as required years.
3. If the role is mainly selling, account management, recruiting, finance, legal or operations, the answer is "not", even if the title says AI.
4. If the posting does not say enough to apply rules 1-3, the answer is "cannot_tell".

The posting:
- Board: {{BOARD}}
- Title: {{TITLE}}
- Location: {{LOCATION}}
- Employment type field: {{EMPLOYMENT}}
- Text:
{{TEXT}}

Answer with ONLY a JSON object, no other text:
{"verdict": "show" | "not" | "cannot_tell", "score": <integer 0-10>, "reasons": ["<short reason quoting the posting>", ...]}
