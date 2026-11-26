# Source-grounded shortlist

## What was run
Top 5 postings kept by filter v1.1 (`python3 -m js3.shortlist --top 5 --run-claude`, 2026-11-25). Each was sent once to Claude (`claude -p`, prompt `prompts/justify-v1.md`), which returned 3 to 5 claims, each with a verbatim quote or `NOT STATED`. Raw output, the exact prompt and its SHA-256 are in `out/shortlist/claude_raw/`.

| # | Board | Title | Filter score |
|---|---|---|---|
| 1 | databricks | Staff Machine Learning Engineer | 6 |
| 2 | databricks | Staff Machine Learning Engineer, CustomerLake (ML/LLM) | 6 |
| 3 | openai | Research Scientist / Research Engineer - Foundations, Search | 6 |
| 4 | openai | Machine Learning Data Scientist - Consumer Forecasting | 6 |
| 5 | openai | Research Engineer / Research Scientist, Human Flourishing | 6 |

## Two checks, kept separate
1. **Automatic quote check (`js3/evidence.py`):** is the quote actually in the posting? 25 claims: **21 quotes found, 4 NOT STATED, 0 invented.** A found quote is only a *candidate*, never "supported".
2. **Claim labels (`labels/shortlist_claim_labels.csv`):** does the quote prove the claim? **17 supported, 4 insufficient, 4 cannot tell, 0 contradicted.**

The gap between the two is the point: **21 quotes were real, but only 17 proved their claim.**

## Abstention
All 4 NOT STATED claims are output as **"I cannot tell"** (FILTER.md section 2), never as support. Examples are claims about things the postings never address.

## Relevance is not entailment (marked case)
*openai / Machine Learning Data Scientist - Consumer Forecasting, claim 3*
- **Claim:** the role includes building internal tooling and platforms, which overlaps with Priya's ML platform interests.
- **Quote (found verbatim):** "Contribute to self-service forecasting tools and internal platforms"
- **Label: insufficient.** "Platforms" sounds like the filter's `ml platform` keyword, but the quote is about forecasting tools for business teams. It shows no ML-platform work. The quote is relevant and real, and the claim is still not entailed.

## The other insufficient labels
- "Machine learning" in a title does not show the claimed "ml engineer" match too.
- "Familiarity with" RAG and fine-tuning is a candidate requirement, not a statement that the job does that work.
- "Training methods" is not "training systems".

## Calls a reader could dispute
- Two research postings, claim 5 (title lacks the target keywords): labeled *cannot tell* because the quote is NOT STATED, but one could argue *contradicted*.
- Two claims that a stack is "standard" for an ML engineer are labeled *supported*: the tools are quoted, but "standard" is a judgment no quote states.

## Provenance
The claim labels were drafted by Claude Code (Claude Code ran in auto mode, so the file was written without a per-edit approval). I reviewed the marked case and the calls listed above. These are AI-drafted, human-reviewed labels.
