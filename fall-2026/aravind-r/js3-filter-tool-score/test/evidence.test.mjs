// FILTER.md §2: the mechanical part of the evidence rules (W10). Entailment itself is
// judged by hand; the code only refuses labels the quote cannot carry. SYNTHETIC text.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { quoteCheck, allowedLabels, validateClaimLabel } from '../src/evidence.mjs';

const TEXT = 'Stripe is a financial infrastructure platform for payments.\nYou will lead the Billing roadmap. 5+ years of product management experience.';

test('exact substring -> exact; anything else -> not a substring', () => {
  assert.equal(quoteCheck('You will lead the Billing roadmap.', TEXT), 'exact');
  assert.equal(quoteCheck('you will lead the billing roadmap.', TEXT), 'not a substring', 'case matters');
  assert.equal(quoteCheck('You will lead the  Billing roadmap.', TEXT), 'not a substring', 'whitespace matters');
  assert.equal(quoteCheck('You will own the Billing roadmap.', TEXT), 'not a substring', 'paraphrase');
  assert.equal(quoteCheck('', TEXT), 'not a substring');
  assert.equal(quoteCheck(null, TEXT), 'not a substring');
});

test('W10: a non-verbatim quote can only be insufficient', () => {
  assert.deepEqual(allowedLabels('not a substring'), ['insufficient']);
  assert.deepEqual(allowedLabels('exact').sort(), ['contradicted', 'insufficient', 'supported']);
  const bad = validateClaimLabel({ claim: 'Role works on billing', quote: 'You own billing.', label: 'supported' }, TEXT);
  assert.equal(bad.ok, false);
  const ok = validateClaimLabel({ claim: 'Role works on billing', quote: 'You own billing.', label: 'insufficient' }, TEXT);
  assert.equal(ok.ok, true);
});

test('labels outside the three are refused; a missing label is refused', () => {
  const q = 'You will lead the Billing roadmap.';
  assert.equal(validateClaimLabel({ claim: 'x', quote: q, label: 'likely' }, TEXT).ok, false);
  assert.equal(validateClaimLabel({ claim: 'x', quote: q }, TEXT).ok, false);
  assert.equal(validateClaimLabel({ claim: 'x', quote: q, label: 'supported' }, TEXT).ok, true);
});
