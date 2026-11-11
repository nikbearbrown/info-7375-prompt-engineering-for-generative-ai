// The loop (src/loop.mjs) against GATE.md: exits and exit codes, error policy, state
// preservation, the failure counter, the trace, and --replay (boundary rows 38-41 at
// the loop level, with real zero-network assertions). Every test runs in a temp project
// tree with a stubbed fetch; nothing here touches the network or the real out/.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, symlinkSync, readdirSync, statSync } from 'node:fs';
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
  // Check the permission bits, not a failed write: an administrator account can write a
  // read-only file, so a write attempt would pass or fail depending on who runs the test.
  for (const p of [b.state_before, b.state_after]) assert.equal(statSync(join(root, p)).mode & 0o222, 0, `${p} has no write bits`);
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

// ---- timeouts, on an injected clock: no test waits on a real timer -------------------

// A fake clock and timer. By default the stub fetch never answers; when it is called,
// the most recent timer "fires" on the next microtask, moving the clock forward by that
// timer's delay, so the policy's abort runs exactly as it would at the deadline.
// answers[i], if given, is the response to call i instead. At each call the stub also
// records the trace lines already on disk, to show events are written as they happen.
function hangingNetwork(startAt, laterAt = startAt, { root, answers = [] } = {}) {
  let reads = 0;
  let t = laterAt;
  const timers = [];
  const calls = [];
  const traceAtCall = [];
  const traceNow = () => {
    if (!root || !existsSync(join(root, 'out/traces'))) return [];
    const [file] = readdirSync(join(root, 'out/traces'));
    return readFileSync(join(root, 'out/traces', file), 'utf8').trim().split('\n').map(l => JSON.parse(l).event);
  };
  return {
    calls, timers, traceAtCall,
    now: () => (reads++ === 0 ? startAt : t), // the run starts at startAt; later reads see laterAt onward
    setTimer: (fn, ms) => { const h = { fn, ms }; timers.push(h); return h; },
    clearTimer: h => { h.cleared = true; },
    sleep: async ms => { t += ms; },
    fetchImpl: (url, init) => {
      calls.push(url);
      traceAtCall.push(traceNow());
      const a = answers[calls.length - 1];
      if (a) return Promise.resolve({ status: a.status, headers: new Headers(a.headers ?? {}), text: async () => a.body });
      return new Promise((_, reject) => {
        init.signal.addEventListener('abort', () => reject(new Error('aborted')));
        queueMicrotask(() => { const h = timers.at(-1); if (!h.cleared) { t += h.ms; h.fn(); } });
      });
    },
  };
}
const iso = ms => new Date(ms).toISOString();
const boardEvents = events => events.filter(e => !['run_start', 'config', 'failures_written', 'run_end'].includes(e.event));

test('timeout (injected clock): a hanging board times out at 15 s, retries once after 2 s, times out again: error: timeout, exit 10', async () => {
  const root = project([FOUR[0]]);
  const net = hangingNetwork(T);
  const started = performance.now();
  const r = await runLoop({ argv: ['--config', 'boards.json', '--label', 'timeout'], root, cwd: root, log: () => {}, ...net });
  assert.ok(performance.now() - started < 2000, 'no real 15 s wait');
  assert.deepEqual(net.timers.map(h => h.ms), [15_000, 15_000]);
  assert.equal(net.calls.length, 2, 'one counted retry, no more');
  const events = readFileSync(join(root, r.trace), 'utf8').trim().split('\n').map(l => JSON.parse(l));
  assert.deepEqual(events.filter(e => e.event === 'request').map(e => e.outcome), ['timeout', 'timeout']);
  assert.equal(events.find(e => e.event === 'retry').wait_ms, 2000);
  // Order and time: request 1 (sent at T) -> retry (at the 15 s timeout) -> request 2 (sent 2 s later).
  const seq = boardEvents(events);
  assert.deepEqual(seq.map(e => e.event), ['board_start', 'request', 'retry', 'request', 'board_result']);
  const [, req1, retry, req2] = seq;
  assert.equal(req1.at, iso(T));
  assert.equal(Date.parse(retry.at) - Date.parse(req1.at), 15_000, 'retry written when request 1 timed out, 15 s of injected time later');
  assert.equal(Date.parse(req2.at) - Date.parse(retry.at), 2_000, 'request 2 sent after the 2 s wait');
  assert.equal(req1.completed_at, iso(T + 15_000));
  assert.equal(req2.completed_at, iso(T + 32_000));
  assert.equal(board(r, 'gh-stripe').disposition, 'error: timeout');
  assert.equal(board(r, 'gh-stripe').raw_count, null);
  assert.ok(!existsSync(join(root, 'out/state/gh-stripe.json')));
  assert.equal(r.exitCode, 10);
});

test('timeout (injected clock): begun with 3 s left, the request is aborted at the deadline and not retried: exit 11', async () => {
  const root = project([FOUR[0]]);
  const net = hangingNetwork(T, T + 57_000);
  const started = performance.now();
  const r = await runLoop({ argv: ['--config', 'boards.json', '--label', 'deadline'], root, cwd: root, log: () => {}, ...net });
  assert.ok(performance.now() - started < 2000, 'no real wait');
  assert.deepEqual(net.timers.map(h => h.ms), [3000], 'min(15 s, remaining)');
  assert.equal(net.calls.length, 1, 'no overrun-inducing second action');
  const seq = boardEvents(readFileSync(join(root, r.trace), 'utf8').trim().split('\n').map(l => JSON.parse(l)));
  assert.deepEqual(seq.map(e => e.event), ['board_start', 'request', 'no_retry', 'board_result']);
  assert.equal(seq[1].at, iso(T + 57_000));
  assert.equal(seq[1].completed_at, iso(T + 60_000));
  assert.equal(seq[2].at, iso(T + 60_000), 'the no-retry decision is recorded at the deadline');
  assert.equal(board(r, 'gh-stripe').disposition, 'error: timeout');
  assert.equal(r.status, 'budget-exhausted');
  assert.equal(r.exitCode, 11);
});

test('timeout then 200 (the shape of the pre-fix baseline): events are appended as they happen, in order', async () => {
  const root = project(LV_ONLY);
  const net = hangingNetwork(T, T, { root, answers: [undefined, { status: 200, body: lv(UUIDS) }] });
  const r = await runLoop({ argv: ['--config', 'boards.json', '--label', 'timeout-then-ok'], root, cwd: root, log: () => {}, ...net });
  assert.equal(net.calls.length, 2);
  // When request 2 is sent, request 1 and the retry are already on disk: not buffered.
  assert.deepEqual(net.traceAtCall[1].slice(-3), ['board_start', 'request', 'retry']);
  const events = readFileSync(join(root, r.trace), 'utf8').trim().split('\n').map(l => JSON.parse(l));
  const seq = boardEvents(events);
  assert.deepEqual(seq.map(e => [e.event, e.outcome ?? null]), [['board_start', null], ['request', 'timeout'], ['retry', null], ['request', 'ok'], ['board_result', null]]);
  const [, req1, retry, req2] = seq;
  assert.equal(Date.parse(retry.at) - Date.parse(req1.at), 15_000);
  assert.equal(Date.parse(req2.at) - Date.parse(retry.at), 2_000);
  const ats = events.map(e => Date.parse(e.at));
  assert.deepEqual(ats, [...ats].sort((a, b) => a - b), 'trace times never go backwards');
  assert.equal(req1.raw_path, null, 'a timed-out attempt has no body');
  assert.equal(req2.raw_path, `out/raw/${r.run}/lv-spotify.attempt2.json`);
  assert.equal(board(r, 'lv-spotify').raw_path, req2.raw_path);
  assert.equal(r.exitCode, 0);
});

// ---- a replay is not an attempted run: out/failures.json is left alone -------------

test('replay leaves an existing out/failures.json byte for byte', async () => {
  const root = replayProject();
  const before = `${JSON.stringify({ 'lv-spotify': { consecutive: 1, last_error: 'error: timeout', last_run: 'earlier', escalate: false } }, null, 2)}\n`;
  writeFileSync(join(root, 'out/failures.json'), before);
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/lv-spotify.json'], noNetwork());
  assert.equal(r.exitCode, 0);
  assert.equal(readFileSync(join(root, 'out/failures.json'), 'utf8'), before);
  assert.equal(r.ev('failures_written').length, 0);
  assert.equal(r.ev('failures_unchanged')[0].reason, 'replay is not an attempted run');
});

test('replay does not create out/failures.json', async () => {
  const root = replayProject();
  const r = await run(root, ['--config', 'boards.json', '--label', 'replay', '--replay', 'out/raw/lv-spotify.json'], noNetwork());
  assert.equal(r.exitCode, 0);
  assert.ok(!existsSync(join(root, 'out/failures.json')));
});

// ---- a state write that fails ends the run as error, exit 12, never a crash ---------

test('a raw Lever response with a null id: saveState refuses it, the run ends error, exit 12, run_end written', async () => {
  const root = project(LV_ONLY);
  const f = router({ spotify: res(200, JSON.stringify([{ id: UUIDS[0], text: 'Job' }, { id: null, text: 'Job' }])) });
  let r;
  await assert.doesNotReject(async () => { r = await run(root, ['--config', 'boards.json', '--label', 'null-id'], f); }, 'runLoop must not throw');
  assert.equal(r.status, 'error');
  assert.equal(r.exitCode, 12);
  assert.match(r.reason, /STATE_INTEGRITY/);
  assert.equal(r.events.at(-1).event, 'run_end');
  assert.equal(r.events.at(-1).exit_code, 12);
  assert.ok(!existsSync(join(root, 'out/state/lv-spotify.json')), 'no state written');
  assert.deepEqual(readdirSync(join(root, 'out/state')), [], 'no temp file left behind');
  assert.ok(existsSync(join(root, r.ev('request')[0].raw_path)), 'the raw body is still saved as evidence');
});

// ---- duplicate ids in one raw response fail that board, not the run -----------------

test('a raw Greenhouse response with a duplicate id: board error: malformed, no state, run incomplete (exit 10)', async () => {
  const root = project([FOUR[0], FOUR[1]]);
  const f = router({ stripe: res(200, gh([101, 101])), airbnb: res(200, gh([10])) });
  const r = await run(root, ['--config', 'boards.json', '--label', 'dup-id'], f);
  assert.match(board(r, 'gh-stripe').disposition, /^error: malformed \(duplicate id 101\)$/);
  assert.equal(board(r, 'gh-stripe').new_count, null);
  assert.ok(!existsSync(join(root, 'out/state/gh-stripe.json')), 'no state update for the malformed board');
  assert.equal(board(r, 'gh-airbnb').disposition, 'observed', 'the other board is still observed');
  assert.equal(r.status, 'incomplete');
  assert.equal(r.exitCode, 10);
});
