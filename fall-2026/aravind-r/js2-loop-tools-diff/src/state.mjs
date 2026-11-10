// Seen-id state (CONTRACT.md, "In" and "Out"). Absent file = first run = baseline.
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export function loadState(path) {
  if (!existsSync(path)) return null;
  const s = JSON.parse(readFileSync(path, 'utf8'));
  if (!Array.isArray(s.ids)) throw new Error(`state file ${path} has no ids list`);
  return s;
}

export function saveState(path, { board, ids, run }) {
  mkdirSync(dirname(path), { recursive: true });
  const sorted = [...new Set(ids.map(Number))].sort((a, b) => a - b);
  writeFileSync(path, JSON.stringify({ board, updated_by_run: run, count: sorted.length, ids: sorted }, null, 2) + '\n');
}

// Pure: which postings are new given the previous state. Baseline reports none.
export function diffNew(jobs, state) {
  if (state === null) return { baseline: true, fresh: [] };
  const seen = new Set(state.ids.map(Number));
  return { baseline: false, fresh: jobs.filter(j => !seen.has(Number(j.id))) };
}
