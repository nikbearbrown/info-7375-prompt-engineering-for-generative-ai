// Phase 5 addendum (Aravind, 2026-11-25): a BLIND sheet of exactly the postings that the
// threshold-0.70 experiment keeps but the final filter v1.1.0-e does not. POST HOC, chosen BY the
// filter difference: it is not held-out and not a random sample. The sheet shows no score,
// decision, or version; those are in phase5/diffset/key.json (do not open before labeling).
// Same columns as the label sheet, so tools/judge-audit.mjs runs on it in label mode.
// Usage: node tools/make-diffset.mjs
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCorpus } from '../src/corpus.mjs';
import { boilerplateLines, roleText, ROLE_START } from '../src/boilerplate.mjs';
import { mulberry32, shuffle } from '../src/rng.mjs';
import { toCsv, parseCsv } from '../src/csv.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SEED = 20261127, OUT = join(ROOT, 'phase5', 'diffset');
const sheetPath = join(OUT, 'diffset-sheet.csv');
if (existsSync(sheetPath) && parseCsv(readFileSync(sheetPath, 'utf8')).some(r => r.my_label || r.my_note)) throw new Error('diffset sheet has labels; refusing to overwrite');
const load = d => new Map(readFileSync(join(ROOT, d, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).map(r => [`${r.board}:${r.id}`, r]));
const base = load('runs/filter/v1.1.0-e'), exp = load('runs/phase5/v1.1.0-e.exp1');
const added = [...exp.values()].filter(r => r.decision === 'keep' && base.get(`${r.board}:${r.id}`).decision !== 'keep').map(r => `${r.board}:${r.id}`).sort();
const corpus = loadCorpus(ROOT).postings, byKey = new Map(corpus.map(p => [`${p.board}:${p.id}`, p])), BP = boilerplateLines(corpus);
const audit = JSON.parse(readFileSync(join(ROOT, 'audit', 'key.json'), 'utf8')), auditOf = Object.fromEntries(Object.entries(audit).map(([a, v]) => [`${v.board}:${v.id}`, a]));
const labelRows = parseCsv(readFileSync(join(ROOT, 'labels', 'label-sheet.csv'), 'utf8')), labelOf = Object.fromEntries(labelRows.map(r => [`${r.board}:${r.posting_id}`, `${r.label_id} (${r.set})`]));
const excerpt = p => { let t = (roleText(p, BP) || p.text).replace(/\s+/g, ' ').trim(); const m = t.search(ROLE_START); if (m > 0) t = '… ' + t.slice(m); return t.length > 500 ? t.slice(0, 500) + ' …' : t; };
mkdirSync(join(OUT, 'postings'), { recursive: true });
const rows = [], key = {};
shuffle(added, mulberry32(SEED)).forEach((k, i) => {
  const id = `D${String(i + 1).padStart(2, '0')}`, p = byKey.get(k);
  writeFileSync(join(OUT, 'postings', `${id}.md`), `# ${id}: ${p.title}\n\n- board: ${p.board}\n- id: ${p.id}\n- location: ${p.location ?? '(missing)'}\n- department: ${p.department ?? '(missing)'}\n- url: ${p.url ?? '(missing)'}\n\n## Posting text (normalized, as the filter saw it)\n\n${p.text}\n`);
  rows.push({ label_id: id, set: 'diffset', board: p.board, posting_id: p.id, title: p.title, location: p.location, department: p.department, excerpt: excerpt(p), posting_file: `phase5/diffset/postings/${id}.md`, my_label: '', my_note: '' });
  const b = base.get(k), e = exp.get(k);
  key[id] = { posting: k, v1_1_0_e: { decision: b.decision, score: b.score, lo: b.lo, hi: b.hi }, exp1: { decision: e.decision, score: e.score }, audit_row: auditOf[k] ?? null, label_row: labelOf[k] ?? null };
});
writeFileSync(sheetPath, toCsv(rows, ['label_id', 'set', 'board', 'posting_id', 'title', 'location', 'department', 'excerpt', 'posting_file', 'my_label', 'my_note']));
writeFileSync(join(OUT, 'key.json'), JSON.stringify({ built_at: new Date().toISOString(), seed: SEED, rule: 'exp1 (threshold 0.70) keep AND v1.1.0-e not keep', post_hoc: true, heldout: false, n: rows.length, rows: key }, null, 2) + '\n');
console.log(JSON.stringify({ n: rows.length, already_audit_rows: Object.values(key).filter(v => v.audit_row).length, label_rows: Object.values(key).filter(v => v.label_row).length }));
