// Providers: every fetch goes through the policy session with redirect: 'manual' and
// timeout = min(15 s, remaining wall clock); parsing never invents a job list.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createNetSession, PolicyError } from '../src/policy.mjs';
import * as greenhouse from '../src/providers/greenhouse.mjs';
import * as lever from '../src/providers/lever.mjs';

function stubFetch(body, status = 200) {
  const calls = [];
  const fn = async (url, init) => { calls.push({ url, init }); return { status, headers: new Headers(), text: async () => body }; };
  fn.calls = calls;
  return fn;
}
function sessionWith(fetchImpl, remainingMs) {
  const timers = [];
  const s = createNetSession({
    deadline: 1000 + remainingMs, now: () => 1000, fetchImpl, sleep: async () => {},
    setTimer: (fn, ms) => { timers.push(ms); return 0; }, clearTimer: () => {},
  });
  s.timers = timers;
  return s;
}

test('provider URLs are the allow-listed ones', () => {
  assert.equal(greenhouse.url('stripe'), 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true');
  assert.equal(lever.url('spotify'), 'https://api.lever.co/v0/postings/spotify?mode=json');
});

for (const [p, token, body] of [[greenhouse, 'stripe', '{"jobs":[]}'], [lever, 'spotify', '[]']]) {
  test(`${p.system}: one fetch through the policy session, redirect manual, timeout min(15 s, remaining)`, async () => {
    const f = stubFetch(body);
    const s = sessionWith(f, 60_000);
    const o = await p.observe(s, token);
    assert.equal(o.kind, 'ok');
    assert.equal(f.calls.length, 1);
    assert.equal(f.calls[0].url, p.url(token));
    assert.equal(f.calls[0].init.method, 'GET');
    assert.equal(f.calls[0].init.redirect, 'manual');
    assert.ok(f.calls[0].init.signal instanceof AbortSignal);
    assert.deepEqual(s.timers, [15_000]);
    const f2 = stubFetch(body);
    const s2 = sessionWith(f2, 4_000);
    await p.observe(s2, token);
    assert.deepEqual(s2.timers, [4_000], 'capped at the wall clock remaining');
  });

  test(`${p.system}: an invalid token is refused before any fetch`, () => {
    const f = stubFetch(body);
    assert.throws(() => p.observe(sessionWith(f, 60_000), '../evil'), PolicyError);
    assert.equal(f.calls.length, 0);
  });
}

test('greenhouse parse: jobs kept, ids passed through unchanged; malformed bodies are errors, not 0 jobs', () => {
  const r = greenhouse.parse(JSON.stringify({ jobs: [{ id: 8124304, title: 'PM', location: { name: 'NYC' }, absolute_url: 'https://x' }] }));
  assert.deepEqual(r, { ok: true, jobs: [{ id: 8124304, title: 'PM', location: 'NYC', url: 'https://x' }] });
  assert.deepEqual(greenhouse.parse('{"jobs":[]}'), { ok: true, jobs: [] }, 'an empty list is reported as empty; the loop decides what that means');
  assert.equal(greenhouse.parse('<html>').error, 'malformed');
  assert.equal(greenhouse.parse('{"status":404,"error":"Job not found"}').error, 'malformed');
  assert.equal(greenhouse.parse('null').error, 'malformed');
});

test('lever parse: UUID ids stay strings; applyUrl is not kept; malformed bodies are errors', () => {
  const id = '2a55d6c9-c564-443a-be3e-a3851db5a93b';
  const r = lever.parse(JSON.stringify([{ id, text: 'PM', categories: { location: 'NYC' }, hostedUrl: 'https://h', applyUrl: 'https://jobs.lever.co/x/apply' }]));
  assert.deepEqual(r, { ok: true, jobs: [{ id, title: 'PM', location: 'NYC', url: 'https://h' }] });
  assert.equal(typeof r.jobs[0].id, 'string');
  assert.ok(!JSON.stringify(r).includes('apply'));
  assert.equal(lever.parse('{"ok":false,"error":"Document not found"}').error, 'malformed');
  assert.equal(lever.parse('nope').error, 'malformed');
});

test('duplicate ids in one raw response are malformed, not two jobs (GATE.md: error: malformed, no state update)', () => {
  const g = greenhouse.parse(JSON.stringify({ jobs: [{ id: 101, title: 'A' }, { id: 101, title: 'A again' }] }));
  assert.equal(g.ok, false);
  assert.equal(g.error, 'malformed');
  assert.match(g.reason, /duplicate id 101/);
  const gMixed = greenhouse.parse(JSON.stringify({ jobs: [{ id: 101 }, { id: '101' }] }));
  assert.equal(gMixed.ok, false, '101 and "101" are the same Greenhouse id');
  const id = '2a55d6c9-c564-443a-be3e-a3851db5a93b';
  const l = lever.parse(JSON.stringify([{ id, text: 'A' }, { id, text: 'A again' }]));
  assert.equal(l.ok, false);
  assert.match(l.reason, /duplicate id/);
  assert.equal(greenhouse.parse(JSON.stringify({ jobs: [{ id: 101 }, { id: 102 }] })).ok, true, 'distinct ids still parse');
});
