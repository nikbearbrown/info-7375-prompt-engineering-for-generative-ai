#!/usr/bin/env node
// js3-filter MCP server, written from scratch (no MCP SDK): JSON-RPC 2.0 over stdio, one JSON
// message per line. Methods: initialize, notifications/initialized, ping, tools/list, tools/call.
//
// One tool, READ-ONLY: score_posting. It scores one posting from the frozen 2026-11-10 snapshot
// (data/MANIFEST.json) with the final filter (FILTER.md v1.1.0-e) and returns the decision, the
// score, the components, and any veto quote.
//
// What it does NOT do: no network, no Claude call, no child process (it never imports
// src/judge.mjs); it never returns posting text, apply URLs, or the audit/label files. The only
// thing it writes is its own transcript: every message in both directions, timestamped, to
// transcripts/<start>-<pid>.jsonl inside this folder (checked by real path).
import { readFileSync, appendFileSync, mkdirSync, realpathSync } from 'node:fs';
import { join, dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';
import { loadFilterSpec } from '../src/spec.mjs';
import { scorePosting } from '../src/filter.mjs';
import { loadCorpus } from '../src/corpus.mjs';
import { boilerplateLines } from '../src/boilerplate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const SUPPORTED_PROTOCOLS = ['2025-06-18', '2025-03-26', '2024-11-05'];
const SERVER_INFO = { name: 'js3-filter', version: '1.1.0-e' };

// ---------- transcript (the only write) ----------
// JS3_TRANSCRIPT_SUBDIR (tests only) picks a subfolder of transcripts/; it must be a plain name.
const SUB = process.env.JS3_TRANSCRIPT_SUBDIR ?? '';
if (SUB && !/^[a-z0-9-]{1,40}$/.test(SUB)) throw new Error('JS3_TRANSCRIPT_SUBDIR must be a plain lowercase name');
const TDIR = join(ROOT, 'transcripts', SUB);
mkdirSync(TDIR, { recursive: true });
if (!realpathSync(TDIR).startsWith(realpathSync(ROOT) + sep)) throw new Error('transcripts/ resolves outside the js3 folder; refusing to write');
const TFILE = join(TDIR, `${new Date().toISOString().replace(/[:.]/g, '')}-${process.pid}.jsonl`);
const log = (dir, raw) => appendFileSync(TFILE, JSON.stringify({ at: new Date().toISOString(), dir, raw }) + '\n');
log('meta', JSON.stringify({ event: 'start', server: SERVER_INFO, node: process.version, pid: process.pid, argv: process.argv.slice(2) }));

// ---------- data, loaded once ----------
const spec = loadFilterSpec(join(ROOT, 'FILTER.md'));
const prefs = JSON.parse(readFileSync(join(ROOT, 'persona', 'persona-prefs.json'), 'utf8'));
const corpus = loadCorpus(ROOT);
const shared = spec.topic.exclude_shared_lines_min_share != null ? boilerplateLines(corpus.postings, spec.topic.exclude_shared_lines_min_share) : null;
const byId = new Map(corpus.postings.map(p => [`${p.board}:${p.id}`, p]));
const boards = corpus.boards.map(b => b.board);

const TOOL = {
  name: 'score_posting',
  title: 'Score a posting (read-only)',
  description: `Score ONE job posting from the frozen 2026-11-10 snapshot (${corpus.postings.length} postings; boards ${boards.join(', ')}) with filter v${spec.version} for the fictional persona Maya Sehgal. Returns keep / reject / cannot_tell, the score, its components, and a quoted veto if any. Read-only: no network, no writes, no posting text returned.`,
  inputSchema: {
    type: 'object',
    properties: { posting_id: { type: 'string', description: 'board:id, e.g. "gh-stripe:8186541"', pattern: '^[a-z0-9-]+:[A-Za-z0-9-]+$' } },
    required: ['posting_id'],
    additionalProperties: false,
  },
  annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
};

function scoreTool(args) {
  const keys = Object.keys(args ?? {});
  if (keys.some(k => k !== 'posting_id') || typeof args?.posting_id !== 'string' || !TOOL.inputSchema.properties.posting_id.pattern || !new RegExp(TOOL.inputSchema.properties.posting_id.pattern).test(args.posting_id))
    return { isError: true, text: `invalid arguments: expected exactly {"posting_id": "board:id"}; got ${JSON.stringify(args ?? null).slice(0, 200)}` };
  const p = byId.get(args.posting_id);
  if (!p) return { isError: true, text: `unknown posting_id ${args.posting_id}: not in the frozen snapshot (boards: ${boards.join(', ')})` };
  const r = scorePosting(p, { spec, prefs, shared });
  const out = { posting_id: args.posting_id, title: p.title, location: p.location, url: p.url, spec_version: r.spec_version,
    decision: r.decision, reason: r.reason, score: r.score, lo: r.lo, hi: r.hi, threshold: spec.threshold, veto: r.veto, unknown: r.unknown,
    components: r.components && { title: r.components.title, topic: r.components.topic, location: r.components.location,
      experience: { value: r.components.experience.value, case: r.components.experience.case, phrase: r.components.experience.phrase, lower_bound: r.components.experience.lower_bound } },
    label: 'RECORD: deterministic filter output; recompute with tools/run-filter.mjs' };
  return { isError: false, text: JSON.stringify(out, null, 1), structured: out };
}

// ---------- JSON-RPC ----------
const ERR = { PARSE: -32700, INVALID_REQUEST: -32600, METHOD_NOT_FOUND: -32601, INVALID_PARAMS: -32602 };
let initialized = false;
function send(msg) { const raw = JSON.stringify(msg); log('server->client', raw); process.stdout.write(raw + '\n'); }
const reply = (id, result) => send({ jsonrpc: '2.0', id, result });
const fail = (id, code, message) => send({ jsonrpc: '2.0', id: id ?? null, error: { code, message } });

export function negotiate(requested) { return SUPPORTED_PROTOCOLS.includes(requested) ? requested : SUPPORTED_PROTOCOLS[0]; }

function handle(msg) {
  if (!msg || typeof msg !== 'object' || Array.isArray(msg) || msg.jsonrpc !== '2.0' || typeof msg.method !== 'string') {
    if (msg && typeof msg === 'object' && !Array.isArray(msg) && ('result' in msg || 'error' in msg)) return; // a response to us: we send no requests, so ignore
    return fail(msg?.id, ERR.INVALID_REQUEST, 'invalid JSON-RPC 2.0 request');
  }
  const isNotification = !('id' in msg);
  if (isNotification) { if (msg.method === 'notifications/initialized') initialized = true; return; } // never answer a notification
  const { id, method, params } = msg;
  switch (method) {
    case 'initialize':
      return reply(id, { protocolVersion: negotiate(params?.protocolVersion), capabilities: { tools: { listChanged: false } }, serverInfo: SERVER_INFO,
        instructions: 'Read-only scorer for a frozen job-posting snapshot. One tool: score_posting. No network, no writes except this server\'s own transcript.' });
    case 'ping': return reply(id, {});
    case 'tools/list': return reply(id, { tools: [TOOL] });
    case 'tools/call': {
      if (params?.name !== TOOL.name) return fail(id, ERR.INVALID_PARAMS, `unknown tool: ${params?.name}`);
      const r = scoreTool(params.arguments);
      return reply(id, { content: [{ type: 'text', text: r.text }], ...(r.structured ? { structuredContent: r.structured } : {}), isError: r.isError });
    }
    default: return fail(id, ERR.METHOD_NOT_FOUND, `method not found: ${method}`);
  }
}

const rl = createInterface({ input: process.stdin });
rl.on('line', line => {
  log('client->server', line);
  if (!line.trim()) return;
  let msg;
  try { msg = JSON.parse(line); } catch { return fail(null, ERR.PARSE, 'parse error'); }
  try { handle(msg); } catch (e) { fail(msg?.id, -32603, `internal error: ${e.message}`); }
});
rl.on('close', () => { log('meta', JSON.stringify({ event: 'stdin closed', initialized })); process.exit(0); });
