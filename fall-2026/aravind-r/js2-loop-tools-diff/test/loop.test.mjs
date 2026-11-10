// The loop (src/loop.mjs) against GATE.md: exits and exit codes, error policy, state
// preservation, the failure counter, the trace, and --replay (boundary rows 38-41 at
// the loop level, with real zero-network assertions). Every test runs in a temp project
// tree with a stubbed fetch; nothing here touches the network or the real out/.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, symlinkSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { runLoop } from '../src/loop.mjs';

const T = Date.parse('2026-11-10T22:00:00Z');
const FOUR = [
  { id: 'gh-stripe', system: 'greenhouse', token: 'stripe' },
  { id: 'gh-airbnb', system: 'greenhouse', token: 'airbnb' },
  { id: 'lv-spotify', system: 'lever', token: 'spotify' },
  { id: 'gh-broken', system: 'greenhouse', token: 'no-such-board-js2' },
];
const LV_ONLY = [FOUR[2]];
const UUIDS = ['2a55d6c9-c564-443a-be3e-a3851db5a93b', '7d1c1e0e-1111-4c2a-9a55-0f0e5a7b9c01', 'b3f0a7d2-2222-4e3b-8f66-1a2b3c4d5e6f'];

const gh = ids => JSON.stringify({ jobs: ids.map(id => ({ id, title: `Job ${id}`, location: { name: 'NYC' }, absolute_url: `https://example.test/${id}` })) });
const lv = ids => JSON.stringify(ids.map(id => ({ id, text: `Job ${id}`, categories: { location: 'NYC' }, hostedUrl: `https://example.test/${id}`, applyUrl: `https://jobs.lever.co/spotify/${id}/apply` })));
const res = (status, body = '', headers = {}) => ({ status, body, headers });
const NOT_FOUND = res(404, '{"status":404,"error":"Job not found"}');

function project(boards) {
  const root = mkdtempSync(join(tmpdir(), 'js2-loop-'));
  writeFileSync(join(root, 'boards.json'), JSON.stringify(boards));
  return root;
}

// Stubbed fetch keyed by board token; a list is served in order. Records every call.
function router(byToken) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    const token = /\/boards\/([^/]+)\/jobs|\/postings\/([^/?]+)/.exec(url).slice(1).find(Boolean);
    const list = [].concat(byToken[token]);
    const r = list[Math.min(calls.filter(c => c.url === url).length - 1, list.length - 1)];
    if (!r) throw new Error(`no stub for ${url}`);
    return { status: r.status, headers: new Headers(r.headers), text: async () => r.body };
  };
  fn.calls = calls;
  return fn;
}
const noNetwork = () => { const f = router({}); return f; };

async function run(root, argv, fetchImpl, now = () => T) {
  const lines = [];
  const r = await runLoop({ argv, root, cwd: root, fetchImpl, now, sleep: async () => {}, log: l => lines.push(l) });
  const events = readFileSync(join(root, r.trace), 'utf8').trim().split('\n').map(l => JSON.parse(l));
  return { ...r, lines, events, ev: name => events.filter(e => e.event === name) };
}
const board = (r, id) => r.boards.find(b => b.board === id);
const json = (root, p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
// GATE.md: ids compare as exact strings. Pre-patch state.mjs stores Greenhouse ids as
// numbers and the patch stores decimal strings, so these tests hold under both.
const strs = ids => ids.map(String);
const normal = () => router({ stripe: res(200, gh([1, 2])), airbnb: res(200, gh([10])), spotify: res(200, lv(UUIDS)), 'no-such-board-js2': NOT_FOUND });

test('normal four-board run: three observed, the 404 recorded as an error (not 0 jobs), run incomplete, exit 10', async () => {
  const root = project(FOUR);
  const f = normal();
  const r = await run(root, ['--config', 'boards.json', '--label', 'normal'], f);
  assert.equal(r.status, 'incomplete');
  assert.equal(r.exitCode, 10);
  assert.equal(f.calls.length, 4, 'one request per board; the 404 is not retried');
  assert.ok(f.calls.every(c => c.init.redirect === 'manual' && c.init.method === 'GET'));
  const broken = board(r, 'gh-broken');
  assert.equal(broken.disposition, 'error: not found');
  assert.equal(broken.raw_count, null);
  assert.equal(broken.new_count, null);
  assert.equal(broken.state_updated, false);
  assert.ok(!existsSync(join(root, 'out/state/gh-broken.json')), 'a failed board writes no state');
  assert.ok(!r.lines.some(l => /gh-broken.*0 (jobs|new)/.test(l)));
  assert.equal(board(r, 'gh-stripe').disposition, 'observed');
  assert.deepEqual(strs(board(r, 'gh-stripe').new_ids), ['1', '2'], 'first run: every id is new (S_before is empty)');
  assert.equal(board(r, 'lv-spotify').new_count, 3);
  assert.equal(r.ev('request').length, 4);
  for (const q of r.ev('request')) assert.ok(existsSync(join(root, q.raw_path)), `raw body saved: ${q.raw_path}`);
  assert.equal(readFileSync(join(root, r.ev('request')[3].raw_path), 'utf8'), NOT_FOUND.body, 'the error body is saved too');
  assert.deepEqual(r.ev('run_end')[0].exit_code, 10);
  assert.equal(r.events[0].event, 'run_start');
  assert.equal(r.events[0].mode, 'live');
  assert.equal(json(root, 'out/failures.json')['gh-broken'].consecutive, 1);
  assert.equal(json(root, 'out/failures.json')['gh-broken'].escalate, false);
});

test('second consecutive failing run escalates gh-broken; successes reset to zero; Greenhouse ids unchanged', async () => {
  const root = project(FOUR);
  await run(root, ['--config', 'boards.json', '--label', 'first'], normal());
  const r = await run(root, ['--config', 'boards.json', '--label', 'second'], normal());
  assert.equal(board(r, 'gh-broken').escalate, true);
  assert.deepEqual(json(root, 'out/failures.json')['gh-broken'], { consecutive: 2, last_error: 'error: not found', last_run: r.run, escalate: true });
  assert.equal(json(root, 'out/failures.json')['gh-stripe'].consecutive, 0);
  assert.equal(board(r, 'gh-stripe').disposition, 'unchanged (no new IDs)');
  assert.equal(board(r, 'gh-stripe').new_count, 0);
  assert.equal(readdirSync(join(root, 'out/traces')).length, 2, 'one trace per run: run ids differ even with a frozen clock');
});

test('--max-requests 2: budget-exhausted, exit 11, two requests, unattempted boards listed', async () => {
  const root = project(FOUR);
  const f = normal();
  const r = await run(root, ['--config', 'boards.json', '--label', 'budget2', '--max-requests', '2'], f);
  assert.equal(r.status, 'budget-exhausted');
  assert.equal(r.exitCode, 11);
  assert.equal(f.calls.length, 2);
  assert.deepEqual(r.unattempted, [{ board: 'lv-spotify', budget: 'requests' }, { board: 'gh-broken', budget: 'requests' }]);
  assert.equal(json(root, 'out/failures.json')['lv-spotify'], undefined, 'a board the budget skipped is neither a success nor a failure');
});

test('--max-requests 20 is rejected before networking: error, exit 12, zero requests, trace says why', async () => {
  const root = project(FOUR);
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'budget20', '--max-requests', '20'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  assert.match(r.ev('run_end')[0].reason, /exceeds the hard maximum 8/);
});

test('--judge claude is rejected before any subprocess or network action: exit 12', async () => {
  const root = project(FOUR);
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'judge', '--judge', 'claude'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  assert.match(r.reason, /--judge none only/);
});

test('empty list, no prior state: empty (unverified), no state written, exit 10', async () => {
  const root = project(LV_ONLY);
  const r = await run(root, ['--config', 'boards.json', '--label', 'empty'], router({ spotify: res(200, '[]') }));
  assert.equal(board(r, 'lv-spotify').disposition, 'empty (unverified)');
  assert.equal(r.exitCode, 10);
  assert.ok(!existsSync(join(root, 'out/state/lv-spotify.json')));
});

test('empty list with prior seen ids: suspect: empty, state bytes unchanged, exit 10', async () => {
  const root = project([FOUR[0]]);
  await run(root, ['--config', 'boards.json', '--label', 'seed'], router({ stripe: res(200, gh([1, 2])) }));
  const before = readFileSync(join(root, 'out/state/gh-stripe.json'), 'utf8');
  const r = await run(root, ['--config', 'boards.json', '--label', 'empty'], router({ stripe: res(200, '{"jobs":[]}') }));
  assert.equal(board(r, 'gh-stripe').disposition, 'suspect: empty');
  assert.equal(r.exitCode, 10);
  assert.equal(readFileSync(join(root, 'out/state/gh-stripe.json'), 'utf8'), before);
});

test('malformed body: error: malformed, no retry, no state, raw body still saved', async () => {
  const root = project([FOUR[0]]);
  const f = router({ stripe: res(200, '<html>maintenance</html>') });
  const r = await run(root, ['--config', 'boards.json', '--label', 'malformed'], f);
  assert.match(board(r, 'gh-stripe').disposition, /^error: malformed/);
  assert.equal(f.calls.length, 1);
  assert.ok(!existsSync(join(root, 'out/state/gh-stripe.json')));
  assert.equal(readFileSync(join(root, board(r, 'gh-stripe').raw_path), 'utf8'), '<html>maintenance</html>');
});

test('HTTP 503 then 200: one counted retry after 2 s, then observed', async () => {
  const root = project([FOUR[0]]);
  const f = router({ stripe: [res(503, 'busy'), res(200, gh([1]))] });
  const r = await run(root, ['--config', 'boards.json', '--label', 'retry'], f);
  assert.equal(f.calls.length, 2);
  assert.equal(r.ev('retry')[0].wait_ms, 2000);
  assert.equal(board(r, 'gh-stripe').disposition, 'observed');
  assert.equal(r.exitCode, 0);
});

test('pre-run and post-run state snapshots are saved read-only for the checker', async () => {
  const root = project([FOUR[0]]);
  await run(root, ['--config', 'boards.json', '--label', 'a'], router({ stripe: res(200, gh([1])) }));
  const r = await run(root, ['--config', 'boards.json', '--label', 'b'], router({ stripe: res(200, gh([1, 2])) }));
  const b = board(r, 'gh-stripe');
  assert.deepEqual(strs(json(root, b.state_before).ids), ['1']);
  assert.deepEqual(strs(json(root, b.state_after).ids), ['1', '2']);
  assert.deepEqual(strs(b.new_ids), ['2']);
  assert.throws(() => writeFileSync(join(root, b.state_before), 'x'), /EACCES|EPERM/);
});

// ---- boundary rows 38-41 at the loop level: real zero-network assertions ----------

function replayProject() {
  const root = project(LV_ONLY);
  mkdirSync(join(root, 'out/raw'), { recursive: true });
  mkdirSync(join(root, 'out/state'), { recursive: true });
  writeFileSync(join(root, 'out/raw/lv-spotify.json'), lv(UUIDS));
  return root;
}

test('row 38 (loop): --replay out/raw/lv-spotify.json makes zero requests and is labeled mode: replay', async () => {
  const root = replayProject();
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/lv-spotify.json'], f);
  assert.equal(f.calls.length, 0, 'zero fetch calls');
  assert.equal(r.requests, 0);
  assert.equal(r.events[0].mode, 'replay');
  assert.equal(r.ev('replay_read')[0].network_requests, 0);
  assert.equal(r.ev('request').length, 0);
  assert.equal(board(r, 'lv-spotify').raw_path, 'out/raw/lv-spotify.json');
  assert.ok(r.lines.at(-1).includes('[mode: replay]'));
  assert.equal(r.exitCode, 0);
});

test('row 39 (loop): --replay out/raw/../state/lv-spotify.json: error, exit 12, zero requests', async () => {
  const root = replayProject();
  writeFileSync(join(root, 'out/state/lv-spotify.json'), lv(UUIDS));
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/../state/lv-spotify.json'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  assert.match(r.reason, /not under out\/raw/);
});

test('row 40 (loop): --replay of a symlink escaping out/raw/: error, exit 12, zero requests', async () => {
  const root = replayProject();
  const outside = mkdtempSync(join(tmpdir(), 'js2-loop-outside-'));
  writeFileSync(join(outside, 'secret.json'), lv(UUIDS));
  symlinkSync(join(outside, 'secret.json'), join(root, 'out/raw/escape.json'));
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/escape.json'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  assert.match(r.reason, /not under out\/raw/);
});

test('row 41 (loop): --replay of a missing file: error, exit 12, no fallback request', async () => {
  const root = replayProject();
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/missing.json'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0, 'no fallback to a live fetch');
  assert.match(r.reason, /replay file missing/);
});

test('--replay with a multi-board config is an error before any action', async () => {
  const root = replayProject();
  writeFileSync(join(root, 'boards.json'), JSON.stringify(FOUR));
  const f = noNetwork();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/lv-spotify.json'], f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  assert.match(r.reason, /single-board config/);
});
