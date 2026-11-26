# Sign-off: Job-Search Agent 3

My words, typed in chat 2026-11-25. The test list is in the README.

```text
Sign-off — Job-Search Agent 3
Checked:
I checked the filter rules for title matching, topic words, experience level, US location, and the minimum
topic-word threshold. I also checked the filter options, evidence claims, abstention behavior, level and location
extraction, and MCP server handshake and tool calls using the repository tests listed above.
(tests/test_filter.py, tests/test_filter_options.py, tests/test_evidence.py, tests/test_mcp_server.py)
I also reviewed 54 audit postings and labeled 20 held-out postings. For the shortlist, I reviewed the quoted
evidence and checked whether the claims were actually supported by the posting.

How:
I reviewed the rules, made the decisions about which changes to accept or reject, and did the manual posting
reviews. I ran the automated tests, but Claude wrote every test from my FILTER.md before writing the code. I also
used Claude's help during the review, so I am not claiming that every part of the evaluation was done independently.

Not checked:
* I did not verify that every shortlisted posting is still open and accepting applications.
* I did not verify every extracted claim against every employer's complete, live posting.
* I did not test every possible sentence structure that could make a skill optional, preferred, or learnable rather
  than required.
* I did not test the agent against every possible job-board format or unexpected response.

Not claiming:
This agent does not prove that a job is a perfect fit, that Rohan meets every employer requirement, or that he will
get an interview or an offer. It only filters and ranks postings using the rules and evidence available to it.

Signed or withheld: ____________
```

## Driver's seat

| task | Claude should | I should | why the judgment stays mine | pointer |
|---|---|---|---|---|
| filter rules | format them, find gaps, test them | decide which words and rules count, and why | [ ] | `a725b4a4`, FILTER.md Appendix A |
| reject audit | draw the sample blind, count, compute intervals | judge each posting | [ ] | `9ee00800`, audit/my-verdicts-2026-11-25.txt |
| rule changes A–D | measure each one | accept or reject each one | [ ] | `8a6b77e4`, FILTER.md Revisions |
| held-out labels | draw the set, hide verdicts | label each posting | [ ] | labels/my-heldout-labels-2026-11-25.txt |
| claim labels | auto-label, show the quote | confirm or override the "read" labels | [ ] | SHORTLIST.md |
| tool trust | run probes, record transcripts | decide whether to trust each server | [ ] | TOOL-EVALUATIONS.md |
| is a posting worth my time | rank and quote evidence | decide, and apply | [ ] | SCORE-CHANGES.md (#14, #4 vs my rules) |
