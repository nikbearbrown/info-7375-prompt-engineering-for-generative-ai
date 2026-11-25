// In-place CSV cell editing that leaves every untouched byte as it was: the raw text of each
// cell (quotes included), the line endings, a BOM, and a trailing newline are kept. Only the
// cells you set are re-serialized (quoted only when they need it).
export function parseRaw(text) {
  const bom = text.startsWith('﻿') ? '﻿' : '';
  const s = text.slice(bom.length);
  const lines = []; // { cells: [raw strings], eol }
  let cells = [], start = 0, q = false, i = 0;
  for (; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === '"') { if (s[i + 1] === '"') i++; else q = false; } continue; }
    if (c === '"') q = true;
    else if (c === ',') { cells.push(s.slice(start, i)); start = i + 1; }
    else if (c === '\n' || c === '\r') {
      const eol = c === '\r' && s[i + 1] === '\n' ? '\r\n' : c;
      cells.push(s.slice(start, i)); lines.push({ cells, eol }); cells = [];
      i += eol.length - 1; start = i + 1;
    }
  }
  if (start < s.length || cells.length) { cells.push(s.slice(start)); lines.push({ cells, eol: '' }); }
  return { bom, lines };
}
export function unquote(raw) { return raw.startsWith('"') && raw.endsWith('"') && raw.length >= 2 ? raw.slice(1, -1).replace(/""/g, '"') : raw; }
export function quote(v) { const s = String(v ?? ''); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }
export function serialize({ bom, lines }) { return bom + lines.map(l => l.cells.join(',') + l.eol).join(''); }

export class Sheet {
  constructor(text) {
    this.doc = parseRaw(text);
    this.header = this.doc.lines[0].cells.map(c => unquote(c).trim());
    this.rows = this.doc.lines.slice(1).filter(l => l.cells.some(c => c !== ''));
  }
  col(name) { const i = this.header.indexOf(name); if (i < 0) throw new Error(`no column ${name}`); return i; }
  get(row, name) { return unquote(row.cells[this.col(name)] ?? '').trim(); }
  set(row, name, value) { const i = this.col(name); while (row.cells.length <= i) row.cells.push(''); row.cells[i] = quote(value); }
  has(name) { return this.header.includes(name); }
  // Adds an empty column at the end of every row (header gets the name). Existing cells are untouched.
  addColumn(name) {
    if (this.has(name)) return;
    this.doc.lines[0].cells.push(quote(name)); this.header.push(name);
    for (const r of this.rows) { while (r.cells.length < this.header.length - 1) r.cells.push(''); r.cells.push(''); }
  }
  toString() { return serialize(this.doc); }
}
