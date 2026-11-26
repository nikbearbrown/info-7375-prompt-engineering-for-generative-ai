---
version: justify_v1
---
A keyword filter put this job posting on a shortlist for one job seeker. Write the justification for that shortlist entry as a list of short, checkable claims about the posting.

Job seeker (a fictional persona; this is everything you know about them): {{persona}}
They want: data engineering, machine learning or AI roles; anywhere in the United States; at most 4 years of required experience; master's roles and internships count.

Posting:
- company: {{company}}
- title: {{title}}
- location: {{location}}
- text:
<<<
{{text}}
>>>

Write 4 to 7 claims. Include exactly one claim of type "role" (what kind of work this job is), exactly one of type "location" (where the job is), and exactly one of type "years" (how much experience it requires). The others may be "skill", "degree" or "other". Each claim is one sentence about the posting. Each claim carries a quote copied character for character from the posting's title, location or text that you think supports it. If the posting does not state something (for example, no years are mentioned), say so in the claim and give an empty quote.

Reply with exactly one JSON object and nothing else: no code fences, and no text before or after it:

{"claims": [{"type": "role", "claim": "...", "quote": "..."}, ...]}
