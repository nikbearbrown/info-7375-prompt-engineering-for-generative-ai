// Computes the reject audit from Aravind's hand verdicts (audit/audit-sheet.csv) and the filter's
// decisions. Every sample-based error figure is an ESTIMATE with an exact (Clopper-Pearson) 95%
// interval, for this snapshot only, never a rate for all postings.
//
// Views, reported side by side:
//   A   v1.0.0 decisions (audit/key.json, the run the sample was drawn from) vs FIRST-pass verdicts
//   B   a later run's decisions (--run, default runs/filter/v1.1.0-e, the final filter) vs FINAL verdicts
//   A'  v1.0.0 decisions vs FINAL verdicts (summary only: isolates the verdict change)
// first pass = first_pass_verdict where the row was rechecked, else my_verdict (commit 1c9ce17b).
// final      = my_verdict (after the recheck in audit/recheck-plan.json).
// Only rows declared in audit/judging-plan.json are counted. Strata come from the v1.0.0 draw.
//
// Usage: node tools/audit-results.mjs [--sheet audit/audit-sheet.csv] [--run runs/filter/v1.1.0-e] [--out audit]
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parseCsv } from '../src/csv.mjs';
import { clopperPearson } from '../src/stats.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { sheet: { type: 'string', default: 'audit/audit-sheet.csv' }, run: { type: 'string', default: 'runs/filter/v1.1.0-e' }, out: { type: 'string', default: 'audit' } } });
const VERDICTS = ['relevant', 'not_relevant', 'cannot_tell'];
const STRATA = ['random_reject', 'closest_call', 'kept', 'cannot_tell'];
const readJson = p => JSON.parse(readFileSync(join(ROOT, p), 'utf8'));
const rows = parseCsv(readFileSync(resolve(ROOT, values.sheet), 'utf8'));
const key = readJson('audit/key.json');
const sample = readJson('audit/sample.json');
const plan = readJson('audit/judging-plan.json');
const recheckPlan = existsSync(join(ROOT, 'audit', 'recheck-plan.json')) ? readJson('audit/recheck-plan.json') : null;
const named = existsSync(join(ROOT, 'audit', 'named-false-friends.json')) ? readJson('audit/named-false-friends.json') : [];
const die = m => { console.error(m); process.exit(2); };

// ---------- validation ----------
const toJudge = new Set(plan.to_judge), notJudged = new Set(plan.not_judged);
if (rows.length !== Object.keys(key).length) die(`sheet has ${rows.length} rows, key has ${Object.keys(key).length}`);
const stray = rows.filter(r => !toJudge.has(r.audit_id) && !notJudged.has(r.audit_id));
if (stray.length) die(`row(s) not in the judging plan: ${stray.map(r => r.audit_id).join(', ')}`);
const missing = rows.filter(r => toJudge.has(r.audit_id) && !VERDICTS.includes(r.my_verdict));
if (missing.length) die(`${missing.length} planned row(s) without a valid my_verdict (${VERDICTS.join(' | ')}): ${missing.map(r => r.audit_id).join(', ')}`);
const invalid = rows.filter(r => (r.my_verdict && !VERDICTS.includes(r.my_verdict)) || (r.first_pass_verdict && !VERDICTS.includes(r.first_pass_verdict)));
if (invalid.length) die(`invalid verdict on: ${invalid.map(r => r.audit_id).join(', ')}`);
const offPlan = rows.filter(r => notJudged.has(r.audit_id) && r.my_verdict);

// ---------- decisions ----------
const runPath = join(ROOT, values.run, 'results.jsonl');
const later = existsSync(runPath) ? new Map(readFileSync(runPath, 'utf8').trim().split('\n').map(JSON.parse).map(r => [`${r.board}:${r.id}`, r])) : null;
const laterSummary = later ? readJson(join(values.run, 'summary.json')) : null;
const joined = rows.filter(r => toJudge.has(r.audit_id)).map(r => {
  const k = key[r.audit_id], l = later?.get(`${k.board}:${k.id}`);
  return { ...r, ...k, d_a: k.decision, d_b: l?.decision ?? null, comp_b: l?.components ?? null };
});
const first = r => r.first_pass_verdict || r.my_verdict;
const final = r => r.my_verdict;
const rechecked = joined.filter(r => r.first_pass_verdict);

const VIEWS = [{ id: 'A', label: `v${sample.spec_version} decisions vs first-pass verdicts`, decision: r => r.d_a, verdict: first, comp: r => r.components }];
if (later) VIEWS.push({ id: 'B', label: `v${laterSummary.spec_version} decisions vs final verdicts`, decision: r => r.d_b, verdict: final, comp: r => r.comp_b });
if (later && rechecked.length) VIEWS.push({ id: "A'", label: `v${sample.spec_version} decisions vs final verdicts (summary only: isolates the verdict change from the rule change)`, decision: r => r.d_a, verdict: final, comp: r => r.components, summaryOnly: true });

const isError = (v, r) => (v.decision(r) === 'reject' && v.verdict(r) === 'relevant') || (v.decision(r) === 'keep' && v.verdict(r) === 'not_relevant');
const pct = x => `${(100 * x).toFixed(1)}%`;
const ci = (x, n) => { const c = clopperPearson(x, n); return { x, n, estimate: c.estimate, lower: c.lower, upper: c.upper, text: `${x} of ${n} (estimate ${pct(c.estimate)}, exact 95% interval ${pct(c.lower)} to ${pct(c.upper)})` }; };
const inStratum = s => joined.filter(r => r.strata.includes(s));
const drawnIn = s => Object.values(key).filter(v => v.strata.includes(s)).length;
const reasonOf = r => (r.my_note.match(/recheck \d{4}-\d{2}-\d{2}: (.*)$/) ?? [])[1] ?? '';
const cell = s => String(s ?? '').replace(/\|/g, '/');

// ---------- report ----------
const out = { computed_at: new Date().toISOString(), sampled_from: `v${sample.spec_version}`, compared_run: later ? values.run : null, plan_sha256: plan.sha256_of_to_judge, views: {} };
let md = `# Reject audit — results\n\nComputed ${out.computed_at} from \`${values.sheet}\` (hand verdicts by Aravind), \`audit/key.json\` (v${sample.spec_version} decisions)${later ? ` and \`${values.run}\` (v${laterSummary.spec_version} decisions)` : ''}. Sample drawn from the v${sample.spec_version} run with seed ${sample.seed} (\`audit/sample.json\`).\n\n`
  + `## Judging plan (declared ${plan.declared_at.slice(0, 10)}, before any verdict)\n\n- ${plan.rule}.\n- Judged (${plan.to_judge.length}): ${plan.to_judge.join(', ')}.\n- Not judged (${plan.not_judged.length}): ${plan.not_judged.join(', ')}.\n- ${plan.note}\n- SHA-256 of the judged list: ${plan.sha256_of_to_judge}.\n`
  + (offPlan.length ? `- **Off-plan verdicts reported, not counted:** ${offPlan.map(r => `${r.audit_id}=${r.my_verdict}`).join(', ')}.\n` : '') + '\n';

if (rechecked.length) {
  const revised = rechecked.filter(r => r.first_pass_verdict !== r.my_verdict);
  const declared = recheckPlan?.ids ?? [];
  const undeclared = rechecked.filter(r => !declared.includes(r.audit_id)).map(r => r.audit_id);
  const open = declared.filter(id => !rechecked.some(r => r.audit_id === id));
  md += `## Recheck (second pass)\n\n`
    + `- Declared before the recheck in \`audit/recheck-plan.json\` (${recheckPlan?.declared_at ?? 'missing'}; ${recheckPlan?.amended ? `amended ${recheckPlan.amended}` : 'not amended'}): ${declared.length} ids.\n`
    + `- Definition used: ${recheckPlan?.definition ?? '(not recorded)'}.\n`
    + `- Reason: ${recheckPlan?.reason ?? '(plan file missing)'}\n`
    + `- **Rechecked ${rechecked.length}; revised ${revised.length}; unchanged ${rechecked.length - revised.length}.**${open.length ? ` Not yet rechecked: ${open.join(', ')}.` : ''}${undeclared.length ? ` **Rechecked but not declared:** ${undeclared.join(', ')}.` : ''}\n`
    + `- **Selection caveat:** ${recheckPlan?.selection_caveat ?? 'recheck rows were chosen after seeing the results.'}\n`
    + `- **Definition caveat:** the relevance definition changed between the passes (persona corrected after the first-pass results, \`f3cefa22\`).${later ? ` View B measures v${laterSummary.spec_version} on rows whose results motivated it (dev use), so it is not an independent test; the held-out labels are.` : ''}\n\n`
    + `| audit_id | title | first pass | final | reason (Aravind's note) |\n|---|---|---|---|---|\n`
    + rechecked.map(r => `| ${r.audit_id} | ${cell(r.title)} | ${r.first_pass_verdict} | ${r.my_verdict}${r.first_pass_verdict === r.my_verdict ? ' (unchanged)' : ''} | ${cell(reasonOf(r))} |`).join('\n') + '\n\n';
  out.recheck = { declared: declared.length, rechecked: rechecked.length, revised: revised.length, revised_ids: revised.map(r => r.audit_id), open, undeclared };
}

md += `## Side by side\n\nEach stratum is reported separately; strata are never pooled into one error rate. An error is a reject judged relevant or a keep judged not_relevant. cannot_tell decisions and cannot_tell verdicts are not counted as errors (they are listed in the views below).\n\n`
  + `| stratum | judged | ${VIEWS.map(v => `view ${v.id} errors`).join(' | ')} |\n|---|---|${VIEWS.map(() => '---|').join('')}\n`;
for (const s of STRATA) {
  const rs = inStratum(s);
  md += `| ${s} | ${rs.length} of ${drawnIn(s)} | ${VIEWS.map(v => { const e = rs.filter(r => isError(v, r)).length; return s === 'random_reject' && rs.length ? ci(e, rs.length).text : String(e); }).join(' | ')} |\n`;
}
md += `\n${VIEWS.map(v => `- **View ${v.id}:** ${v.label}.`).join('\n')}\n`
  + `- The random_reject rows are a uniform sample of **v${sample.spec_version}'s** ${sample.population.rejects} rejects. Under a later version they measure how that version does on those same postings; they are not a sample of the later version's rejects.\n\n`;

for (const v of VIEWS.filter(v => !v.summaryOnly)) {
  md += `## View ${v.id}: ${v.label}\n\n`;
  out.views[v.id] = { label: v.label, strata: {} };
  for (const s of STRATA) {
    const rs = inStratum(s);
    const tally = Object.fromEntries(VERDICTS.map(x => [x, rs.filter(r => v.verdict(r) === x).length]));
    const dec = Object.fromEntries(['keep', 'cannot_tell', 'reject'].map(x => [x, rs.filter(r => v.decision(r) === x).length]));
    const errors = rs.filter(r => isError(v, r));
    const entry = { n: rs.length, verdicts: tally, decisions: dec, errors: errors.length, error_ids: errors.map(r => r.audit_id) };
    md += `### ${s} (judged ${rs.length} of ${drawnIn(s)})\n\nVerdicts: ${VERDICTS.map(x => `${x} ${tally[x]}`).join(', ')}. Decisions: ${Object.entries(dec).map(([k, n]) => `${k} ${n}`).join(', ')}.\n\n`;
    if (s === 'random_reject' && rs.length) {
      const c = ci(errors.length, rs.length); entry.interval_95 = [c.lower, c.upper];
      md += `**Errors: ${c.text}.** What this can show: the first ${rs.length} of ${drawnIn(s)} uniform draws (seeded order) from the ${sample.population.rejects} v${sample.spec_version} rejects in this snapshot. It estimates the error share within that population only, not for all postings, boards, dates, or versions.${errors.length === 0 ? ` Zero errors does not mean zero: the data allow up to ${pct(c.upper)}.` : ''}${tally.cannot_tell ? ` ${tally.cannot_tell} cannot_tell verdict(s) are counted as not-errors; counted as errors: ${ci(errors.length + tally.cannot_tell, rs.length).text}.` : ''}\n\n`;
    } else if (s === 'closest_call') md += `**Errors: ${errors.length} of ${rs.length}.** Selected by distance to the v${sample.spec_version} threshold, not sampled: no population interval applies.\n\n`;
    else if (s === 'kept') md += rs.length ? `**Errors: ${errors.length} of ${rs.length}.**\n\n` : `v${sample.spec_version} kept nothing, so this stratum is empty.\n\n`;
    const show = rs.filter(r => isError(v, r) || v.decision(r) !== 'reject' || v.verdict(r) === 'cannot_tell');
    if (show.length) md += `| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |\n|---|---|---|---|---|---|---|---|---|\n`
      + show.map(r => { const c = v.comp(r) ?? {}; return `| ${r.audit_id} | ${cell(r.title)} | ${v.decision(r)} | ${v.verdict(r)}${isError(v, r) ? ' **(error)**' : ''} | ${c.title?.value} | ${c.location?.value} | ${c.experience?.value} (${c.experience?.phrase ?? '—'}) | ${c.topic?.value} (${(c.topic?.terms ?? []).join(', ') || '—'}) | ${cell(r.my_note)} |`; }).join('\n') + '\n\n';
    out.views[v.id].strata[s] = entry;
  }
}

if (named.length) {
  const ROLE = { primary: 'Primary false friend', secondary: 'Secondary note', known_limit: 'Known limit' };
  md += `## Named false friends (Aravind's call, from postings judged by hand)\n\n`
    + named.map(f => `- **${ROLE[f.role] ?? 'False friend'}: "${f.term}"**, named by ${f.named_by} on ${f.date}.${f.rows.length ? ` Rows: ${f.rows.join(', ')}.` : ''} ${f.why}\n  - Text: ${f.line}`).join('\n') + '\n\n';
  out.named_false_friends = named;
}

const pm = Object.values(key).filter(v => v.strata.includes('pm_reject')).length;
md += `## Not checked\n\n`
  + `- **PM-titled rejects (pm_reject):** ${pm} drawn (seed ${sample.pm_reject_seed}) from ${sample.population.pm_reject_pool} PM/product-titled v${sample.spec_version} rejects; **none judged**. No error estimate exists for PM-titled rejects, where a false reject matters most.\n`
  + `- **Random rejects, draws ${inStratum('random_reject').length + 1}-${drawnIn('random_reject')}:** on the sheet, not judged, not counted.\n`
  + (rechecked.length ? `- **Recheck coverage:** the ${joined.length - rechecked.length} judged rows outside the recheck plan keep their first-pass verdict under the corrected definition.\n` : '');
out.not_checked = { pm_reject: { drawn: pm, population: sample.population.pm_reject_pool, judged: 0 }, random_reject_unjudged: drawnIn('random_reject') - inStratum('random_reject').length };
out.off_plan_verdicts = offPlan.map(r => r.audit_id);
writeFileSync(join(resolve(ROOT, values.out), 'RESULTS.md'), md);
writeFileSync(join(resolve(ROOT, values.out), 'results.json'), JSON.stringify(out, null, 2) + '\n');
console.log(md);
