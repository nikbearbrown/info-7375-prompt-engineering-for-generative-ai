// FILTER.md §3: every board's raw response -> {id, board, title, location, department,
// text, url}. applyUrl is never read. An unavailable board has null counts, never 0.
import { plainText } from './text.mjs';

const str = v => (typeof v === 'string' && v.trim() ? v.trim() : null);

function greenhouse(job, board) {
  const depts = (job.departments ?? []).map(d => d?.name).filter(n => typeof n === 'string' && n.trim()).map(n => n.trim());
  return {
    id: String(job.id), board,
    title: str(job.title),
    location: str(job.location?.name),
    department: depts.length ? depts.join('; ') : null,
    text: plainText(job.content ?? ''),
    url: str(job.absolute_url),
  };
}

function lever(p, board) {
  const c = p.categories ?? {};
  const all = Array.isArray(c.allLocations) ? c.allLocations.map(str).filter(Boolean) : [];
  const parts = [p.descriptionPlain, ...(Array.isArray(p.lists) ? p.lists.flatMap(l => [l?.text, plainText(l?.content ?? '')]) : []), p.additionalPlain]
    .map(s => (typeof s === 'string' ? s.trim() : '')).filter(Boolean);
  return {
    id: String(p.id), board,
    title: str(p.text),
    location: all.length ? all.join('; ') : str(c.location),
    department: str(c.department),
    text: parts.join('\n'),
    url: str(p.hostedUrl),
  };
}

const unavailable = (board, system, reason) => ({ board, system, status: 'unavailable', reason, raw_count: null, postings: [], skipped: { null_id: null }, warnings: [] });

export function normalizeBoard({ board, system, body }) {
  if (typeof body !== 'string') return unavailable(board, system, 'no raw body');
  let j;
  try { j = JSON.parse(body); } catch { return unavailable(board, system, 'raw body is not JSON'); }
  let items;
  if (system === 'greenhouse') {
    if (!j || typeof j !== 'object' || !Array.isArray(j.jobs)) return unavailable(board, system, `no jobs array (body: ${body.slice(0, 80)})`);
    items = j.jobs;
  } else if (system === 'lever') {
    if (!Array.isArray(j)) return unavailable(board, system, `not a postings array (body: ${body.slice(0, 80)})`);
    items = j;
  } else return unavailable(board, system, `unknown system ${system}`);

  const warnings = [];
  let nullIds = 0;
  const kept = [];
  const seen = new Set();
  for (const item of items) {
    if (item?.id === null || item?.id === undefined) { nullIds++; continue; }
    const key = String(item.id);
    if (seen.has(key)) return unavailable(board, system, `malformed: duplicate id ${JSON.stringify(item.id)}`);
    seen.add(key);
    kept.push(system === 'greenhouse' ? greenhouse(item, board) : lever(item, board));
  }
  if (nullIds) warnings.push(`${board}: skipped ${nullIds} posting(s) with a null id`);
  return { board, system, status: 'ok', reason: null, raw_count: items.length, postings: kept, skipped: { null_id: nullIds }, warnings };
}
