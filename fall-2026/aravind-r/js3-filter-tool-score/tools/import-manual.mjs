// DEVIATION (FILTER.md §4, 2026-11-25): the intended path was a tool-less `claude -p` call; it
// failed for every posting on the account's spend limit (commit 3caf2978). Fallback: Aravind pastes
// each rendered prompt (manual/prompts/<id>.txt) into claude.ai and saves Claude's raw reply,
// unedited, as manual/responses/<id>.txt. This tool imports those replies.
//
// Each reply is validated by the SAME code as an automated reply (src/justify.mjs:
// schema, exact-substring quote check, label rules). An invalid reply is recorded as invalid:
// never repaired, re-prompted, or replaced. A record that already exists is not overwritten.
// A reply whose posting_id names another posting is REJECTED before validation (filing guard,
// src/justify.mjs checkReplyPosting): nothing is written for it, and the exit code is 3.
//
// Usage:
//   node tools/import-manual.mjs --model "<model as shown in claude.ai>" --date YYYY-MM-DD [--interface "claude.ai web, incognito chat"] [--dir runs/claude/justify.v1-v1.1.0-e] [--run runs/filter/v1.1.0-e]
// Then build the claims table without calling Claude:
//   node tools/justify-shortlist.mjs --no-call
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCorpus } from '../src/corpus.mjs';
import { validateJustification, checkReplyPosting } from '../src/justify.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: {
  model: { type: 'string' }, date: { type: 'string' }, interface: { type: 'string', default: 'claude.ai web, incognito chat' },
  dir: { type: 'string', default: 'runs/claude/justify.v1-v1.1.0-e' }, run: { type: 'string', default: 'runs/filter/v1.1.0-e' },
} });
if (!values.model) throw new Error('--model is required: the model name as claude.ai showed it');
if (!/^\d{4}-\d{2}-\d{2}$/.test(values.date ?? '')) throw new Error('--date YYYY-MM-DD is required: the day the replies were obtained');
const sha = s => createHash('sha256').update(s).digest('hex');
const DIR = resolve(ROOT, values.dir);
const manifest = JSON.parse(readFileSync(join(DIR, 'manual', 'prompts', 'manifest.json'), 'utf8'));
const results = new Map(readFileSync(join(ROOT, values.run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).map(r => [`${r.board}:${r.id}`, r]));
const posts = new Map(loadCorpus(ROOT).postings.map(p => [`${p.board}:${p.id}`, p]));
const respDir = join(DIR, 'manual', 'responses');
const have = existsSync(respDir) ? new Set(readdirSync(respDir)) : new Set();

const report = [];
for (const m of manifest.prompts) {
  const out = join(DIR, `${m.id}.json`);
  if (existsSync(out)) { report.push({ id: m.id, status: 'already imported (not overwritten)' }); continue; }
  if (!have.has(`${m.id}.txt`)) { report.push({ id: m.id, status: 'no response file yet' }); continue; }
  const prompt = readFileSync(join(DIR, 'manual', 'prompts', m.file), 'utf8');
  if (sha(prompt) !== m.sha256) throw new Error(`${m.file}: prompt changed since it was rendered (SHA-256 mismatch); refusing to import`);
  const raw = readFileSync(join(respDir, `${m.id}.txt`), 'utf8');
  const guard = checkReplyPosting(raw, m.posting);
  if (!guard.ok) {
    const owner = manifest.prompts.find(x => x.posting === guard.got);
    report.push({ id: m.id, status: `REJECTED, not imported: ${guard.reason}${owner ? ` (that posting is ${owner.id})` : ''}` });
    process.exitCode = 3;
    continue;
  }
  const v = validateJustification(raw, { postingId: m.posting, postingText: posts.get(m.posting).text, postingLocation: posts.get(m.posting).location });
  const rec = {
    label: 'JUDGMENT', posting: m.posting, audit_id: m.id, decision: results.get(m.posting)?.decision ?? m.decision, spec_version: manifest.spec_version,
    prompt_file: manifest.prompt_file, prompt_template_sha256: manifest.prompt_template_sha256, prompt_sha256: m.sha256,
    manual_paste: true, interface: values.interface, model_reported_by_user: values.model, models: [values.model], date_obtained: values.date,
    at: `${values.date} (manual; imported ${new Date().toISOString()})`, session_id: null, exit_code: null, error: null,
    reply_sha256: sha(raw), reply_text: raw, prompt,
    validation_at_import: { ok: v.ok, errors: v.errors, claims: v.claims.length, claims_with_rule_violations: v.claims_with_rule_violations ?? null },
  };
  writeFileSync(out, JSON.stringify(rec, null, 2) + '\n');
  report.push({ id: m.id, status: v.ok ? `imported, valid, ${v.claims.length} claims, ${v.claims_with_rule_violations} with rule violations` : `imported, INVALID (kept as is): ${v.errors.join('; ')}` });
}
console.log(JSON.stringify(report, null, 1));
