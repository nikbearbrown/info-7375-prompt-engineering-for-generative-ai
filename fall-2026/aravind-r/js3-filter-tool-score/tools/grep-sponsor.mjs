// Read-only check (Aravind, 2026-11-25): every line of normalized snapshot text that mentions
// "sponsor" or "visa", so the 0-veto result can be checked for phrasings the veto list misses.
// Changes no rule. Usage: node tools/grep-sponsor.mjs > audit/sponsor-visa-hits.md
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCorpus } from '../src/corpus.mjs';
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const RE = /sponsor|\bvisas?\b/i;
const hits = [];
for (const p of loadCorpus(ROOT).postings) for (const line of p.text.split('\n')) {
  const m = line.match(RE); if (!m) continue;
  const i = m.index, t = line.replace(/\s+/g, ' ');
  hits.push({ board: p.board, id: p.id, title: p.title, match: m[0], line: t.length > 240 ? '…' + line.slice(Math.max(0, i - 110), i + 130).replace(/\s+/g, ' ') + '…' : t });
}
const byLine = new Map(); for (const h of hits) { const k = h.line; if (!byLine.has(k)) byLine.set(k, []); byLine.get(k).push(h); }
console.log(`# "sponsor" / "visa" in the snapshot text\n\nGenerated ${new Date().toISOString().slice(0, 10)} by \`tools/grep-sponsor.mjs\` (regex ${RE}, case-insensitive, normalized text). ${hits.length} matching lines in ${new Set(hits.map(h => h.board + ':' + h.id)).size} postings; ${byLine.size} distinct lines. No rule was changed.\n`);
console.log('| # | distinct line | postings (board:id) | count |\n|---|---|---|---|');
let n = 0;
for (const [line, hs] of [...byLine].sort((a, b) => b[1].length - a[1].length)) {
  const ids = hs.map(h => `${h.board}:${h.id}`);
  console.log(`| ${++n} | ${line.replace(/\|/g, '\\|')} | ${ids.slice(0, 6).join(', ')}${ids.length > 6 ? `, … (+${ids.length - 6})` : ''} | ${hs.length} |`);
}
