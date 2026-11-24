Decide whether this job posting is worth the candidate's time to apply to.

Use only the two JSON objects below. The candidate object holds the candidate's experience titles and skills. The posting object holds the posting's title, location and description.

Answer one question: is this posting worth the candidate's time to read in full? Call it "relevant" if it is, and "not relevant" if it is not. If the title or the description is empty, the verdict is "cannot judge".

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
