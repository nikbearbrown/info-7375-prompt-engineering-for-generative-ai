# Sign-off: Job-Search Agent 3

**Provenance.** "Checked", "How", "Not claiming", the first two "Not checked" items and the driver's-seat "why"
column are my words, typed in chat on 2026-11-25. At my request ("list specific things I did not check… keep that
distinction clear"), Claude Code then sharpened the "How" line, wrote "Not checked" items 3–7, and added the last sentence of "Not claiming" from facts in this
repository. Each one gives the file that shows it. I read them before signing.

```text
Sign-off — Job-Search Agent 3
Checked:
I checked the filter rules for title matching, topic words, experience level, US location, and the minimum
topic-word threshold. I also checked the filter options, evidence claims, abstention behavior, level and location
extraction, and MCP server handshake and tool calls using the repository tests
(tests/test_filter.py, tests/test_filter_options.py, tests/test_evidence.py, tests/test_mcp_server.py).
I also reviewed 54 audit postings and labeled 20 held-out postings. For the shortlist, I reviewed the quoted
evidence for each claim, with Claude's "read" labels in front of me (SHORTLIST.md).

How:
- Tests: written by Claude, from my FILTER.md, before Claude wrote the code. I did not write any test. I ran the
  suite myself: evidence/logs/13-tests-run-by-me.txt.
- Rules and rule changes: my decisions (FILTER.md Appendix A, Revisions). Claude measured them.
- Audit verdicts and held-out labels: by hand, blind to the filter's verdict, typed by me (audit/, labels/).
- Counts, intervals and Claude-scorer runs: computed by Claude's scripts. I did not recompute them myself.
- Shortlist claim labels and tool evaluations: Claude drafted, I reviewed with Claude's help.
I am not claiming that every part of the evaluation was done independently.

Not checked:
1. I did not verify that every shortlisted posting is still open and accepting applications.
2. I did not verify every extracted claim against every employer's complete, live posting.
3. The tool server still scores with filter v1 (every result says "filter_version": "v1"). I did not check
   that its answers match v1.1, the filter in FILTER.md now.
4. The claim labeler counts "languages like Go, Java, C/C++", "X or Y" and "experience … is helpful" as
   required. That made it too generous on 6 of 16 shortlist claims (SHORTLIST.md), and it is not fixed.
5. The Claude scorer ran once per posting (P1/P2/C2). I did not repeat any run to see whether the same
   verdict comes back.
6. The required/preferred heading word lists (evidence.py) were never measured on their own. Two parser
   bugs were found only by chance (curly apostrophe; "four (4) years"), so others may remain.
7. Rohan's persona lists no Spring Boot, although my filter calls it "his main framework". I did not
   reconcile the persona with the filter.

Not claiming:
This agent does not prove that a job is a perfect fit, that Rohan meets every employer requirement, or that he will
get an interview or an offer. It only filters and ranks postings using the rules and evidence available to it.
It is not fully reliable: v1.1 found neither of my 2 held-out Y postings, and the 0 of 32 reject audit result is a
sample estimate, not a measured rate for all postings.

Signed or withheld: Signed — Arundhati Kandelkar, 25/11/2026
```

## Driver's seat

The "why" column is in my words, typed in chat 2026-11-25.

| task | Claude should | I should | why the judgment stays mine | pointer |
|---|---|---|---|---|
| filter rules | format them, find gaps, test them | decide which words and rules count, and why | I decide which skills, titles, experience levels, and locations matter for the roles I want. | `a725b4a4`, FILTER.md Appendix A |
| reject audit | draw the sample blind, count, compute intervals | judge each posting | The tool can select the sample and calculate results, but I have to decide whether each rejected posting was actually relevant. | `9ee00800`, audit/my-verdicts-2026-11-25.txt |
| rule changes A–D | measure each one | accept or reject each one | Claude can show how each change affects the results, but I decide which trade-offs are acceptable. | `8a6b77e4`, FILTER.md Revisions |
| held-out labels | draw the set, hide verdicts | label each posting | I have to judge whether each posting matches my criteria without using the filter's verdict as the answer. | labels/my-heldout-labels-2026-11-25.txt |
| claim labels | auto-label, show the quote | confirm or override the "read" labels | I have to read the full sentence and decide whether the posting really supports, contradicts, or gives insufficient evidence for each claim. | SHORTLIST.md |
| tool trust | run probes, record transcripts | decide whether to trust each server | Claude can run tests and show what a server does, but I am responsible for deciding what access I am comfortable giving it. | TOOL-EVALUATIONS.md |
| is a posting worth my time | rank and quote evidence | decide, and apply | The agent can rank jobs and show evidence, but I make the final decision about where to spend my time and whether to apply. | SCORE-CHANGES.md (#14, #4 vs my rules) |
