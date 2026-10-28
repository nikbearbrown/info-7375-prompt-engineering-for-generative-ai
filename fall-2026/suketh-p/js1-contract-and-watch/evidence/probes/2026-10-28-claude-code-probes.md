# Claude Code probes, 2026-10-28

Two `claude -p` calls Claude Code made while choosing how the judge reaches Claude. Both ran in an empty scratch directory with Claude Code 2.1.291, before any judge code existed. Neither call contained a posting or the persona.

## Probe 1: can `claude -p` run with nothing turned on? (about 06:13 EDT)

```bash
printf 'Reply with exactly the word OK and nothing else.' | claude -p --tools "" \
  --system-prompt "You are a test endpoint." --setting-sources "" --strict-mcp-config \
  --disable-slash-commands --no-session-persistence --verbose --output-format stream-json
```

Recorded from the stream:

| Field | Value |
|---|---|
| tools | `[]` |
| mcp_servers | `[]` |
| slash_commands | `[]` |
| plugins | four built-in plugins only: `cc-plugin-sec-default`, `cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-plugin-authoring` |
| model | `claude-opus-5-5` |
| apiKeySource | `none` (the Claude Code login was used, not an API key) |
| result | `OK` |
| usage | `input_tokens` 2, `cache_creation_input_tokens` 826, `output_tokens` 4 |

**What this shows.** Our text was about 20 tokens (a 5-word system prompt and an 11-word message), yet the request carried about 828 input tokens. Claude Code adds context of its own that the agent does not write and cannot see. That conflicts with the CONTRACT.md refusal "Send anything to Claude beyond the fixed instructions, fictional résumé, and public posting" if the judge uses this route.

## Probe 2: what is that added context? (about 06:31 EDT)

Same flags plus `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, with a system prompt asking Claude to quote, verbatim, all text in its context before the user message.

**Result.** The request was declined before any output: `API Error: Opus 5's safeguards flagged this message`, details `[reasoning_extraction]`. Usage: `input_tokens` 4, `cache_creation_input_tokens` 1363, `output_tokens` 0.

**What this shows.** The added context could not be inspected this way, and Claude Code did not try another route. The decline also showed that `claude -p --output-format json` reports such a decline as an error result. `jobwatch/transports.py` turns that into a `JudgeError`, never a verdict.

**Not explained.** The input count rose from about 828 to 1,367 tokens while our own text grew by only about 50 tokens. The cause is unknown, and Claude Code did not investigate further.
