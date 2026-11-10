// The second judge: Claude under a prompt contract. A JUDGMENT, never a record.
// Every call is a fresh `claude -p` session in an empty directory with no tools,
// so it reads nothing but the prompt. Output that fails the validator is recorded
// as `invalid`: never repaired, replaced, or retried into a pass.
import { spawnSync } from 'node:child_process';
import { readFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { contentText } from './text.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
export const POSTING_FIELDS = ['title', 'location.name', 'departments', 'content'];
export const PERSONA_FIELDS = ['years_pm', 'locations', 'needs_sponsorship', 'domains', 'experience', 'education', 'skills', 'projects'];
const KEYS = ['verdict', 'cited_posting_fields', 'cited_persona_fields', 'justification'];
// v2 prompt (prompts/judge.v2.md) adds one required key: evidence quotes for gates 2, 3, 5, 6.
export const EVIDENCE_KEYS = ['gate2', 'gate3', 'gate5', 'gate6'];

export function ruleSection(contractPath = join(HERE, '..', 'CONTRACT.md')) {
  const md = readFileSync(contractPath, 'utf8');
  const m = md.match(/## The rule\n([\s\S]*?)\n## /);
  if (!m) throw new Error('CONTRACT.md has no "The rule" section');
  return m[1].trim();
}

// The persona as Claude sees it: the rule fields plus the résumé without its contact block.
export function personaView(resume, prefs) {
  const { _label, ...fields } = prefs;
  const { personal, _comment, attested, attested_date, attestation_note, ...rest } = resume;
  return JSON.stringify({ ...fields, ...rest }, null, 1);
}

export function postingView(p) {
  return JSON.stringify({ id: p.id, title: p.title, 'location.name': p.location?.name ?? '', departments: (p.departments ?? []).map(d => d.name), content: contentText(p.content) }, null, 1);
}

export function buildPrompt(template, { rule, persona, posting }) {
  return template.replace('{{RULE}}', rule).replace('{{PERSONA}}', persona).replace('{{POSTING}}', posting);
}

export function validateClaudeOutput(text, { schema = 'v1' } = {}) {
  const keysWanted = schema === 'v2' ? [...KEYS, 'evidence'] : KEYS;
  const errors = [];
  let obj;
  try { obj = JSON.parse(String(text).trim()); } catch { return { ok: false, errors: ['not a bare JSON object'], value: null }; }
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return { ok: false, errors: ['not a JSON object'], value: null };
  const keys = Object.keys(obj).sort();
  if (keys.join() !== [...keysWanted].sort().join()) errors.push(`keys must be exactly ${keysWanted.join(', ')}; got ${keys.join(', ')}`);
  if (schema === 'v2') {
    const ev = obj.evidence;
    if (!ev || typeof ev !== 'object' || Array.isArray(ev)) errors.push('evidence must be an object');
    else {
      if (Object.keys(ev).sort().join() !== [...EVIDENCE_KEYS].sort().join()) errors.push(`evidence keys must be exactly ${EVIDENCE_KEYS.join(', ')}`);
      for (const k of EVIDENCE_KEYS) if (typeof ev[k] !== 'string' || !ev[k].trim()) errors.push(`evidence.${k} must be a non-empty string`);
    }
  }
  if (!['relevant', 'not_relevant'].includes(obj.verdict)) errors.push('verdict not in enum');
  for (const [k, allowed] of [['cited_posting_fields', POSTING_FIELDS], ['cited_persona_fields', PERSONA_FIELDS]]) {
    const v = obj[k];
    if (!Array.isArray(v) || v.length === 0) errors.push(`${k} must be a non-empty list`);
    else if (!v.every(x => allowed.includes(x))) errors.push(`${k} has values outside ${allowed.join('/')}`);
  }
  if (typeof obj.justification !== 'string' || !obj.justification.trim()) errors.push('justification must be a non-empty string');
  else if (obj.justification.length > 600) errors.push('justification over 600 characters');
  return { ok: errors.length === 0, errors, value: errors.length ? null : obj };
}

export function callClaude(prompt, { model, runner = spawnSync } = {}) {
  const cwd = mkdtempSync(join(tmpdir(), 'js1-judge-'));
  const args = ['-p', prompt, '--tools', '', '--no-session-persistence', '--output-format', 'json'];
  if (model) args.push('--model', model);
  const at = new Date().toISOString();
  const r = runner('claude', args, { cwd, encoding: 'utf8', maxBuffer: 1 << 24, timeout: 300000 });
  let envelope = null;
  try { envelope = JSON.parse(r.stdout); } catch { /* recorded below */ }
  return {
    at, exit_code: r.status,
    error: envelope ? (envelope.is_error ? String(envelope.result) : null) : `could not parse claude output: ${(r.stderr || r.stdout || '').slice(0, 300)}`,
    text: envelope && !envelope.is_error ? envelope.result : null,
    models: envelope?.modelUsage ? Object.keys(envelope.modelUsage) : [],
    session_id: envelope?.session_id ?? null,
  };
}

// One judged posting. The verdict is labeled JUDGMENT; an invalid reply stays invalid.
export function claudeJudge(posting, { resume, prefs, template, model, runner }) {
  const prompt = buildPrompt(template, { rule: ruleSection(), persona: personaView(resume, prefs), posting: postingView(posting) });
  const call = callClaude(prompt, { model, runner });
  const v = call.text === null ? { ok: false, errors: [call.error ?? 'no reply'], value: null } : validateClaudeOutput(call.text);
  return {
    claude_label: 'JUDGMENT',
    claude_verdict: v.ok ? v.value.verdict : 'invalid',
    claude_justification: v.ok ? v.value : null,
    claude_validation_errors: v.errors,
    claude_raw: call.text,
    claude_call: { at: call.at, exit_code: call.exit_code, models: call.models, session_id: call.session_id, error: call.error },
  };
}

// Recorded, never used to reject or change a verdict: is every quote (other than
// "not found") an exact substring of the posting text Claude was given (HTML decoded,
// tags stripped, case lowered, exactly as postingView sends it)?
export function quoteFidelity(evidence, posting) {
  const text = contentText(posting.content);
  const per = {};
  for (const k of EVIDENCE_KEYS) {
    const q = evidence?.[k];
    per[k] = q === 'not found' ? 'not found' : (typeof q === 'string' && text.includes(q) ? 'exact' : 'not a substring');
  }
  return { ok: Object.values(per).every(v => v !== 'not a substring'), per_gate: per };
}
