// Phase 3: one tool-less `claude -p` call per shortlisted posting (shortlist = keep ∪ cannot_tell,
// FILTER.md §5.2) under the given filter run. Every raw response is saved with its date, model,
// session id, the prompt file and its SHA-256, and the exact prompt sent. Replies are validated;
// an invalid reply stays invalid (no retry). Claude's labels are PROPOSALS: my_label is left empty.
// A posting that already has a saved response is not called again.
// Usage: node tools/justify-shortlist.mjs [--run runs/filter/v1.1.0-e] [--prompt prompts/justify.v1.md] [--model claude-sonnet-5-5]
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCorpus } from '../src/corpus.mjs';
import { definitionFromFilter, personaView, postingView, buildPrompt, validateJustification } from '../src/justify.mjs';
import { callClaude } from '../src/judge.mjs';
import { toCsv } from '../src/csv.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { run: { type: 'string', default: 'runs/filter/v1.1.0-e' }, prompt: { type: 'string', default: 'prompts/justify.v1.md' }, model: { type: 'string', default: 'claude-sonnet-5-5' } } });
const template = readFileSync(join(ROOT, values.prompt), 'utf8');
const promptSha = createHash('sha256').update(template).digest('hex');
const tag = basename(values.prompt, '.md');
const summary = JSON.parse(readFileSync(join(ROOT, values.run, 'summary.json'), 'utf8'));
const results = readFileSync(join(ROOT, values.run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const shortlist = results.filter(r => r.decision === 'keep' || r.decision === 'cannot_tell');
const key = JSON.parse(readFileSync(join(ROOT, 'audit', 'key.json'), 'utf8'));
const auditId = Object.fromEntries(Object.entries(key).map(([a, v]) => [`${v.board}:${v.id}`, a]));
const posts = new Map(loadCorpus(ROOT).postings.map(p => [`${p.board}:${p.id}`, p]));
const definition = definitionFromFilter(readFileSync(join(ROOT, 'FILTER.md'), 'utf8'));
const persona = personaView(JSON.parse(readFileSync(join(ROOT, 'persona', 'persona-prefs.json'), 'utf8')));
const outDir = join(ROOT, 'runs', 'claude', `${tag}-v${summary.spec_version}`);
mkdirSync(outDir, { recursive: true });

const rows = [], perPosting = [];
for (const r of shortlist) {
  const k = `${r.board}:${r.id}`, p = posts.get(k), name = auditId[k] ?? k.replace(/[^a-z0-9-]/gi, '_');
  const file = join(outDir, `${name}.json`);
  let rec;
  if (existsSync(file)) rec = JSON.parse(readFileSync(file, 'utf8'));
  else {
    const prompt = buildPrompt(template, { definition, persona, posting: postingView(p) });
    process.stderr.write(`calling claude for ${name} (${k}) ... `);
    const call = callClaude(prompt, { model: values.model });
    process.stderr.write(`${call.error ? 'error' : 'ok'} at ${call.at}\n`);
    rec = { label: 'JUDGMENT', posting: k, audit_id: auditId[k] ?? null, decision: r.decision, spec_version: summary.spec_version,
      prompt_file: values.prompt, prompt_sha256: promptSha, model_requested: values.model,
      at: call.at, models: call.models, session_id: call.session_id, exit_code: call.exit_code, error: call.error,
      args_without_prompt: call.args_without_prompt, prompt, reply_text: call.text, envelope: call.envelope };
    writeFileSync(file, JSON.stringify(rec, null, 2) + '\n');
  }
  const v = rec.reply_text === null ? { ok: false, errors: [rec.error ?? 'no reply'], claims: [] } : validateJustification(rec.reply_text, { postingId: k, postingText: p.text });
  perPosting.push({ audit_id: rec.audit_id, posting: k, title: p.title, decision: r.decision, at: rec.at, models: rec.models, valid: v.ok, errors: v.errors, claims: v.claims.length, rule_violations: v.claims_with_rule_violations ?? null });
  for (const c of v.claims) rows.push({ audit_id: rec.audit_id ?? '', posting: k, title: p.title, decision: r.decision, claim_no: c.n, claim: c.claim, kind: c.kind, quote: c.quote ?? '', quote_check: c.quote_check, proposed_label: c.proposed_label, allowed_labels: (c.allowed_labels ?? []).join('/'), abstain: c.abstain, rule_violations: (c.errors ?? []).join('; '), my_label: '', my_note: '' });
}
mkdirSync(join(ROOT, 'shortlist'), { recursive: true });
const csvPath = join(ROOT, 'shortlist', `claims-${tag}-v${summary.spec_version}.csv`);
if (existsSync(csvPath) && readFileSync(csvPath, 'utf8').split('\n').slice(1).some(l => /,(supported|contradicted|insufficient),[^,]*$/.test(l))) throw new Error(`${csvPath} already has hand labels; refusing to overwrite`);
writeFileSync(csvPath, toCsv(rows, ['audit_id', 'posting', 'title', 'decision', 'claim_no', 'claim', 'kind', 'quote', 'quote_check', 'proposed_label', 'allowed_labels', 'abstain', 'rule_violations', 'my_label', 'my_note']));
writeFileSync(join(ROOT, 'shortlist', `summary-${tag}-v${summary.spec_version}.json`), JSON.stringify({ computed_at: new Date().toISOString(), run: values.run, spec_version: summary.spec_version, prompt_file: values.prompt, prompt_sha256: promptSha, model_requested: values.model, shortlist: perPosting }, null, 2) + '\n');
console.log(JSON.stringify({ shortlist: perPosting.length, claims: rows.length, invalid: perPosting.filter(x => !x.valid).map(x => x.audit_id ?? x.posting), csv: csvPath.slice(ROOT.length + 1) }));
