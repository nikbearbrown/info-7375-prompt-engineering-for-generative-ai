// Mechanical FALSE-FRIEND CANDIDATES for the audit. A candidate is a match that may be for
// the wrong reason; it is not a finding. Aravind names the false friend from a posting
// judged by hand. Open audit/false-friend-candidates.md only AFTER filling audit-sheet.csv.
// Usage: node tools/false-friends.mjs [--run runs/filter/v1.0.0]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { loadCorpus } from '../src/corpus.mjs';
import { parseFilterSpec } from '../src/spec.mjs';
import { ROLE_START } from '../src/boilerplate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { run: { type: 'string', default: 'runs/filter/v1.0.0' } } });
const spec = parseFilterSpec(readFileSync(join(ROOT, 'FILTER.md'), 'utf8'));
const results = new Map(readFileSync(join(ROOT, values.run, 'results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse).map(r => [`${r.board}:${r.id}`, r]));
const postings = loadCorpus(ROOT).postings;
const auditKey = JSON.parse(readFileSync(join(ROOT, 'audit', 'key.json'), 'utf8'));
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const ww = t => new RegExp(`(?<![a-z0-9])${esc(t.toLowerCase())}(?![a-z0-9])`, 'g');
const NON_US = /\b(emea|europe|uk|united kingdom|london|dublin|ireland|canada|toronto|latam|brazil|mexico|india|singapore|apac|japan|germany|spain|france|australia|east coast)\b/i;

// Where does a term match? title/department = about the role; text before the role heading = intro.
function termPlaces(p, term) {
  const lower = p.text.toLowerCase(), cut = lower.search(ROLE_START);
  const hits = [...lower.matchAll(ww(term))].map(m => m.index);
  return { inTitleOrDept: ww(term).test(`${p.title ?? ''}\n${p.department ?? ''}`.toLowerCase()),
    intro: cut > 0 ? hits.filter(i => i < cut).length : 0, role: cut > 0 ? hits.filter(i => i >= cut).length : hits.length, first: hits[0] ?? -1 };
}
const snip = (text, i, len) => i < 0 ? '' : '…' + text.slice(Math.max(0, i - 70), i + len + 70).replace(/\s+/g, ' ') + '…';

// Corpus table: for each board and topic term, how many matching postings match ONLY in the intro.
const rows = [];
for (const board of [...new Set(postings.map(p => p.board))]) {
  const ps = postings.filter(p => p.board === board);
  for (const t of spec.topic.terms) {
    const pl = ps.map(p => termPlaces(p, t)).filter(x => x.inTitleOrDept || x.intro || x.role);
    rows.push({ board, term: t, matching: pl.length, of: ps.length, only_intro: pl.filter(x => !x.inTitleOrDept && x.intro && !x.role).length });
  }
}

let md = `# False-friend candidates (mechanical; generated ${new Date().toISOString().slice(0, 10)})\n\n`
  + `**Open this only after you have filled \`audit/audit-sheet.csv\`.** Nothing here is a finding. A candidate is a match that *may* be for the wrong reason. The false friend is named by Aravind, from a posting judged by hand.\n\n`
  + `"Intro" means text before the first role heading (${ROLE_START}); in this snapshot that is usually the company's "About us" text. Spec v${spec.version}.\n\n`
  + `## 1. Corpus: topic terms that match only in the company intro\n\n| board | term | postings matching | of | match only in intro |\n|---|---|---|---|---|\n`
  + rows.filter(r => r.matching).map(r => `| ${r.board} | ${r.term} | ${r.matching} | ${r.of} | ${r.only_intro} |`).join('\n') + '\n\n';

md += `## 2. Audit rows: each match that might be for the wrong reason\n\n`;
for (const [aid, k] of Object.entries(auditKey)) {
  const p = postings.find(x => x.board === k.board && String(x.id) === String(k.id));
  const r = results.get(`${k.board}:${k.id}`); const c = r.components; if (!c) continue;
  const flags = [];
  for (const t of c.topic.terms) {
    const pl = termPlaces(p, t);
    if (!pl.inTitleOrDept && !pl.role) flags.push(`topic **${t}** matched only in the intro: ${snip(p.text, pl.first, t.length)}`);
  }
  if (c.location.value === 1 && /remote/i.test(c.location.matched ?? '') && NON_US.test(p.location ?? '')) flags.push(`location matched **Remote** in "${p.location}" (also names a non-US place)`);
  if (c.location.value === 1 && /->/.test(c.location.matched ?? '')) flags.push(`location matched alias **${c.location.matched}** in "${p.location}"`);
  if (c.title.value > 0 && c.experience.case === 'stated' && !/product|program|pm\b/.test(c.experience.sentence ?? '')) flags.push(`experience E=${c.experience.value} from a sentence that does not mention product/program: "${c.experience.sentence}"`);
  if (c.experience.case === 'junior range') flags.push(`experience set to 0 by junior range "${c.experience.phrase}"`);
  if (c.title.junior_term) flags.push(`title junior override by **${c.title.junior_term}** in "${p.title}"`);
  if (flags.length) md += `### ${aid} (${k.board}) ${p.title}\n- decision **${k.decision}**, score ${k.score}; strata: ${k.strata.join(', ')}\n${flags.map(f => `- ${f}`).join('\n')}\n\n`;
}
writeFileSync(join(ROOT, 'audit', 'false-friend-candidates.md'), md);
console.log(`wrote audit/false-friend-candidates.md`);
