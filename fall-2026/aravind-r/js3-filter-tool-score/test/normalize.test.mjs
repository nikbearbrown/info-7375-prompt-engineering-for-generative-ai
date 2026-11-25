// FILTER.md §3: one schema, per-board missing-field behavior. W6, W9.
// Fixtures marked SYNTHETIC are made up; tests marked SNAPSHOT read data/.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { normalizeBoard } from '../src/normalize.mjs';
import { ROOT, SNAPSHOT } from '../testlib/helpers.mjs';

const KEYS = ['board', 'department', 'id', 'location', 'text', 'title', 'url'];
const ghJob = (o = {}) => ({ id: 101, title: ' Product Manager ', location: { name: 'San Francisco' },
  departments: [{ name: 'Payments' }, { name: 'Product' }], content: '&lt;p&gt;Hello &amp;amp; welcome&lt;/p&gt;',
  absolute_url: 'https://example.com/gh/101', metadata: [], ...o });
const lvPost = (o = {}) => ({ id: 'aaaa-1', text: 'Product Manager', categories: { location: 'New York, NY', allLocations: ['New York, NY', 'Remote'], department: 'Product' },
  descriptionPlain: 'Intro.', lists: [{ text: 'What you do', content: '<li>Ship</li><li>Learn</li>' }], additionalPlain: 'Benefits.',
  hostedUrl: 'https://example.com/lv/aaaa-1', applyUrl: 'https://example.com/lv/aaaa-1/apply-SECRET', ...o });

// ---------- W6: unavailable is not zero ----------
test('W6 SNAPSHOT: gh-broken 404 body -> unavailable with null counts, never 0', () => {
  const body = readFileSync(join(SNAPSHOT, 'gh-broken.attempt1.json'), 'utf8');
  const r = normalizeBoard({ board: 'gh-broken', system: 'greenhouse', body });
  assert.equal(r.status, 'unavailable');
  assert.equal(r.raw_count, null);
  assert.deepEqual(r.postings, []);
  assert.ok(r.reason);
});

test('W6 SYNTHETIC: non-JSON, missing body, and wrong shape are unavailable', () => {
  for (const [system, body] of [['greenhouse', 'not json'], ['greenhouse', null], ['greenhouse', '{"nope":[]}'], ['lever', '{"jobs":[]}']]) {
    const r = normalizeBoard({ board: 'x', system, body });
    assert.equal(r.status, 'unavailable', `${system} ${body}`);
    assert.equal(r.raw_count, null);
  }
});

test('SYNTHETIC: an empty but valid board is ok with 0 postings (that is a real 0)', () => {
  const r = normalizeBoard({ board: 'x', system: 'greenhouse', body: '{"jobs":[]}' });
  assert.equal(r.status, 'ok');
  assert.equal(r.raw_count, 0);
});

// ---------- schema ----------
test('SYNTHETIC Greenhouse: mapping per FILTER.md §3.1', () => {
  const r = normalizeBoard({ board: 'gh-x', system: 'greenhouse', body: JSON.stringify({ jobs: [ghJob()] }) });
  const [p] = r.postings;
  assert.deepEqual(Object.keys(p).sort(), KEYS);
  assert.equal(p.id, '101');
  assert.equal(p.title, 'Product Manager');
  assert.equal(p.location, 'San Francisco');
  assert.equal(p.department, 'Payments; Product');
  assert.equal(p.text, 'Hello & welcome');
  assert.equal(p.url, 'https://example.com/gh/101');
});

test('SYNTHETIC Lever: mapping per §3.1, allLocations joined', () => {
  const r = normalizeBoard({ board: 'lv-x', system: 'lever', body: JSON.stringify([lvPost()]) });
  const [p] = r.postings;
  assert.deepEqual(Object.keys(p).sort(), KEYS);
  assert.equal(p.title, 'Product Manager');
  assert.equal(p.location, 'New York, NY; Remote');
  assert.equal(p.department, 'Product');
  for (const s of ['Intro.', 'What you do', 'Ship', 'Learn', 'Benefits.']) assert.ok(p.text.includes(s), s);
  assert.equal(p.url, 'https://example.com/lv/aaaa-1');
});

test('W9 SYNTHETIC: applyUrl never appears in normalized output', () => {
  const r = normalizeBoard({ board: 'lv-x', system: 'lever', body: JSON.stringify([lvPost()]) });
  const out = JSON.stringify(r);
  assert.ok(!out.includes('apply-SECRET'));
  assert.ok(!out.includes('applyUrl'));
});

test('W9 SYNTHETIC: Lever with no allLocations falls back to categories.location; missing fields become null', () => {
  const r = normalizeBoard({ board: 'lv-x', system: 'lever', body: JSON.stringify([lvPost({ categories: { location: 'Stockholm' }, hostedUrl: undefined })]) });
  const [p] = r.postings;
  assert.equal(p.location, 'Stockholm');
  assert.equal(p.department, null);
  assert.equal(p.url, null);
});

// ---------- null and duplicate ids ----------
test('W9 SYNTHETIC: a null id is skipped and counted with a warning; the rest survive', () => {
  const body = JSON.stringify({ jobs: [ghJob({ id: null }), ghJob({ id: 102 }), ghJob({ id: undefined })] });
  const r = normalizeBoard({ board: 'gh-x', system: 'greenhouse', body });
  assert.equal(r.status, 'ok');
  assert.equal(r.raw_count, 3);
  assert.equal(r.skipped.null_id, 2);
  assert.deepEqual(r.postings.map(p => p.id), ['102']);
  assert.ok(r.warnings.some(w => /null id/i.test(w)));
});

test('SYNTHETIC: a duplicate id makes the board unavailable: malformed (inherited from JS2)', () => {
  const r = normalizeBoard({ board: 'gh-x', system: 'greenhouse', body: JSON.stringify({ jobs: [ghJob({ id: 5 }), ghJob({ id: '5' })] }) });
  assert.equal(r.status, 'unavailable');
  assert.match(r.reason, /malformed/);
});

// ---------- the real snapshot ----------
test('SNAPSHOT: MANIFEST hashes match the files on disk', () => {
  const m = JSON.parse(readFileSync(join(ROOT, 'data', 'MANIFEST.json'), 'utf8'));
  for (const f of m.files) {
    const h = createHash('sha256').update(readFileSync(join(ROOT, f.path))).digest('hex');
    assert.equal(h, f.sha256, f.path);
  }
});

test('SNAPSHOT: counts match the JS2 trace; every posting has exactly the 7 keys; no applyUrl leaks', () => {
  const m = JSON.parse(readFileSync(join(ROOT, 'data', 'MANIFEST.json'), 'utf8'));
  let total = 0;
  for (const f of m.files.filter(f => f.raw_count_in_js2_trace !== null)) {
    const body = readFileSync(join(ROOT, f.path), 'utf8');
    const r = normalizeBoard({ board: f.board, system: f.system, body });
    assert.equal(r.status, 'ok', f.board);
    assert.equal(r.postings.length, f.raw_count_in_js2_trace, f.board);
    for (const p of r.postings) assert.deepEqual(Object.keys(p).sort(), KEYS);
    if (f.system === 'lever') {
      const applyUrls = JSON.parse(body).map(x => x.applyUrl).filter(Boolean);
      const out = JSON.stringify(r);
      assert.ok(applyUrls.length > 0);
      for (const u of applyUrls) assert.ok(!out.includes(u), 'applyUrl leaked');
    }
    total += r.postings.length;
  }
  assert.equal(total, m.postings_total);
});
