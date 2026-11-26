---
version: label_claims_v1
---
You are checking claims about one job posting against the posting's own text. You did not write these claims. Judge each claim only by what the posting says, using these rules (from FILTER.md, section B):

- supported: the posting has words that, read on their own, say what the claim says. Plain abbreviations count ("SF" = San Francisco); inference does not.
- contradicted: some words in the posting say the opposite of the claim (for example, the claim "requires 4 years or less" against "7+ years of experience"). If both a supporting and a contradicting passage exist, the label is contradicted.
- insufficient: nothing contradicts the claim, and nothing in the posting states it. This includes a word that appears in another sense, a passage about the company rather than this job, or a claim that needs a step the text does not take.

Posting:
- company: {{company}}
- title: {{title}}
- location: {{location}}
- text:
<<<
{{text}}
>>>

Claims (numbered from 0):
{{claims}}

Reply with exactly one JSON object and nothing else: no code fences, and no text before or after it. Give one entry per claim, in order:

{"labels": [{"i": 0, "label": "supported", "evidence": "<the exact words from the posting your label rests on, or empty>", "why": "<one short sentence>"}, ...]}
