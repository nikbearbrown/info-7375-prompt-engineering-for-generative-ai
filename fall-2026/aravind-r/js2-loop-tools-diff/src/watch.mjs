#!/usr/bin/env node
// The watch: fetch one allow-listed board (or read a saved response for a labeled
// seeded run), save the raw response, report only postings new since the last run,
// and judge each one twice (RECORD by the rule, JUDGMENT by Claude).
//
// node src/watch.mjs --board stripe --state state/seen-ids.json --label live
//   [--from-file <saved raw response>] [--judge claude|none] [--model <id>]
//   [--resume persona/maya-sehgal.resume.json] [--prefs persona/persona-prefs.json] [--runs runs]
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { boardUrl, guardedFetch, Refused } from './fetch.mjs';
import { validatePersona, validatePrefs } from './persona.mjs';
import { loadState, saveState, diffNew } from './state.mjs';
import { judgePosting, validateRuleResult } from './rule.mjs';
import { claudeJudge } from './claude-judge.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const { values: a } = parseArgs({ options: {
  board: { type: 'string' }, state: { type: 'string' }, label: { type: 'string' },
  'from-file': { type: 'string' }, judge: { type: 'string', default: 'claude' }, model: { type: 'string' },
  resume: { type: 'string', default: join(ROOT, 'persona/maya-sehgal.resume.json') },
  prefs: { type: 'string', default: join(ROOT, 'persona/persona-prefs.json') },
  runs: { type: 'string', default: join(ROOT, 'runs') },
} });

function die(code, msg) { console.error(`REFUSED: ${msg}`); process.exit(code); }
if (!a.board || !a.state || !a.label) die(2, '--board, --state and --label are required');
if (!/^[a-z0-9-]+$/.test(a.label)) die(2, '--label must be kebab-case');
if (a['from-file'] && !a.label.includes('seeded')) die(2, 'a run read from a saved file must carry "seeded" in its --label');
if (!['claude', 'none'].includes(a.judge)) die(2, '--judge must be claude or none');

const resume = JSON.parse(readFileSync(a.resume, 'utf8'));
const pv = validatePersona(resume);
if (!pv.ok) die(3, `persona validation failed:\n  ${pv.errors.join('\n  ')}`);
const prefs = JSON.parse(readFileSync(a.prefs, 'utf8'));
const pp = validatePrefs(prefs);
if (!pp.ok) die(3, `persona-prefs validation failed: ${pp.errors.join('; ')}`);

const startedAt = new Date().toISOString();
const stamp = startedAt.replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
const runId = `${stamp}-${a.label}`;
const dir = join(a.runs, runId);
const requests = [];

let raw, source;
if (a['from-file']) {
  raw = readFileSync(a['from-file'], 'utf8');
  source = { kind: 'SEEDED: saved response read from disk, no network', file: relative(ROOT, a['from-file']) };
} else {
  try { raw = await guardedFetch(boardUrl(a.board), { log: requests }); }
  catch (e) { if (e instanceof Refused) die(4, e.message); throw e; }
  source = { kind: 'live fetch', url: boardUrl(a.board) };
}
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, 'raw-response.json'), raw);

const jobs = JSON.parse(raw).jobs;
if (!Array.isArray(jobs)) die(5, 'response has no jobs list');
const state = loadState(a.state);
const { baseline, fresh } = diffNew(jobs, state);

const template = readFileSync(join(ROOT, 'prompts/judge.v1.md'), 'utf8');
const results = [];
for (const p of fresh) {
  const r = judgePosting(p, prefs);
  const v = validateRuleResult(r);
  if (!v.ok) die(6, `rule justification for ${p.id} fails closed: ${v.errors.join('; ')}`);
  const c = a.judge === 'claude' ? claudeJudge(p, { resume, prefs, template, model: a.model })
    : { claude_label: 'JUDGMENT', claude_verdict: 'not run', claude_justification: null };
  results.push({ ...r, ...c });
}

saveState(a.state, { board: a.board, ids: [...(state?.ids ?? []), ...jobs.map(j => j.id)], run: runId });
const meta = {
  run: runId, started_at: startedAt, finished_at: new Date().toISOString(), board: a.board, source,
  network_requests: requests, state_file: relative(ROOT, a.state), baseline,
  jobs_in_response: jobs.length, previously_seen: state?.ids.length ?? 0, new_postings: fresh.length,
  persona_validation: { ok: pv.ok, emails: pv.emails.length, phones: pv.phones.length },
  judge: a.judge, prompt: 'prompts/judge.v1.md',
};
writeFileSync(join(dir, 'run-meta.json'), JSON.stringify(meta, null, 2) + '\n');
writeFileSync(join(dir, 'report.json'), JSON.stringify(results, null, 2) + '\n');
writeFileSync(join(dir, 'report.md'), renderReport(meta, results));
console.log(`${runId}: ${jobs.length} jobs, ${baseline ? 'BASELINE (0 reported as new)' : `${fresh.length} new`}. ${relative(ROOT, dir)}/report.md`);

function renderReport(m, rs) {
  const L = [`# Watch report: ${m.run}`, '', '## Summary', '',
    `${m.source.kind.startsWith('SEEDED') ? '**SEEDED RUN** (a saved response read from disk, not a live fetch). ' : ''}Board \`${m.board}\`: ${m.jobs_in_response} postings in the response; ${m.baseline ? 'this is the baseline run, so none are reported as new' : `${m.new_postings} new since the last run`}.`,
    'Rule verdicts are a **RECORD** (recomputable from the cited fields). Claude verdicts are a **JUDGMENT** (a model\'s opinion, not a fact, never overriding the rule).', '',
    '## Run record', '', `- Started: ${m.started_at} · Source: ${m.source.kind}${m.source.url ? ` · ${m.source.url}` : ` · ${m.source.file}`}`,
    `- Network requests: ${m.network_requests.length ? m.network_requests.map(r => `${r.host} (${r.status ?? '-'}, ${r.result})`).join('; ') : 'none'}`,
    `- State: \`${m.state_file}\` (${m.previously_seen} ids before this run)`, ''];
  if (!rs.length) return L.join('\n') + '\n';
  L.push('## New postings', '', '| id | title | location | rule verdict (RECORD) | first failed gate | Claude verdict (JUDGMENT) |', '|---|---|---|---|---|---|');
  for (const r of rs) {
    const g = r.rule_justification;
    L.push(`| ${r.id} | ${r.title} | ${g.gates[3].posting_value} | ${r.rule_verdict} | ${g.first_failed ? `${g.first_failed} ${g.gates[g.first_failed - 1].name}` : '—'} | ${r.claude_verdict} |`);
  }
  for (const r of rs) {
    L.push('', `### ${r.id}: ${r.title}`, '', `<${r.absolute_url}>`, '', `**Rule (RECORD): ${r.rule_verdict}**`, '');
    for (const g of r.rule_justification.gates) L.push(`- Gate ${g.gate} ${g.name}: ${g.pass ? 'pass' : 'FAIL'}${g.gate === r.rule_justification.first_failed ? ' ← first failure' : ''}. Posting \`${g.posting_field}\` = ${JSON.stringify(g.posting_value)}; compared with ${g.compared_with.source} \`${g.compared_with.field}\`${g.threshold ? ` (${g.threshold})` : ''}${g.matched ? `; matched "${g.matched}"` : ''}.`);
    const dc = r.rule_justification.domain_citation;
    L.push(`- Domain citation (not a gate): ${dc === 'none' ? 'none' : dc.map(d => `${d.term} (${d.where})`).join(', ')}`, '');
    if (r.claude_verdict === 'not run') L.push('**Claude (JUDGMENT): not run**');
    else if (r.claude_verdict === 'invalid') L.push(`**Claude (JUDGMENT): invalid**, rejected by the validator: ${r.claude_validation_errors.join('; ')}`);
    else L.push(`**Claude (JUDGMENT): ${r.claude_verdict}** (${r.claude_call.at}, ${r.claude_call.models.join(', ')}). ${r.claude_justification.justification} Cited posting: ${r.claude_justification.cited_posting_fields.join(', ')}; persona: ${r.claude_justification.cited_persona_fields.join(', ')}.`);
  }
  return L.join('\n') + '\n';
}
