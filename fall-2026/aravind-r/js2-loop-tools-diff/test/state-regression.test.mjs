// Regression test for GATE.md wrong version 10: Lever UUID ids cast with Number(...).
// Written before the src/state.mjs patch; expected to FAIL on JS1's src/state.mjs.
//
// Reproduction (real runs, 2026-11-10, pre-fix src/state.mjs):
//   out/snapshots/20261110T215021538Z-prefix-lever-baseline/lv-spotify.after.json  → [null]
//   out/snapshots/20261110T215313703Z-prefix-lever-replay-2/lv-spotify.before.json → [0, null]
//
// Uses only src/state.mjs's existing exports: loadState(path), saveState(path, { board,
// ids, run }), diffNew(jobs, state). Every fixture is in a fresh temp directory; nothing
// here reads or writes out/. The Lever and Greenhouse ids below are literals copied from
// out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json and
// out/state/gh-stripe.json.
//
// loadState takes only a path, so the board's system comes from the file itself: these
// fixtures carry the "board" field saveState writes ("lv-spotify", "gh-stripe").
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadState, saveState, diffNew } from '../src/state.mjs';

const LEVER_IDS = [
  '2a55d6c9-c564-443a-be3e-a3851db5a93b',
  '2d67c471-9015-41c0-a041-b982ec4a14fd',
  'f263a2af-0a4e-4540-a0f6-adb3655e027b',
];
const GREENHOUSE_IDS = [5416444, 5601879, 5895430];

const tempState = name => join(mkdtempSync(join(tmpdir(), 'js2-state-regression-')), name);
const writeState = (path, board, ids) =>
  writeFileSync(path, `${JSON.stringify({ board, updated_by_run: 'fixture', count: ids.length, ids }, null, 2)}\n`);
const sorted = ids => [...ids].sort();

test('1. fresh Lever UUIDs: save, then load returns exactly those strings', () => {
  const p = tempState('lv-spotify.json');
  saveState(p, { board: 'lv-spotify', ids: LEVER_IDS, run: 'case-1' });
  const s = loadState(p);
  assert.deepEqual(sorted(s.ids), sorted(LEVER_IDS));
});

test('2. second cycle: load, add one new UUID, save, load returns exact strings; no number, no null', () => {
  const p = tempState('lv-spotify.json');
  writeState(p, 'lv-spotify', LEVER_IDS.slice(0, 2));
  const before = loadState(p);
  saveState(p, { board: 'lv-spotify', ids: [...before.ids, LEVER_IDS[2]], run: 'case-2' });
  const after = loadState(p);
  assert.deepEqual(sorted(after.ids), sorted(LEVER_IDS));
  assert.ok(after.ids.every(id => typeof id !== 'number'), `numbers in ${JSON.stringify(after.ids)}`);
  assert.ok(after.ids.every(id => id !== null), `null in ${JSON.stringify(after.ids)}`);
});

test('3. repeat: the same UUIDs observed again yield 0 new ids', () => {
  const p = tempState('lv-spotify.json');
  saveState(p, { board: 'lv-spotify', ids: LEVER_IDS, run: 'case-3-first' });
  const jobs = LEVER_IDS.map(id => ({ id }));
  const { fresh } = diffNew(jobs, loadState(p));
  assert.equal(fresh.length, 0, `reported new: ${JSON.stringify(fresh.map(j => j.id))}`);
});

test('4. legacy state: numeric Greenhouse ids load as decimal strings', () => {
  const p = tempState('gh-stripe.json');
  writeState(p, 'gh-stripe', GREENHOUSE_IDS);
  const s = loadState(p);
  assert.deepEqual(sorted(s.ids), sorted(GREENHOUSE_IDS.map(String)));
});

test('5. corrupt state: a Lever state file holding [0, null] makes load throw STATE_INTEGRITY', () => {
  const p = tempState('lv-spotify.json');
  writeState(p, 'lv-spotify', [0, null]);
  assert.throws(() => loadState(p), err => err instanceof Error && err.code === 'STATE_INTEGRITY');
});
