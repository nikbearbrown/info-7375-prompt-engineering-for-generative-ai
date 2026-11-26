// Phase 3 (FILTER.md §2, §4): builds the justification prompt from its three parts and validates
// Claude's reply. Pure: no process, no network. The call itself is in src/judge.mjs.
//   prompt  = prompts/justify.v1.md (the template)
//   context = DEFINITION (FILTER.md §1) + PERSONA (persona-prefs.json fields) + POSTING
import { quoteCheck, allowedLabels } from './evidence.mjs';

export function definitionFromFilter(md) {
  const intro = md.match(/## 1\. What makes a posting relevant\n([\s\S]*?)\n### 1\.1/);
  const tpm = md.match(/- \*\*Technical Program Manager roles[^\n]*\n([\s\S]*?)\n- \*\*`:` is a cut character/);
  if (!intro || !tpm) throw new Error('FILTER.md: relevance definition or TPM rule not found');
  // Bullets of the TPM rule, minus the one about how the filter applies it (not part of the definition).
  const bullets = tpm[1].split(/\n(?=  - )/).map(b => b.trim()).filter(b => b && !/hand judgment/.test(b));
  // The dated history note "(corrected ..., v1.0.0 read this as ...)" is documentation, not definition.
  const intro_ = intro[1].trim().replace(/\s*\(corrected 2026-11-25[\s\S]*?ceiling of 3\)/, '');
  return `${intro_}\n\nTechnical Program Manager roles:\n${bullets.join('\n')}`;
}
export function personaView(prefs) {
  return JSON.stringify(Object.fromEntries(Object.entries(prefs).filter(([k]) => !k.startsWith('_'))), null, 1);
}
export function postingView(p) {
  return JSON.stringify({ id: `${p.board}:${p.id}`, title: p.title, location: p.location, department: p.department, text: p.text }, null, 1);
}
export function buildPrompt(template, { definition, persona, posting }) {
  for (const k of ['{{DEFINITION}}', '{{PERSONA}}', '{{POSTING}}']) if (!template.includes(k)) throw new Error(`template lacks ${k}`);
  return template.replace('{{DEFINITION}}', definition).replace('{{PERSONA}}', persona).replace('{{POSTING}}', posting);
}

const CLAIM_KEYS = ['abstain', 'claim', 'kind', 'proposed_label', 'quote'];
// Invalid replies are recorded as invalid: never repaired, replaced, or retried into a pass.
export function validateJustification(text, { postingId, postingText }) {
  const errors = [];
  let obj;
  try { obj = JSON.parse(String(text).trim()); } catch { return { ok: false, errors: ['not a bare JSON object'], claims: [] }; }
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return { ok: false, errors: ['not a JSON object'], claims: [] };
  if (Object.keys(obj).sort().join() !== 'claims,posting_id') errors.push(`top-level keys must be exactly posting_id, claims; got ${Object.keys(obj).sort().join(', ')}`);
  if (obj.posting_id !== postingId) errors.push(`posting_id ${JSON.stringify(obj.posting_id)} is not ${postingId}`);
  if (!Array.isArray(obj.claims) || obj.claims.length < 1) return { ok: false, errors: [...errors, 'claims must be a non-empty list'], claims: [] };
  const claims = obj.claims.map((c, i) => {
    const e = [];
    if (!c || typeof c !== 'object') return { n: i + 1, errors: ['claim is not an object'] };
    if (Object.keys(c).sort().join() !== CLAIM_KEYS.join()) e.push(`keys must be exactly ${CLAIM_KEYS.join(', ')}`);
    if (typeof c.claim !== 'string' || !c.claim.trim()) e.push('claim text missing');
    if (!['quoted', 'judgment'].includes(c.kind)) e.push('kind not quoted/judgment');
    if (!['supported', 'contradicted', 'insufficient'].includes(c.proposed_label)) e.push('proposed_label not in enum');
    if (typeof c.abstain !== 'boolean') e.push('abstain not boolean');
    if (!(c.quote === null || typeof c.quote === 'string')) e.push('quote must be a string or null');
    if (c.abstain === true && (c.quote !== null || c.proposed_label !== 'insufficient')) e.push('abstain requires quote null and label insufficient');
    const quote_check = c.quote === null ? 'none' : quoteCheck(c.quote, postingText);
    const allowed = c.quote === null ? ['insufficient'] : allowedLabels(quote_check);
    if (['supported', 'contradicted', 'insufficient'].includes(c.proposed_label) && !allowed.includes(c.proposed_label)) e.push(`proposed_label ${c.proposed_label} not allowed: quote is ${quote_check}`);
    return { n: i + 1, ...c, quote_check, allowed_labels: allowed, errors: e };
  });
  const claimErrors = claims.filter(c => c.errors.length).length;
  return { ok: errors.length === 0, errors, claims, claims_with_rule_violations: claimErrors };
}

// Filing guard for manual pastes: a reply whose posting_id names a different posting than the one
// its file is for is most likely saved under the wrong filename. It is REJECTED (not imported, not
// recorded as an invalid Claude reply), so a misfiled reply can never be counted for the wrong posting.
// A reply that is not parseable JSON passes this guard and is then recorded as invalid by validation.
export function checkReplyPosting(raw, expectedPostingId) {
  let obj;
  try { obj = JSON.parse(String(raw).trim()); } catch { return { ok: true, reason: 'not JSON: left to validation' }; }
  const got = obj && typeof obj === 'object' ? obj.posting_id : undefined;
  if (got === expectedPostingId) return { ok: true, reason: 'posting_id matches' };
  return { ok: false, got: got ?? null, reason: `posting_id ${JSON.stringify(got ?? null)} is not ${expectedPostingId}: likely saved under the wrong filename` };
}
