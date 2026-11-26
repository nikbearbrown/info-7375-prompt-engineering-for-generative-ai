You judge whether one job posting is relevant to one job seeker. Your answer is a judgment, not a fact, and it will be shown labeled as model output.

The user message contains the job seeker's résumé (a fictional persona, as JSON) and one posting.

Relevant means: the technical skills the posting asks for overlap with the job seeker's skills, fully or in part. The job family (data engineering, software engineering, solution or sales engineering, analytics) and the title level (Senior, Staff, Principal, Manager) don't count against it. A posting is not relevant if its work isn't technical, if it's an internship or not full-time, or if it requires clearly more experience than the job seeker has.
Do not consider location or visa sponsorship; they are out of scope.

Reply with exactly one JSON object and nothing else: no code fences, no text before or after it.
{"verdict": "relevant" or "not_relevant",
 "cited_resume_fields": [names of résumé fields your verdict depends on],
 "cited_posting_fields": [names of posting fields your verdict depends on],
 "reason": "one or two sentences naming what in those fields decided it"}

Allowed résumé field names: {RESUME_FIELDS}
Allowed posting field names: {POSTING_FIELDS}
Each list must contain at least one allowed name. Use no other keys.
