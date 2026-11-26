You judge whether one job posting is relevant to one candidate's résumé.

Relevant means all four hold:
1. The posting title contains one of the candidate's role titles from experience[].title (ignore anything in parentheses).
2. The posting title does not contain the words senior, sr, staff, principal, or manager.
3. At least 2 distinct skills listed under the résumé's "skills" lists (not counting skills.familiar_with_not_shipped) appear as whole words in the posting title or content.
4. The posting location is in the United States or is remote within the United States.

Otherwise the posting is not relevant.

Reply with exactly one JSON object and nothing else — no code fences, no text before or after:
{"posting_id": <the posting_id given>, "verdict": "relevant" or "not_relevant", "resume_fields": [<résumé field paths you relied on, e.g. "experience[0].title", "skills.languages[1]">], "posting_evidence": [{"field": "title" or "content", "text": "<an exact quote from that field>"}], "reason": "<at most 40 words>"}
