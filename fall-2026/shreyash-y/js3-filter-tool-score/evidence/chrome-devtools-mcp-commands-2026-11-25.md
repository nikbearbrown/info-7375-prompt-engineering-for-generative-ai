# How chrome-devtools-mcp was run (2026-11-25)

*Written by Claude Code after the runs, from the commands it ran in the session. The independent review
noted that no committed record held them. The package is the copy already in the npx cache:
`~/.npm/_npx/ba38acecdf97096f/node_modules/chrome-devtools-mcp` (version 1.10.1, `package.json`). Node
24.22.2, Google Chrome 157.*

## Session 1: declared tools only (17:26:23 EST)

`transcripts/other-server/chrome-devtools-mcp-1.10.1-declared-2026-11-25.jsonl`

```bash
CDM=~/.npm/_npx/ba38acecdf97096f/node_modules/chrome-devtools-mcp
CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1 CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1 \
  python3 -m js3.mcp_client --out transcripts/other-server/chrome-devtools-mcp-1.10.1-declared-2026-11-25.jsonl \
  -- node $CDM/build/src/bin/chrome-devtools-mcp.js --isolated --headless --usageStatistics=false --performanceCrux=false
```

The calls were `initialize`, `notifications/initialized` and `tools/list`. The server's stderr, saved in
the transcript, confirms one setting: "turning off usage statistics. process.env['CI'] ||
process.env['CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS'] is set."

## Session 2: one public posting page (17:26:49–17:26:55 EST)

`transcripts/other-server/chrome-devtools-mcp-1.10.1-posting-check-2026-11-25.jsonl`, written by
`evidence/chrome-devtools-mcp-session2.py`, which is the script that ran, copied unchanged.

The command line and environment were the same as session 1, set inside the script. The calls were:

1. `list_pages`
2. `navigate_page` (`type: "url"`, the posting's own URL, `klaviyo:7792539003`)
3. `take_snapshot`
4. `list_network_requests` (`pageSize: 200`)

No `click`, `fill`, `fill_form`, `type_text`, `upload_file` or `evaluate_script` was sent.

`list_network_requests` answered "Showing 1-200 of 231 (Page 1 of 2)", and page 2 was not requested.
So the 51 distinct hosts are those in the first 200 of the page's 231 requests: **at least 51**.

## The allow-list

This page load was a deliberate exception to the agent's 3-host allow-list (GATE.md section 6). It was
made for the evaluation Shreyash asked for in FILTER.md answer 13 ("I also want to test
`chrome-devtools-mcp` to see if it is useful for checking job postings"). It ran once, with no
`--allowedUrlPattern`, in a temporary profile that was deleted afterwards. The agent itself never uses
this server.
