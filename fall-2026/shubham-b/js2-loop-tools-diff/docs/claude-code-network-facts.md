# Claude Code network & flag facts (docs read 2026-10-29 by a docs-research subagent; quotes via WebFetch)

Sources: https://code.claude.com/docs/en/network-config.md · data-usage.md · env-vars.md · cli-reference.md ·
permissions.md · headless.md · legal-and-compliance.md (all under https://code.claude.com/docs/en/)

## Hosts relevant to a headless subscription run
- api.anthropic.com: "Claude API requests, including the WebFetch domain safety check, feature flag fetches, and telemetry event logging"
- claude.ai: account authentication · platform.claude.com: "OAuth token exchange, refresh, and revocation"
- mcp-proxy.anthropic.com: claude.ai MCP connectors (on by default for claude.ai users; disable with ENABLE_CLAUDEAI_MCP_SERVERS=false)
- downloads.claude.ai: auto-updater/version checks · formulae.brew.sh: update checks on Homebrew installs
- http-intake.logs.us5.datadoghq.com / browser-intake-us5-datadoghq.com: telemetry/error reports (only when the CLI uses the Anthropic API directly; DISABLE_TELEMETRY / DISABLE_ERROR_REPORTING)
- Statsig/Sentry are not named in current docs.
- WebFetch domain check sends the hostname only to api.anthropic.com; NOT disabled by CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC (only skipWebFetchPreflight setting).

## Env vars
- CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1: disables auto-updates, telemetry, error reporting, /feedback, release notes, availability checks, feature-flag fetching.
- CLAUDE_CODE_DISABLE_CLAUDE_MDS=1: no CLAUDE.md/memory files loaded.
- ENABLE_CLAUDEAI_MCP_SERVERS=false: no claude.ai MCP connectors.

## Flags (documented)
- --no-session-persistence (print mode): sessions not saved/resumable.
- --tools "": disables all built-in tools (not MCP; add --disallowedTools "mcp__*").
- --strict-mcp-config with no --mcp-config: no MCP servers.
- --setting-sources accepts user,project,local; empty value NOT documented → use `project` from an EMPTY cwd
  (verified 2026-10-29: same 2,333-token context as the empty value).
- Without --bare, project .claude/settings.json hooks and .mcp.json still apply → hence the empty cwd.
- --bare never reads OAuth creds (needs ANTHROPIC_API_KEY) → not usable here.
- --output-format json: result, session_id, total_cost_usd, per-model usage; non-zero exit on failure.
- Permissions: WebFetch(domain:host) matches that hostname only; file rules use Edit(//abs/path/**) (Write(path) rules never
  match); --permission-mode dontAsk denies anything not pre-allowed; --add-dir grants file access to a dir.

## Recommended isolated judge call
cd <empty temp dir> && CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 ENABLE_CLAUDEAI_MCP_SERVERS=false \
  claude -p "<prompt>" --no-session-persistence --tools "" --disallowedTools "mcp__*" --strict-mcp-config \
  --setting-sources project --output-format json --model <model>

## Sandboxed agent (action-surface run c)
claude -p "<prompt>" --permission-mode dontAsk --tools "WebFetch,Read,Edit,Write" \
  --allowedTools "WebFetch(domain:boards-api.greenhouse.io)" "Edit(//abs/sandbox/**)" "Read(//abs/sandbox/**)" --add-dir /abs/sandbox
(from an empty cwd = the sandbox; plus the env vars above)

## Terms of use
Legal page: OAuth "is intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans and is
designed to support ordinary use of Claude Code". Products/services routing others' requests must use API keys. Personal, ordinary
use of `claude -p` by the subscriber is consistent with the docs; it is not explicitly called "supported programmatic use".
