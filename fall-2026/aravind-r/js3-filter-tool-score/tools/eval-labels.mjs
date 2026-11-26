// Phase 5: a filter run's decisions against Aravind's hand labels, for ONE set (dev or heldout).
// "Surfaced" = keep or cannot_tell (the shortlist, FILTER.md §5.2). Positive = labeled relevant.
// The held-out set is refused unless --heldout-final is passed; each held-out evaluation is
// appended to phase5/heldout-log.jsonl so every look at held-out is on record.
// The label sheet is ENRICHED (8 of 20 per half are PM-titled): these counts are not population rates.
// Usage: node tools/eval-labels.mjs --run runs/filter/v1.1.0-e --set dev
//        node tools/eval-labels.mjs --run <run> --set heldout --heldout-final --why "<declared purpose>"
import { readFileSync, appendFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parseCsv } from '../src/csv.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { run: { type: 'string' }, set: { type: 'string' }, 'heldout-final': { type: 'boolean', default: false }, why: { type: 'string' } } });
if (!values.run || !['dev', 'heldout'].includes(values.set)) throw new Error('--run <dir> and --set dev|heldout are required');
if (values.set === 'heldout' && (!values['heldout-final'] || !values.why)) throw new Error('held-out needs --heldout-final and --why "<declared purpose>"');
const frozen = JSON.parse(readFileSync(join(ROOT, 'labels', `${values.set === 'heldout' ? 'heldout.frozen' : 'dev'}.json`), 'utf8'));
const ids = frozen.ids;
if (createHash('sha256').update([...ids].sort().join('\n')).digest('hex') !== frozen.sha256_of_ids) throw new Error(`${values.set} ids do not match their frozen hash`);
const labels = new Map(parseCsv(readFileSync(join(ROOT, 'labels', 'label-sheet.csv'), 'utf8')).filter(r => r.set === values.set).map(r => [`${r.board}:${r.posting_id}`, r.my_label]));
const summary = JSON.parse(readFileSync(join(ROOT, values.run, 'summary.json'), 'utf8'));
const res = new Map(readFileSync(join(ROOT, values.run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).map(r => [`${r.board}:${r.id}`, r]));
const t = { surfaced_relevant: 0, surfaced_not_relevant: 0, surfaced_cannot_tell_label: 0, rejected_relevant: 0, rejected_not_relevant: 0, rejected_cannot_tell_label: 0 };
const rows = [];
for (const k of ids) {
  const lab = labels.get(k); if (!lab) throw new Error(`${k}: no label`);
  const d = res.get(k).decision, s = d === 'reject' ? 'rejected' : 'surfaced';
  t[`${s}_${lab === 'cannot_tell' ? 'cannot_tell_label' : lab}`]++;
  rows.push({ posting: k, decision: d, label: lab });
}
const rel = t.surfaced_relevant + t.rejected_relevant, surf = t.surfaced_relevant + t.surfaced_not_relevant + t.surfaced_cannot_tell_label;
const out = { at: new Date().toISOString(), set: values.set, n: ids.length, run: values.run, spec_version: summary.spec_version, filter_sha256: summary.filter_sha256,
  labels: { relevant: rel, not_relevant: t.surfaced_not_relevant + t.rejected_not_relevant, cannot_tell: t.surfaced_cannot_tell_label + t.rejected_cannot_tell_label },
  counts: t, surfaced: surf, recall: rel ? `${t.surfaced_relevant}/${rel}` : 'n/a', precision: surf ? `${t.surfaced_relevant}/${surf}` : 'n/a (nothing surfaced)',
  note: 'Enriched sample (8 of 20 PM-titled). Counts, not population rates.', why: values.why ?? null };
if (values.set === 'heldout') appendFileSync(join(ROOT, 'phase5', 'heldout-log.jsonl'), JSON.stringify({ ...out, rows }) + '\n');
console.log(JSON.stringify(out, null, 1));
