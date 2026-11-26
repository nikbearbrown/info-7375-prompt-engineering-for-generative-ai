// Applies Aravind's Checkpoint 3 label decisions (shortlist/my-labels.json) to the claim table.
// Every claim takes Claude's proposed_label unless overridden. Each confirmed label is checked
// against the evidence rules (FILTER.md §2, with the 2026-11-25 location-field amendment):
// supported/contradicted need an exact quote from the body or the location field. Any violation
// stops the tool; nothing is written.
// Usage: node tools/confirm-claims.mjs [--claims shortlist/claims-justify.v1-v1.1.0-e.csv]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parseCsv, toCsv } from '../src/csv.mjs';
import { loadCorpus } from '../src/corpus.mjs';
import { quoteSource } from '../src/justify.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { claims: { type: 'string', default: 'shortlist/claims-justify.v1-v1.1.0-e.csv' } } });
const rows = parseCsv(readFileSync(join(ROOT, values.claims), 'utf8'));
const decisions = JSON.parse(readFileSync(join(ROOT, 'shortlist', 'my-labels.json'), 'utf8'));
const overrides = new Map(decisions.overrides.map(o => [o.claim, o]));
const posts = new Map(loadCorpus(ROOT).postings.map(p => [`${p.board}:${p.id}`, p]));
const ids = new Set(rows.map(r => `${r.audit_id}.${r.claim_no}`));
const unknown = [...overrides.keys()].filter(k => !ids.has(k));
if (unknown.length) throw new Error(`overrides name claims not in the table: ${unknown.join(', ')}`);

const errors = [], out = [];
for (const r of rows) {
  const id = `${r.audit_id}.${r.claim_no}`, o = overrides.get(id), p = posts.get(r.posting);
  const label = o?.label ?? r.proposed_label;
  const quote = o ? o.quote : (r.quote || null);
  const src = quote ? quoteSource(quote, { postingText: p.text, postingLocation: p.location }) : null;
  if (o && o.quote_source && src !== o.quote_source) errors.push(`${id}: quote source is ${src}, decisions file says ${o.quote_source}`);
  if (['supported', 'contradicted'].includes(label) && !src) errors.push(`${id}: ${label} needs an exact quote from the body or location field`);
  out.push({ ...r, my_label: label, my_quote: quote ?? '', my_quote_source: src ?? '', agrees_with_claude: label === r.proposed_label ? 'yes' : 'no', my_note: o?.note ?? 'accepted Claude\'s proposed label' });
}
if (errors.length) { console.error(errors.join('\n')); process.exit(2); }
const outPath = values.claims.replace(/claims-/, 'claims-confirmed-');
writeFileSync(join(ROOT, outPath), toCsv(out, [...Object.keys(rows[0]).filter(k => !['my_label', 'my_note'].includes(k)), 'my_label', 'my_quote', 'my_quote_source', 'agrees_with_claude', 'my_note']));
const tally = (key) => out.reduce((a, r) => (a[r[key]] = (a[r[key]] ?? 0) + 1, a), {});
const summary = { computed_at: new Date().toISOString(), claims: out.length, proposed: tally('proposed_label'), confirmed: tally('my_label'), disagreements: out.filter(r => r.agrees_with_claude === 'no').map(r => `${r.audit_id}.${r.claim_no}: ${r.proposed_label} -> ${r.my_label}`), kind: tally('kind'), abstained: out.filter(r => r.abstain === 'true').length, quote_source: tally('quote_source') };
writeFileSync(join(ROOT, 'shortlist', 'confirmed-summary.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 1));
