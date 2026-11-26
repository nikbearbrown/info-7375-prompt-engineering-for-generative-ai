// The judge tool's CSV editing: untouched bytes stay identical; only the set cells change.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { Sheet } from '../src/sheet.mjs';
import { parseCsv } from '../src/csv.mjs';
import { ROOT } from '../testlib/helpers.mjs';

test('round-trip is byte-identical (the real audit sheet, and odd quoting/CRLF/BOM)', () => {
  const real = readFileSync(join(ROOT, 'audit', 'audit-sheet.csv'), 'utf8');
  assert.equal(new Sheet(real).toString(), real);
  const odd = '﻿id,"title",my_verdict,my_note\r\n1,"quoted, with comma","",\r\n2,"has ""quotes""\nand newline",x,"n"\r\n';
  assert.equal(new Sheet(odd).toString(), odd);
});

test('setting a verdict and a note changes only those cells', () => {
  const text = 'id,title,my_verdict,my_note\n1,"Product Manager, Payments",,\n2,"Engineer ""II""",,\n';
  const sh = new Sheet(text);
  sh.set(sh.rows[0], 'my_verdict', 'relevant');
  sh.set(sh.rows[0], 'my_note', 'location fits, "3+ years", ok');
  const out = sh.toString();
  assert.equal(out, 'id,title,my_verdict,my_note\n1,"Product Manager, Payments",relevant,"location fits, ""3+ years"", ok"\n2,"Engineer ""II""",,\n');
  assert.deepEqual(parseCsv(out)[0], { id: '1', title: 'Product Manager, Payments', my_verdict: 'relevant', my_note: 'location fits, "3+ years", ok' });
});

test('judge-audit.mjs stays blind: it never reads the key, results, candidates, or plan strata', () => {
  const src = readFileSync(join(ROOT, 'tools', 'judge-audit.mjs'), 'utf8').replace(/\/\/.*$/gm, '');
  for (const s of ['key.json', 'results.jsonl', 'false-friend', 'sample.json', 'RESULTS', 'strata', 'score', 'decision', 'components']) assert.ok(!src.includes(s), `judge-audit.mjs mentions ${s}`);
  assert.ok(!readdirSync(join(ROOT, 'tools')).includes('judge-audit.test.mjs'));
});

test('addColumn appends an empty column and leaves every existing cell byte-identical', () => {
  const text = 'id,title,my_verdict,my_note\n1,"a, b",relevant,"x ""y"""\n2,c,,\n';
  const sh = new Sheet(text);
  sh.addColumn('first_pass_verdict');
  assert.equal(sh.toString(), 'id,title,my_verdict,my_note,first_pass_verdict\n1,"a, b",relevant,"x ""y""",\n2,c,,,\n');
  sh.set(sh.rows[0], 'first_pass_verdict', 'relevant');
  sh.set(sh.rows[0], 'my_verdict', 'not_relevant');
  assert.deepEqual(parseCsv(sh.toString())[0], { id: '1', title: 'a, b', my_verdict: 'not_relevant', my_note: 'x "y"', first_pass_verdict: 'relevant' });
  sh.addColumn('first_pass_verdict'); // idempotent
  assert.equal(sh.header.filter(h => h === 'first_pass_verdict').length, 1);
});
