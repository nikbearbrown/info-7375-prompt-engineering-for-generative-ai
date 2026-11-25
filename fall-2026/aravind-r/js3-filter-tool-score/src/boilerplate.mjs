// Lines of posting text shared by many postings on the same board (company intros,
// benefits, legal text). Used only for display (sheet excerpts) and for flagging
// false-friend candidates. It is NOT part of the filter (FILTER.md §6 is).
export function boilerplateLines(postings, minShare = 0.2) {
  const byBoard = new Map();
  for (const p of postings) {
    if (!byBoard.has(p.board)) byBoard.set(p.board, { n: 0, counts: new Map() });
    const b = byBoard.get(p.board); b.n++;
    for (const line of new Set(p.text.split('\n').map(l => l.trim()).filter(l => l.length >= 20))) b.counts.set(line, (b.counts.get(line) ?? 0) + 1);
  }
  const out = new Map();
  for (const [board, b] of byBoard) out.set(board, new Set([...b.counts].filter(([, c]) => c / b.n >= minShare).map(([l]) => l)));
  return out;
}
export const roleText = (p, bp) => p.text.split('\n').filter(l => !(bp.get(p.board)?.has(l.trim()))).join('\n');
// The first common role-section heading; text before it is usually the company intro.
export const ROLE_START = /what you(?:'|’)ll do|responsibilities|about the role|in this role|the opportunity|what you will do/i;
