1. MCP servers and tools

js3-score: has one tool, score_posting(board_key, posting_id). board_key must be one of ashby:notion, greenhouse:duolingo, greenhouse:robinhood or greenhouse:stripe. Its description says it judges one posting from the frozen corpus with FILTER v2 (conditions C1–C4), never returns the posting’s text, and refuses postings in the sealed sets.
Other servers in this session:
easel (chart)
Claude Docs (batch, guide, update, create, delete, export, query, read)
Claude_Browser (navigate, read_page, computer, preview*, tabs*, and others)
Claude_Code_iOS_Simulator (control, build)
terminal (read_terminal, run_in_terminal, and others)
visualize (read_me, show_widget)
mcp-registry
scheduled-tasks
the desktop app’s own servers (ccd_session, ccd_turn, ccd_pr, ccd_view, ccd_settings, ccd_sidebar, ccd_window, ccd_host, ccd_directory, ccd_connectors, ccd_session_mgmt)
2. score_posting with greenhouse:stripe / 7737124, exactly as returned:

{"filter": "FILTER.md v2", "verdict": "relevant", "conditions": {"C1": {"status": "pass", "reason": "the title contains a target title: Product Manager"}, "C2": {"status": "pass", "reason": "the location is workable: New York"}, "C3": {"status": "pass", "reason": "the text is present (FILTER v2's C3 asks only that); no persona skill found"}, "C4": {"status": "pass", "reason": "no seniority word in the title, and no stated minimum above 3 years in the text"}}, "score": 0, "missing": [], "claims": [{"claim": "The title names a target role: Product Manager.", "field": "title"}, {"claim": "The location is workable: New York.", "field": "location"}, {"claim": "The title has no seniority word.", "field": "title"}, {"claim": "The posting asks for no more than 3 years of experience.", "field": "text"}]}
3. score_posting with greenhouse:stripe / 0000000, exactly as returned. It came back as a tool error, not a JSON result:

no posting with this board key and id in the frozen corpus (FILTER.md §3)