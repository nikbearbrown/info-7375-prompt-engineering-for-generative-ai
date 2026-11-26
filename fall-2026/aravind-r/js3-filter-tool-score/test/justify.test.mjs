// Phase 3 validator and prompt assembly (no Claude call). SYNTHETIC posting text.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { validateJustification, buildPrompt, definitionFromFilter } from '../src/justify.mjs';
import { CLAUDE_ARGS } from '../src/judge.mjs';
import { ROOT } from '../testlib/helpers.mjs';

const TEXT = 'Preferred Qualifications\n5+ years in product management.\nLocation: San Francisco, CA';
const ok = claims => JSON.stringify({ posting_id: 'b:1', claims });
const c = (o = {}) => ({ claim: 'Five years are preferred.', kind: 'quoted', quote: '5+ years in product management.', proposed_label: 'supported', abstain: false, ...o });

test('a well-formed reply with a verbatim quote validates', () => {
  const r = validateJustification(ok([c()]), { postingId: 'b:1', postingText: TEXT });
  assert.equal(r.ok, true); assert.equal(r.claims[0].quote_check, 'exact'); assert.equal(r.claims_with_rule_violations, 0);
});
test('a paraphrased quote cannot carry supported (W10)', () => {
  const r = validateJustification(ok([c({ quote: '5 years of product management' })]), { postingId: 'b:1', postingText: TEXT });
  assert.equal(r.claims[0].quote_check, 'not a substring');
  assert.deepEqual(r.claims[0].allowed_labels, ['insufficient']);
  assert.equal(r.claims_with_rule_violations, 1);
});
test('abstain needs quote null and insufficient', () => {
  const good = validateJustification(ok([c({ claim: 'The posting does not state sponsorship.', quote: null, proposed_label: 'insufficient', abstain: true })]), { postingId: 'b:1', postingText: TEXT });
  assert.equal(good.claims_with_rule_violations, 0);
  const bad = validateJustification(ok([c({ abstain: true })]), { postingId: 'b:1', postingText: TEXT });
  assert.equal(bad.claims_with_rule_violations, 1);
});
test('wrong posting id, extra keys, prose, or code fences are invalid, never repaired', () => {
  assert.equal(validateJustification(JSON.stringify({ posting_id: 'b:2', claims: [c()] }), { postingId: 'b:1', postingText: TEXT }).ok, false);
  assert.equal(validateJustification(JSON.stringify({ posting_id: 'b:1', claims: [c()], verdict: 'relevant' }), { postingId: 'b:1', postingText: TEXT }).ok, false);
  assert.equal(validateJustification('Here you go: ' + ok([c()]), { postingId: 'b:1', postingText: TEXT }).ok, false);
  assert.equal(validateJustification('```json\n' + ok([c()]) + '\n```', { postingId: 'b:1', postingText: TEXT }).ok, false);
});
test('prompt assembly fills all three slots from FILTER.md and the template', () => {
  const tpl = readFileSync(join(ROOT, 'prompts', 'justify.v1.md'), 'utf8');
  const def = definitionFromFilter(readFileSync(join(ROOT, 'FILTER.md'), 'utf8'));
  assert.match(def, /never 7\+/); assert.match(def, /owning product\s+direction/);
  const p = buildPrompt(tpl, { definition: def, persona: '{}', posting: '{"id":"b:1"}' });
  assert.ok(!p.includes('{{'));
});
test('the Claude call is tool-less, MCP-less, and not persisted', () => {
  assert.deepEqual(CLAUDE_ARGS.slice(0, 2), ['--tools', '']);
  assert.ok(CLAUDE_ARGS.includes('--strict-mcp-config') && CLAUDE_ARGS.includes('--no-session-persistence'));
});

test('amendment 2026-11-25: a quote may come from the location field; its source is recorded', () => {
  const reply = ok([c({ claim: 'The role is in San Francisco.', quote: 'San Francisco, Seattle', kind: 'quoted' })]);
  const withField = validateJustification(reply, { postingId: 'b:1', postingText: TEXT, postingLocation: 'San Francisco, Seattle' });
  assert.equal(withField.claims[0].quote_check, 'exact');
  assert.equal(withField.claims[0].quote_source, 'field:location');
  const bodyFirst = validateJustification(ok([c()]), { postingId: 'b:1', postingText: TEXT, postingLocation: 'x' });
  assert.equal(bodyFirst.claims[0].quote_source, 'body');
  const noField = validateJustification(reply, { postingId: 'b:1', postingText: TEXT });
  assert.equal(noField.claims[0].quote_check, 'not a substring');
});
