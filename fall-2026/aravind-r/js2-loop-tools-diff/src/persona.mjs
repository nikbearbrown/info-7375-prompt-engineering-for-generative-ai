// Persona validation (CONTRACT.md, "In" and "Refuses"): every email ends
// @example.com and every phone uses a 555 exchange, or nothing runs.

const EMAIL = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi;
const PHONE = /(?:\+?1[\s.-]?)?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b/g;

function strings(node, path = '$', out = []) {
  if (typeof node === 'string') out.push([path, node]);
  else if (Array.isArray(node)) node.forEach((v, i) => strings(v, `${path}[${i}]`, out));
  else if (node && typeof node === 'object') for (const [k, v] of Object.entries(node)) strings(v, `${path}.${k}`, out);
  return out;
}

export function validatePersona(resume) {
  const errors = [], emails = [], phones = [];
  if (!resume || typeof resume !== 'object') return { ok: false, errors: ['résumé is not a JSON object'], emails, phones };
  for (const [path, s] of strings(resume)) {
    for (const m of s.matchAll(EMAIL)) {
      emails.push({ path, value: m[0] });
      if (!m[0].toLowerCase().endsWith('@example.com')) errors.push(`${path}: email ${m[0]} does not end @example.com`);
    }
    for (const m of s.matchAll(PHONE)) {
      phones.push({ path, value: m[0] });
      if (m[2] !== '555') errors.push(`${path}: phone ${m[0]} does not use a 555 exchange`);
    }
  }
  if (emails.length === 0) errors.push('no email found: cannot confirm the persona is fictional');
  return { ok: errors.length === 0, errors, emails, phones };
}

export function validatePrefs(p) {
  const errors = [];
  if (!Number.isInteger(p?.years_pm)) errors.push('years_pm must be an integer');
  if (!Array.isArray(p?.locations) || !p.locations.every(x => typeof x === 'string' && x)) errors.push('locations must be a list of strings');
  if (typeof p?.needs_sponsorship !== 'boolean') errors.push('needs_sponsorship must be a boolean');
  if (!Array.isArray(p?.domains) || !p.domains.every(x => typeof x === 'string' && x)) errors.push('domains must be a list of strings');
  return { ok: errors.length === 0, errors };
}
