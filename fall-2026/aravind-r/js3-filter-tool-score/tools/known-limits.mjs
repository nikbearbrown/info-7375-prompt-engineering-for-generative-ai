// Counts for the known limits in FILTER.md §5.3 (Aravind, 2026-11-25). Measurement only: no rule
// changes. Heuristics are stated next to each count; they are approximations, checked against the
// audit rows that prompted them. Writes audit/known-limits.json.
// Usage: node tools/known-limits.mjs
import { writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { loadCorpus } from '../src/corpus.mjs';
import { boilerplateLines, roleText } from '../src/boilerplate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const postings = loadCorpus(ROOT).postings;
const PM_TITLE = /\bproduct\b|\bprogram manager\b/i; // same title rule as the label sheet
const pm = postings.filter(p => PM_TITLE.test(p.title ?? ''));
const id = p => `${p.board}:${p.id}`;
const DASH = '[-–—]';
const YEARS_ANY = new RegExp(`\\d+\\s*\\+\\s*years?|\\d+\\s*${DASH}\\s*\\d+\\s*\\+?\\s*years?|\\d+\\s+or more years?|\\d+\\s+to\\s+\\d+\\s*years?`, 'i');
const lines = p => p.text.split('\n').map(l => l.trim()).filter(Boolean);
const isHeading = l => l.length < 60 && !/[.:;,]$/.test(l) && !YEARS_ANY.test(l);

// 1. Years only under a "Preferred" heading.
const PREF = /^(preferred|nice to have|bonus|it'?s a plus|pluses)/i;
function yearsOnlyPreferred(p) {
  const ls = lines(p); let inPref = false; const where = [];
  for (const l of ls) {
    if (isHeading(l)) { inPref = PREF.test(l); continue; }
    if (YEARS_ANY.test(l)) where.push(inPref);
  }
  return where.length > 0 && where.every(Boolean);
}
const prefOnly = pm.filter(yearsOnlyPreferred);

// 2. Spelled-out numbers of years.
const SPELLED = /\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen)\s*(\(\d+\)\s*)?(\+|plus)?\s*(or more\s*)?years?\b/i;
const spelledAll = postings.filter(p => lines(p).some(l => SPELLED.test(l) && /experience/i.test(l)));
const spelledPm = spelledAll.filter(p => PM_TITLE.test(p.title ?? ''));

// 3. Years stated without the word "experience" in the same sentence (A042's case).
const noExpWord = pm.filter(p => lines(p).some(l => YEARS_ANY.test(l) && !/experience/i.test(l)) && !lines(p).some(l => YEARS_ANY.test(l) && /experience/i.test(l)));

// 4. Airbnb postings with no role body: almost nothing left after removing lines shared by >= 20% of the board.
const bp = boilerplateLines(postings);
const airbnb = postings.filter(p => p.board === 'gh-airbnb');
const ROLE_BODY_MIN = 300;
const noBody = airbnb.filter(p => roleText(p, bp).replace(/\s+/g, ' ').trim().length < ROLE_BODY_MIN);

// 5. Near-duplicates: identical normalized text, different ids.
const byText = new Map();
for (const p of postings) { const h = createHash('sha256').update(p.text).digest('hex'); if (!byText.has(h)) byText.set(h, []); byText.get(h).push(p); }
const dupGroups = [...byText.values()].filter(g => g.length > 1);

// 6. Title tier vs body level: a plain-PM title whose body asks for a more senior level.
const CORE_PLAIN = /^(product manager|technical program manager|technical product manager)\b/i;
const SENIOR_BODY = /\b(looking for|seeking|hiring) an? (senior staff|staff|principal|group|lead) (product|program) manager/i;
const mismatch = postings.filter(p => CORE_PLAIN.test(p.title ?? '') && SENIOR_BODY.test(p.text));

const out = {
  computed_at: new Date().toISOString(), snapshot: 'data/MANIFEST.json', postings: postings.length, pm_titled: pm.length, pm_title_rule: String(PM_TITLE),
  preferred_only_years: { heuristic: `PM-titled; every line with a years phrase sits after a short heading line matching ${PREF}`, count: prefOnly.length, ids: prefOnly.map(id) },
  spelled_out_years: { heuristic: `a line containing "experience" and ${SPELLED}`, count_all: spelledAll.length, count_pm_titled: spelledPm.length, ids_pm_titled: spelledPm.map(id) },
  years_without_experience_word: { heuristic: 'PM-titled; has a years phrase, but no line has both a years phrase and the word "experience" (so the filter reads experience as unknown)', count: noExpWord.length, ids: noExpWord.map(id) },
  airbnb_no_role_body: { heuristic: `Airbnb postings whose text, after removing lines shared by >= 20% of Airbnb postings, is under ${ROLE_BODY_MIN} characters`, count: noBody.length, of: airbnb.length, ids: noBody.map(id) },
  identical_text_different_ids: { groups: dupGroups.length, postings_in_groups: dupGroups.reduce((a, g) => a + g.length, 0), groups_detail: dupGroups.map(g => g.map(p => `${id(p)} ${p.title}`)) },
  title_vs_body_level: { heuristic: `title starts with ${CORE_PLAIN}; body matches ${SENIOR_BODY}`, count: mismatch.length, ids: mismatch.map(p => `${id(p)} ${p.title}`) },
};
writeFileSync(join(ROOT, 'audit', 'known-limits.json'), JSON.stringify(out, null, 2) + '\n');
const brief = { ...out }; for (const k of Object.keys(brief)) if (brief[k]?.ids) brief[k] = { ...brief[k], ids: brief[k].ids.length > 12 ? [...brief[k].ids.slice(0, 12), '…'] : brief[k].ids };
brief.identical_text_different_ids = { groups: out.identical_text_different_ids.groups, postings_in_groups: out.identical_text_different_ids.postings_in_groups };
console.log(JSON.stringify(brief, null, 1));
