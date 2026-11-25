// Run the filter (FILTER.md §6) over the frozen snapshot. No network.
// Writes runs/filter/v<version>/{results.jsonl, summary.json}. Results carry no posting text.
// Usage: node tools/run-filter.mjs [--filter FILTER.md] [--out runs/filter]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parseFilterSpec } from '../src/spec.mjs';
import { scorePosting, rankResults } from '../src/filter.mjs';
import { loadCorpus } from '../src/corpus.mjs';
import { boilerplateLines } from '../src/boilerplate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { filter: { type: 'string', default: 'FILTER.md' }, out: { type: 'string', default: 'runs/filter' } } });
const filterPath = resolve(ROOT, values.filter);
const md = readFileSync(filterPath, 'utf8');
const spec = parseFilterSpec(md);
const prefs = JSON.parse(readFileSync(join(ROOT, 'persona', 'persona-prefs.json'), 'utf8'));
const { boards, postings } = loadCorpus(ROOT);

const share = spec.topic.exclude_shared_lines_min_share;
const shared = share != null ? boilerplateLines(postings, share) : null;
const results = rankResults(postings.map(p => scorePosting(p, { spec, prefs, shared })));
const count = (rs, k) => rs.filter(r => r.decision === k).length;
const summary = {
  ran_at: new Date().toISOString(), node: process.version,
  filter_file: values.filter, filter_sha256: createHash('sha256').update(md).digest('hex'), spec_version: spec.version,
  threshold: spec.threshold, network_requests: 0,
  shared_lines: shared ? { min_share: share, per_board: Object.fromEntries([...shared].map(([b, set]) => [b, set.size])) } : null, data: 'data/MANIFEST.json (frozen 2026-11-10 snapshot)',
  boards: boards.map(b => {
    const rs = results.filter(r => r.board === b.board);
    return { board: b.board, status: b.status, reason: b.reason, raw_count: b.raw_count, skipped_null_id: b.skipped.null_id, warnings: b.warnings,
      scored: b.status === 'ok' ? rs.length : null,
      keep: b.status === 'ok' ? count(rs, 'keep') : null, cannot_tell: b.status === 'ok' ? count(rs, 'cannot_tell') : null,
      reject: b.status === 'ok' ? count(rs, 'reject') : null, veto: b.status === 'ok' ? rs.filter(r => r.veto).length : null };
  }),
  totals: { scored: results.length, keep: count(results, 'keep'), cannot_tell: count(results, 'cannot_tell'), reject: count(results, 'reject'), veto: results.filter(r => r.veto).length,
    near_band: results.filter(r => r.score !== null && !r.veto && Math.abs(r.score - spec.threshold) <= spec.near_band).length },
};
const dir = resolve(ROOT, values.out, `v${spec.version}`);
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, 'results.jsonl'), results.map(r => JSON.stringify(r)).join('\n') + '\n');
writeFileSync(join(dir, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify({ out: dir.slice(ROOT.length + 1), ...summary.totals, boards: summary.boards.map(b => `${b.board}:${b.status}`) }));
