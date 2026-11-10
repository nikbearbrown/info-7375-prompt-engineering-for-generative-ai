// One test per row of test/boundary-cases.md, each asserting that row's predicted
// outcome against src/policy.mjs. Network rows use a stubbed fetch (no real network);
// the time row uses an injected clock and timer; file rows use a temp-dir tree built
// during the test, never the submission's own out/.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir, homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  LIMITS, checkRequest, createNetSession, createFilePolicy, checkCliOptions, validToken, boardUrl, PolicyError,
} from '../src/policy.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// The "Predicted" column of test/boundary-cases.md, copied verbatim. The last test
// fails if this and the committed table ever disagree.
const PREDICTED = {
  1: 'allow', 2: 'allow', 3: 'deny', 4: 'deny', 5: 'deny', 6: 'deny', 7: 'deny', 8: 'deny', 9: 'deny',
  10: 'allow', 11: 'deny', 12: 'deny', 13: 'deny', 14: 'allow', 15: 'deny', 16: 'deny', 17: 'ask', 18: 'ask',
  19: 'deny', 20: 'deny', 21: 'deny', 22: 'deny', 23: 'allow', 24: 'deny', 25: 'deny', 26: 'deny',
  27: 'allow', 28: 'allow', 29: 'allow', 30: 'ask', 31: 'allow', 32: 'deny', 33: 'deny',
  34: 'deny retry', 35: 'allow one retry', 36: 'allow, capped at 3 s', 37: 'ask',
  38: 'allow', 39: 'deny', 40: 'deny', 41: 'deny',
};

const covered = new Set();
function row(n, name, fn) {
  covered.add(n);
  test(`row ${String(n).padStart(2, '0')} [${PREDICTED[n]}]: ${name}`, fn);
}

// ---- fixtures ----------------------------------------------------------------

// Stubbed fetch: returns the queued responses in order and records every call.
function stubFetch(responses) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    const r = responses[Math.min(calls.length - 1, responses.length - 1)];
    if (typeof r === 'function') return r(url, init);
    return { status: r.status, headers: new Headers(r.headers ?? {}), text: async () => r.body ?? '' };
  };
  fn.calls = calls;
  return fn;
}
const OK = { status: 200, body: '{"jobs":[]}' };
const T0 = 1_000_000;
function session(fetchImpl, extra = {}) {
  const waits = [];
  const s = createNetSession({ deadline: T0 + 60_000, now: () => T0, fetchImpl, sleep: async ms => { waits.push(ms); }, ...extra });
  s.waits = waits;
  return s;
}

// A disposable project tree: out/{traces,state,raw}, boards.json, a sibling out-evil/,
// and an outside directory that symlinks point into.
function tree() {
  const root = mkdtempSync(join(tmpdir(), 'js2-policy-root-'));
  const outside = mkdtempSync(join(tmpdir(), 'js2-policy-outside-'));
  for (const d of ['out/traces', 'out/state', 'out/raw', 'out-evil']) mkdirSync(join(root, d), { recursive: true });
  writeFileSync(join(root, 'boards.json'), '[]\n');
  writeFileSync(join(root, 'out/state/gh-stripe.json'), JSON.stringify({ ids: ['1', '2', '3'] }));
  writeFileSync(join(root, 'out/state/gh-airbnb.json'), JSON.stringify({ ids: ['10', '11'] }));
  writeFileSync(join(root, 'out/state/lv-spotify.json'), JSON.stringify({ ids: [] }));
  writeFileSync(join(root, 'out/raw/lv-spotify.json'), '[]');
  writeFileSync(join(outside, 'secret.json'), '{"secret":true}');
  symlinkSync(outside, join(root, 'out/link'));
  symlinkSync(join(outside, 'secret.json'), join(root, 'out/raw/escape.json'));
  return { root, outside };
}

// Network row: the policy decision, and the same request through a session, which
// must send exactly one fetch when allowed and none when denied.
async function netRow(n, req) {
  const p = checkRequest(req);
  assert.equal(p.decision, PREDICTED[n], p.reason);
  const f = stubFetch([OK]);
  const o = await session(f).get(req);
  if (PREDICTED[n] === 'allow') {
    assert.equal(o.kind, 'ok');
    assert.equal(f.calls.length, 1);
    assert.equal(f.calls[0].init.method, 'GET');
    assert.equal(f.calls[0].init.redirect, 'manual');
  } else {
    assert.equal(o.kind, 'denied');
    assert.equal(f.calls.length, 0, 'a denied request must never reach fetch');
  }
  return p;
}

// ---- rows 1-9: network -----------------------------------------------------------

row(1, 'GET Greenhouse stripe jobs?content=true', () =>
  netRow(1, { method: 'GET', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true' }));

row(2, 'GET Lever spotify ?mode=json', () =>
  netRow(2, { method: 'GET', url: 'https://api.lever.co/v0/postings/spotify?mode=json' }));

row(3, 'GET example.com: host off-list', async () => {
  const p = await netRow(3, { method: 'GET', url: 'https://example.com/jobs' });
  assert.match(p.reason, /not on the allow-list/);
});

row(4, 'GET boards-api.greenhouse.io.evil.example: suffix trick', async () => {
  const p = await netRow(4, { method: 'GET', url: 'https://boards-api.greenhouse.io.evil.example/v1/boards/stripe/jobs' });
  assert.match(p.reason, /not on the allow-list/);
});

row(5, 'GET over http://', async () => {
  const p = await netRow(5, { method: 'GET', url: 'http://boards-api.greenhouse.io/v1/boards/stripe/jobs' });
  assert.match(p.reason, /https/);
});

row(6, 'POST Lever .../apply', async () => {
  const p = await netRow(6, { method: 'POST', url: 'https://api.lever.co/v0/postings/spotify/123/apply' });
  assert.match(p.reason, /GET only/);
});

row(7, 'GET Greenhouse jobs/123/questions: extra path segment', async () => {
  const p = await netRow(7, { method: 'GET', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123/questions' });
  assert.match(p.reason, /path not on the allow-list/);
});

row(8, 'allow-listed GET answered by 301 -> evil.example is not followed', async () => {
  const f = stubFetch([{ status: 301, headers: { location: 'https://evil.example/' }, body: '' }]);
  const o = await session(f).get({ method: 'GET', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs' });
  assert.equal(o.kind, 'redirect');
  assert.equal(o.location, 'https://evil.example/');
  assert.equal(f.calls.length, 1, 'no follow-up fetch');
  assert.equal(f.calls[0].init.redirect, 'manual');
  assert.ok(f.calls.every(c => !c.url.includes('evil.example')));
  assert.equal(o.retry.retry, false);
});

row(9, 'GET with user:pw@ in the URL', async () => {
  const p = await netRow(9, { method: 'GET', url: 'https://user:pw@api.lever.co/v0/postings/spotify' });
  assert.match(p.reason, /credentials/);
});

// ---- rows 10-18: files ---------------------------------------------------------

row(10, 'create out/traces/run.json', () => {
  const { root } = tree();
  assert.equal(createFilePolicy({ root }).checkWrite('out/traces/run.json').decision, PREDICTED[10]);
});

row(11, 'create out/../boards.json', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkWrite('out/../boards.json');
  assert.equal(d.decision, PREDICTED[11]);
  assert.match(d.reason, /outside out\//);
});

row(12, 'create out-evil/x.json beside out/', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkWrite('out-evil/x.json');
  assert.equal(d.decision, PREDICTED[12]);
  assert.match(d.reason, /outside out\//);
});

row(13, 'create out/link/x.json where out/link -> outside temp dir', () => {
  const { root, outside } = tree();
  const d = createFilePolicy({ root }).checkWrite('out/link/x.json');
  assert.equal(d.decision, PREDICTED[13]);
  assert.ok(d.path.startsWith(createFilePolicy({ root: outside }).root), `resolved to ${d.path}`);
});

row(14, 'read boards.json inside the project', () => {
  const { root } = tree();
  assert.equal(createFilePolicy({ root }).checkRead('boards.json').decision, PREDICTED[14]);
});

row(15, 'overwrite boards.json', () => {
  const { root } = tree();
  assert.equal(createFilePolicy({ root }).checkWrite('boards.json').decision, PREDICTED[15]);
});

row(16, 'read path.join(os.homedir(), ".ssh", "id_ed25519")', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkRead(join(homedir(), '.ssh', 'id_ed25519'));
  assert.equal(d.decision, PREDICTED[16]);
  assert.match(d.reason, /outside the project/);
});

row(17, 'delete out/state/gh-stripe.json without approval', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkDelete('out/state/gh-stripe.json');
  assert.equal(d.decision, PREDICTED[17]);
  assert.match(d.reason, /needs approval/);
});

row(18, 'overwrite out/state/gh-stripe.json with a smaller seen-id set, no approval', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkWrite('out/state/gh-stripe.json', { nextIds: ['1'] });
  assert.equal(d.decision, PREDICTED[18]);
  assert.match(d.reason, /remove 2 seen id/);
});

// ---- rows 19-26: more network --------------------------------------------------

row(19, 'mailto:recruiter@example.com', async () => {
  const p = await netRow(19, { method: 'GET', url: 'mailto:recruiter@example.com' });
  assert.match(p.reason, /https/);
});

row(20, 'POST Greenhouse jobs', async () => {
  const p = await netRow(20, { method: 'POST', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs' });
  assert.match(p.reason, /GET only/);
});

row(21, 'GET jobs.lever.co/.../apply (a posting applyUrl)', async () => {
  const p = await netRow(21, { method: 'GET', url: 'https://jobs.lever.co/spotify/123/apply' });
  assert.match(p.reason, /not on the allow-list/);
});

row(22, 'GET .../boards/%2e%2e/jobs: raw-string guard, before new URL() normalizes', async () => {
  const url = 'https://boards-api.greenhouse.io/v1/boards/%2e%2e/jobs';
  assert.equal(new URL(url).pathname, '/v1/jobs', 'precondition: the URL parser would normalize this away');
  const p = await netRow(22, { method: 'GET', url });
  assert.equal(p.reason, 'raw path has encoded or forbidden characters', 'denied by the raw guard, not by luck after parsing');
  assert.equal(validToken('%2e%2e'), false);
  assert.throws(() => boardUrl('greenhouse', '%2e%2e'), PolicyError);
  assert.throws(() => boardUrl('greenhouse', '../x'), PolicyError);
});

row(23, 'GET https://BOARDS-API.GREENHOUSE.IO/...: hostname lowercased, then exact', async () => {
  const p = await netRow(23, { method: 'GET', url: 'https://BOARDS-API.GREENHOUSE.IO/v1/boards/stripe/jobs' });
  assert.equal(p.canonical, 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs');
});

row(24, 'GET trailing-dot hostname', async () => {
  const p = await netRow(24, { method: 'GET', url: 'https://boards-api.greenhouse.io./v1/boards/stripe/jobs' });
  assert.match(p.reason, /trailing-dot/);
});

row(25, 'GET on port 8443', async () => {
  const p = await netRow(25, { method: 'GET', url: 'https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs' });
  assert.match(p.reason, /port 8443/);
});

row(26, 'allow-listed GET with Authorization: Bearer test', async () => {
  const p = await netRow(26, {
    method: 'GET', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs', headers: { Authorization: 'Bearer test' },
  });
  assert.match(p.reason, /header Authorization/);
});

// ---- rows 27-30: approvals (27 and 30 share one policy, i.e. one run's approval state)

row(27, 'delete out/state/gh-stripe.json with --approve out/state/gh-stripe.json', () => {
  const { root } = tree();
  const fp = createFilePolicy({ root, approve: ['out/state/gh-stripe.json'] });
  const d = fp.checkDelete('out/state/gh-stripe.json');
  assert.equal(d.decision, PREDICTED[27]);
  assert.equal(d.approved, true);
});

row(28, 'read out/state/gh-stripe.json', () => {
  const { root } = tree();
  assert.equal(createFilePolicy({ root }).checkRead('out/state/gh-stripe.json').decision, PREDICTED[28]);
});

row(29, 'shrink out/state/gh-stripe.json with matching --approve', () => {
  const { root } = tree();
  const fp = createFilePolicy({ root, approve: ['out/state/gh-stripe.json'] });
  const d = fp.checkWrite('out/state/gh-stripe.json', { nextIds: ['1'] });
  assert.equal(d.decision, PREDICTED[29]);
  assert.equal(d.approved, true);
});

row(30, 'second guarded delete of the same path in the same run, after row 27 consumed the approval', () => {
  const { root } = tree();
  const fp = createFilePolicy({ root, approve: ['out/state/gh-stripe.json'] });
  const target = join(root, 'out/state/gh-stripe.json');
  // Row 27's step, in this same run: the approved delete, carried out.
  assert.equal(fp.checkDelete('out/state/gh-stripe.json').decision, 'allow');
  rmSync(target);
  // Restore only the disposable file, through an ordinary allowed create.
  assert.equal(fp.checkWrite('out/state/gh-stripe.json').decision, 'allow');
  writeFileSync(target, JSON.stringify({ ids: ['1', '2', '3'] }));
  const d = fp.checkDelete('out/state/gh-stripe.json');
  assert.equal(d.decision, PREDICTED[30]);
  assert.match(d.reason, /approval already used/);
});

// ---- rows 31-33: CLI -----------------------------------------------------------------

row(31, '--max-requests 2 with 4 distinct boards: accepted; only 2 requests sent', async () => {
  const c = checkCliOptions({ 'max-requests': '2' });
  assert.equal(c.decision, PREDICTED[31], c.reason);
  assert.equal(c.limits.requests, 2);
  const f = stubFetch([{ status: 200, body: '[]' }]);
  const s = session(f, { maxRequests: c.limits.requests });
  const urls = [
    'https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true',
    'https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true',
    'https://api.lever.co/v0/postings/spotify?mode=json',
    'https://boards-api.greenhouse.io/v1/boards/no-such-board-js2/jobs?content=true',
  ];
  const kinds = [];
  for (const url of urls) kinds.push((await s.get({ method: 'GET', url })).kind);
  assert.deepEqual(kinds, ['ok', 'ok', 'budget', 'budget']);
  assert.equal(f.calls.length, 2, 'at most two HTTP attempts');
});

row(32, '--max-requests 20: rejected, not clamped', () => {
  const c = checkCliOptions({ 'max-requests': '20' });
  assert.equal(c.decision, PREDICTED[32]);
  assert.match(c.reason, /exceeds the hard maximum 8/);
  assert.throws(() => createNetSession({ maxRequests: 20, deadline: T0 }), PolicyError);
});

row(33, '--judge claude', () => {
  const c = checkCliOptions({ judge: 'claude' });
  assert.equal(c.decision, PREDICTED[33]);
  assert.match(c.reason, /--judge none only/);
  assert.equal(checkCliOptions({ judge: 'none' }).decision, 'allow');
});

// ---- rows 34-36: retry and time -----------------------------------------------------

const GH = { method: 'GET', url: 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs' };

row(34, 'stubbed 429 with Retry-After: 30: rate-limited, no second request', async () => {
  assert.equal(PREDICTED[34], 'deny retry');
  const f = stubFetch([{ status: 429, headers: { 'retry-after': '30' } }, OK]);
  const s = session(f);
  const o = await s.get(GH);
  assert.equal(o.kind, 'http');
  assert.equal(o.status, 429);
  assert.equal(o.retry.retry, false);
  assert.equal(o.retry.reason, 'rate-limited');
  assert.equal(f.calls.length, 1);
  assert.deepEqual(s.waits, []);
});

row(35, 'stubbed 429 with Retry-After: 2: one retry after 2 s, and never a third attempt', async () => {
  assert.equal(PREDICTED[35], 'allow one retry');
  const f = stubFetch([{ status: 429, headers: { 'retry-after': '2' } }, OK]);
  const s = session(f);
  const o = await s.get(GH);
  assert.equal(o.kind, 'ok');
  assert.equal(f.calls.length, 2);
  assert.deepEqual(s.waits, [2000], 'delay taken from the header');
  // Limited to one retry: a second 429 is not retried again.
  const f2 = stubFetch([{ status: 429, headers: { 'retry-after': '2' } }]);
  const s2 = session(f2);
  const o2 = await s2.get(GH);
  assert.equal(o2.kind, 'http');
  assert.equal(f2.calls.length, 2);
  assert.equal(s2.requests, 2);
});

row(36, 'GET begun with 3 s of wall clock left: timeout 3 s, fetch aborted at the deadline', async () => {
  assert.equal(PREDICTED[36], 'allow, capped at 3 s');
  let t = 0; // injected clock: the run's deadline is 3000 ms away
  const timers = [];
  const setTimer = (fn, ms) => { timers.push({ fn, ms }); return timers.length; };
  let signal;
  const f = stubFetch([(url, init) => new Promise((_, reject) => {
    signal = init.signal;
    init.signal.addEventListener('abort', () => reject(new Error('aborted')));
    queueMicrotask(() => { t += timers[0].ms; timers[0].fn(); }); // the clock reaches the timer
  })]);
  const s = createNetSession({ deadline: 3000, now: () => t, fetchImpl: f, setTimer, clearTimer: () => {}, sleep: async () => {} });
  const o = await s.get(GH);
  assert.equal(timers[0].ms, 3000, 'min(15 s, remaining)');
  assert.equal(signal.aborted, true);
  assert.equal(o.kind, 'timeout');
  assert.equal(f.calls.length, 1, 'no second action past the deadline');
  assert.equal(o.retry.budgetExhausted, 'wall-clock');
});

// ---- row 37: approval path binding --------------------------------------------------

row(37, 'delete out/state/gh-airbnb.json with an unconsumed --approve for gh-stripe.json', () => {
  const { root } = tree();
  const fp = createFilePolicy({ root, approve: ['out/state/gh-stripe.json'] });
  const d = fp.checkDelete('out/state/gh-airbnb.json');
  assert.equal(d.decision, PREDICTED[37]);
  assert.equal(fp.checkDelete('out/state/gh-stripe.json').decision, 'allow', 'the stripe approval was still unused');
});

// ---- rows 38-41: --replay path ------------------------------------------------------

row(38, '--replay out/raw/lv-spotify.json', () => {
  const { root } = tree();
  assert.equal(createFilePolicy({ root }).checkReplayPath('out/raw/lv-spotify.json').decision, PREDICTED[38]);
});

row(39, '--replay out/raw/../state/lv-spotify.json (an existing file, but not under out/raw/)', () => {
  const { root } = tree();
  assert.ok(existsSync(join(root, 'out/state/lv-spotify.json')));
  const d = createFilePolicy({ root }).checkReplayPath('out/raw/../state/lv-spotify.json');
  assert.equal(d.decision, PREDICTED[39]);
  assert.match(d.reason, /not under out\/raw/);
});

row(40, '--replay out/raw/escape.json, a symlink to a file outside out/raw/', () => {
  const { root, outside } = tree();
  assert.equal(readFileSync(join(root, 'out/raw/escape.json'), 'utf8'), '{"secret":true}', 'precondition: the link resolves');
  const d = createFilePolicy({ root }).checkReplayPath('out/raw/escape.json');
  assert.equal(d.decision, PREDICTED[40]);
  assert.ok(d.path.startsWith(createFilePolicy({ root: outside }).root));
});

row(41, '--replay out/raw/missing.json', () => {
  const { root } = tree();
  const d = createFilePolicy({ root }).checkReplayPath('out/raw/missing.json');
  assert.equal(d.decision, PREDICTED[41]);
  assert.equal(d.reason, 'replay file missing');
});

// ---- the table itself ---------------------------------------------------------------

test('every row of test/boundary-cases.md has a test, with its prediction copied verbatim', () => {
  const md = readFileSync(join(ROOT, 'test/boundary-cases.md'), 'utf8');
  const fromTable = {};
  for (const line of md.split('\n')) {
    const m = /^\|\s*(\d+)\s*\|/.exec(line);
    if (!m) continue;
    const cells = line.split('|').map(c => c.trim());
    fromTable[Number(m[1])] = cells[4];
  }
  assert.equal(Object.keys(fromTable).length, 41);
  assert.deepEqual(fromTable, PREDICTED);
  assert.deepEqual([...covered].sort((a, b) => a - b), Object.keys(fromTable).map(Number));
});

test('LIMITS in src/policy.mjs match the GATE.md budget table and retry rules', () => {
  const gate = readFileSync(join(ROOT, 'GATE.md'), 'utf8');
  const cell = label => new RegExp(`^\\|\\s*${label}\\s*\\|\\s*(.+?)\\s*\\|`, 'm').exec(gate)?.[1];
  assert.equal(cell('Unique boards attempted'), String(LIMITS.boards));
  assert.equal(cell('HTTP requests, including retries'), String(LIMITS.requests));
  assert.equal(cell('Wall-clock duration'), `${LIMITS.wallSeconds} seconds`);
  assert.equal(cell('Timeout per HTTP attempt'), `\`min(${LIMITS.attemptTimeoutMs / 1000} seconds, wall-clock time remaining)\``);
  assert.equal(cell('Retries per failed attempt/board'), String(LIMITS.retriesPerBoard));
  assert.match(gate, new RegExp(`after a ${LIMITS.retryWaitMs / 1000}-second wait`));
  assert.match(gate, new RegExp(`at most \\*\\*${LIMITS.retryAfterMaxSeconds} seconds\\*\\*`));
});
