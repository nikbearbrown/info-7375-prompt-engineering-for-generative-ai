# FRICTIONAL.md: JS3 honest log

_Claude Code drafted options for these entries at my request; I chose one for each and edited it (SOURCES.md)._

### 1. Writing the filter before the code (JS3-CP1 `50551836`)

I accepted most ★ answers without much argument, because I wanted the gate committed before the fetch. The one I changed was rag. I had picked it, but Priya's résumé never mentions RAG, so a keep on "rag" would have produced a claim her résumé can't back. I cut it.

### 2. What the reject audit showed me (my verdicts: JS3-CP7)

By my judgment, 1 of 30 random rejects was wrong: R08, "AWS GTM Partnership Lead", rejected only by the exclude word "Lead". So the honest statement is the bound in `audit-summary.md` (at most 14.9 % of this snapshot's rejects), not a miss rate.

The false friend I found was `agents`, in rows C08 and R20. It matched because both accounting postings say "principal-vs-agent", an accounting term, not AI agents.

### 3. Relevance is not entailment (`shortlist/claims.md`)

In S01, Claude claimed "the level fits early-career" and quoted "Have industry experience in machine learning research". The quote is about the job, but it says nothing about the level, so I labelled it insufficient. The words matched, and the claim still wasn't supported.

### 4. The tool server and trust (EVAL-OWN-SERVER.md, EVAL-OTHER-SERVER.md)

For my own server I chose **allow, bounded** to this one task. For the teaching server I chose **deny for JS3**, but allow it for the Chapter 8 exercise. What surprised me: Claude Code's first message was `server/discover`, which isn't in the lifecycle I was taught, and the teaching server answers it with -32000.

### 5. What I accepted, modified or rejected from Claude

- **Accepted:** the code, the tests and the seeded draws.
- **Modified:** the reasons for `python` and `sql` in FILTER.md 1.4.
- **Rejected:** the topic word `rag`, and the API-key route from my JS1 `.env` (it returned 401), so the justifications went through my Claude Code account instead.

### 6. Unresolved

"agents" is in 174 of 174 Notion postings. By my own 90 % rule it should go on Notion's ignore list, but Notion keeps nothing anyway because of the location spelling ("San Francisco, California"). The two rules interact, and I measured only one change.
