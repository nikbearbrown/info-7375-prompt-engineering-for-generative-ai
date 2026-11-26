// The audit tooling: exact intervals, CSV round-trip, seeded sampling.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { clopperPearson } from '../src/stats.mjs';
import { toCsv, parseCsv } from '../src/csv.mjs';
import { mulberry32, sample } from '../src/rng.mjs';

const near = (a, b, tol = 5e-4) => assert.ok(Math.abs(a - b) < tol, `${a} vs ${b}`);

test('Clopper-Pearson matches published exact values', () => {
  near(clopperPearson(0, 30).upper, 0.1157);   // rule of three gives ~0.10; exact is 0.1157
  near(clopperPearson(0, 40).upper, 0.0881);
  const r = clopperPearson(3, 30); near(r.lower, 0.0211); near(r.upper, 0.2653);
  const h = clopperPearson(5, 10); near(h.lower, 0.1871); near(h.upper, 0.8129);
  assert.equal(clopperPearson(0, 30).lower, 0);
  assert.equal(clopperPearson(30, 30).upper, 1);
  assert.throws(() => clopperPearson(4, 3));
});

test('CSV round-trips commas, quotes, newlines; tolerates BOM and CRLF', () => {
  const rows = [{ a: 'x,y', b: 'say "hi"', c: 'line1\nline2' }, { a: '', b: 'plain', c: '' }];
  const csv = toCsv(rows, ['a', 'b', 'c']);
  assert.deepEqual(parseCsv(csv), rows);
  assert.deepEqual(parseCsv('﻿a,b\r\n1,2\r\n'), [{ a: '1', b: '2' }]);
});

test('seeded sampling is reproducible and seed-dependent', () => {
  const xs = Array.from({ length: 100 }, (_, i) => i);
  assert.deepEqual(sample(xs, 10, mulberry32(7)), sample(xs, 10, mulberry32(7)));
  assert.notDeepEqual(sample(xs, 10, mulberry32(7)), sample(xs, 10, mulberry32(8)));
  assert.equal(new Set(sample(xs, 30, mulberry32(1))).size, 30);
});
