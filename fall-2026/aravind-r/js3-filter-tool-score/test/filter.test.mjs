// Wrong versions W1, W2, W3, W5, W7, W8 from FILTER.md §5, plus the component tables in §1.2.
// All postings are SYNTHETIC fixtures.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadFilterSpec } from '../src/spec.mjs';
import { scorePosting, rankResults } from '../src/filter.mjs';
import { FILTER_MD, PREFS, mk, clone } from '../testlib/helpers.mjs';

const spec = loadFilterSpec(FILTER_MD);
const score = (p, s = spec, prefs = PREFS) => scorePosting(p, { spec: s, prefs });

// ---------- W1: whole words, not substrings ----------
test('W1: "data" does not match "database"', () => {
  const r = score(mk({ department: 'Infra', text: 'You will own our database migration.' }));
  assert.ok(!r.components.topic.terms.includes('data'));
});

test('W1: "Intern" does not match "International" (no junior override)', () => {
  const r = score(mk({ title: 'Product Manager, International Expansion' }));
  assert.equal(r.components.title.value, 1);
});

test('W1: location alias "LA" does not match "Lagos" or "LATAM"; "SF" does match', () => {
  assert.equal(score(mk({ location: 'Lagos, Nigeria' })).components.location.value, 0);
  assert.equal(score(mk({ location: 'Mexico City, LATAM' })).components.location.value, 0);
  assert.equal(score(mk({ location: 'SF, SEA, NY' })).components.location.value, 1);
});

// ---------- title tiers ----------
test('title tiers: core 1, adjacent 0.5, other 0, junior 0; prefix cut at , - ( :', () => {
  assert.equal(score(mk({ title: 'Senior Product Manager, Payments' })).components.title.value, 1);
  assert.equal(score(mk({ title: 'Staff Product Manager - Billing' })).components.title.value, 0.5);
  assert.equal(score(mk({ title: 'Product Marketing Manager' })).components.title.value, 0);
  assert.equal(score(mk({ title: 'Product Manager: New Grad Accelerator' })).components.title.value, 0);
  assert.equal(score(mk({ title: 'Associate Product Manager' })).components.title.value, 0);
  assert.equal(score(mk({ title: '  product   manager (Risk)' })).components.title.value, 1);
});

// ---------- experience table ----------
// v1.1.0-a (2026-11-25): tiers follow persona-prefs.json preferred_max_years 4 / stretch_max_years 6.
// (v1.0.0 tested years_pm+1 = 3 -> 1, 4 -> 0.5, 5+ -> 0.)
test('experience: <= preferred_max -> 1, <= stretch_max -> stretch, more -> 0, junior range -> 0, absent -> unknown', () => {
  const e = t => score(mk({ text: t })).components.experience;
  assert.equal(e('3+ years of product management experience.').value, 1);
  assert.equal(e('4+ years of experience as a PM.').value, 1);
  assert.equal(e('5+ years of experience as a PM.').value, spec.experience.stretch_value);
  assert.equal(e('7+ years of experience.').value, 0);
  assert.equal(e('8+ years of experience.').value, 0);
  assert.equal(e('0-2 years of experience.').value, 0);
  assert.equal(e('We ship things.').value, null);
  assert.ok(score(mk({ text: 'We ship things.' })).unknown.includes('experience'));
});

// v1.1.0-d (cites A010): the "N-M+ years" misread found 2026-11-25 is fixed; this was a TODO test.
test('v1.1.0-d: ranges read the lower bound; a lone N+ is unchanged', () => {
  const lb = t => score(mk({ text: t })).components.experience.lower_bound;
  assert.equal(lb('6-10 years of product management experience.'), 6);
  assert.equal(lb('6–10+ years of product management experience.'), 6);
  assert.equal(lb('6-10+ years of product management experience.'), 6);
  assert.equal(lb('5 to 7 years of product management experience.'), 5);
  assert.equal(lb('10+ years of product management experience.'), 10);
  assert.equal(lb('3 or more years of experience.'), 3);
  assert.equal(score(mk({ text: '6–10+ years of product management experience.' })).components.experience.value, spec.experience.stretch_value);
  assert.equal(score(mk({ text: '0 to 2 years of experience.' })).components.experience.case, 'junior range');
});

test('prefs without the corrected experience fields are refused, not silently defaulted', () => {
  assert.throws(() => scorePosting(mk(), { spec, prefs: { ...PREFS, preferred_max_years: undefined } }));
  assert.throws(() => scorePosting(mk(), { spec, prefs: { ...PREFS, preferred_max_years: 6, stretch_max_years: 4 } }));
});

test('experience: only a phrase in a sentence containing "experience" counts', () => {
  const r = score(mk({ text: 'We were founded 10+ years ago.\n2+ years of product experience required.' }));
  assert.equal(r.components.experience.value, 1);
  assert.equal(r.components.experience.lower_bound, 2);
});

// ---------- W2: a veto is a veto ----------
test('W2: a no-sponsorship posting that is otherwise perfect scores 0, is rejected, and quotes the phrase', () => {
  const p = mk({ text: 'Payments and fintech. 2+ years of experience. Unfortunately we are unable to sponsor visas for this role.' });
  const r = score(p);
  assert.equal(r.score, 0);
  assert.equal(r.decision, 'reject');
  assert.equal(r.veto.rule, 'sponsorship');
  assert.equal(r.veto.phrase, 'unable to sponsor');
  assert.ok(p.text.includes(r.veto.quote), 'quote is verbatim from the posting');
  assert.ok(r.veto.quote.toLowerCase().includes('unable to sponsor'));
});

test('W2: citizenship veto applies regardless of sponsorship preference', () => {
  const r = score(mk({ text: 'Must hold an active security clearance. 2+ years of experience.' }), spec, { ...PREFS, needs_sponsorship: false });
  assert.equal(r.veto.rule, 'citizenship');
  assert.equal(r.score, 0);
});

test('sponsorship veto does not apply when needs_sponsorship is false', () => {
  const r = score(mk({ text: 'We are unable to sponsor visas. 2+ years of experience.' }), spec, { ...PREFS, needs_sponsorship: false });
  assert.equal(r.veto, null);
});

// ---------- W3: distinct terms, saturating ----------
test('W3: repeating a topic word does not raise the score; two distinct terms beat one repeated', () => {
  const once = score(mk({ department: 'Product', text: 'payments.' })).components.topic.value;
  const many = score(mk({ department: 'Product', text: 'payments '.repeat(20) })).components.topic.value;
  const two = score(mk({ department: 'Product', text: 'payments and mobile.' })).components.topic.value;
  assert.equal(once, many);
  assert.ok(two > many);
  const all = score(mk({ department: 'Product', text: 'payments mobile data fintech e-commerce' })).components.topic.value;
  assert.equal(all, 1);
});

// ---------- W5: unknown is not a match ----------
test('W5: missing location that could flip the decision gives cannot_tell, not keep', () => {
  const r = score(mk({ location: '', text: '3+ years of experience.' }));
  assert.ok(r.unknown.includes('location'));
  assert.ok(r.lo < spec.threshold && r.hi >= spec.threshold);
  assert.equal(r.decision, 'cannot_tell');
});

test('W5: missing location that cannot flip it is decided (non-PM title -> reject)', () => {
  const r = score(mk({ title: 'Account Executive', location: '' }));
  assert.equal(r.decision, 'reject');
});

test('W5: the displayed score never decides (imputed value inside the gap -> still cannot_tell)', () => {
  const s = clone(spec); s.experience.impute = 1.0; // displayed score would clear the threshold
  const r = score(mk({ text: 'We ship things.' }), s); // experience unknown, topic 0
  assert.ok(r.score >= s.threshold);
  assert.equal(r.decision, 'cannot_tell');
});

test('§2.3: missing title or text under min_text_chars -> cannot_tell, but vetoes still apply', () => {
  assert.equal(score(mk({ title: '' })).decision, 'cannot_tell');
  assert.equal(score(mk({ text: 'Short.', pad: false })).decision, 'cannot_tell');
  const v = score(mk({ text: 'We cannot sponsor.', pad: false }));
  assert.equal(v.decision, 'reject');
  assert.equal(v.veto.rule, 'sponsorship');
});

// ---------- W7: >= at the threshold, with rounding ----------
test('W7: a score exactly at the threshold is keep (0.4 + 0.25 + 0.05 must not round down)', () => {
  const s = clone(spec);
  s.weights = { title: 0.4, location: 0.25, experience: 0.25, topic: 0.1 };
  s.threshold = 0.7; s.topic.saturate_at = 2;
  const r = score(mk({ text: 'payments.' }), s); // T=1, L=1, P=0.5, E unknown -> lo = 0.7
  assert.equal(r.lo, 0.7);
  assert.equal(r.decision, 'keep');
});

// ---------- W8: ranking ----------
test('W8: ranking is keep by score desc, then cannot_tell, then reject; ties by board then id', () => {
  const rows = [
    { board: 'b', id: '2', decision: 'reject', score: 0.65 },
    { board: 'a', id: '9', decision: 'cannot_tell', score: 0.9 },
    { board: 'b', id: '1', decision: 'keep', score: 0.8 },
    { board: 'a', id: '5', decision: 'keep', score: 0.8 },
    { board: 'a', id: '3', decision: 'keep', score: 0.95 },
    { board: 'a', id: '4', decision: 'reject', score: 0 },
  ];
  assert.deepEqual(rankResults(rows).map(r => r.board + r.id), ['a3', 'a5', 'b1', 'a9', 'b2', 'a4']);
  assert.deepEqual(rows.map(r => r.id), ['2', '9', '1', '5', '3', '4'], 'input not mutated');
});

test('result carries components, weights used, and the spec version', () => {
  const r = score(mk({ text: '3+ years of experience. payments.' }));
  assert.equal(r.spec_version, spec.version);
  for (const k of ['title', 'topic', 'experience', 'location']) assert.ok(k in r.components, k);
  assert.ok(r.lo <= r.score && r.score <= r.hi);
});

// ---------- W13: title + topic cannot buy back a failed location or experience ----------
// Exact combinations from FILTER.md §5 (W13), under the committed §6 spec. Topic is set by the
// number of distinct terms: "payments and mobile" -> P = 1; "payments" -> P = 0.5; none -> 0.
test('W13: core + L0 + E1 + P1 -> reject', () => {
  const r = score(mk({ location: 'Dublin, Ireland', text: 'payments and mobile. 3+ years of experience.' }));
  assert.deepEqual([r.components.title.value, r.components.location.value, r.components.experience.value, r.components.topic.value], [1, 0, 1, 1]);
  assert.equal(r.decision, 'reject');
});
test('W13: core + L1 + E0 + P1 -> reject', () => {
  const r = score(mk({ text: 'payments and mobile. 8+ years of experience.' }));
  assert.deepEqual([r.components.title.value, r.components.location.value, r.components.experience.value, r.components.topic.value], [1, 1, 0, 1]);
  assert.equal(r.decision, 'reject');
});
test('W13: core + L1 + E0.5 + P0 -> reject', () => {
  const r = score(mk({ text: '5+ years of experience.' })); // E = 0.5 under v1.1.0-a (was 4+ under v1.0.0)
  assert.deepEqual([r.components.title.value, r.components.location.value, r.components.experience.value, r.components.topic.value], [1, 1, 0.5, 0]);
  assert.equal(r.decision, 'reject');
});
test('W13: core + L1 + E0.5 + P0.5 (one term) -> keep', () => {
  const r = score(mk({ text: 'payments. 5+ years of experience.' })); // E = 0.5 under v1.1.0-a
  assert.deepEqual([r.components.title.value, r.components.location.value, r.components.experience.value, r.components.topic.value], [1, 1, 0.5, 0.5]);
  assert.equal(r.decision, 'keep');
});

// ---------- v1.1.0-b: topic words outside lines shared by many postings on the board ----------
test('v1.1.0-b: a topic word only in a shared (boilerplate) line does not count; title, department and own lines do', () => {
  const intro = 'Stripe is a financial infrastructure platform used to accept payments and grow revenue.';
  const shared = new Map([['syn', new Set([intro])]]);
  const s = clone(spec); s.topic.exclude_shared_lines_min_share = 0.2;
  const onlyIntro = mk({ department: 'Product', text: `${intro}\nYou will lead the roadmap.` });
  assert.deepEqual(scorePosting(onlyIntro, { spec: s, prefs: PREFS, shared }).components.topic.terms, []);
  assert.deepEqual(scorePosting(onlyIntro, { spec: s, prefs: PREFS, shared }).components.topic.shared_lines_checked, true);
  const ownLine = mk({ department: 'Product', text: `${intro}\nYou will own mobile payments.` });
  assert.deepEqual(scorePosting(ownLine, { spec: s, prefs: PREFS, shared }).components.topic.terms.sort(), ['mobile', 'payments']);
  const inTitle = mk({ title: 'Product Manager, Payments', department: 'Data', text: intro });
  assert.deepEqual(scorePosting(inTitle, { spec: s, prefs: PREFS, shared }).components.topic.terms.sort(), ['data', 'payments']);
});

test('v1.1.0-b: scored without corpus context, the result says shared lines were not checked', () => {
  const s = clone(spec); s.topic.exclude_shared_lines_min_share = 0.2;
  assert.equal(scorePosting(mk({ text: 'payments.' }), { spec: s, prefs: PREFS }).components.topic.shared_lines_checked, false);
});

// ---------- v1.1.0-c: the two missed no-sponsorship phrasings (e0d80ff0), bounded ----------
const VETO_C_PHRASE = 'no visa/relocation support';
const VETO_C_PATTERN = 'unable to provide (?:[a-z]+ ){0,3}visa sponsorship';
const specC = () => { const s = clone(spec); s.vetoes.sponsorship = [...s.vetoes.sponsorship.filter(p => p !== VETO_C_PHRASE), VETO_C_PHRASE]; s.vetoes.sponsorship_patterns = [VETO_C_PATTERN]; return s; };

test('v1.1.0-c: both missed phrasings from e0d80ff0 now veto, quoting the posting verbatim', () => {
  for (const line of [
    'This position needs to be based in the Beijing, China office 5 days a week. No Visa/Relocation Support.',
    "Please note that this role requires candidates to possess a valid right to work in Singapore. We are unable to provide work visa sponsorship for this position in accordance with Singapore's employment regulations.",
  ]) {
    const p = mk({ text: `3+ years of experience.\n${line}` });
    const r = scorePosting(p, { spec: specC(), prefs: PREFS });
    assert.equal(r.veto?.rule, 'sponsorship', line);
    assert.equal(r.score, 0);
    assert.ok(p.text.includes(r.veto.quote), 'quote is verbatim');
  }
});

test('v1.1.0-c: the bounded pattern does NOT match the false friends in e0d80ff0', () => {
  for (const line of [
    'Serve as an executive sponsor for key customer relationships.',
    'Represent Stripe in the financial sponsor ecosystem, including through relevant industry events.',
    'Demonstrated experience delivering third-party sponsorships and company-hosted events.',
    'Sell and manage event sponsorship, and build relationships with sponsors.',
    'Card network protocols with Visa and Mastercard; BIN sponsorship models.',
    'We are unable to provide relocation, but we offer visa sponsorship.',
    'We are unable to provide a laptop stipend, relocation help or any form of visa sponsorship.',
  ]) {
    const r = scorePosting(mk({ text: `3+ years of experience.\n${line}` }), { spec: specC(), prefs: PREFS });
    assert.equal(r.veto, null, line);
  }
});

test('v1.1.0-c: patterns apply only when the persona needs sponsorship', () => {
  const r = scorePosting(mk({ text: 'We are unable to provide work visa sponsorship.' }), { spec: specC(), prefs: { ...PREFS, needs_sponsorship: false } });
  assert.equal(r.veto, null);
});

// ---------- v1.1.0-e: TPM titles are adjacent, not core (cites A027, A044, A052) ----------
test('v1.1.0-e: Technical Program Manager titles score the adjacent tier; a strong TPM posting is not kept', () => {
  const r = score(mk({ title: 'Technical Program Manager, Payments', text: 'payments and mobile. 5+ years of experience.' }));
  assert.equal(r.components.title.tier, 'adjacent');
  assert.equal(r.components.title.value, spec.title.tiers.adjacent.value);
  assert.equal(r.decision, 'reject');
  assert.equal(score(mk({ title: 'Senior Technical Program Manager' })).components.title.tier, 'adjacent');
});
