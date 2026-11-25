// Computes the reject audit from Aravind's filled-in audit/audit-sheet.csv and audit/key.json.
// Every sample-based error figure is an ESTIMATE with an exact (Clopper-Pearson) 95% interval,
// for this snapshot and this filter version only, never a rate for all postings.
// Only the rows declared in audit/judging-plan.json (before any verdict) are counted; rows the
// plan leaves unjudged may stay empty, and any verdict on them is reported but not counted.
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

const plan = JSON.parse(readFileSync(join(ROOT, 'audit', 'judging-plan.json'), 'utf8'));
const toJudge = new Set(plan.to_judge), notJudged = new Set(plan.not_judged);
if (rows.length !== Object.keys(key).length) { console.error(`sheet has ${rows.length} rows, key has ${Object.keys(key).length}`); process.exit(2); }
const stray = rows.filter(r => !toJudge.has(r.audit_id) && !notJudged.has(r.audit_id));
if (stray.length) { console.error(`row(s) not in the judging plan: ${stray.map(r => r.audit_id).join(', ')}`); process.exit(2); }
const bad = rows.filter(r => toJudge.has(r.audit_id) && !VERDICTS.includes(r.my_verdict));
if (bad.length) { console.error(`${bad.length} planned row(s) without a valid my_verdict (${VERDICTS.join(' | ')}): ${bad.map(r => r.audit_id).join(', ')}`); process.exit(2); }
const invalid = rows.filter(r => r.my_verdict && !VERDICTS.includes(r.my_verdict));
if (invalid.length) { console.error(`invalid my_verdict on: ${invalid.map(r => `${r.audit_id}="${r.my_verdict}"`).join(', ')}`); process.exit(2); }
const offPlan = rows.filter(r => notJudged.has(r.audit_id) && r.my_verdict);

const joined = rows.filter(r => toJudge.has(r.audit_id)).map(r => ({ ...r, ...key[r.audit_id] }));
const inStratumAll = st => Object.entries(key).filter(([, v]) => v.strata.includes(st)).map(([a]) => a);
// Two passes. first = first_pass_verdict if the row was rechecked, else my_verdict (commit 1c9ce17b).
// second = my_verdict after the recheck (audit/recheck-plan.json). Without a recheck there is one pass.
const rechecked = joined.filter(r => r.first_pass_verdict);
const badFp = rechecked.filter(r => !VERDICTS.includes(r.first_pass_verdict));
if (badFp.length) { console.error(`invalid first_pass_verdict on: ${badFp.map(r => r.audit_id).join(', ')}`); process.exit(2); }
const PASSES = rechecked.length ? { first: r => r.first_pass_verdict || r.my_verdict, second: r => r.my_verdict } : { first: r => r.my_verdict };
const reasonOf = r => (r.my_note.match(/recheck \d{4}-\d{2}-\d{2}: (.*)$/) ?? [])[1] ?? '';
// An error is a decided posting whose decision disagrees with the hand verdict.
const isErrorBy = v => r => (r.decision === 'reject' && v(r) === 'relevant') || (r.decision === 'keep' && v(r) === 'not_relevant');
const pct = x => `${(100 * x).toFixed(1)}%`;
const out = { computed_at: new Date().toISOString(), spec_version: sample.spec_version, seed: sample.seed, passes: Object.keys(PASSES), strata: {} };
let md = `# Reject audit — results (spec v${sample.spec_version})\n\nComputed ${out.computed_at} from \`${values.sheet}\` (hand verdicts by Aravind) and \`audit/key.json\`. Sample drawn with seed ${sample.seed} (\`audit/sample.json\`).\n\n`
  + `## Judging plan (declared ${plan.declared_at.slice(0, 10)}, before any verdict)\n\n- ${plan.rule}.\n- Judged (${plan.to_judge.length}): ${plan.to_judge.join(', ')}.\n- Not judged (${plan.not_judged.length}): ${plan.not_judged.join(', ')}.\n- ${plan.note}\n- SHA-256 of the judged list: ${plan.sha256_of_to_judge}.\n`
  + (offPlan.length ? `- **Off-plan verdicts reported, not counted:** ${offPlan.map(r => `${r.audit_id}=${r.my_verdict}`).join(', ')}.\n` : '') + '\n';
out.plan_sha256 = plan.sha256_of_to_judge;

if (rechecked.length) {
  let rp = null; try { rp = JSON.parse(readFileSync(join(ROOT, 'audit', 'recheck-plan.json'), 'utf8')); } catch { /* reported below */ }
  const revised = rechecked.filter(r => r.first_pass_verdict !== r.my_verdict);
  const declared = rp?.ids ?? [];
  const undeclared = rechecked.filter(r => !declared.includes(r.audit_id)).map(r => r.audit_id);
  const open = declared.filter(id => !rechecked.some(r => r.audit_id === id));
  md += `## Recheck (second pass)\n\n`
    + `- Declared before the recheck in \`audit/recheck-plan.json\` (${rp?.declared_at ?? 'missing'}): ${declared.length} ids. Reason: ${rp?.reason ?? '(plan file missing)'}\n`
    + `- First-pass verdicts: commit \`${rp?.first_pass_commit ?? '?'}\`, kept per row in \`first_pass_verdict\`.\n`
    + `- **Rechecked ${rechecked.length}; revised ${revised.length}; unchanged ${rechecked.length - revised.length}.**${open.length ? ` Not yet rechecked: ${open.join(', ')}.` : ''}${undeclared.length ? ` **Rechecked but not declared:** ${undeclared.join(', ')}.` : ''}\n`
    + `- **Selection caveat:** ${rp?.selection_caveat ?? 'recheck rows were chosen after seeing the results.'}\n\n`
    + `| audit_id | title | first pass | second pass | reason |\n|---|---|---|---|---|\n`
    + rechecked.map(r => `| ${r.audit_id} | ${r.title} | ${r.first_pass_verdict} | ${r.my_verdict}${r.first_pass_verdict === r.my_verdict ? ' (unchanged)' : ''} | ${reasonOf(r)} |`).join('\n') + '\n\n';
  out.recheck = { declared: declared.length, rechecked: rechecked.length, revised: revised.length, revised_ids: revised.map(r => r.audit_id), open, undeclared };
}

// Each stratum is reported on its own. Strata are never pooled into one error rate: they were
// drawn from different populations (or selected, not drawn).
md += `Each stratum is reported separately. They are never pooled into one error rate.${rechecked.length ? ' Where two passes exist, both are shown; the second pass is the headline.' : ''}\n\n`;
const ciText = (x, n) => { const c = clopperPearson(x, n); return `${x} of ${n}: estimate ${pct(c.estimate)}, exact 95% interval ${pct(c.lower)} to ${pct(c.upper)}`; };
for (const s of ['random_reject', 'closest_call', 'kept', 'cannot_tell']) {
  const rs = joined.filter(r => r.strata.includes(s));
  const drawn = inStratumAll(s).length;
  const entry = { n: rs.length };
  md += `## ${s} (judged ${rs.length} of ${drawn} on the sheet)\n\n`;
  const per = {};
  for (const [p, v] of Object.entries(PASSES)) {
    const tally = Object.fromEntries(VERDICTS.map(x => [x, rs.filter(r => v(r) === x).length]));
    const errors = rs.filter(isErrorBy(v));
    per[p] = { tally, errors };
    entry[p] = { my_verdicts: tally, errors: errors.length, error_ids: errors.map(r => r.audit_id) };
    if (s === 'random_reject' && rs.length) { const c = clopperPearson(errors.length, rs.length); entry[p].interval_95 = [c.lower, c.upper]; }
  }
  const passNames = Object.keys(PASSES);
  md += passNames.length > 1
    ? `| pass | relevant | not_relevant | cannot_tell | ${s === 'kept' ? 'false keeps' : 'false rejects / disagreements'} |\n|---|---|---|---|---|\n` + passNames.map(p => `| ${p} | ${per[p].tally.relevant} | ${per[p].tally.not_relevant} | ${per[p].tally.cannot_tell} | ${per[p].errors.length} |`).join('\n') + '\n\n'
    : `My verdicts: ${VERDICTS.map(x => `${x} ${per.first.tally[x]}`).join(', ')}.\n\n`;
  const head = passNames.at(-1);
  if (s === 'random_reject' && rs.length) {
    const e = per[head].errors.length, ct = per[head].tally.cannot_tell, c = clopperPearson(e, rs.length);
    md += `**False rejects (I judged relevant), ${head} pass: ${ciText(e, rs.length)}.**${passNames.length > 1 ? ` First pass: ${ciText(per.first.errors.length, rs.length)}.` : ''}\n\n`
      + `What this can show: the sample is the first ${rs.length} of ${drawn} uniform draws (seeded order) from the ${sample.population.rejects} rejects in this snapshot, under spec v${sample.spec_version}. It estimates the false-reject share *within that population* only, not a rate for all postings, other boards, other dates, or other filter versions. ${e === 0 ? `Zero errors in ${rs.length} does not mean zero errors: the data are consistent with a false-reject share as high as ${pct(c.upper)}. ` : ''}`
      + `${ct ? `${ct} row(s) I judged cannot_tell are counted as not-errors; counted as errors, the interval would be ${(() => { const c2 = clopperPearson(e + ct, rs.length); return `${pct(c2.lower)} to ${pct(c2.upper)}`; })()}. ` : ''}`
      + `${passNames.length > 1 ? 'The second pass revised only rows chosen after seeing the filter results (see the selection caveat), so it is not a blind estimate; the first-pass figure is shown for that reason.' : ''}\n\n`;
  } else if (s === 'closest_call') {
    md += `**Disagreements (${head} pass): ${per[head].errors.length} of ${rs.length}**${passNames.length > 1 ? ` (first pass: ${per.first.errors.length})` : ''}. Decided rows only; cannot_tell rows are listed, not counted. These rows were *selected* by distance to the threshold, not sampled, so no population interval applies.\n\n`;
  } else if (s === 'kept') {
    md += rs.length ? `**False keeps (${head} pass): ${per[head].errors.length} of ${rs.length}.**\n\n` : `No postings were kept by spec v${sample.spec_version}, so there is nothing to sample. A false-keep rate cannot be estimated for this version.\n\n`;
  } else {
    md += `The filter abstained on these. My verdicts say what an answer would have been.\n\n`;
  }
  const show = rs.filter(r => passNames.some(p => isErrorBy(PASSES[p])(r)) || r.decision === 'cannot_tell');
  if (show.length) md += `| audit_id | title | decision | score | T | L | E (phrase) | P (terms) | ${passNames.length > 1 ? 'first | second' : 'my verdict'} | my note |\n|---|---|---|---|---|---|---|---|---|${passNames.length > 1 ? '---|' : ''}---|\n`
    + show.map(r => { const c = r.components ?? {}; return `| ${r.audit_id} | ${r.title} | ${r.decision} | ${r.score} | ${c.title?.value} | ${c.location?.value} | ${c.experience?.value} (${c.experience?.phrase ?? '—'}) | ${c.topic?.value} (${(c.topic?.terms ?? []).join(', ') || '—'}) | ${passNames.map(p => PASSES[p](r)).join(' | ')} | ${(r.my_note || '').replace(/\|/g, '/')} |`; }).join('\n') + '\n\n';
  out.strata[s] = entry;
}
const pmDrawn = inStratumAll('pm_reject');
md += `## Not checked\n\n`
  + `- **PM-titled rejects (pm_reject):** ${pmDrawn.length} drawn (seed ${sample.pm_reject_seed}) from a population of ${sample.population.pm_reject_pool} PM/product-titled rejects; **none judged**. No error estimate exists for PM-titled rejects, the group where a false reject would matter most.\n`
  + `- **Random rejects, draws ${inStratumAll('random_reject').length - joined.filter(r => r.strata.includes('random_reject')).length > 0 ? `${joined.filter(r => r.strata.includes('random_reject')).length + 1}-${inStratumAll('random_reject').length}` : 'none'}:** on the sheet, not judged, not counted.\n`;
out.not_checked = { pm_reject: { drawn: pmDrawn.length, population: sample.population.pm_reject_pool, judged: 0 }, random_reject_unjudged: inStratumAll('random_reject').filter(a => !toJudge.has(a)).length };
out.off_plan_verdicts = offPlan.map(r => r.audit_id);
writeFileSync(join(resolve(ROOT, values.out), 'RESULTS.md'), md);
writeFileSync(join(resolve(ROOT, values.out), 'results.json'), JSON.stringify(out, null, 2) + '\n');
console.log(md);
