# Network

What the agent contacts, what it enforces, and what it cannot enforce (CONTRACT.md §11).

## The agent's own requests (enforced)

- **One host:** `boards-api.greenhouse.io`, from `[http].allowed_hosts` in `config/agent.toml`.
- **One request per run:** `GET https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`.
- **Enforcement** (`src/job_search_agent/http.py`, `AllowListTransport`): HTTPS only; every redirect target is re-checked against the allow-list (at most 3); a 30 s timeout and a 50 MB body cap. Links inside job descriptions are never requested.
- **Seeded runs** (`jsa run --replay FILE`) make no network request at all.
- **Tests:** `tests/test_http.py`, `test_pipeline_issues_exactly_one_request`, `test_links_in_content_never_requested`, `test_replay_makes_no_network_request`. The test harness blocks real sockets (`test_network_is_blocked`).

## The `claude` executable (documented, not enforced)

The model opinion comes from the subscription-authenticated `claude` CLI, started once per posting as a separate process. **The agent cannot enforce which hosts that process contacts.** It can only limit what the process is given.

Hosts the Claude Code documentation names for a headless subscription run (read 2026-10-29; sources and quotes in [`claude-code-network-facts.md`](claude-code-network-facts.md)):

| Host | Purpose (per the docs) |
|---|---|
| `api.anthropic.com` | Model requests (and, when WebFetch is used, its domain safety check) |
| `claude.ai` | Account authentication |
| `platform.claude.com` | OAuth token exchange and refresh |

Further hosts in the docs (`mcp-proxy.anthropic.com`, `downloads.claude.ai`, telemetry and error-report hosts) are switched off or not reached by how the judge is launched, below. This is what the docs say; the agent does not observe the child's traffic.

How the judge is launched (`src/job_search_agent/judge/backend.py`; PLAN amendments R1 and R9), as recorded in every call's raw log:

```text
claude -p --no-session-persistence --tools "" --disallowedTools "mcp__*" --strict-mcp-config \
  --setting-sources project --safe-mode --output-format json --model claude-sonnet-5-5
```

- Run from a fresh, empty working directory, `data/tmp/claude-<uuid>/`, removed afterwards.
- No tools, no MCP servers, no session saved. The posting and the projected résumé go in on stdin.
- The child's environment is built from an allowlist, plus `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and `ENABLE_CLAUDEAI_MCP_SERVERS=false`. API-key variables are never passed, and `--bare` (which needs an API key) is never used.
- If `claude` is missing or not signed in, the judgment is `UNAVAILABLE` and stays pending. The agent never falls back to an API key.

## Credentials

Subscription credentials stay inside Claude Code's own storage. The agent never reads them. Outputs are scanned for credential patterns (`jsa audit-privacy`), and stderr that matches one is withheld (`test_stderr_with_credential_pattern_withheld`).

## Action surface (c) only

The Chapter 3 surface (c) deliberately gave Claude `WebFetch` limited to `boards-api.greenhouse.io`. Per the docs, WebFetch also sends the hostname to `api.anthropic.com` for a safety check, and its fetches run inside the `claude` process, outside `AllowListTransport`. This is one reason surface (a) was chosen: [`experiments/ACTION_SURFACES.md`](experiments/ACTION_SURFACES.md).
