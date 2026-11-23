# Sign-off and driver's seat: Job-Search Agent 3

My notes of 2026-11-22, organized by Claude Code at my request. It checked them against the record, updated two lines
that had already happened by the time I sent them (my own test and my recomputation), and added the commit and file
pointers. The checks, the decisions and the signature are mine; my notes are kept word for word outside the repo.

## Sign-off

**Sign-off: Job-Search Agent 3**

**Checked:**
- The filter's rejects. I judged 55 audit cards by hand, blind, and froze my verdicts before the answers were opened
  (`45fc2c0`). Of 30 random rejects I would have kept 1, card 17; once I saw the "U.S. Person Required" line its card
  had hidden, I would reject it too, so 0 of 30 (`js3/audit/2026-11-21T044414Z/RESULTS.md`, `AFTER-REVEAL.md`).
- The filter's keeps. Of the 18 kept postings in the audit, I judged 16 and agreed with all 16; the other 2 were "?".
- A fresh held-out set. I judged 30 cards by hand and froze my verdicts (`1e2b1e1`). Their answers were opened once,
  after the changes to measure and their predictions were committed (`1c9a37e`): FILTER.md v1.0's keep or reject
  agreed with all 27 cards I judged (`js3/score/EXPERIMENTS.md`, `cb1b50c`).
- The shortlist's claims. I labeled all 105 claims by hand and froze them before the checker's labels were opened
  (`1608a04`). The rule-based checker agrees with me on 101 (`57041c4`), and on 102 after my four flip checks
  (`cb4943a`).
- R1 rejects a posting that is not full time: my own test, `tests/test_aravind_own_rule.py`.
- The audit and claims numbers come back from the saved files: my recomputation, below.

**How:**
- **By hand:** the 190 judgments above (55, 30 and 105), my answer on card 17 after the reveal, my change of 09.6
  before the freeze, and the four flip checks.
- **By a test I wrote before reading Claude's code:** `tests/test_aravind_own_rule.py`. I wrote the case (a software
  engineering internship) and the expected result (rejected, with R1 deciding) from my own R1; Claude Code supplied
  only the empty skeleton and the call to the filter. I ran it myself on 2026-11-22 at 3:18 AM ET: `OK`.
- **By recomputation:** at 3:19 AM ET I reran `tools/score_audit.py` and `tools/score_claims.py` myself. The numbers
  were the same (51 of 55 agree, 1 miss, 3 "?"; 1 miss in 30 and a 14.9% bound, 0 in 30 and 9.5% after the reveal;
  the checker agrees on 101 of 105), and both RESULTS.md files came out byte for byte the same.
- **With Claude's help:** Claude Code built the filter, the board readers, the audit, held-out and claims kits, the
  scoring scripts, the held-out experiment tool, the MCP server and the first drafts of both evaluations, FILTER.md
  v1.1 around my three calls, and the test suite (348 tests with mine; 82 of 82 planted mistakes caught on
  2026-11-21). It ran those checks and the held-out measurement, fixed the cards after card 17, and found the sentence
  behind each claim disagreement.

**Not checked:**
- Postings beyond what the audit covers: one day's saved answers (2026-11-20) of three boards (OpenAI, Verkada and
  Palantir). Nothing live, and no other boards.
- Whether the boards' own fields are right about the jobs (employment type, places, dates). I judged what the postings
  say.
- Whether export-control requirements make a particular job legally available to Jane. All six of my "?" verdicts
  hinge on such lines or on clearance.
- Whether either MCP server is secure or conforms to the MCP specification. Both evaluations say not conformant and not
  shown to be secure.
- Whether the results hold as postings change, and whether v1.1 holds on new labels: I made my three v1.1 calls after
  seeing the held-out results, so that set no longer tests them, and no fresh set has been labeled since.

**Not claiming:** This agent is a job-posting evaluation tool, not a guarantee that Jane is eligible for a job or will
get an interview. It does not apply for jobs, contact employers or verify legal work authorization. It also gives no
miss rate for all postings: the audit only bounds the misses among one day's rejects (at most 9.5% with my card-17
answer, 14.9% as frozen).

**Signed or withheld:** Signed: Aravind Sundaravadivelu, 2026-11-22. (Withheld until the v1.1 work was done, as I
chose earlier that day; signed after it, so the sign-off covers it.)

## Driver's seat

| Claude does | I do | Why the judgment that a posting is worth my time stays mine | Where it shows |
|---|---|---|---|
| Collects postings from the three boards and puts them in one format (the agent Claude Code built). | Decide whether each opportunity is worth considering. | A matching title does not necessarily mean the job fits my goals. | the filter run, `js3/filter-run/2026-11-21T044414Z/report.md`; my 55 and 30 verdicts (`45fc2c0`, `1e2b1e1`) |
| Applies FILTER.md's rules and scores postings. | Write the rules (FILTER.md Section 1, in four drafts) and decide whether they make sense. | I understand the type of software engineering work I want. | FILTER.md v1.0 in `66e26d9`; my drafts in `filter-drafts/` |
| Flags possible sponsorship, clearance, location and experience restrictions. | Review unclear requirements and decide when more information is needed. | A keyword match cannot always explain the real meaning of a job requirement. | card 17 (`AFTER-REVEAL.md`); my six "?" verdicts |
| Compares my judgments with the filter's and the checker's results and highlights disagreements. | Review disagreements and decide whether to change my judgment or the rule. | Agreement with the filter does not automatically make a decision correct. | the audit's and the claims' RESULTS.md (`79df09c`, `57041c4`); `FLIP-CHECKS.md` (`cb4943a`) |
| Runs the agent and prepares the results. | Decide whether I trust the tool and whether its output is useful. | I am responsible for how I use the results and the decisions I make from them. | my trust lines in `js3/mcp/EVALUATION-OWN.md` and `EVALUATION-OTHER.md`; the live Claude Code run (`ad1714d`) |
