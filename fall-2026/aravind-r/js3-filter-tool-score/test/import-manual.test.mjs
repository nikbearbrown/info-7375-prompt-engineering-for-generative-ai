// Filing guard for the manual claude.ai route (FILTER.md §4 deviation). Replies here are SYNTHETIC.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, cpSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { checkReplyPosting } from '../src/justify.mjs';
import { ROOT } from '../testlib/helpers.mjs';

test('checkReplyPosting: match passes, another posting is rejected, non-JSON is left to validation', () => {
  assert.equal(checkReplyPosting('{"posting_id":"gh-stripe:1","claims":[]}', 'gh-stripe:1').ok, true);
  const bad = checkReplyPosting('{"posting_id":"gh-stripe:2","claims":[]}', 'gh-stripe:1');
  assert.equal(bad.ok, false); assert.equal(bad.got, 'gh-stripe:2');
  assert.equal(checkReplyPosting('{"claims":[]}', 'gh-stripe:1').ok, false);
  assert.equal(checkReplyPosting('```json {} ```', 'gh-stripe:1').ok, true);
});

test('import-manual refuses a misfiled reply: no record written, exit code 3; the correctly filed one imports', () => {
  const real = join(ROOT, 'runs', 'claude', 'justify.v1-v1.1.0-e');
  const dir = mkdtempSync(join(tmpdir(), 'js3-import-test-'));
  mkdirSync(join(dir, 'manual'), { recursive: true });
  cpSync(join(real, 'manual', 'prompts'), join(dir, 'manual', 'prompts'), { recursive: true });
  mkdirSync(join(dir, 'manual', 'responses'));
  const m = JSON.parse(readFileSync(join(dir, 'manual', 'prompts', 'manifest.json'), 'utf8'));
  const [a, b] = m.prompts;
  // a's file holds a reply for b (the A005/A010 mix-up); b's file holds b's own reply.
  const reply = posting => JSON.stringify({ posting_id: posting, claims: [{ claim: 'The posting does not state sponsorship.', kind: 'quoted', quote: null, proposed_label: 'insufficient', abstain: true }] });
  writeFileSync(join(dir, 'manual', 'responses', `${a.id}.txt`), reply(b.posting));
  writeFileSync(join(dir, 'manual', 'responses', `${b.id}.txt`), reply(b.posting));
  const r = spawnSync(process.execPath, [join(ROOT, 'tools', 'import-manual.mjs'), '--model', 'synthetic-test', '--date', '2026-11-25', '--dir', dir], { encoding: 'utf8' });
  assert.equal(r.status, 3, r.stderr);
  const status = JSON.parse(r.stdout).find(x => x.id === a.id).status; // stdout is a JSON report
  assert.ok(status.startsWith(`REJECTED, not imported: posting_id "${b.posting}" is not ${a.posting}`), status);
  assert.ok(!existsSync(join(dir, `${a.id}.json`)), 'no record for the misfiled reply');
  assert.ok(existsSync(join(dir, `${b.id}.json`)), 'the correctly filed reply is imported');
});
