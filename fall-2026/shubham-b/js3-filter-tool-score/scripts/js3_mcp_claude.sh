#!/usr/bin/env bash
# Runs Claude Code headless as the MCP client of our tool server (JS3 step 2.3).
# The server writes the wire transcript, both directions, to data/js3/mcp/<name>.jsonl;
# Claude's final JSON reply goes to data/js3/mcp/<name>.claude.json.
# The config with absolute paths lives in data/tmp/ (gitignored), and Claude runs from an
# empty directory with no settings, no built-in tools and no session saved.
# Usage: scripts/js3_mcp_claude.sh <name> "<prompt>"
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
name="$1"; prompt="$2"
work="$root/data/tmp/mcp-$name"; mkdir -p "$work/empty"
[[ -e "$root/data/js3/mcp/$name.jsonl" ]] && { echo "data/js3/mcp/$name.jsonl exists" >&2; exit 2; }
cat > "$work/mcp.json" <<JSON
{"mcpServers": {"jsa": {"type": "stdio", "command": "$root/.venv/bin/python",
  "args": ["-m", "job_search_agent.js3", "serve", "--transcript", "data/js3/mcp/$name.jsonl"]}}}
JSON
cd "$work/empty"
claude -p "$prompt" --mcp-config "$work/mcp.json" --strict-mcp-config \
  --allowedTools "mcp__jsa__score_posting" --tools "" --setting-sources "" \
  --no-session-persistence --model claude-sonnet-5-5 --output-format json \
  < /dev/null > "$root/data/js3/mcp/$name.claude.json"
echo "wrote data/js3/mcp/$name.jsonl and data/js3/mcp/$name.claude.json"
