You are writing a source-grounded justification for one job posting, for one fictional job seeker. You do NOT decide whether she should apply and you do NOT give a score. You state claims about what the posting says that bear on the definition below, and you ground every claim in the posting's own text.

DEFINITION OF A RELEVANT POSTING (from the job seeker's filter document):
{{DEFINITION}}

JOB SEEKER'S PREFERENCES (fictional persona):
{{PERSONA}}

POSTING (the only source you may use; do not use any outside knowledge about the company):
{{POSTING}}

INSTRUCTIONS
1. Write 4 to 8 atomic claims. One fact per claim. Cover, when the posting addresses them: the role's title and level; the years of experience it REQUIRES (say whether a years figure is under a required/minimum heading or a preferred/bonus heading); the location; sponsorship or work authorization; the product domain.
2. For each claim, copy ONE quote from the POSTING TEXT, character for character, that the claim rests on. Do not paraphrase, fix typos, change case, or join separate sentences. Keep it under 300 characters.
3. If the posting does not state the fact a claim needs, set "quote" to null, set "abstain" to true, set "proposed_label" to "insufficient", and write the claim as "The posting does not state ...". Never fill a gap from outside knowledge.
4. "kind" is "quoted" if the claim only restates what the quote says, or "judgment" if it goes beyond the quote (an inference, a comparison with the job seeker's preferences, or a reading of tone).
5. "proposed_label", judged against the posting text only:
   - "supported": the quote, by itself, entails the claim.
   - "contradicted": the quote entails that the claim is false.
   - "insufficient": no quote entails the claim either way, or the quote is only on topic.
   Write claims that you expect to be supported or insufficient; do not write false claims on purpose.

OUTPUT FORMAT. Reply with one JSON object and nothing else: no prose, no code fences. Exactly these keys:
{"posting_id": "<the id given above>",
 "claims": [ {"claim": "<one sentence>", "kind": "quoted" or "judgment", "quote": "<exact substring of the posting text>" or null, "proposed_label": "supported" or "contradicted" or "insufficient", "abstain": true or false} ] }
