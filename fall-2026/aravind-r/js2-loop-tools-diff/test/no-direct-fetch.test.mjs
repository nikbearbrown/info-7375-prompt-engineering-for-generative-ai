// Only src/policy.mjs may call fetch( directly. Every other file reaches the network
// through createNetSession, so the policy cannot be bypassed by a stray call.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// fetch( / fetch ( / globalThis.fetch( / window.fetch( — but not guardedFetch( or fetchImpl(.
const DIRECT_FETCH = /(?<![\w$])fetch\s*\(/;

test('the direct-fetch pattern catches direct calls and ignores other names', () => {
  for (const s of ['await fetch(url)', 'fetch (u)', 'globalThis.fetch(u)', 'x = window.fetch(u, init)']) assert.match(s, DIRECT_FETCH, s);
  for (const s of ['guardedFetch(u)', 'fetchImpl(u)', 'prefetch(u)', 'const fetchImpl = globalThis.fetch;']) assert.doesNotMatch(s, DIRECT_FETCH, s);
});

test('no file in src/ other than policy.mjs calls fetch( directly', () => {
  const files = readdirSync(join(ROOT, 'src'), { recursive: true }).filter(f => /\.(m|c)?js$/.test(f));
  assert.ok(files.includes('policy.mjs'), 'precondition: the scan sees src/policy.mjs');
  const offenders = [];
  for (const f of files) {
    if (f === 'policy.mjs') continue;
    readFileSync(join(ROOT, 'src', f), 'utf8').split('\n').forEach((line, i) => {
      if (DIRECT_FETCH.test(line)) offenders.push(`src/${f}:${i + 1}: ${line.trim()}`);
    });
  }
  assert.deepEqual(offenders, []);
});
