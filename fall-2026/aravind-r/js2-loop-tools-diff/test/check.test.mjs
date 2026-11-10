// The independent checker (src/check.mjs), GATE.md rules 1-3. Every fixture here is a
// hand-built out/ tree (trace, raw bodies, state snapshots), not produced by the loop or
// src/state.mjs, so these tests stay true before and after the state.mjs patch.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { checkTrace, canonicalRawId, validPersistedId, formatResult, exitCodeFor } from '../src/check.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const UUIDS = ['2a55d6c9-c564-443a-be3e-a3851db5a93b', '7d1c1e0e-1111-4c2a-9a55-0f0e5a7b9c01', 'b3f0a7d2-2222-4e3b-8f66-1a2b3c4d5e6f'];
const lv = ids => JSON.stringify(ids.map(id => ({ id, text: 'Job', hostedUrl: 'https://example.test' })));
const gh = ids => JSON.stringify({ jobs: ids.map(id => ({ id, title: 'Job' })) });

// Builds out/ with one trace for one board. pre/post: id arrays, or null for "no state file".
function fixture({ system = 'lever', raw, pre = null, post = null, claim, disposition = 'observed', run = 'r1', mode = 'live' }) {
  const root = mkdtempSync(join(tmpdir(), 'js2-check-'));
  for (const d of ['out/traces', 'out/raw', 'out/snapshots', 'out/reports']) mkdirSync(join(root, d), { recursive: true });
  const board = system === 'lever' ? 'lv-spotify' : 'gh-stripe';
  let rawPath = null;
  if (raw !== undefined) { rawPath = `out/raw/${run}-${board}.json`; writeFileSync(join(root, rawPath), raw); }
  const snap = (ids, which) => {
    if (ids === null) return null;
    const p = `out/snapshots/${run}-${board}.${which}.json`;
    writeFileSync(join(root, p), JSON.stringify({ board, ids }));
    return p;
  };
  const result = {
    event: 'board_result', board, system, disposition, raw_path: rawPath,
    raw_count: 999, new_count: 999, // deliberately wrong: the checker must not use these
    new_ids: claim, state_before: snap(pre, 'before'), state_after: snap(post, 'after'),
  };
  const trace = `out/traces/${run}.jsonl`;
  writeFileSync(join(root, trace), [{ event: 'run_start', run, mode }, result].map(e => JSON.stringify(e)).join('\n') + '\n');
  return { root, trace };
}
const rule = (r, n) => r.boards[0].rules.find(x => x.rule === n);

test('correct first observation of a Lever board: all three rules pass', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: null, post: UUIDS, claim: UUIDS });
  const r = checkTrace(trace, { root });
  assert.equal(r.pass, true, JSON.stringify(r.boards[0].rules));
});

test('correct second observation: 0 new expected and claimed, state unchanged: passes', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: UUIDS, post: UUIDS, claim: [] });
  assert.equal(checkTrace(trace, { root }).pass, true);
});

test('pre-fix baseline shape (post-run state [null]): rule 3 fails; rules 1 and 2 pass', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: null, post: [null], claim: UUIDS });
  const r = checkTrace(trace, { root });
  assert.equal(rule(r, 1).pass, true);
  assert.equal(rule(r, 2).pass, true, 'the first-run count of 3 new is correct');
  assert.equal(rule(r, 3).pass, false);
  assert.match(rule(r, 3).detail, /post-run state has 1 invalid id\(s\), e\.g\. null/);
  assert.match(rule(r, 3).detail, /3 id\(s\) missing from post-run state/);
  assert.match(rule(r, 3).detail, /first observation: 0 valid persisted id\(s\), raw has 3/);
  assert.equal(r.pass, false);
});

test('pre-fix replay shape (pre [null], 3 new claimed again): rule 2 agrees with the false claim, rule 3 catches it', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: [null], post: [null], claim: UUIDS, run: 'r2', mode: 'replay' });
  const r = checkTrace(trace, { root });
  assert.equal(r.mode, 'replay');
  assert.equal(rule(r, 2).pass, true, 'rule 2 recomputes against the corrupt pre-run set, so it agrees');
  assert.equal(rule(r, 3).pass, false, 'rule 3 is what catches the finished-but-wrong answer');
  assert.match(rule(r, 3).detail, /pre-run state has 1 invalid id/);
  assert.equal(r.pass, false);
});

test('rule 2 fails a wrong new-id claim against a valid pre-run set', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: UUIDS, post: UUIDS, claim: UUIDS });
  const r = checkTrace(trace, { root });
  assert.equal(rule(r, 2).pass, false);
  assert.match(rule(r, 2).detail, /expected 0 new, claimed 3/);
});

test('rule 1 fails a success claimed on an empty response', () => {
  const { root, trace } = fixture({ raw: '[]', pre: null, post: null, claim: [] });
  const r = checkTrace(trace, { root });
  assert.equal(rule(r, 1).pass, false);
  assert.match(rule(r, 1).detail, /empty response cannot prove/);
});

test('rule 1 fails a success claimed on a raw response with duplicate or null ids', () => {
  const { root, trace } = fixture({ raw: lv([UUIDS[0], UUIDS[0], null]), pre: null, post: [UUIDS[0]], claim: [UUIDS[0]] });
  const r = checkTrace(trace, { root });
  assert.equal(rule(r, 1).pass, false);
  assert.match(rule(r, 1).detail, /1 invalid id\(s\); 1 duplicate id\(s\)/);
});

test('a failed board must not change state and must not claim new ids', () => {
  const ok = fixture({ raw: '{"ok":false}', pre: UUIDS, post: UUIDS, claim: null, disposition: 'error: not found' });
  assert.equal(checkTrace(ok.trace, { root: ok.root }).pass, true);
  const changed = fixture({ raw: '{"ok":false}', pre: UUIDS, post: [], claim: null, disposition: 'error: not found' });
  const r = checkTrace(changed.trace, { root: changed.root });
  assert.equal(rule(r, 3).pass, false);
  assert.match(rule(r, 3).detail, /dropped 3 pre-run id|state changed/);
});

test('rule 3: Greenhouse ids persisted as numbers are not canonical strings', () => {
  const { root, trace } = fixture({ system: 'greenhouse', raw: gh([1, 2]), pre: null, post: [1, 2], claim: [1, 2] });
  const r = checkTrace(trace, { root });
  assert.equal(rule(r, 2).pass, true);
  assert.equal(rule(r, 3).pass, false);
  const okStrings = fixture({ system: 'greenhouse', raw: gh([1, 2]), pre: null, post: ['1', '2'], claim: [1, 2] });
  assert.equal(checkTrace(okStrings.trace, { root: okStrings.root }).pass, true);
});

test('wrong version 16: the checker ignores the loop report and the trace counts', () => {
  const { root, trace } = fixture({ raw: lv(UUIDS), pre: UUIDS, post: UUIDS, claim: [] });
  writeFileSync(join(root, 'out/reports/r1.json'), JSON.stringify({ status: 'finished', boards: [{ board: 'lv-spotify', new_count: 0, raw_count: 0 }] }));
  const r = checkTrace(trace, { root });
  assert.equal(r.pass, true, 'raw_count/new_count of 999 in the trace were not used');
  assert.match(rule(r, 1).detail, /^3 raw job\(s\)/);
  assert.throws(() => checkTrace('out/reports/r1.json', { root }), /loop report/);
});

test('the checker reads nothing outside out/', () => {
  const { root } = fixture({ raw: lv(UUIDS), pre: null, post: UUIDS, claim: UUIDS });
  writeFileSync(join(root, 'elsewhere.jsonl'), '{"event":"run_start"}\n');
  assert.throws(() => checkTrace('elsewhere.jsonl', { root }), /not under out\//);
});

test('id canonicalization: Greenhouse decimal, Lever UUID strings only', () => {
  assert.equal(canonicalRawId('greenhouse', 8124304), '8124304');
  assert.equal(canonicalRawId('greenhouse', '8124304'), '8124304');
  assert.equal(canonicalRawId('greenhouse', -1), null);
  assert.equal(canonicalRawId('greenhouse', null), null);
  assert.equal(canonicalRawId('lever', UUIDS[0]), UUIDS[0]);
  assert.equal(canonicalRawId('lever', 123), null);
  assert.equal(validPersistedId('greenhouse', 8124304), false, 'persisted ids must be strings');
  assert.equal(validPersistedId('lever', null), false);
});

test('CLI with no --trace is a usage error, exit 2', () => {
  const r = spawnSync(process.execPath, [join(ROOT, 'src/check.mjs')], { encoding: 'utf8' });
  assert.equal(r.status, 2);
  assert.match(r.stderr, /usage/);
});

// A run that ended before observing any board (the shape of 20261110T215039252Z-prefix-lever-replay).
function noObservationTrace(status = 'error', exitCode = 12) {
  const root = mkdtempSync(join(tmpdir(), 'js2-check-'));
  mkdirSync(join(root, 'out/traces'), { recursive: true });
  const trace = 'out/traces/r0.jsonl';
  writeFileSync(join(root, trace), [
    { event: 'run_start', run: 'r0', mode: 'replay' },
    { event: 'config', run: 'r0' },
    { event: 'run_end', run: 'r0', status, exit_code: exitCode, reason: 'refused: --replay : replay file not under out/raw/' },
  ].map(e => JSON.stringify(e)).join('\n') + '\n');
  return { root, trace };
}

test('a run with no observations does not pass: NO OBSERVATIONS (run status: error), non-passing exit', () => {
  const { root, trace } = noObservationTrace();
  const r = checkTrace(trace, { root });
  assert.equal(r.boards.length, 0);
  assert.equal(r.pass, false, 'zero observations is not a pass');
  assert.equal(r.runStatus, 'error', 'run status read from the trace run_end event');
  const lines = formatResult(r, trace);
  assert.ok(lines.includes('r0: NO OBSERVATIONS (run status: error)'), lines.join('\n'));
  assert.ok(!lines.some(l => /\bPASS\b/.test(l)), lines.join('\n'));
  assert.equal(exitCodeFor([r]), 1);
  assert.equal(exitCodeFor([checkTrace(fixture({ raw: lv(UUIDS), pre: null, post: UUIDS, claim: UUIDS }).trace, { root: fixture({ raw: lv(UUIDS), pre: null, post: UUIDS, claim: UUIDS }).root })]), 0);
});

test('a passing run and a no-observation run together still exit non-passing', () => {
  const ok = fixture({ raw: lv(UUIDS), pre: null, post: UUIDS, claim: UUIDS });
  const none = noObservationTrace();
  assert.equal(exitCodeFor([checkTrace(ok.trace, { root: ok.root }), checkTrace(none.trace, { root: none.root })]), 1);
});
