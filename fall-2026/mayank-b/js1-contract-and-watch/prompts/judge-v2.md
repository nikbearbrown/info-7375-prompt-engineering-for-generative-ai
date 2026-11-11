You are judging one job posting for one job seeker. Your answer is a judgment, not a fact.

The job seeker is a fictional persona. You only see these résumé fields (path: value):
{{RESUME_FIELDS}}

You only see these posting fields:
{{POSTING_FIELDS}}

Question: is this posting worth this person's time to apply to? Judge the role itself: what work the title implies, whether this person's skills and level fit that work, and whether its location works for them. Do not decide by checking whether the title contains a search.target_titles term; a keyword match alone is not enough.

Reply with exactly one JSON object and nothing else: no code fences, no text before or after it. Use exactly these keys:
{"posting_id": <the posting's id, as a number>, "verdict": "relevant" or "not_relevant", "resume_fields": [the résumé field paths you relied on, chosen from the paths above], "posting_fields": [the posting fields you relied on: "title" and/or "location.name"], "justification": "<one or two sentences that name every field you cite by its path, with its value>"}
