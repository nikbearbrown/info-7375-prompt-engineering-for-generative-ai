// Interactive, BLIND judging of audit/audit-sheet.csv, one row at a time.
// It reads only the sheet, the posting text files, and the list of planned row ids in
// audit/judging-plan.json. It never opens the key, the filter run, or the candidate lists, so it
// cannot show what the filter decided or why.
//
// Keys:  r relevant · n not_relevant · c cannot_tell · s skip (this session) · o full posting text · q quit
// After each verdict: an optional one-line note (Enter for none).
// The CSV is written back after every row (temp file + rename). Only the my_verdict and my_note
// cells of that row change; every other byte is left as it was (src/sheet.mjs).
// Resumable: starts at the first planned row whose my_verdict is empty.
//
// Usage: ~/.nvm/versions/node/v20.20.2/bin/node tools/judge-audit.mjs [--sheet audit/audit-sheet.csv] [--all]
//   --all   offer every row with an empty verdict, not only the planned ones
//
// Recheck mode: ... tools/judge-audit.mjs --recheck A005,A010,...   (or --recheck plan, which reads
// the ids in audit/recheck-plan.json). For each id it shows the row, the previous verdict, and the
// full-text lines that mention years/experience, location, and sponsorship. The new verdict goes
// in my_verdict; the previous one is kept in a new column first_pass_verdict; my_note becomes
// "recheck 2026-11-25: <reason>" (a reason is required; an earlier note is kept before it).
// Resumable: ids whose first_pass_verdict is already set are skipped.
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { createInterface } from 'node:readline';
import { Sheet } from '../src/sheet.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { sheet: { type: 'string', default: 'audit/audit-sheet.csv' }, all: { type: 'boolean', default: false }, recheck: { type: 'string' } } });
const SHEET = resolve(ROOT, values.sheet);
const planned = values.all ? null : new Set(JSON.parse(readFileSync(join(ROOT, 'audit', 'judging-plan.json'), 'utf8')).to_judge);
const VERDICT = { r: 'relevant', n: 'not_relevant', c: 'cannot_tell' };

let lastWritten = readFileSync(SHEET, 'utf8');
const sheet = new Sheet(lastWritten);

function save() {
  const onDisk = readFileSync(SHEET, 'utf8');
  if (onDisk !== lastWritten) throw new Error(`${values.sheet} changed on disk while judging; stopped without writing. Re-run to resume.`);
  const next = sheet.toString(), tmp = `${SHEET}.tmp`;
  writeFileSync(tmp, next); renameSync(tmp, SHEET);
  lastWritten = next;
}

// Piped (non-TTY) input: one shared line iterator, so queued lines are not lost between prompts.
// End of input returns null, which callers treat as quit.
let pipedLines = null;
function line(prompt) {
  if (!process.stdin.isTTY) {
    pipedLines ??= createInterface({ input: process.stdin })[Symbol.asyncIterator]();
    process.stdout.write(prompt);
    return pipedLines.next().then(r => (r.done ? null : r.value));
  }
  return new Promise(res => { const rl = createInterface({ input: process.stdin, output: process.stdout }); rl.question(prompt, a => { rl.close(); res(a); }); });
}
function key(prompt) {
  if (!process.stdin.isTTY) return line(prompt).then(a => (a === null ? 'q' : (a.trim()[0] ?? '').toLowerCase()));
  process.stdout.write(prompt);
  return new Promise(res => {
    process.stdin.setRawMode(true); process.stdin.resume();
    process.stdin.once('data', d => {
      process.stdin.setRawMode(false); process.stdin.pause();
      const s = d.toString();
      const k = s === '\u0003' || s === '\u0004' ? 'q' : s[0].toLowerCase();
      process.stdout.write(k + '\n'); res(k);
    });
  });
}
const wrap = (s, w = 96) => s.replace(new RegExp(`(.{1,${w}})(\\s+|$)`, 'g'), '    $1\n').trimEnd();

// ---------- recheck mode ----------
const RECHECK_DATE = '2026-11-25';
const LINE_GROUPS = [
  ['years / experience', /\byears?\b|experience/i],
  ['location', /\blocation|remote|hybrid|on-?site|in[- ]office|based in|relocat|days a week/i],
  ['sponsorship / work authorization', /sponsor|\bvisas?\b|citizen|right to work|work authori[sz]ation|clearance/i],
];
function postingText(file) {
  const t = readFileSync(join(ROOT, file), 'utf8');
  const i = t.indexOf('## Posting text');
  return i < 0 ? t : t.slice(i);
}
function evidenceLines(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  return LINE_GROUPS.map(([name, re]) => {
    const hits = [];
    for (const l of lines) {
      const m = l.match(re); if (!m) continue;
      hits.push(l.length > 260 ? '…' + l.slice(Math.max(0, m.index - 120), m.index + 140) + '…' : l);
      if (hits.length >= 8) break;
    }
    return [name, hits];
  });
}
async function recheckMode(arg) {
  const ids = arg === 'plan' ? JSON.parse(readFileSync(join(ROOT, 'audit', 'recheck-plan.json'), 'utf8')).ids : arg.split(',').map(x => x.trim()).filter(Boolean);
  const rowOf = new Map(sheet.rows.map(r => [sheet.get(r, 'audit_id'), r]));
  const missing = ids.filter(id => !rowOf.has(id)); if (missing.length) throw new Error(`not on the sheet: ${missing.join(', ')}`);
  const empty = ids.filter(id => !sheet.get(rowOf.get(id), 'my_verdict')); if (empty.length) throw new Error(`no first-pass verdict to recheck: ${empty.join(', ')}`);
  if (!sheet.has('first_pass_verdict')) { sheet.addColumn('first_pass_verdict'); save(); }
  const todo = ids.filter(id => !sheet.get(rowOf.get(id), 'first_pass_verdict'));
  console.log(`Recheck: ${todo.length} of ${ids.length} id(s) left. Keys: r relevant · n not_relevant · c cannot_tell · s skip · o full text · q quit. A reason is required.\n`);
  let left = todo.length;
  for (const id of todo) {
    const row = rowOf.get(id), file = sheet.get(row, 'posting_file'), prev = sheet.get(row, 'my_verdict');
    const show = () => {
      console.log(`── RECHECK ${id} ──────────────────────── (${left} left)\n  title:      ${sheet.get(row, 'title')}\n  location:   ${sheet.get(row, 'location') || '(missing)'}\n  department: ${sheet.get(row, 'department') || '(missing)'}\n  full text:  ${file}\n  previous verdict: ${prev}${sheet.get(row, 'my_note') ? `  (note: ${sheet.get(row, 'my_note')})` : ''}\n`);
      for (const [name, hits] of evidenceLines(postingText(file))) console.log(`  lines mentioning ${name}:\n${hits.length ? hits.map(h => wrap(h)).join('\n') : '    (none in the posting text)'}\n`);
    };
    show();
    let k;
    for (;;) {
      k = await key(`new verdict [r/n/c] (previous: ${prev}), s skip, o full text, q quit: `);
      if (k === 'o') { console.log('\n' + readFileSync(join(ROOT, file), 'utf8') + '\n'); show(); continue; }
      if (k in VERDICT || k === 's' || k === 'q') break;
      console.log(`  "${k}" is not a key.`);
    }
    if (k === 'q') break;
    if (k === 's') { console.log('  skipped (offered again next run)\n'); left--; continue; }
    let reason = '';
    while (!reason) {
      const a = await line('  reason (required, one line): ');
      if (a === null) { console.log(`\n  input ended before a reason; ${id} not saved.`); process.exit(0); }
      reason = a.replace(/[\r\n]+/g, ' ').trim();
    }
    const old = sheet.get(row, 'my_note');
    sheet.set(row, 'first_pass_verdict', prev);
    sheet.set(row, 'my_verdict', VERDICT[k]);
    sheet.set(row, 'my_note', `${old ? `${old} | ` : ''}recheck ${RECHECK_DATE}: ${reason}`);
    save();
    console.log(`  saved ${id}: ${prev} -> ${VERDICT[k]}${prev === VERDICT[k] ? ' (unchanged)' : ''}\n`);
    left--;
  }
  const remaining = ids.filter(id => !sheet.get(rowOf.get(id), 'first_pass_verdict')).length;
  console.log(`Stopped. ${remaining} recheck id(s) still open. Every recheck given is already saved.`);
  process.exit(0);
}
if (values.recheck) await recheckMode(values.recheck);

const queue = sheet.rows.filter(r => (!planned || planned.has(sheet.get(r, 'audit_id'))) && sheet.get(r, 'my_verdict') === '');
const total = planned ? planned.size : sheet.rows.length;
console.log(`${values.sheet}: ${queue.length} row(s) left to judge${planned ? ` of ${total} planned` : ''}. Keys: r relevant · n not_relevant · c cannot_tell · s skip · o full text · q quit\n`);

let done = 0;
for (const row of queue) {
  const id = sheet.get(row, 'audit_id'), file = sheet.get(row, 'posting_file');
  const show = () => console.log(`── ${id} ─────────────────────────────── (${queue.length - done} left)\n  title:      ${sheet.get(row, 'title')}\n  location:   ${sheet.get(row, 'location') || '(missing)'}\n  department: ${sheet.get(row, 'department') || '(missing)'}\n  full text:  ${file}\n  excerpt:\n${wrap(sheet.get(row, 'excerpt'))}\n`);
  show();
  let k;
  for (;;) {
    k = await key('verdict [r/n/c], s skip, o full text, q quit: ');
    if (k === 'o') { try { console.log('\n' + readFileSync(join(ROOT, file), 'utf8') + '\n'); } catch (e) { console.log(`cannot read ${file}: ${e.message}`); } show(); continue; }
    if (k in VERDICT || k === 's' || k === 'q') break;
    console.log(`  "${k}" is not a key.`);
  }
  if (k === 'q') break;
  if (k === 's') { console.log('  skipped (still empty; offered again next run)\n'); done++; continue; }
  const note = ((await line('  note (optional, Enter for none): ')) ?? '').replace(/[\r\n]+/g, ' ').trim();
  sheet.set(row, 'my_verdict', VERDICT[k]);
  if (note) sheet.set(row, 'my_note', note);
  save();
  console.log(`  saved ${id} = ${VERDICT[k]}${note ? ` · note: ${note}` : ''}\n`);
  done++;
}
const left = sheet.rows.filter(r => (!planned || planned.has(sheet.get(r, 'audit_id'))) && sheet.get(r, 'my_verdict') === '').length;
console.log(`Stopped. ${left} row(s) still without a verdict${planned ? ' (planned rows)' : ''}. Every verdict given is already saved.`);
process.exit(0);
