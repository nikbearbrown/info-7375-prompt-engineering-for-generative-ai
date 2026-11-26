You are checking whether one job posting fits a candidate. You write
claims. Each claim must be tied to the posting's own words.

Candidate: Priya Nair (fictional persona), an ML/AI engineer.
Target title keywords (from data/target.example.json): {{target_title_keywords}}
Excluded terms (from data/target.example.json): {{excluded_terms}}

Posting
- board: {{board}}
- id: {{id}}
- title: {{title}}
- location: {{location}}
- body:
<<<POSTING
{{body}}
POSTING>>>

Task
Write 3 to 5 claims that justify why this posting fits Priya as an ML/AI
engineer. For each claim give one quote:
- The quote must be copied verbatim from the title, location or body above:
  the same words in the same order, with no paraphrase, no ellipsis and no
  words added. Keep it short (one phrase or sentence).
- If the posting does not state anything that supports the claim, the quote
  must be exactly NOT STATED (capital letters, nothing else).
- Do not use outside knowledge about the company or the role. Use only the
  text between POSTING markers, the title and the location.

Output
Return JSON only: no prose, no Markdown, no code fences. Exact shape:
{"claims": [{"claim": "<one sentence>", "quote": "<verbatim quote or NOT STATED>"}]}
The "claims" list must have 3 to 5 items, and each item must have exactly the
keys "claim" and "quote", both strings.
