// The ONLY module that starts a process (FILTER.md §4, W12): one tool-less `claude -p` call.
// Fresh empty temp folder as cwd; no built-in tools (--tools ""); no MCP servers
// (--strict-mcp-config with no --mcp-config); no session saved (--no-session-persistence).
// Not imported by the filter, the normalizer, the evidence checker, or the MCP server.
import { spawnSync } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const CLAUDE_ARGS = ['--tools', '', '--strict-mcp-config', '--no-session-persistence', '--output-format', 'json'];

export function callClaude(prompt, { model, runner = spawnSync } = {}) {
  const cwd = mkdtempSync(join(tmpdir(), 'js3-justify-'));
  const args = ['-p', prompt, ...CLAUDE_ARGS, ...(model ? ['--model', model] : [])];
  const at = new Date().toISOString();
  const r = runner('claude', args, { cwd, encoding: 'utf8', maxBuffer: 1 << 24, timeout: 300000 });
  let envelope = null;
  try { envelope = JSON.parse(r.stdout); } catch { /* recorded below */ }
  return {
    at, cwd, args_without_prompt: args.slice(2), exit_code: r.status,
    error: envelope ? (envelope.is_error ? String(envelope.result) : null) : `could not parse claude output: ${String(r.stderr || r.stdout || r.error || '').slice(0, 300)}`,
    text: envelope && !envelope.is_error ? envelope.result : null,
    models: envelope?.modelUsage ? Object.keys(envelope.modelUsage) : [],
    session_id: envelope?.session_id ?? null,
    envelope,
  };
}
