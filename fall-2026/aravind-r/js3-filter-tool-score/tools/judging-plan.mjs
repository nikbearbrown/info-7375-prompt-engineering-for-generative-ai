// Declares, BEFORE any verdict, which audit rows Aravind judges (decision in chat, 2026-11-25):
// the first 30 of the 40 random rejects in seeded draw order, plus all 15 closest calls.
// A031-equivalents (draws 31-40) and the PM stratum (A056-A070) stay unjudged.
// The draw order is recomputed exactly as tools/make-samples.mjs drew it (seed 20261125,
// first use of the PRNG), and checked against audit/key.json. Lists are written sorted, without
// stratum labels, so the plan file does not unblind the sheet.
// Usage: node tools/judging-plan.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mulberry32, sample } from '../src/rng.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const S = JSON.parse(readFileSync(join(ROOT, 'audit', 'sample.json'), 'utf8'));
const key = JSON.parse(readFileSync(join(ROOT, 'audit', 'key.json'), 'utf8'));
const results = readFileSync(join(ROOT, S.from_run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const k = r => `${r.board}:${r.id}`;
const auditIdOf = Object.fromEntries(Object.entries(key).map(([a, v]) => [`${v.board}:${v.id}`, a]));
const order = sample(results.filter(r => r.decision === 'reject'), 40, mulberry32(S.seed)).map(r => auditIdOf[k(r)]);
const inStratum = s => Object.entries(key).filter(([, v]) => v.strata.includes(s)).map(([a]) => a).sort();
if (JSON.stringify([...order].sort()) !== JSON.stringify(inStratum('random_reject'))) throw new Error('recomputed draw order does not match key.json');
const N_RANDOM = 30;
const toJudge = [...order.slice(0, N_RANDOM), ...inStratum('closest_call')].sort();
const notJudged = Object.keys(key).filter(a => !toJudge.includes(a)).sort();
const plan = {
  declared_at: new Date().toISOString(), declared_by: 'Aravind, in chat, 2026-11-25, before any verdict',
  spec_version: S.spec_version,
  rule: `judge the first ${N_RANDOM} of the 40 random rejects in seeded draw order (seed ${S.seed}) and all ${inStratum('closest_call').length} closest calls; the other 10 random rejects and all ${inStratum('pm_reject').length} PM-titled rejects stay unjudged`,
  note: 'A001-A030 is NOT the first 30 draws: sheet rows were shuffled after drawing. The draw order is recomputed from the seed by this script.',
  to_judge: toJudge, not_judged: notJudged,
  sha256_of_to_judge: createHash('sha256').update(toJudge.join('\n')).digest('hex'),
};
writeFileSync(join(ROOT, 'audit', 'judging-plan.json'), JSON.stringify(plan, null, 2) + '\n');
writeFileSync(join(ROOT, 'audit', 'RESULTS.md'), `# Reject audit — results (spec v${S.spec_version})\n\n## Judging plan (declared ${plan.declared_at.slice(0, 10)}, before any verdict)\n\n`
  + `- Judged: ${plan.rule.split(';')[0]}. That is ${toJudge.length} rows: ${toJudge.join(', ')}.\n`
  + `- Not judged: ${notJudged.length} rows: ${notJudged.join(', ')}.\n`
  + `- ${plan.note}\n- Plan file: \`audit/judging-plan.json\` (SHA-256 of the judged list ${plan.sha256_of_to_judge}).\n\n`
  + `**No verdicts yet.** \`tools/audit-results.mjs\` replaces the rest of this file once the judged rows are filled in.\n`);
console.log(JSON.stringify({ to_judge: toJudge.length, not_judged: notJudged.length }));
