// FILTER.md is the filter. These tests check that the code reads it and that its
// numbers have the properties the document claims (W4, W11).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { loadFilterSpec, parseFilterSpec } from '../src/spec.mjs';
import { scorePosting } from '../src/filter.mjs';
import { FILTER_MD, ROOT, PREFS, mk, clone } from '../testlib/helpers.mjs';

const spec = loadFilterSpec(FILTER_MD);

test('FILTER.md has exactly one filter-spec block and it parses', () => {
  const md = readFileSync(FILTER_MD, 'utf8');
  assert.equal((md.match(/```json filter-spec/g) ?? []).length, 1);
  assert.match(spec.version, /^\d+\.\d+\.\d+(-[a-z0-9.]+)?$/);
  assert.match(md, new RegExp(`\\*\\*Version ${spec.version.replace(/\./g, '\\.')}\\b`), 'header version matches the spec block');
});

test('parseFilterSpec refuses a document without the block', () => {
  assert.throws(() => parseFilterSpec('# no spec here'));
});

test('weights are in [0,1], sum to 1, threshold in (0,1)', () => {
  const w = spec.weights;
  for (const k of ['title', 'location', 'experience', 'topic']) assert.ok(w[k] >= 0 && w[k] <= 1, k);
  assert.ok(Math.abs(w.title + w.location + w.experience + w.topic - 1) < 1e-9);
  assert.ok(spec.threshold > 0 && spec.threshold < 1);
});

test('W4: the spec cannot keep a posting without a PM title (max score with T=0 < threshold)', () => {
  assert.ok(1 - spec.weights.title < spec.threshold, `max non-title score ${1 - spec.weights.title} >= threshold ${spec.threshold}`);
  const p = mk({ title: 'Data Engineer, Payments', location: 'San Francisco', department: 'Fintech',
    text: 'Payments, fintech, data, mobile and e-commerce. 2+ years of experience.' });
  const r = scorePosting(p, { spec, prefs: PREFS });
  assert.equal(r.components.title.value, 0);
  assert.equal(r.decision, 'reject');
});

test('W11: behavior follows the spec object, not constants in the code', () => {
  // One topic term, so the score is below 1 and a stricter threshold can reject it.
  // (Fixed after the gate commit: the first fixture scored 1.0, which no threshold <= 1 rejects.)
  const p = mk({ text: 'Payments. 3+ years of experience in product.' });
  const r = scorePosting(p, { spec, prefs: PREFS });
  assert.equal(r.decision, 'keep');
  assert.ok(r.score < 0.99);
  const strict = clone(spec); strict.threshold = 0.99;
  assert.equal(scorePosting(p, { spec: strict, prefs: PREFS }).decision, 'reject');
  const noTopic = clone(spec); noTopic.topic.terms = ['zzz-not-a-word'];
  assert.equal(scorePosting(p, { spec: noTopic, prefs: PREFS }).components.topic.value, 0);
});

test('W11: src/filter.mjs hard-codes no weight, threshold, or term from the spec', () => {
  const src = readFileSync(join(ROOT, 'src', 'filter.mjs'), 'utf8').replace(/\/\/.*$/gm, '');
  for (const lit of ['0.40', '0.25', '0.70', '0.10', '.7', '.25']) assert.ok(!src.includes(lit), `literal ${lit} in filter.mjs`);
  for (const term of ['fintech', 'unable to sponsor', 'security clearance', 'Product Manager', 'New Grad']) assert.ok(!src.includes(term), `term "${term}" in filter.mjs`);
});
