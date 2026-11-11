// The written rule (CONTRACT.md, "The rule"), applied as written. A RECORD:
// anyone can recompute it from the fields each gate cites.
import { contentText, sentences } from './text.mjs';

export const TITLE_LIST = [
  'Product Manager', 'Senior Product Manager', 'Sr. Product Manager', 'AI Product Manager',
  'Technical Product Manager', 'Web3 Product Manager', 'Technical Program Manager', 'Senior Technical Program Manager',
];
export const JUNIOR_TITLE_TERMS = ['Associate', 'APM', 'Intern', 'New Grad'];
export const NO_SPONSOR_PHRASES = ['unable to sponsor', 'not able to sponsor', 'will not sponsor', 'does not sponsor', 'cannot sponsor', 'without sponsorship', 'sponsorship is not available'];
export const CITIZEN_PHRASES = ['security clearance', 'u.s. citizen', 'us citizenship', 'citizenship is required'];

const DASH = '[-–—]';
const RANGE = new RegExp(`(\\d+)\\s*${DASH}\\s*(\\d+)\\s*\\+?\\s*years?`, 'g');
const YEARS_PHRASE = new RegExp(`(\\d+)\\s*\\+\\s*years?|(\\d+)\\s*${DASH}\\s*\\d+\\s*years?|(\\d+)\\s+or more years?`);

export function titlePrefix(title) {
  const cuts = [',', ' - ', '('].map(c => title.indexOf(c)).filter(i => i >= 0);
  return (cuts.length ? title.slice(0, Math.min(...cuts)) : title).trim();
}

const prefsRef = (field, value) => ({ source: 'persona-prefs.json', field, value });
const contractRef = (field, value) => ({ source: 'CONTRACT.md', field, value });
const wholeWord = term => new RegExp(`(?<![a-z0-9])${term.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![a-z0-9])`);

export function judgePosting(posting, prefs) {
  const title = posting.title ?? '';
  const loc = posting.location?.name ?? '';
  const text = contentText(posting.content);
  const gates = [];

  const prefix = titlePrefix(title);
  gates.push({ gate: 1, name: 'Title', pass: TITLE_LIST.includes(prefix),
    posting_field: 'title', posting_value: title, extracted: prefix,
    compared_with: contractRef('title list', TITLE_LIST) });

  // Revision 2026-10-31 (CONTRACT.md, Gate 2): title terms match whole words only.
  const juniorTerm = JUNIOR_TITLE_TERMS.find(t => new RegExp(`(?<![A-Za-z0-9])${t}(?![A-Za-z0-9])`).test(title)) ?? null;
  const lowRange = [...text.matchAll(RANGE)].find(m => Number(m[2]) <= 2)?.[0] ?? null;
  gates.push({ gate: 2, name: 'Not junior', pass: !juniorTerm && !lowRange,
    posting_field: 'title; content', posting_value: { title, junior_term: juniorTerm, range_upper_le_2: lowRange },
    compared_with: contractRef('junior title terms; range upper bound <= 2', JUNIOR_TITLE_TERMS) });

  let phrase = null, n = null;
  for (const s of sentences(text)) {
    if (!s.includes('experience')) continue;
    const m = s.match(YEARS_PHRASE);
    if (m) { phrase = m[0]; n = Number(m[1] ?? m[2] ?? m[3]); break; }
  }
  const ceiling = prefs.years_pm + 1;
  gates.push({ gate: 3, name: 'Experience ceiling', pass: n === null || n <= ceiling,
    posting_field: 'content', posting_value: phrase === null ? 'not stated' : { phrase, lower_bound: n },
    compared_with: prefsRef('years_pm', prefs.years_pm), threshold: `N <= years_pm + 1 = ${ceiling}` });

  const hit = prefs.locations.find(l => loc.toLowerCase().includes(l.toLowerCase())) ?? null;
  gates.push({ gate: 4, name: 'Location', pass: hit !== null,
    posting_field: 'location.name', posting_value: loc, matched: hit,
    compared_with: prefsRef('locations', prefs.locations) });

  const noSponsor = prefs.needs_sponsorship ? (NO_SPONSOR_PHRASES.find(p => text.includes(p)) ?? null) : null;
  gates.push({ gate: 5, name: 'Sponsorship', pass: noSponsor === null,
    posting_field: 'content', posting_value: prefs.needs_sponsorship ? (noSponsor ?? 'no no-sponsorship phrase found') : 'not checked: needs_sponsorship is false',
    compared_with: prefsRef('needs_sponsorship', prefs.needs_sponsorship) });

  const citizen = CITIZEN_PHRASES.find(p => text.includes(p)) ?? null;
  gates.push({ gate: 6, name: 'Citizenship / clearance', pass: citizen === null,
    posting_field: 'content', posting_value: citizen ?? 'no citizenship/clearance phrase found',
    compared_with: contractRef('citizenship/clearance phrases', CITIZEN_PHRASES) });

  const depts = (posting.departments ?? []).map(d => d.name ?? '');
  const domains = [];
  for (const term of prefs.domains) {
    const re = wholeWord(term);
    if (depts.some(d => re.test(d.toLowerCase()))) domains.push({ term, where: 'departments[].name' });
    else if (re.test(text)) domains.push({ term, where: 'content' });
  }

  const firstFailed = gates.find(g => !g.pass)?.gate ?? null;
  return {
    id: posting.id, title, absolute_url: posting.absolute_url,
    rule_verdict: firstFailed === null ? 'relevant' : 'not_relevant',
    rule_label: 'RECORD',
    rule_justification: { gates, first_failed: firstFailed, domain_citation: domains.length ? domains : 'none' },
  };
}

// Fails closed (CONTRACT.md, "Refuses" and Wrong version 2): every gate must cite
// its posting field and value and what it was compared with.
export function validateRuleResult(r) {
  const errors = [];
  if (r == null || r.id == null) errors.push('missing posting id');
  if (!['relevant', 'not_relevant'].includes(r?.rule_verdict)) errors.push('rule_verdict not in enum');
  if (r?.rule_label !== 'RECORD') errors.push('rule verdict not labeled RECORD');
  const gates = r?.rule_justification?.gates;
  if (!Array.isArray(gates) || gates.length !== 6) errors.push('justification must list all six gates');
  else gates.forEach((g, i) => {
    if (g.gate !== i + 1) errors.push(`gate ${i + 1} out of order`);
    if (typeof g.pass !== 'boolean') errors.push(`gate ${i + 1}: pass is not boolean`);
    if (!g.posting_field) errors.push(`gate ${i + 1}: no posting field cited`);
    if (g.posting_value === undefined || g.posting_value === null || g.posting_value === '') errors.push(`gate ${i + 1}: no posting value cited`);
    const c = g.compared_with;
    if (!c?.source || !c?.field || c.value === undefined) errors.push(`gate ${i + 1}: does not cite what it was compared with`);
    if ([3, 4, 5].includes(g.gate) && c?.source !== 'persona-prefs.json') errors.push(`gate ${g.gate}: must cite a persona-prefs.json field`);
  });
  if (Array.isArray(gates) && gates.length === 6) {
    const ff = gates.find(g => !g.pass)?.gate ?? null;
    if (r.rule_justification.first_failed !== ff) errors.push('first_failed does not match the gates');
    if ((ff === null) !== (r.rule_verdict === 'relevant')) errors.push('verdict does not follow from the gates');
  }
  if (r?.rule_justification?.domain_citation === undefined) errors.push('domain citation missing');
  return { ok: errors.length === 0, errors };
}
