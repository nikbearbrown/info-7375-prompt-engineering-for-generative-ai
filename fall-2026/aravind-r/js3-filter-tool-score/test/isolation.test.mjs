// W12 (FILTER.md §4, §5): only src/judge.mjs may spawn processes. The filter, the
// normalizer, and the evidence checker must be pure. Phase 4 adds the server's
// import-graph check.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT } from '../testlib/helpers.mjs';

const SRC = join(ROOT, 'src');

test('W12: only src/judge.mjs imports node:child_process', () => {
  for (const f of ['spec.mjs', 'filter.mjs', 'normalize.mjs', 'evidence.mjs']) assert.ok(existsSync(join(SRC, f)), `src/${f} exists`);
  for (const f of readdirSync(SRC, { recursive: true }).filter(f => String(f).endsWith('.mjs'))) {
    if (f === 'judge.mjs') continue;
    const s = readFileSync(join(SRC, f), 'utf8');
    assert.ok(!/child_process/.test(s), `src/${f} references child_process`);
  }
});

test('W12: filter, normalizer, and evidence checker make no network calls', () => {
  for (const f of ['spec.mjs', 'filter.mjs', 'normalize.mjs', 'evidence.mjs']) {
    const s = readFileSync(join(SRC, f), 'utf8');
    assert.ok(!/\bfetch\s*\(|node:https?|node:net|node:dgram/.test(s), `src/${f} reaches the network`);
  }
});
