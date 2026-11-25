# Shortlist review — is each reason backed by the posting? (JS3 2.2)

Written 2026-11-25 for the shortlist produced under FILTER v2.1 (`shortlist/shortlist.json`, `SHORTLIST.md`: 67 kept postings).

## Who labeled what

| Labels | By | Where |
|---|---|---|
| 496 claims, each `supported` (with a verbatim quote) or `insufficient` (quote null) | **code** (`reports/shortlist.py`, rule FILTER.md §2), `label_by: "code"` | `shortlist/shortlist.json` |
| final label of the claim reviewed below | **Isaac** | `shortlist/review.csv` (kept apart, so a re-run of the script can't erase it) |

Code labels by rule: title 67 supported; location 67 supported; skills 161 supported; years 21 supported / 46 insufficient; visa 67 insufficient; salary 7 supported / 60 insufficient. Code never proposes `contradicted`: a contradicting sentence (e.g. "8+ years") makes the rule cut the posting, so it never reaches the shortlist. All 323 quotes were checked to be word-for-word substrings of their title, location or JD, by re-reading the raw files (2026-11-25, 0 mismatches). That every claim has a label is pinned by `tests/test_js3_shortlist.py`.

No Claude output is shown in this file.

## Relevance is not entailment

**Stripe 7235875, "Software Engineer, Privy"** (https://stripe.com/jobs/search?gh_jid=7235875)

| | |
|---|---|
| Claim (code) | "The JD asks for AWS, which Aarav has" |
| Quote | "In practice, we use  boring technology  like Node, React, and AWS so we can focus our engineering energy entirely on pushing the boundaries of Privy's core product, e.g" (verbatim, double spaces included) |
| Code label | supported (AWS is in the sentence, as a word) |
| **Final label (Isaac)** | **insufficient** |

The sentence is **relevant**: it names a skill Aarav has, used in the team's stack. In Isaac's words, matching the stack the company uses is still a good plus. But it does not **entail** the claim. It says what the company uses, not what it asks of an applicant. FILTER.md §2 rules this out: a matched word must be used "in the sense the claim means (a requirement, not … the company intro)".

What follows from it: AWS is this posting's **only** rule-3 skill. The posting passed rule 3, and so reached the shortlist, on a sentence that asks nothing of Aarav. The label changes the evidence, not the verdict. Whether Aarav applies is still a fit judgment, and Isaac counts the shared stack as a plus.

Other places the same gap shows (code `supported`, not reviewed): "Much of our stack runs on Kubernetes" (openai, Compute - Storage), and skills that appear only under "Preferred qualifications" (openai, ChatGPT Shopping). LABELING_RULE counts nice-to-have as a requirement, so the second one is closer to the line.

## Abstention: when the agent says "I cannot tell"

**Rule (FILTER.md §2, Isaac's decision D3, 2026-11-24):** the agent abstains only when there is no text to judge, meaning an empty or tags-only JD (rule E), or text it can't trace to a saved raw file. Missing information is not a reason to abstain: rules 4–6 pass and the claim is labeled `insufficient`. A posting is never cut, or held back, for something the board didn't write. The shortlist shows those labels next to the verdict, e.g. "relevant — insufficient: years, visa, salary".

**Counterexample showing its limit: Stripe 8198280, "Software Engineer, Backend" (audit sample S16).** Under FILTER v1 the years line said `skipped: no years in posting` (`audit/v1/all_verdicts.json`), so the shortlist labeled "The JD requires at most 4 years" `insufficient`, i.e. "not stated". The JD does state it: "plus **six (6) years** of software development experience". The v1 number pattern stopped at the ")". So "insufficient" did not mean the posting was silent. It meant **the reader** couldn't see the answer, and the posting stayed relevant. The abstention rule assumes that "no years found" equals "no years written", and this counterexample shows that's not always true. FILTER v2 (B2) reads "(6) years" and cuts this posting at rule 4. The general limit stays: any wording the pattern doesn't know (e.g. "six years" with no digit) turns a stated requirement into an `insufficient` claim and keeps the posting.

## Limits of this shortlist

- **Long quotes on Ashby postings:** sentences are split at ". ", "!", "?" and newlines. Ashby JDs often list items without stops, so 16 of 189 JD quotes are longer than 300 characters (the longest is 2,430). The quote is still verbatim, but it is a paragraph, and a reader has to find the matched word in it.
- **Only one claim was reviewed by hand.** The other 495 carry the code's label only.
