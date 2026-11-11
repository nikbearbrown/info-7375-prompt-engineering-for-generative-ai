You are screening one job posting for one candidate. Decide whether the posting is worth this
candidate's time to apply to.

Candidate résumé (JSON):
{{RESUME_JSON}}

Job posting (JSON):
{{POSTING_JSON}}

The ONE change from v1: treat a stated years-of-experience number as a soft preference, not a
cutoff. Do not mark a non-senior role not_relevant only because it asks for more years than the
candidate has; a recent MS graduate with a co-op may still be worth applying for roles asking up to
about 5 years. Seniority in the title still counts.

Answer with exactly one JSON object and nothing else: no code fences, no prose before or after.
It must have exactly these four keys:

- "verdict": "relevant" or "not_relevant"
- "resume_fields": a non-empty list of the résumé fields your verdict relies on, written as paths
  into the résumé JSON above, for example "skills.languages" or "experience[0].title"
- "posting_fields": a non-empty list drawn only from "title", "location.name", "content", "departments"
- "reason": one sentence linking those fields to your verdict
