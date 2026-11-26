// The from-scratch MCP server (Phase 4): protocol behaviour, the read-only tool, the transcript,
// and the import graph (no judge, no process, no network). Postings come from the frozen snapshot.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync, readdirSync, rmSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { ROOT } from '../testlib/helpers.mjs';
import { loadCorpus } from '../src/corpus.mjs';

const SERVER = join(ROOT, 'mcp', 'server.mjs');

function session(lines, sub) {
  return new Promise((res, rej) => {
    const p = spawn(process.execPath, [SERVER], { env: { ...process.env, JS3_TRANSCRIPT_SUBDIR: sub }, stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '', err = '';
    p.stdout.on('data', d => { out += d; }); p.stderr.on('data', d => { err += d; });
    p.on('error', rej);
    p.on('close', code => res({ code, err, msgs: out.trim() ? out.trim().split('\n').map(l => JSON.parse(l)) : [] }));
    for (const l of lines) p.stdin.write((typeof l === 'string' ? l : JSON.stringify(l)) + '\n');
    p.stdin.end();
  });
}
const init = (v = '2025-06-18') => ({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: v, capabilities: {}, clientInfo: { name: 'node-test', version: '0' } } });
const call = (id, args, name = 'score_posting') => ({ jsonrpc: '2.0', id, method: 'tools/call', params: { name, arguments: args } });
const byId = (msgs, id) => msgs.find(m => m.id === id);

test('MCP server: handshake, tools/list, tools/call, errors, and a two-way transcript', async () => {
  const sub = `test-${process.pid}`;
  try {
    const { code, msgs } = await session([
      init(), { jsonrpc: '2.0', method: 'notifications/initialized' },
      { jsonrpc: '2.0', id: 2, method: 'tools/list' },
      call(3, { posting_id: 'gh-stripe:8186541' }),
      call(4, { posting_id: 'gh-stripe:000' }),
      call(5, { posting_id: 'gh-stripe:8186541', path: '/etc/passwd' }),
      call(6, { posting_id: 'gh-stripe:8186541' }, 'write_file'),
      { jsonrpc: '2.0', id: 7, method: 'resources/list' },
      '{not json',
      { jsonrpc: '2.0', id: 8, method: 'ping' },
    ], sub);
    assert.equal(code, 0);
    assert.equal(msgs.length, 9, 'one reply per request, none for the notification');
    const i = byId(msgs, 1).result;
    assert.equal(i.protocolVersion, '2025-06-18'); assert.deepEqual(i.capabilities, { tools: { listChanged: false } });
    const tools = byId(msgs, 2).result.tools;
    assert.equal(tools.length, 1); assert.equal(tools[0].name, 'score_posting'); assert.equal(tools[0].annotations.readOnlyHint, true);
    const ok = byId(msgs, 3).result;
    assert.equal(ok.isError, false); assert.equal(ok.structuredContent.decision, 'keep'); assert.equal(ok.structuredContent.spec_version, '1.1.0-e');
    const post = loadCorpus(ROOT).postings.find(p => p.board === 'gh-stripe' && p.id === '8186541');
    const wire = JSON.stringify(ok);
    assert.ok(!wire.includes(post.text.slice(0, 200)), 'no posting text returned');
    assert.ok(!/applyUrl|apply/i.test(Object.keys(ok.structuredContent).join(',')), 'no apply URL field');
    assert.equal(byId(msgs, 4).result.isError, true);
    assert.equal(byId(msgs, 5).result.isError, true, 'extra arguments are refused');
    assert.equal(byId(msgs, 6).error.code, -32602);
    assert.equal(byId(msgs, 7).error.code, -32601);
    assert.ok(msgs.some(m => m.id === null && m.error?.code === -32700));
    assert.deepEqual(byId(msgs, 8).result, {});
    const dir = join(ROOT, 'transcripts', sub);
    const files = readdirSync(dir); assert.equal(files.length, 1);
    const t = readFileSync(join(dir, files[0]), 'utf8').trim().split('\n').map(l => JSON.parse(l));
    assert.ok(t.every(e => e.at && ['meta', 'client->server', 'server->client'].includes(e.dir)));
    assert.equal(t.filter(e => e.dir === 'client->server').length, 10);
    assert.equal(t.filter(e => e.dir === 'server->client').length, 9);
  } finally { rmSync(join(ROOT, 'transcripts', sub), { recursive: true, force: true }); }
});

test('MCP server: an unsupported protocol version gets the server\'s latest; a bad transcript subdir is refused', async () => {
  const sub = `test-v-${process.pid}`;
  try {
    const { msgs } = await session([init('1999-01-01')], sub);
    assert.equal(byId(msgs, 1).result.protocolVersion, '2025-06-18');
  } finally { rmSync(join(ROOT, 'transcripts', sub), { recursive: true, force: true }); }
  const bad = await session([init()], '../escape');
  assert.notEqual(bad.code, 0); assert.match(bad.err, /plain lowercase name/);
  assert.ok(!existsSync(join(ROOT, 'escape')));
});

test('W12: the server\'s import graph has no judge, no child process, no network, and no write but its transcript', () => {
  const seen = new Set(), stack = [SERVER];
  while (stack.length) {
    const f = stack.pop(); if (seen.has(f)) continue; seen.add(f);
    const src = readFileSync(f, 'utf8');
    for (const m of src.matchAll(/from\s+'(\.[^']+)'/g)) stack.push(resolve(dirname(f), m[1]));
  }
  const files = [...seen];
  assert.ok(!files.some(f => f.endsWith('judge.mjs')), 'judge.mjs reachable');
  for (const f of files) {
    const src = readFileSync(f, 'utf8');
    assert.ok(!/child_process|node:net|node:https?|node:dgram|\bfetch\s*\(/.test(src), `${f} has a process or network path`);
    if (f !== SERVER) assert.ok(!/writeFile|appendFile|rmSync|unlink|rename/.test(src), `${f} writes files`);
  }
  const server = readFileSync(SERVER, 'utf8');
  assert.equal((server.match(/appendFileSync\(/g) ?? []).length, 1, 'one appendFileSync call: the transcript logger');
  assert.ok(!/writeFileSync|rmSync|unlink|rename/.test(server));
});

test('fixed finding (2026-11-25): the tool description admits the quoted veto sentence', async () => {
  const sub = `test-d-${process.pid}`;
  try {
    const { msgs } = await session([init(), { jsonrpc: '2.0', id: 2, method: 'tools/list' }, call(3, { posting_id: 'gh-airbnb:8299386' })], sub);
    const d = byId(msgs, 2).result.tools[0].description;
    assert.match(d, /veto sentence quoted from the posting/); assert.doesNotMatch(d, /no posting text returned/);
    const v = byId(msgs, 3).result.structuredContent.veto;
    assert.ok(v.quote.length <= 300 && v.quote.includes('No Visa/Relocation Support.'));
  } finally { rmSync(join(ROOT, 'transcripts', sub), { recursive: true, force: true }); }
});
