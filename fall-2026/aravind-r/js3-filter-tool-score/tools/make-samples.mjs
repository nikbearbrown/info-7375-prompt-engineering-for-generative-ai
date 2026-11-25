// Draws the Phase 2 audit sample and the Phase 5 label sheet from one filter run, with
// recorded seeds. Both sheets are BLIND: they show the posting, never the filter's decision,
// score, or matched words. Verdict and label columns are left empty for Aravind.
// Usage: node tools/make-samples.mjs [--run runs/filter/v1.0.0]
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCorpus } from '../src/corpus.mjs';
import { mulberry32, sample, shuffle } from '../src/rng.mjs';
import { toCsv } from '../src/csv.mjs';
import { boilerplateLines, roleText, ROLE_START } from '../src/boilerplate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { run: { type: 'string', default: 'runs/filter/v1.0.0' }, force: { type: 'boolean', default: false } } });
const AUDIT_SEED = 20261125, LABEL_SEED = 7375;
const N_RANDOM_REJECTS = 40, N_CLOSEST = 15, N_KEPT = 15;
const LABEL_HALF = 20, LABEL_PM_PER_HALF = 8;
const PM_TITLE = /\bproduct\b|\bprogram manager\b/i; // title only, independent of the filter

const summary = JSON.parse(readFileSync(join(ROOT, values.run, 'summary.json'), 'utf8'));
const results = readFileSync(join(ROOT, values.run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const key = r => `${r.board}:${r.id}`;
const corpus = loadCorpus(ROOT).postings;
const byKey = new Map(corpus.map(p => [key(p), p]));
const BP = boilerplateLines(corpus); // display only: excerpts skip lines shared by >= 20% of a board's postings
for (const d of ['audit', 'labels']) if (existsSync(join(ROOT, d, d === 'audit' ? 'audit-sheet.csv' : 'label-sheet.csv')) && !values.force) throw new Error(`${d}/ sheet exists; refusing to overwrite hand verdicts (use --force only on an empty sheet)`);

const oneLine = s => s.replace(/\s+/g, ' ').trim();
// Display only: start at the role section when a common heading is present, else after boilerplate.
const excerpt = p => {
  let t = oneLine(roleText(p, BP) || p.text);
  const m = t.search(ROLE_START); if (m > 0) t = '… ' + t.slice(m);
  return t.length > 500 ? t.slice(0, 500) + ' …' : t;
};
function writePosting(file, p, sheetId) {
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, `# ${sheetId}: ${p.title ?? '(no title)'}\n\n- board: ${p.board}\n- id: ${p.id}\n- location: ${p.location ?? '(missing)'}\n- department: ${p.department ?? '(missing)'}\n- url: ${p.url ?? '(missing)'}\n\n## Posting text (normalized, as the filter saw it)\n\n${p.text}\n`);
}

// ---------- audit ----------
const rand = mulberry32(AUDIT_SEED);
const rejects = results.filter(r => r.decision === 'reject');
const kept = results.filter(r => r.decision === 'keep');
const scored = results.filter(r => r.score !== null && !r.veto);
const strata = new Map(); // key -> Set of strata
const add = (r, s) => { if (!strata.has(key(r))) strata.set(key(r), new Set()); strata.get(key(r)).add(s); };
sample(rejects, N_RANDOM_REJECTS, rand).forEach(r => add(r, 'random_reject'));
[...scored].sort((a, b) => Math.abs(a.score - summary.threshold) - Math.abs(b.score - summary.threshold) || key(a).localeCompare(key(b)))
  .slice(0, N_CLOSEST).forEach(r => add(r, 'closest_call'));
(kept.length <= N_KEPT ? kept : sample(kept, N_KEPT, rand)).forEach(r => add(r, 'kept'));
results.filter(r => r.decision === 'cannot_tell').forEach(r => add(r, 'cannot_tell'));

const auditKeys = shuffle([...strata.keys()].sort(), rand);
const auditRows = [], auditKey = {};
auditKeys.forEach((k, i) => {
  const id = `A${String(i + 1).padStart(3, '0')}`, p = byKey.get(k), r = results.find(x => key(x) === k);
  writePosting(join(ROOT, 'audit', 'postings', `${id}.md`), p, id);
  auditRows.push({ audit_id: id, board: p.board, title: p.title, location: p.location, department: p.department, excerpt: excerpt(p), posting_file: `audit/postings/${id}.md`, my_verdict: '', my_note: '' });
  auditKey[id] = { board: r.board, id: r.id, strata: [...strata.get(k)].sort(), decision: r.decision, score: r.score, lo: r.lo, hi: r.hi, veto: r.veto, components: r.components, unknown: r.unknown };
});
writeFileSync(join(ROOT, 'audit', 'audit-sheet.csv'), toCsv(auditRows, ['audit_id', 'board', 'title', 'location', 'department', 'excerpt', 'posting_file', 'my_verdict', 'my_note']));
writeFileSync(join(ROOT, 'audit', 'key.json'), JSON.stringify(auditKey, null, 2) + '\n');
const strataCounts = {}; for (const v of Object.values(auditKey)) for (const s of v.strata) strataCounts[s] = (strataCounts[s] ?? 0) + 1;
writeFileSync(join(ROOT, 'audit', 'sample.json'), JSON.stringify({
  drawn_at: new Date().toISOString(), from_run: values.run, spec_version: summary.spec_version, filter_sha256: summary.filter_sha256,
  seed: AUDIT_SEED, prng: 'mulberry32 (src/rng.mjs)',
  method: {
    random_reject: `${N_RANDOM_REJECTS} drawn uniformly without replacement from all ${rejects.length} rejects (first use of the PRNG)`,
    closest_call: `the ${N_CLOSEST} scored, non-vetoed postings with the smallest |score - threshold| (threshold ${summary.threshold}); ties by board:id`,
    kept: kept.length <= N_KEPT ? `all ${kept.length} kept postings` : `${N_KEPT} drawn from ${kept.length} kept`,
    cannot_tell: 'all cannot_tell postings',
    rows: 'one row per posting; a posting in several strata appears once and counts in each; row order shuffled with the same PRNG',
  },
  population: { rejects: rejects.length, kept: kept.length, cannot_tell: results.length - rejects.length - kept.length, scored: results.length },
  rows: auditRows.length, strata_counts: strataCounts,
}, null, 2) + '\n');

// ---------- labels (separate from the audit) ----------
const lrand = mulberry32(LABEL_SEED);
const auditSet = new Set(auditKeys);
const pool = results.filter(r => !auditSet.has(key(r)));
const pmPool = pool.filter(r => PM_TITLE.test(r.title ?? '')).sort((a, b) => key(a).localeCompare(key(b)));
const otherPool = pool.filter(r => !PM_TITLE.test(r.title ?? '')).sort((a, b) => key(a).localeCompare(key(b)));
const pm = sample(pmPool, 2 * LABEL_PM_PER_HALF, lrand), other = sample(otherPool, 2 * (LABEL_HALF - LABEL_PM_PER_HALF), lrand);
const halves = {
  dev: [...pm.slice(0, LABEL_PM_PER_HALF), ...other.slice(0, LABEL_HALF - LABEL_PM_PER_HALF)],
  heldout: [...pm.slice(LABEL_PM_PER_HALF), ...other.slice(LABEL_HALF - LABEL_PM_PER_HALF)],
};
const labelRows = [];
let n = 0;
for (const r of shuffle([...halves.dev.map(r => ['dev', r]), ...halves.heldout.map(r => ['heldout', r])], lrand)) {
  const [set, res] = r, p = byKey.get(key(res)), id = `L${String(++n).padStart(2, '0')}`;
  writePosting(join(ROOT, 'labels', 'postings', `${id}.md`), p, id);
  labelRows.push({ label_id: id, set, board: p.board, posting_id: p.id, title: p.title, location: p.location, department: p.department, excerpt: excerpt(p), posting_file: `labels/postings/${id}.md`, my_label: '', my_note: '' });
}
writeFileSync(join(ROOT, 'labels', 'label-sheet.csv'), toCsv(labelRows, ['label_id', 'set', 'board', 'posting_id', 'title', 'location', 'department', 'excerpt', 'posting_file', 'my_label', 'my_note']));
const frozen = set => {
  const ids = halves[set].map(key).sort();
  return { set, frozen_at: new Date().toISOString(), seed: LABEL_SEED, prng: 'mulberry32 (src/rng.mjs)', n: ids.length,
    pm_titled: halves[set].filter(r => PM_TITLE.test(r.title ?? '')).length, ids, sha256_of_ids: createHash('sha256').update(ids.join('\n')).digest('hex') };
};
writeFileSync(join(ROOT, 'labels', 'heldout.frozen.json'), JSON.stringify(frozen('heldout'), null, 2) + '\n');
writeFileSync(join(ROOT, 'labels', 'dev.json'), JSON.stringify(frozen('dev'), null, 2) + '\n');
writeFileSync(join(ROOT, 'labels', 'sample.json'), JSON.stringify({
  drawn_at: new Date().toISOString(), from_run: values.run, seed: LABEL_SEED, prng: 'mulberry32 (src/rng.mjs)',
  pm_title_regex: String(PM_TITLE), excluded: `the ${auditSet.size} audit postings`,
  pool: { pm_titled: pmPool.length, other: otherPool.length },
  method: `${2 * LABEL_PM_PER_HALF} drawn from PM/product-titled pool, ${2 * (LABEL_HALF - LABEL_PM_PER_HALF)} from the rest; first half of each to dev, second to held-out; rows shuffled`,
  enriched: `PM/product-titled postings are ${pmPool.length} of ${pool.length} in the pool but ${2 * LABEL_PM_PER_HALF} of ${2 * LABEL_HALF} on the sheet. Precision/recall on this sheet are NOT population rates.`,
}, null, 2) + '\n');
console.log(JSON.stringify({ audit_rows: auditRows.length, strataCounts, label_rows: labelRows.length, pm_pool: pmPool.length, other_pool: otherPool.length }));
