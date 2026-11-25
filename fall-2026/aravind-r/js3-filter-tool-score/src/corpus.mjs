// Loads the frozen snapshot through MANIFEST.json, refusing any file whose SHA-256 changed.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { normalizeBoard } from './normalize.mjs';

export function loadCorpus(root) {
  const manifest = JSON.parse(readFileSync(join(root, 'data', 'MANIFEST.json'), 'utf8'));
  const boards = manifest.files.map(f => {
    let buf = null;
    try { buf = readFileSync(join(root, f.path)); } catch { return normalizeBoard({ board: f.board, system: f.system, body: null }); }
    const sha = createHash('sha256').update(buf).digest('hex');
    if (sha !== f.sha256) throw new Error(`${f.path}: SHA-256 ${sha} does not match MANIFEST ${f.sha256}`);
    return normalizeBoard({ board: f.board, system: f.system, body: buf.toString('utf8') });
  });
  return { manifest, boards, postings: boards.flatMap(b => b.postings) };
}
