Decide whether this job posting is worth the candidate's time to apply to.

Use only the two JSON objects below. The candidate object holds the candidate's experience titles and skills. The posting object holds the posting's title, location and description.

Apply this rule. The posting is "relevant" if and only if all three hold:
1. The posting title contains, as a whole word ignoring case, a word from the candidate's experience titles other than "Co-op"; "Engineering" also counts when "Engineer" is one of those words.
2. The posting description names at least one of the candidate's skills, as a whole word ignoring case.
3. The posting title does not contain "Manager", "Director" or "Head".
Otherwise it is "not relevant". If the title or the description is empty, the verdict is "cannot judge". Location never decides.

CANDIDATE:
{{RESUME_JSON}}

POSTING:
{{POSTING_JSON}}

Output contract. Reply with exactly one JSON object and nothing else: no prose, no code fences. It must have exactly these keys:

- "verdict": one of "relevant", "not relevant", "cannot judge"
- "confidence": one of "low", "medium", "high"
- "resume_fields": a non-empty list drawn from "experience[].title", "skills" (the candidate fields your verdict rests on)
- "posting_fields": a non-empty list drawn from "title", "location.name", "content" (the posting fields your verdict rests on)
- "justification": at most 800 characters, naming those fields; put any words you quote from the posting or the candidate in double quotes, copied exactly
