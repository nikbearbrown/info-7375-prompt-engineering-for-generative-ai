Label each claim below against this one job posting's own text.

The claims are about whether the posting fits a candidate. Judge them only from the POSTING object: its title, location and text. Do not use what you know about the company or the job market.

Labels (these definitions are the rule; follow them exactly):
- "supported": a quote from this posting asserts the claim.
- "contradicted": a quote from this posting asserts the opposite of the claim (for example "5+ years of experience" or a "Staff" title against an early-career level; a single named office with no remote option against "Boston or remotely"; "we are unable to sponsor" against visa sponsorship).
- "insufficient": no quote asserts the claim or its opposite. This includes text where a word appears but does not assert the claim: "AWS" naming a partner or customer does not mean the role asks for AWS; "Python" in a list of client SDKs does not mean the job is Python work.
- If the posting has both a quote that supports the claim and a quote that contradicts it, the label is "insufficient", and you give both quotes in "conflict".

Quotes: copy them exactly, character for character, from the POSTING object (title, location or text), at most 300 characters each. A quote that is not found verbatim in this posting makes your label invalid.

POSTING:
{{POSTING_JSON}}

CLAIMS:
{{CLAIMS_JSON}}

Output contract. Reply with exactly one JSON object and nothing else: no prose, no code fences. It must be:
{"labels": [ ...one object per claim, in the order given... ]}
Each label object has exactly these keys:
- "id": the claim's id, as given
- "label": one of "supported", "contradicted", "insufficient"
- "quote": the quote for "supported" or "contradicted"; null for "insufficient"
- "conflict": null, or {"for": "<quote>", "against": "<quote>"} only when the label is "insufficient" because the posting says both
