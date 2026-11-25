// Computes the reject audit from Aravind's filled-in audit/audit-sheet.csv and audit/key.json.
// Every sample-based error figure is an ESTIMATE with an exact (Clopper-Pearson) 95% interval,
// for this snapshot and this filter version only, never a rate for all postings.
// Usage: node tools/audit-results.mjs [--sheet audit/audit-sheet.csv] [--out audit]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parseCsv } from '../src/csv.mjs';
import { clopperPearson } from '../src/stats.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { sheet: { type: 'string', default: 'audit/audit-sheet.csv' }, out: { type: 'string', default: 'audit' } } });
const VERDICTS = ['relevant', 'not_relevant', 'cannot_tell'];
const rows = parseCsv(readFileSync(resolve(ROOT, values.sheet), 'utf8'));
const key = JSON.parse(readFileSync(join(ROOT, 'audit', 'key.json'), 'utf8'));
const sample = JSON.parse(readFileSync(join(ROOT, 'audit', 'sample.json'), 'utf8'));

const bad = rows.filter(r => !VERDICTS.includes(r.my_verdict));
if (bad.length) { console.error(`${bad.length} row(s) without a valid my_verdict (${VERDICTS.join(' | ')}): ${bad.map(r => r.audit_id).join(', ')}`); process.exit(2); }
if (rows.length !== Object.keys(key).length) { console.error(`sheet has ${rows.length} rows, key has ${Object.keys(key).length}`); process.exit(2); }

const joined = rows.map(r => ({ ...r, ...key[r.audit_id] }));
// An error is a decided posting whose decision disagrees with the hand verdict.
const isError = r => (r.decision === 'reject' && r.my_verdict === 'relevant') || (r.decision === 'keep' && r.my_verdict === 'not_relevant');
const pct = x => `${(100 * x).toFixed(1)}%`;
const out = { computed_at: new Date().toISOString(), spec_version: sample.spec_version, seed: sample.seed, strata: {} };
let md = `# Reject audit — results (spec v${sample.spec_version})\n\nComputed ${out.computed_at} from \`${values.sheet}\` (hand verdicts by Aravind) and \`audit/key.json\`. Sample drawn with seed ${sample.seed} (\`audit/sample.json\`).\n\n`;

// Each stratum is reported on its own. Strata are never pooled into one error rate: they were
// drawn from different populations (or selected, not drawn).
md += `Each stratum is reported separately. They are never pooled into one error rate.\n\n`;
for (const s of ['random_reject', 'pm_reject', 'closest_call', 'kept', 'cannot_tell']) {
  const rs = joined.filter(r => r.strata.includes(s));
  const tally = Object.fromEntries(VERDICTS.map(v => [v, rs.filter(r => r.my_verdict === v).length]));
  const errors = rs.filter(isError);
  const entry = { n: rs.length, my_verdicts: tally, errors: errors.length, error_ids: errors.map(r => r.audit_id) };
  md += `## ${s} (n = ${rs.length})\n\nMy verdicts: ${VERDICTS.map(v => `${v} ${tally[v]}`).join(', ')}.\n\n`;
  if ((s === 'random_reject' || s === 'pm_reject') && rs.length) {
    const ci = clopperPearson(errors.length, rs.length);
    const popN = s === 'random_reject' ? sample.population.rejects : sample.population.pm_reject_pool;
    const popDesc = s === 'random_reject' ? `the ${popN} rejects in this snapshot` : `the ${popN} PM/product-titled rejects not already on the audit or label sheet`;
    entry.interval_95 = [ci.lower, ci.upper];
    md += `**False rejects (I judged relevant): ${errors.length} of ${rs.length}.** Estimate ${pct(ci.estimate)}, exact 95% interval ${pct(ci.lower)} to ${pct(ci.upper)}.\n\n`
      + `What this can show: the sample is ${rs.length} of ${popDesc}, under spec v${sample.spec_version}. It estimates the false-reject share *within that population* only. It is not a rate for all postings, other boards, other dates, or other filter versions. ${errors.length === 0 ? `Zero errors in ${rs.length} does not mean zero errors: the data are consistent with a false-reject share as high as ${pct(ci.upper)}.` : ''}`
      + ` ${tally.cannot_tell ? `${tally.cannot_tell} row(s) I could not judge are counted as not-errors; with them counted as errors the interval would be ${(() => { const c = clopperPearson(errors.length + tally.cannot_tell, rs.length); return `${pct(c.lower)} to ${pct(c.upper)}`; })()}.` : ''}\n\n`;
  } else if (s === 'closest_call') {
    md += `**Disagreements: ${errors.length} of ${rs.length}** (decided rows only; cannot_tell rows are listed, not scored). These were *selected* by distance to the threshold, not sampled, so no population interval applies.\n\n`;
  } else if (s === 'kept') {
    md += rs.length ? `**False keeps (I judged not relevant): ${errors.length} of ${rs.length}.** ${sample.method.kept.startsWith('all') ? 'This is every kept posting (a census), so no interval is needed.' : (() => { const c = clopperPearson(errors.length, rs.length); return `Exact 95% interval ${pct(c.lower)} to ${pct(c.upper)}.`; })()}\n\n` : `No postings were kept by spec v${sample.spec_version}, so there is nothing to sample. A false-keep rate cannot be estimated for this version.\n\n`;
  } else {
    md += `The filter abstained on these. My verdicts above say what an answer would have been.\n\n`;
  }
  const show = rs.filter(r => isError(r) || r.decision === 'cannot_tell');
  if (show.length) md += `| audit_id | title | decision | score | T | L | E (phrase) | P (terms) | my verdict | my note |\n|---|---|---|---|---|---|---|---|---|---|\n`
    + show.map(r => { const c = r.components ?? {}; return `| ${r.audit_id} | ${r.title} | ${r.decision} | ${r.score} | ${c.title?.value} | ${c.location?.value} | ${c.experience?.value} (${c.experience?.phrase ?? '—'}) | ${c.topic?.value} (${(c.topic?.terms ?? []).join(', ') || '—'}) | ${r.my_verdict} | ${r.my_note || ''} |`; }).join('\n') + '\n\n';
  out.strata[s] = entry;
}
writeFileSync(join(resolve(ROOT, values.out), 'RESULTS.md'), md);
writeFileSync(join(resolve(ROOT, values.out), 'results.json'), JSON.stringify(out, null, 2) + '\n');
console.log(md);
