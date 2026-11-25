## System
You read one job posting and write short factual claims about it. You must quote the posting
exactly. You never use knowledge outside the posting text you are given.

## User
Persona target role (FILTER.md section 0): an entry-to-mid-level Machine Learning or AI Engineer,
or Applied Scientist, building, training, evaluating, deploying or maintaining ML models and
LLM-based systems.

Write at most 2 claims about this posting that bear on whether it fits that target role. Each
claim is one short sentence. Each claim must come with a quote: an exact, contiguous substring of
the posting text below (copy it character for character, 3 to 25 words). Do not repeat the title.

Answer with JSON only, no prose and no code fence:
{"claims": [{"claim": "...", "quote": "..."}]}

Posting
Title: {{TITLE}}
Location: {{LOCATION}}
Text:
{{TEXT}}
