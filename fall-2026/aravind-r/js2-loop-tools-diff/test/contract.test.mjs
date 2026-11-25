// Tests for CONTRACT.md. Each "Wrong version" from the contract is built here as a
// mutant, and the test proves the check that guards it fails on that mutant.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { judgePosting, validateRuleResult, titlePrefix } from '../src/rule.mjs';
import { diffNew, loadState, saveState } from '../src/state.mjs';
import { guardedFetch, boardUrl, Refused } from '../src/fetch.mjs';
import { validatePersona, validatePrefs } from '../src/persona.mjs';
import { validateClaudeOutput, claudeJudge, quoteFidelity } from '../src/claude-judge.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const board = JSON.parse(readFileSync(join(ROOT, 'test/fixtures/constructed-board.json'), 'utf8'));
const prefs = JSON.parse(readFileSync(join(ROOT, 'persona/persona-prefs.json'), 'utf8'));
const resume = JSON.parse(readFileSync(join(ROOT, 'persona/maya-sehgal.resume.json'), 'utf8'));

// Hand-computed from CONTRACT.md for the constructed fixture: [verdict, first failed gate].
const EXPECTED = {
  101: ['relevant', null], 102: ['not_relevant', 1], 103: ['relevant', null], 104: ['not_relevant', 1],
  105: ['not_relevant', 3], 106: ['not_relevant', 5], 107: ['not_relevant', 4], 108: ['not_relevant', 6],
  109: ['not_relevant', 1], 110: ['relevant', null],
};
const judgeAll = jobs => jobs.map(j => judgePosting(j, prefs));
function mismatches(results) {
  return results.filter(r => {
    const e = EXPECTED[r.id];
    return !e || r.rule_verdict !== e[0] || r.rule_justification.first_failed !== e[1];
  }).map(r => r.id);
}

test('rule: every constructed posting gets the hand-computed verdict and first failed gate, by id', () => {
  assert.deepEqual(mismatches(judgeAll(board.jobs)), []);
});

test('Wrong version 1 (misaligned verdicts): an off-by-one pairing is caught by checking by id', () => {
  const right = judgeAll(board.jobs);
  const sorted = [...board.jobs].sort((x, y) => x.title.localeCompare(y.title));
  // Mutant: verdicts computed on a sorted copy, then zipped back onto the original order.
  const mutant = board.jobs.map((j, i) => ({ ...judgePosting(sorted[i], prefs), id: j.id }));
  assert.ok(mismatches(mutant).length > 0, 'the misaligned mutant must be detected');
  // Adjacent fixture postings really do have opposite verdicts, so a one-step shift shows up.
  const shifted = right.map((r, i) => ({ ...right[(i + 1) % right.length], id: r.id }));
  assert.ok(mismatches(shifted).length > 0);
});

test('Wrong version 2 (uncited justification): the validator rejects a gate with no field cited', () => {
  for (const r of judgeAll(board.jobs)) assert.equal(validateRuleResult(r).ok, true, `real result ${r.id} must validate`);
  const r = judgeAll(board.jobs)[0];
  const noPostingField = structuredClone(r); noPostingField.rule_justification.gates[2].posting_field = '';
  const noPrefsField = structuredClone(r); delete noPrefsField.rule_justification.gates[3].compared_with;
  const prefsFromWrongSource = structuredClone(r); prefsFromWrongSource.rule_justification.gates[4].compared_with.source = 'CONTRACT.md';
  const noGates = structuredClone(r); noGates.rule_justification.gates = [];
  for (const bad of [noPostingField, noPrefsField, prefsFromWrongSource, noGates]) assert.equal(validateRuleResult(bad).ok, false);
});

test('Wrong version 3 (constant judge): an always-relevant judge fails on the known not-relevant postings', () => {
  const mutant = judgeAll(board.jobs).map(r => ({ ...r, rule_verdict: 'relevant', rule_justification: { ...r.rule_justification, first_failed: null } }));
  const caught = mismatches(mutant);
  for (const id of [102, 104, 105, 106]) assert.ok(caught.includes(id), `${id} must be caught`);
  const real = Object.fromEntries(judgeAll(board.jobs).map(r => [r.id, r.rule_verdict]));
  for (const id of [102, 104, 105, 106]) assert.equal(real[id], 'not_relevant');
});

test('Wrong version 4 (seen-id bug): baseline reports none; the seeded second run reports exactly the new ids', () => {
  const dir = mkdtempSync(join(tmpdir(), 'js1-state-'));
  const statePath = join(dir, 'seen.json');
  const earlier = board.jobs.filter(j => ![103, 107].includes(j.id));
  const first = diffNew(earlier, loadState(statePath));
  assert.equal(first.baseline, true);
  assert.deepEqual(first.fresh, []);
  saveState(statePath, { board: 'fixture', ids: earlier.map(j => j.id), run: 'baseline' });
  const second = diffNew(board.jobs, loadState(statePath));
  assert.deepEqual(second.fresh.map(j => j.id), [103, 107]);
  // Mutant: ignores state, so it re-reports baseline ids.
  const mutantFresh = board.jobs;
  assert.notDeepEqual(mutantFresh.map(j => j.id), [103, 107]);
  saveState(statePath, { board: 'fixture', ids: [...loadState(statePath).ids, ...board.jobs.map(j => j.id)], run: 'second' });
  assert.deepEqual(diffNew(board.jobs, loadState(statePath)).fresh, [], 'a third run with nothing new reports nothing');
});

test('Gate details as written: title cut, case-insensitive location, sentence-scoped years', () => {
  assert.equal(titlePrefix('Product Manager, Payments'), 'Product Manager');
  assert.equal(titlePrefix('Product Manager - Radar'), 'Product Manager');
  assert.equal(titlePrefix('Technical Program Manager (AI)'), 'Technical Program Manager');
  const r110 = judgePosting(board.jobs.find(j => j.id === 110), prefs);
  assert.equal(r110.rule_justification.gates[3].pass, true, '"remote" matches "Remote" ignoring case');
  assert.equal(r110.rule_justification.gates[2].posting_value.lower_bound, 3, 'boilerplate "10 years ago" is not in an experience sentence');
  assert.deepEqual(r110.rule_justification.domain_citation, [{ term: 'mobile', where: 'content' }]);
});

test('Refuses: hosts off the allow-list, plain http, and redirects', async () => {
  const ok = async () => ({ status: 200, ok: true, text: async () => '{"jobs":[]}', headers: new Map() });
  await assert.rejects(guardedFetch('https://api.lever.co/v0/postings/x', { fetchImpl: ok }), Refused);
  await assert.rejects(guardedFetch('http://boards-api.greenhouse.io/v1/boards/stripe/jobs', { fetchImpl: ok }), Refused);
  const redirect = async () => ({ status: 302, ok: false, headers: new Map([['location', 'https://evil.example/']]) });
  const log = [];
  await assert.rejects(guardedFetch(boardUrl('stripe'), { fetchImpl: redirect, log }), Refused);
  assert.equal(log[0].result, 'refused: redirect');
  assert.throws(() => boardUrl('stripe/../../x'), Refused);
  assert.equal(await guardedFetch(boardUrl('stripe'), { fetchImpl: ok }), '{"jobs":[]}');
});

test('Refuses: a résumé with a real-looking email or phone does not validate', () => {
  assert.equal(validatePersona(resume).ok, true, 'the shipped Maya Sehgal file passes');
  const realEmail = structuredClone(resume); realEmail.personal.email = 'maya@gmail.com';
  const realPhone = structuredClone(resume); realPhone.personal.phone = '(617) 373-2000';
  const noEmail = structuredClone(resume); delete realEmail.x; noEmail.personal.email = '';
  for (const bad of [realEmail, realPhone, noEmail]) assert.equal(validatePersona(bad).ok, false);
  assert.equal(validatePrefs(prefs).ok, true);
  assert.equal(validatePrefs({ ...prefs, years_pm: '2' }).ok, false);
});

test('watch CLI refuses to start on a failing persona (exit 3) and writes nothing', () => {
  const dir = mkdtempSync(join(tmpdir(), 'js1-cli-'));
  const bad = join(dir, 'bad.json');
  writeFileSync(bad, JSON.stringify({ personal: { email: 'someone@gmail.com' } }));
  const r = spawnSync(process.execPath, [join(ROOT, 'src/watch.mjs'), '--board', 'stripe', '--state', join(dir, 's.json'), '--label', 'seeded-x',
    '--from-file', join(ROOT, 'test/fixtures/constructed-board.json'), '--resume', bad, '--runs', join(dir, 'runs'), '--judge', 'none'], { encoding: 'utf8' });
  assert.equal(r.status, 3);
  assert.match(r.stderr, /persona validation failed/);
});

test('watch CLI end to end on the constructed fixture: baseline then a labeled seeded run', () => {
  const dir = mkdtempSync(join(tmpdir(), 'js1-cli-'));
  const earlier = join(dir, 'earlier.json');
  writeFileSync(earlier, JSON.stringify({ jobs: board.jobs.filter(j => ![103, 107].includes(j.id)) }));
  const run = (file, label) => spawnSync(process.execPath, [join(ROOT, 'src/watch.mjs'), '--board', 'stripe', '--state', join(dir, 's.json'), '--label', label,
    '--from-file', file, '--runs', join(dir, 'runs'), '--judge', 'none'], { encoding: 'utf8' });
  const a = run(earlier, 'seeded-baseline');
  assert.equal(a.status, 0, a.stderr); assert.match(a.stdout, /BASELINE \(0 reported as new\)/);
  const b = run(join(ROOT, 'test/fixtures/constructed-board.json'), 'seeded-second');
  assert.equal(b.status, 0, b.stderr); assert.match(b.stdout, /2 new/);
  const unlabeled = run(earlier, 'second');
  assert.equal(unlabeled.status, 2, 'a run from a saved file must be labeled seeded');
});

test('Claude validator: rejects anything but the fixed format; an invalid reply is recorded, not repaired', () => {
  const good = { verdict: 'relevant', cited_posting_fields: ['title'], cited_persona_fields: ['years_pm'], justification: 'Title is Product Manager; years_pm 2.' };
  assert.equal(validateClaudeOutput(JSON.stringify(good)).ok, true);
  const bad = [
    '```json\n' + JSON.stringify(good) + '\n```',
    'Sure! ' + JSON.stringify(good),
    JSON.stringify({ ...good, verdict: 'Relevant' }),
    JSON.stringify({ ...good, extra: 1 }),
    JSON.stringify({ ...good, cited_posting_fields: [] }),
    JSON.stringify({ ...good, cited_persona_fields: ['salary'] }),
    JSON.stringify({ ...good, justification: 'x'.repeat(601) }),
    '[]',
  ];
  for (const b of bad) assert.equal(validateClaudeOutput(b).ok, false, b.slice(0, 40));
  let calls = 0;
  const runner = () => { calls++; return { status: 0, stdout: JSON.stringify({ is_error: false, result: 'I think it is relevant.', modelUsage: { m: {} } }) }; };
  const r = claudeJudge(board.jobs[0], { resume, prefs, template: '{{RULE}}{{PERSONA}}{{POSTING}}', runner });
  assert.equal(r.claude_verdict, 'invalid');
  assert.equal(r.claude_label, 'JUDGMENT');
  assert.equal(calls, 1, 'no silent retry');
});

test('Gate 2 revision 2026-10-31: junior title terms match whole words only', () => {
  const base = { content: '', location: { name: 'Remote' }, departments: [] };
  const g2 = title => judgePosting({ ...base, id: 1, title }, prefs).rule_justification.gates[1];
  assert.equal(g2('Product Manager, International Payments').pass, true, '"International" is not "Intern"');
  assert.equal(g2('Product Manager, Internal Tools').pass, true);
  assert.equal(g2('Product Manager Intern').pass, false);
  assert.equal(g2('Associate Product Manager').pass, false);
  assert.equal(g2('APM, Payments').pass, false);
  assert.equal(g2('Product Manager: New Grad Accelerator').pass, false);
});

test('v2 schema: evidence object required and well-formed; quote fidelity recorded, not enforced', () => {
  const base = { verdict: 'relevant', cited_posting_fields: ['content'], cited_persona_fields: ['years_pm'], justification: 'x' };
  const ev = { gate2: 'not found', gate3: '3+ years of product management experience', gate5: 'not found', gate6: 'not found' };
  assert.equal(validateClaudeOutput(JSON.stringify({ ...base, evidence: ev }), { schema: 'v2' }).ok, true);
  assert.equal(validateClaudeOutput(JSON.stringify(base), { schema: 'v2' }).ok, false, 'missing evidence');
  assert.equal(validateClaudeOutput(JSON.stringify({ ...base, evidence: { ...ev, gate4: 'x' } }), { schema: 'v2' }).ok, false, 'extra evidence key');
  assert.equal(validateClaudeOutput(JSON.stringify({ ...base, evidence: { ...ev, gate3: '' } }), { schema: 'v2' }).ok, false, 'empty quote');
  assert.equal(validateClaudeOutput(JSON.stringify({ ...base, evidence: [] }), { schema: 'v2' }).ok, false, 'evidence not an object');
  assert.equal(validateClaudeOutput(JSON.stringify({ ...base, evidence: ev })).ok, false, 'v1 schema rejects the extra key');
  const p101 = board.jobs.find(j => j.id === 101);
  assert.deepEqual(quoteFidelity(ev, p101), { ok: true, per_gate: { gate2: 'not found', gate3: 'exact', gate5: 'not found', gate6: 'not found' } });
  assert.equal(quoteFidelity({ ...ev, gate3: '3+ years of PM experience' }, p101).ok, false);
});
