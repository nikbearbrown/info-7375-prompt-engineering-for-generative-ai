# FRICTIONAL — Job-Search Agent 3

- The Greenhouse postings have no description text. The filter runs on title only (plus Greenhouse metadata values) for 1694 of 1779 postings. This was discovered in orientation, recorded in FILTER.md, and affects every scoring and shortlist decision.
- Claude Code drafted the reject audit verdicts. I reviewed and accepted 38 as correct and marked 2 as can't tell. The AI draft is preserved as output/audit_sheet_ai_draft.md. SOURCES.md records what each party did.
- The "software engineer" pairing rule (requires a topic word) rejects 237 Software Engineer postings, 236 of them Greenhouse postings with no description (the other one is from Spotify). Two of these (rows 12 and 38) could not be confirmed as correct or incorrect without description text.
- The MCP server's score_posting tool returns only 0 or 100 despite the tool description promising 0-100. This is documented in MCP_EVALUATION.md. The weighted scorer in js3/scorer.py also produces only two scores per run (100 or 60 with default weights), split exactly by board, as documented in SCORE_REPORT.md.
- "AI Engineer" and "Applied AI Engineer" are not in FILTER.md's role words. 8 postings with these titles were rejected. Found in the reject audit but not measurable from the sample.
- What I accepted from Claude: filter code (js3/filter.py), MCP server and client (js3/mcp_server.py, js3/mcp_client.py), scorer code (js3/scorer.py), all report templates (SCORE_REPORT.md, MCP_EVALUATION.md, REJECT_AUDIT.md), SIGN_OFF.md text, and FRICTIONAL.md text.
- What I wrote myself: FILTER.md — the rules, reasoning, and version history are entirely mine.
- What I modified or decided: the four flagged audit verdict rows (rows 5, 9, 12, 38), the decision to keep rejecting Software Engineer without a topic word, the decision to use exact title matching in the MCP server.
- Scorer weights (60/20/20) were set by me and implemented by Claude.
- What I rejected from Claude: no rules or code were rejected; all deviations are recorded in this file and in SOURCES.md.
- What is unresolved: whether the 2 can't-tell rows are correct rejects. Whether the scorer weights are the right ones. Whether "AI Engineer" should be added to FILTER.md.
