// GATE.md "Wrong implementations the tests must reject", at the loop level, for the
// ones test/policy.test.mjs does not already cover by itself. Wrong version 10 (Lever
// UUIDs cast to Number) is deliberately absent: its regression test is Aravind's, written
// before the src/state.mjs patch.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runLoop } from '../src/loop.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const T = Date.parse('2026-11-10T22:00:00Z');
const B = {
  stripe: { id: 'gh-stripe', system: 'greenhouse', token: 'stripe' },
  airbnb: { id: 'gh-airbnb', system: 'greenhouse', token: 'airbnb' },
  spotify: { id: 'lv-spotify', system: 'lever', token: 'spotify' },
  broken: { id: 'gh-broken', system: 'greenhouse', token: 'no-such-board-js2' },
};
const FOUR = [B.stripe, B.airbnb, B.spotify, B.broken];
const gh = ids => JSON.stringify({ jobs: ids.map(id => ({ id, title: 'Job' })) });
const lv = ids => JSON.stringify(ids.map(id => ({ id, text: 'Job' })));
const res = (status, body = '', headers = {}) => ({ status, body, headers });
const GOOD = { stripe: res(200, gh([1, 2])), airbnb: res(200, gh([10])), spotify: res(200, lv(['2a55d6c9-c564-443a-be3e-a3851db5a93b'])), 'no-such-board-js2': res(404, '{}') };

function project(boards) {
  const root = mkdtempSync(join(tmpdir(), 'js2-wv-'));
  writeFileSync(join(root, 'boards.json'), JSON.stringify(boards));
  return root;
}
function router(byToken) {
  const calls = [];
  const fn = async url => {
    calls.push(url);
    const token = /\/boards\/([^/]+)\/jobs|\/postings\/([^/?]+)/.exec(url).slice(1).find(Boolean);
    const list = [].concat(byToken[token]);
    const r = list[Math.min(calls.filter(u => u === url).length - 1, list.length - 1)];
    return { status: r.status, headers: new Headers(r.headers), text: async () => r.body };
  };
  fn.calls = calls;
  return fn;
}
async function run(root, argv, fetchImpl, extra = {}) {
  const r = await runLoop({ argv, root, cwd: root, fetchImpl, now: () => T, sleep: async () => {}, log: () => {}, ...extra });
  const events = readFileSync(join(root, r.trace), 'utf8').trim().split('\n').map(l => JSON.parse(l));
  return { ...r, events };
}
const args = (...more) => ['--config', 'boards.json', '--label', 'wv', ...more];

test('WV7: a 404 is never retried, and a failing 5xx is retried exactly once', async () => {
  const f404 = router(GOOD);
  await run(project([B.broken]), args(), f404);
  assert.equal(f404.calls.length, 1);
  const f503 = router({ stripe: res(503, 'down') });
  const r = await run(project([B.stripe]), args(), f503);
  assert.equal(f503.calls.length, 2, 'one first attempt + one counted retry, no more');
  assert.equal(r.boards[0].disposition, 'error: http 503');
});

test('WV8: the request budget is checked before each request: --max-requests N sends at most N', async () => {
  for (const n of [1, 2, 3]) {
    const f = router(GOOD);
    const r = await run(project(FOUR), args('--max-requests', String(n)), f);
    assert.equal(f.calls.length, n, `--max-requests ${n}`);
    assert.equal(r.exitCode, 11);
    assert.equal(r.unattempted.length, 4 - n);
  }
  // A retry counts against the same budget: 503 then 200 on the first board uses both.
  const f = router({ ...GOOD, stripe: [res(503, 'down'), res(200, gh([1]))] });
  const r = await run(project(FOUR), args('--max-requests', '2'), f);
  assert.equal(f.calls.length, 2);
  assert.deepEqual(r.unattempted.map(u => u.board), ['gh-airbnb', 'lv-spotify', 'gh-broken']);
});

test('WV8: a retry the request budget cannot fit is not sent; the run is budget-exhausted', async () => {
  const f = router({ stripe: res(503, 'down') });
  const r = await run(project([B.stripe]), args('--max-requests', '1'), f);
  assert.equal(f.calls.length, 1);
  assert.equal(r.status, 'budget-exhausted');
  assert.equal(r.boards[0].disposition, 'error: http 503', 'the board is still recorded as failed, not as 0 jobs');
});

test('WV9: the run with the deliberately broken board is never finished; the controlled three-board run is', async () => {
  const r = await run(project(FOUR), args(), router(GOOD));
  assert.equal(r.status, 'incomplete');
  assert.equal(r.exitCode, 10);
  const ok = await run(project([B.stripe, B.airbnb, B.spotify]), args(), router(GOOD));
  assert.equal(ok.status, 'finished');
  assert.equal(ok.exitCode, 0);
  assert.equal(ok.events.find(e => e.event === 'config').config, 'boards.json', 'the trace names the config used');
});

test('WV11: a duplicate configured board is fetched once and logged skipped: duplicate', async () => {
  const f = router(GOOD);
  const r = await run(project([B.stripe, { id: 'gh-stripe-again', system: 'greenhouse', token: 'stripe' }]), args(), f);
  assert.equal(f.calls.length, 1);
  const skip = r.events.find(e => e.event === 'board_skipped');
  assert.equal(skip.disposition, 'skipped: duplicate');
  assert.equal(skip.duplicate_of, 'gh-stripe');
  assert.equal(r.exitCode, 0, 'a skipped duplicate is not a failure');
});

test('WV12: the loop cannot reach a judge subprocess: --judge claude refused, and no subprocess module in its import graph', async () => {
  const f = router(GOOD);
  const r = await run(project(FOUR), args('--judge', 'claude'), f);
  assert.equal(r.exitCode, 12);
  assert.equal(f.calls.length, 0);
  // Walk src/loop.mjs's static imports, transitively.
  const seen = new Set();
  const external = new Set();
  const walk = file => {
    if (seen.has(file)) return;
    seen.add(file);
    const src = readFileSync(file, 'utf8');
    assert.doesNotMatch(src, /\bimport\s*\(/, `${file}: no dynamic import()`);
    for (const m of src.matchAll(/^\s*import\s[^'"]*['"]([^'"]+)['"]/gm)) {
      if (m[1].startsWith('.')) walk(resolve(dirname(file), m[1]));
      else external.add(m[1]);
    }
  };
  walk(join(ROOT, 'src/loop.mjs'));
  const local = [...seen].map(p => p.slice(join(ROOT, 'src').length + 1)).sort();
  assert.ok(!local.includes('claude-judge.mjs'), 'claude-judge.mjs is not reachable from the loop');
  assert.ok(!local.includes('fetch.mjs'), "JS1's unguarded fetch.mjs is not reachable from the loop");
  assert.ok(![...external].some(m => /child_process|worker_threads|node:cluster/.test(m)), [...external].join(', '));
  assert.deepEqual(local, ['loop.mjs', 'policy.mjs', 'providers/greenhouse.mjs', 'providers/lever.mjs', 'state.mjs']);
});

test('WV15: a CLI flag cannot raise a budget: 9, 20, 0 and non-numbers are rejected before networking', async () => {
  for (const v of ['9', '20', '0', 'many', '-1']) {
    const f = router(GOOD);
    const r = await run(project(FOUR), args('--max-requests', v), f);
    assert.equal(r.exitCode, 12, `--max-requests ${v}`);
    assert.equal(f.calls.length, 0, `--max-requests ${v}`);
  }
});

test('WV6: a failed board keeps its prior state byte for byte and reports no count', async () => {
  const root = project([B.stripe]);
  await run(root, args(), router({ stripe: res(200, gh([1, 2])) }));
  const before = readFileSync(join(root, 'out/state/gh-stripe.json'), 'utf8');
  const r = await run(root, args(), router({ stripe: res(404, '{}') }));
  assert.equal(readFileSync(join(root, 'out/state/gh-stripe.json'), 'utf8'), before);
  assert.equal(r.boards[0].raw_count, null);
  assert.equal(r.boards[0].new_count, null);
});

test('WV17: an ordinary drop in live postings does not shrink the cumulative seen-id state', async () => {
  const root = project([B.stripe]);
  await run(root, args(), router({ stripe: res(200, gh([1, 2, 3])) }));
  const r = await run(root, args(), router({ stripe: res(200, gh([1])) }));
  assert.equal(r.exitCode, 0);
  const ids = JSON.parse(readFileSync(join(root, 'out/state/gh-stripe.json'), 'utf8')).ids.map(String);
  assert.deepEqual(ids, ['1', '2', '3']);
});

test('WV19: a request begun near the 60 s deadline gets only the time remaining as its timeout', async () => {
  const timers = [];
  let reads = 0;
  const now = () => (reads++ === 0 ? T : T + 57_000); // the run starts at T; every later read is 57 s in
  const r = await run(project([B.stripe]), args(), router({ stripe: res(200, gh([1])) }), {
    now,
    setTimer: (fn, ms) => { timers.push(ms); return 0; },
    clearTimer: () => {},
  });
  assert.deepEqual(timers, [3000], 'min(15 s, 60 s - 57 s)');
  assert.equal(r.exitCode, 0);
});

test('wall clock: once the 60 s budget is spent, remaining boards are not attempted (exit 11)', async () => {
  let calls = 0;
  const f = router(GOOD);
  const now = () => (calls === 0 ? T : T + 61_000);
  const fetchImpl = async (url, init) => { calls += 1; return f(url, init); };
  const r = await run(project(FOUR), args(), fetchImpl, { now });
  assert.equal(calls, 1);
  assert.equal(r.status, 'budget-exhausted');
  assert.deepEqual(r.unattempted.map(u => u.budget), ['wall-clock', 'wall-clock', 'wall-clock']);
});
