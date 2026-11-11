You are judging one job posting for one job seeker. Your answer is a judgment, not a fact.

The job seeker is a fictional persona. You only see these résumé fields (path: value):
{{RESUME_FIELDS}}

You only see these posting fields:
{{POSTING_FIELDS}}

Question: is this posting worth this person's time to apply to? Weigh the kind of role, its seniority, and its location against the résumé fields.

Reply with exactly one JSON object and nothing else: no code fences, no text before or after it. Use exactly these keys:
{"posting_id": <the posting's id, as a number>, "verdict": "relevant" or "not_relevant", "resume_fields": [the résumé field paths you relied on, chosen from the paths above], "posting_fields": [the posting fields you relied on: "title" and/or "location.name"], "justification": "<one or two sentences that name every field you cite by its path, with its value>"}
