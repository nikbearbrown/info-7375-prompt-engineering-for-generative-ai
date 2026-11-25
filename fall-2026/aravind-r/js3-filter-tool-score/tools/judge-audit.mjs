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
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { createInterface } from 'node:readline';
import { Sheet } from '../src/sheet.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: { sheet: { type: 'string', default: 'audit/audit-sheet.csv' }, all: { type: 'boolean', default: false } } });
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

function line(prompt) {
  return new Promise(res => { const rl = createInterface({ input: process.stdin, output: process.stdout }); rl.question(prompt, a => { rl.close(); res(a); }); });
}
function key(prompt) {
  if (!process.stdin.isTTY) return line(prompt).then(a => (a.trim()[0] ?? '').toLowerCase());
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
  const note = (await line('  note (optional, Enter for none): ')).replace(/[\r\n]+/g, ' ').trim();
  sheet.set(row, 'my_verdict', VERDICT[k]);
  if (note) sheet.set(row, 'my_note', note);
  save();
  console.log(`  saved ${id} = ${VERDICT[k]}${note ? ` · note: ${note}` : ''}\n`);
  done++;
}
const left = sheet.rows.filter(r => (!planned || planned.has(sheet.get(r, 'audit_id'))) && sheet.get(r, 'my_verdict') === '').length;
console.log(`Stopped. ${left} row(s) still without a verdict${planned ? ' (planned rows)' : ''}. Every verdict given is already saved.`);
process.exit(0);
