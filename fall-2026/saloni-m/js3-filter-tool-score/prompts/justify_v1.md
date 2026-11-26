You are writing the justification for one job posting on a shortlist for a job seeker. The
posting passed a keyword filter. Your job is to say why it might be worth her time, as claims
that can be checked against the posting text.

The job seeker (fictional persona, no contact details):

{{PERSONA_JSON}}

The posting:

{{POSTING_JSON}}

Write 3 to 6 claims. Each claim is one short sentence about the posting and how it fits her. For
each claim give:

- "kind": one of "role", "skill", "experience", "seniority", "degree", "other"
- "claim": the sentence
- "term": the one word or short phrase the claim depends on (a skill name, a role word, or a
  number of years such as "3 years")
- "quote": the exact words from the posting that support the claim, copied character for
  character. If the posting does not say it, use "" and still write the claim.

Reply with only this JSON object and nothing else:

{"claims": [{"kind": "...", "claim": "...", "term": "...", "quote": "..."}]}
