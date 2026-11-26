# The source-grounded shortlist (Chapter 7)

> Claude Code drafted this file from `out/shortlist/v1.0/run.json`, my claim checks (`labels/claim_checks_v1.0.csv`), and the posting texts. Every one of the 69 claims, with its quote and both labels, is in **`out/shortlist/v1.0/claims_table.md`**. Lines marked **My view** are for my own words.

## How each justification was built and checked

1. **Justify.** A fresh Claude session (`prompts/justify_v1.md`) writes the claims: exactly one `core_work`, one `level`, one `employment`, and 1–4 `has`/`lacks`. Each carries a quote copied from the posting, or an empty quote if the posting says nothing on the point.
2. **Verbatim check (code, E1/E3).** A quote that isn't in the posting is `insufficient` and never reaches step 3. Two claims had no quote. No quote was fabricated.
3. **Meaning check (E4).** A second fresh session (`prompts/check_v1.md`) sees only the posting text and the claims: no résumé, no score, no verdict. It labels each claim supported, contradicted, or insufficient.
4. **My hand check.** Blind to the checker (`scripts/claim_server.py`). Under E4, **my label stands where we differ.**
5. **Answer (A1–A3).** `agent3/claims.py` `answer()`.

## The shortlist

The top 10 by score under FILTER.md v1.0, which is the **same set of 10** under v1.2, the version in force, in a slightly different order.

| v1.0 rank | Posting | Score v1.0 → v1.2 (v1.2 rank) | Still listed 11-24? | Answer: checker's labels | **Answer: my labels (E4, in force)** | My posting label |
|---|---|---|---|---|---|---|
| 1 | Software Engineer – Data Infrastructure (Figma) | 15 → 15 (1) | yes | relevant | **relevant** | not in sample |
| 2 | Data Engineer (Snowflake) | 14 → 14 (2) | **no** | relevant | **relevant** | relevant |
| 3 | Backend Engineer – Data Platform (Spotify) | 11 → 11 (4) | yes | **cannot_tell** (A2) | **relevant** | relevant |
| 4 | Senior Solution Engineer (Snowflake) | 11 → 11 (5) | **no** | relevant | **relevant** | not in sample |
| 5 | Senior Solution Engineer (Snowflake) | 11 → 11 (6) | yes | relevant | **relevant** | not in sample |
| 6 | Technical Architect (Snowflake) | 10 → 10 (7) | yes | relevant | **relevant** | relevant |
| 7 | Data & Integration Engineer, Business Systems (Figma) | 10 → 14 (3) | yes | relevant | **relevant** | not in sample |
| 8 | Data Platform Engineer (Figma) | 9 → 9 (8) | **no** | relevant | **relevant** | relevant |
| 9 | Backend Engineer – Data Platform (Spotify) | 8 → 8 (9) | yes | relevant | **relevant** | not in sample |
| 10 | Software Engineer – SnowConvert AI (Snowflake) | 8 → 8 (10) | yes | **cannot_tell** (A2) | **relevant** | relevant |

**Missing source:** the board `no-such-board-js2` returned HTTP 404 in both runs. The shortlist is therefore **incomplete** for that board: "no data, I cannot tell" (A3), not "no relevant postings".

**3 of the 10 are no longer listed** on 2026-11-24. FILTER.md F9 doesn't exclude closed postings. That was noticed while building the shortlist, and no rule was added for it.

## The 69 claims, labeled

| | supported | contradicted | insufficient |
|---|---:|---:|---:|
| **Checker** (fresh Claude session, after the code's verbatim check) | 46 | 1 | 22 |
| **Me** (blind hand check, 2026-11-26 00:15–00:25 UTC) | **69** | 0 | 0 |

**We disagree on 23 claims. Under E4, my labels stand.** This is my decision, made after Claude Code showed me the following, and it is recorded here as made:
- **#16 and #64 have no quote.** Each is "The posting does not say how many years of experience are required…". E3, which I approved, says a claim without a quote is *insufficient* by definition. I labeled both supported.
- **66 of my 69 notes read "job role is relevant".** That judges the job, not whether the quote states the claim.

So **as recorded, my hand check did not test the claims against their quotes.** The checker's labels are the only claim-by-claim judgments here. The checker has a flaw of its own, described next.

### The checker's flaw (Claude Code's design)

To keep the checker from being anchored, it was given no résumé. But a `has`/`lacks` claim has a résumé half ("…the résumé lists both"). **About 14 of the checker's 22 "insufficient" labels give "it contains no résumé" as the reason.** They are artifacts of my pipeline, not findings about the posting. A better design would split each has/lacks claim into the posting's requirement, checked against the posting, and the résumé's match, checked against the résumé. Not done.

## Relevance is not entailment: two real cases

**Case 1: a verbatim quote cut just before the words that reverse it** (posting 4, "Senior Solution Engineer", claim #28)
- Claim: "The posting **requires** a university degree in data science or a related field."
- Quote (verbatim, so it passes the code's check): "University degree in computer science, data science, engineering, mathematics or a related field"
- The sentence it was cut from: "…mathematics or a related field**, or equivalent practical experience**. A Master's in Data Science or Business Analytics is a plus"
- Checker: **contradicted** (contra quote: "or equivalent practical experience"). Mine: supported.
- The posting matches the filter's words, and the quote really is in it. The claim is still false. **A verbatim quote is not support.** This is wrong version WV2 occurring in real data. The test `tests/test_wrong_versions.py::WV2` exists for exactly this, but on real data the meaning check is a Claude session, not code.

**Case 2: the words that scored the posting do not say "required"** (posting 1, "Software Engineer – Data Infrastructure", claim #5)
- The filter matched **Spark, Kafka, Airflow and "streaming"** in one line. Those matches drive its score of 15, the top of the shortlist.
- Claim: "The posting **requires** strong expertise in batch and streaming processing technologies such as Spark, Kafka, or Airflow."
- That line sits under "**We'd love to hear from you if you have:**". The posting never says "required" about it.
- Checker: insufficient. Mine: supported.
- **Caveat, honestly:** this one is arguable. The posting has a *separate* list headed "While it's not required, it's an added plus", so "We'd love to hear" may be its de facto requirements list. That is the point: whether the sentence *states* "required" is a reading, and keyword relevance can't make it.

## The abstention rule and a counterexample that exposes its limits

**The rule** (FILTER.md A1–A3, implemented in `agent3/claims.py` `answer()`):
- **A1:** a posting with under 300 characters of text gets "I cannot tell".
- **A2:** if a core claim (`core_work`, `level`) is contradicted, the answer is not relevant. If a core claim is not supported, the answer is "I cannot tell".
- **A3:** a failed board gets "I cannot tell", never "no relevant postings".

**Where it fired.** With the checker's labels, A2 abstained on **postings 3 and 10**. In both, the posting states no years or seniority level, and the `level` claim was the honest "The posting does not say…" with no quote. I labeled both postings `relevant`. Under E4 (my claim labels), A2 never fires on the shortlist. **A1 never fired on real data:** the shortest posting in the corpus is 2,391 characters.

**Counterexample 1: it abstains where a person can tell.** "Backend Engineer – Data Platform" never states a level, yet nothing in it suggests a level Jack doesn't fit. A2 treats *silence* about seniority as *uncertainty* about relevance. Most postings never state every criterion, so a rule that abstains whenever a core claim lacks a quote abstains on silence, not on doubt.

**Counterexample 2: it answers where it should not. This is the deeper limit.** For postings 4 and 5 ("Senior Solution Engineer"), the supported `core_work` claim reads: "The posting says the main work is **pre-sales solution engineering**: working with the sales team… deliver data-driven demonstrations…". The claim is supported, so A2 answered **relevant**.
- FILTER.md A2 names the core claim as "**the main work is data engineering**". The code checks only that *some* `core_work` claim is supported, **not what it says.** A supported claim that the work is pre-sales counts the same as a supported claim that it is data engineering.
- That is a gap between my own document and my own code. It was found while writing this section, and it is **not fixed**.
- Under my 2026-11-25 definition, where solution engineering doesn't count against a posting, "relevant" happens to be the answer I'd give. Under the definition FILTER.md v1.0 was written for, the same code gives the opposite of the right answer, and **support is not the same as fit.**

> **My view:** ____________
