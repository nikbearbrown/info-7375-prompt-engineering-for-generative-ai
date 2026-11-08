# FRICTIONAL.md — Job-Search Agent 2

Written by Swathi Baba Eswarappa, in my own words.

## Nov 4, 2026

Writing GATE.md before any code felt a little confusing at first because I had to think about all the things that could go wrong before actually building the agent. I changed case 13 because I didn't want the agent to keep waiting for my approval or make changes to the state file without my permission. I accepted Claude's HTTPS rule even though I hadn't included it in my original GATE.md, because it seemed like a sensible way to make network requests safer. When Claude's test assumed what Plaid's data looked like, I asked it to check the actual response first because I didn't want to build something based on assumptions.

Evidence: GATE.md before any code (510a59a); my boundary predictions with case 13 changed (85dbd4c); the https rule in policy.py (5275cc4), tested by the http control in tests/test_policy.py; loop tests before loop code (ed201d4, then e6a70a4); GATE revision (96dde19); first live run (d8a5a7b).

## Nov 5, 2026

What surprised me in the second live run was that the agent found 31 new postings, but only one was marked relevant. It made me realize how limited my title-based rule still is. I didn't expect the naive JS1 watch to also erase its previously saved job IDs when it received an empty response. I thought it would just report zero new jobs, so that was surprising. Something still unresolved is that my agent and my independent check only catch boards that drop to zero postings. Neither notices when a board loses some postings unexpectedly, so that's something I would want to improve later.

Evidence: second live run (bd602a2); independent-check tests C1-C8 before the check (f79e4a9, then 9615734); finished-wrong-answer demo, including the JS1 watch's state going from 923 ids to 0 (ae284ca).

## Nov 5–7, 2026 (review packet)

Running the commands myself felt a little challenging at first, but it helped me understand what was actually happening instead of just trusting Claude's results. When I saw my username in the saved output, I realized I needed to be more careful about privacy. I asked Claude to redact it, but decided not to rewrite the old commit history. The part I understood best from the diff was how the parser was changed to add "(United States)" from the address after "San Francisco HQ", so my rule recognizes it as a US location instead of incorrectly rejecting it. I was surprised that even after fixing the location issue, the job was marked relevant just because its title contained "Analyst." It showed me that fixing one bug doesn't mean the whole relevance rule is accurate. When Claude Code pointed out two mistakes in my decision wording and I corrected them, I learned that even my documentation needs to be checked against what actually happened. I shouldn't claim something unless the evidence supports it. Something I rejected from Claude was its offer to rewrite the git history to remove my username, because it would have changed every commit hash I had already recorded.

Evidence: my reproduction (file 01, 5909627, redacted in dcf9cf9); GATE revision before the fix (d131b5f); tests A1-A5 in tests/test_ashby_address.py before the fix (16da614); my failing run (file 02, 5ac5d93); the fix (4a3db26); my passing runs and decision (files 03-04 and REVIEW-PACKET.md, 4c08a7f).
