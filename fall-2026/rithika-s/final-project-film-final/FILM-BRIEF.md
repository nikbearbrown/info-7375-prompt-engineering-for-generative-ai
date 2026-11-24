# FILM-BRIEF — Agentic Retrieval Lab (final film, under 4:00)
Rithika Sankar Rajeswari · INFO 7375

## 1. Executive summary (0:00–0:42) — what and why, no "how"
In RAG systems, AI agents now write the search queries, not people. If an agent's query finds the wrong passage, the answer built on it is wrong, and nobody sees why. I built Agentic Retrieval Lab to measure, on public data, whether agent-written queries find the right passage as well as the original human question, and which search method handles them best. So far, the agent's rewrites didn't beat the original human question with any search method. This matters to anyone choosing a search method for an AI agent: it's a cheap, repeatable check, and every number in it traces back to a file.

## 2. Introduction (0:42–1:23) — what others have done
- Q2D-Web, from Perplexity, studies search with agent-written queries over about 190 million web documents, but it keeps its corpus, queries and judgments private: the public gets a leaderboard, not the data.
- MS MARCO, from Microsoft, is the standard public set of real search questions with a marked correct passage, but its queries are human only.
- BM25 is the classic keyword search. bge and e5 are widely used small embedding models that search by meaning.
- The gap: there's no small, open experiment that compares human and agent queries across these search methods, that anyone can rerun on a laptop. That's what this project is.

## 3. Methods (1:23–2:21) — how
- Data: 300 MS MARCO questions (fixed seed 42). Claude Haiku 4.5 rewrote each one into 1 main and 3 supporting agent queries, 1,200 in total. A leak check flagged rewrites that gave away the answer.
- Test corpus: 200,000 passages, made of every correct passage, BM25's top-100 near-misses, and random fill.
- Four retrievers: BM25, bge-small, e5-small, and a BM25+bge hybrid.
- Measures: whether the correct passage is in the top 100, and how high it ranks. Each comparison is query by query, with 95% bootstrap intervals.
- Resources, all in hand: one M5 laptop with 16 GB (each embedding model ran in about 8 minutes), my own Anthropic API credits (the logged cost for all LLM calls was $0.63), and a free Hugging Face account. 135 automated tests.
- Next: a length-matched control corpus, harder distractors chosen by dense models, two larger embedding models, and an LLM relevance judge.

## 4. Evaluation (2:21–3:18) — how I'll know it worked
I set these pass/fail rules before the Milestone 2 runs (drafted with Claude, adopted by me):
1. Trust: every test passes and every number links to a dated results folder. Met.
2. Length: if picking the shortest passages beats random, dense results are provisional. It did, by a small margin, so they're provisional.
3. Dense beats BM25 only if the 95% interval is above zero. It was, by +0.32 recall, but my corpus is made of BM25's near-misses, so it flatters dense models.
4. Human vs agent: the human question came out ahead with every search method; the gap shrank from 5 points with keyword search to about 1 point with the meaning-based models, too small to call for e5.
It worked if: the numbers reproduce and the limits are stated. It failed if: a fixed corpus erases the dense advantage. Next, I'll build that fixed corpus.
