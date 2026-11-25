// The filter of FILTER.md §1, applied to one normalized posting. Every number and word
// comes from the spec object (FILTER.md §6) and the persona prefs; none is written here (W11).
import { sentences } from './text.mjs';

const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const wholeWord = term => new RegExp(`(?<![a-z0-9])${esc(term.toLowerCase())}(?![a-z0-9])`);
const r6 = x => Number(x.toFixed(6));
const DASH = '[-–—]';
const RANGE = new RegExp(`(\\d+)\\s*${DASH}\\s*(\\d+)\\s*\\+?\\s*years?`, 'g');
const YEARS_PHRASE = new RegExp(`(\\d+)\\s*\\+\\s*years?|(\\d+)\\s*${DASH}\\s*\\d+\\s*years?|(\\d+)\\s+or more years?`);

export function titlePrefix(title, cutChars) {
  const cuts = cutChars.map(c => title.indexOf(c)).filter(i => i >= 0);
  return (cuts.length ? title.slice(0, Math.min(...cuts)) : title).trim().replace(/\s+/g, ' ');
}

// The exact line of the posting containing the match, cut to a window: an exact substring.
function quoteAround(text, phrase, maxLen = 300) {
  const i = text.toLowerCase().indexOf(phrase);
  if (i < 0) return null;
  let a = text.lastIndexOf('\n', i) + 1;
  let b = text.indexOf('\n', i + phrase.length); if (b < 0) b = text.length;
  if (b - a > maxLen) {
    const half = Math.floor((maxLen - phrase.length) / 2);
    a = Math.max(a, i - half); b = Math.min(b, i + phrase.length + half);
  }
  return text.slice(a, b).trim();
}

function titleComponent(title, spec) {
  const prefix = titlePrefix(title, spec.title.cut_chars).toLowerCase();
  let tier = 'none', value = 0;
  for (const [name, t] of Object.entries(spec.title.tiers)) {
    if (t.titles.some(x => x.toLowerCase() === prefix)) { tier = name; value = t.value; break; }
  }
  const junior = spec.title.junior_terms.find(j => wholeWord(j).test(title.toLowerCase())) ?? null;
  if (junior) value = 0;
  return { value, tier, prefix, junior_term: junior };
}

function experienceComponent(lower, spec, prefs) {
  const x = spec.experience;
  const junior = [...lower.matchAll(RANGE)].find(m => Number(m[2]) <= x.junior_upper_max) ?? null;
  if (junior) return { value: 0, case: 'junior range', phrase: junior[0], lower_bound: Number(junior[1]) };
  for (const s of sentences(lower)) {
    if (!s.includes('experience')) continue;
    const m = s.match(YEARS_PHRASE);
    if (!m) continue;
    const n = Number(m[1] ?? m[2] ?? m[3]);
    const value = n <= prefs.preferred_max_years ? 1 : n <= prefs.stretch_max_years ? x.stretch_value : 0;
    return { value, case: 'stated', phrase: m[0], lower_bound: n, sentence: s };
  }
  return { value: null, case: 'not stated', phrase: null, lower_bound: null };
}

// v1.1.0-b: when the spec sets topic.exclude_shared_lines_min_share, text lines shared by that share
// of the board's postings (company intros, pay and legal boilerplate) are not searched for topic
// words. Title and department always are. `shared` (board -> Set of lines) comes from the corpus;
// a posting scored alone has none, and the result says so (shared_lines_checked: false).
function topicComponent(posting, text, spec, shared) {
  const want = spec.topic.exclude_shared_lines_min_share != null;
  const set = shared?.get(posting.board);
  const kept = want && set ? text.split('\n').filter(l => !set.has(l.trim())) : text.split('\n');
  const hay = [posting.title ?? '', posting.department ?? '', ...kept].join('\n').toLowerCase();
  const terms = spec.topic.terms.filter(t => wholeWord(t).test(hay));
  const out = { value: Math.min(1, terms.length / spec.topic.saturate_at), terms };
  if (want) out.shared_lines_checked = Boolean(set);
  return out;
}

function locationComponent(location, spec, prefs) {
  if (!location) return { value: null, matched: null };
  const l = location.toLowerCase();
  const direct = prefs.locations.find(p => l.includes(p.toLowerCase()));
  if (direct) return { value: 1, matched: direct };
  const alias = Object.keys(spec.location.aliases).find(a => wholeWord(a).test(l));
  if (alias) return { value: 1, matched: `${alias} -> ${spec.location.aliases[alias]}` };
  return { value: 0, matched: null };
}

function findVeto(text, spec, prefs) {
  const lower = text.toLowerCase();
  const lists = [];
  if (prefs.needs_sponsorship) lists.push(['sponsorship', spec.vetoes.sponsorship]);
  lists.push(['citizenship', spec.vetoes.citizenship]);
  for (const [rule, phrases] of lists) {
    const phrase = phrases.find(p => lower.includes(p));
    if (phrase) return { rule, phrase, quote: quoteAround(text, phrase) };
  }
  return null;
}

export function scorePosting(posting, { spec, prefs, shared = null }) {
  if (!Number.isInteger(prefs?.preferred_max_years) || !Number.isInteger(prefs?.stretch_max_years) || prefs.stretch_max_years < prefs.preferred_max_years)
    throw new Error('prefs need integer preferred_max_years <= stretch_max_years (persona-prefs.json, corrected 2026-11-25)');
  const title = posting.title ?? '';
  const text = posting.text ?? '';
  const lower = text.toLowerCase();
  const base = { id: posting.id, board: posting.board, title: posting.title ?? null, spec_version: spec.version };
  const veto = findVeto(text, spec, prefs);

  if (!title.trim() || text.length < spec.min_text_chars) {
    if (veto) return { ...base, decision: 'reject', reason: `veto: ${veto.rule}`, veto, score: 0, lo: 0, hi: 0, components: null, unknown: [] };
    return { ...base, decision: 'cannot_tell', reason: !title.trim() ? 'title missing' : `text under ${spec.min_text_chars} characters`, veto: null, score: null, lo: null, hi: null, components: null, unknown: ['posting'] };
  }

  const components = {
    title: titleComponent(title, spec),
    topic: topicComponent(posting, text, spec, shared),
    experience: experienceComponent(lower, spec, prefs),
    location: locationComponent(posting.location, spec, prefs),
  };
  const unknown = ['experience', 'location'].filter(k => components[k].value === null);
  if (veto) return { ...base, decision: 'reject', reason: `veto: ${veto.rule}`, veto, score: 0, lo: 0, hi: 0, components, unknown };

  const w = spec.weights;
  const sum = fill => r6(Object.keys(w).reduce((acc, k) => acc + w[k] * (components[k].value ?? fill(k)), 0));
  const lo = sum(() => 0);
  const hi = sum(() => 1);
  const score = sum(k => spec[k].impute);
  const decision = hi < spec.threshold ? 'reject' : lo >= spec.threshold ? 'keep' : 'cannot_tell';
  const reason = decision === 'cannot_tell' ? `depends on unknown: ${unknown.join(', ')}` : null;
  return { ...base, decision, reason, veto: null, score, lo, hi, components, unknown };
}

const ORDER = { keep: 0, cannot_tell: 1, reject: 2 };

export function rankResults(results) {
  return [...results].sort((a, b) =>
    ORDER[a.decision] - ORDER[b.decision]
    || (b.score ?? -1) - (a.score ?? -1)
    || String(a.board).localeCompare(String(b.board))
    || String(a.id).localeCompare(String(b.id)));
}
