// FILTER.md §2: the mechanical half of the evidence rules. The code only checks that a
// quote is an exact substring of the posting's normalized text; whether the span entails
// the claim is judged by hand.
export const LABELS = ['supported', 'contradicted', 'insufficient'];

export function quoteCheck(quote, text) {
  return typeof quote === 'string' && quote.length > 0 && typeof text === 'string' && text.includes(quote) ? 'exact' : 'not a substring';
}

export function allowedLabels(status) {
  return status === 'exact' ? [...LABELS] : ['insufficient'];
}

export function validateClaimLabel({ claim, quote, label } = {}, text) {
  const errors = [];
  if (typeof claim !== 'string' || !claim.trim()) errors.push('claim missing');
  if (!LABELS.includes(label)) errors.push(`label must be one of ${LABELS.join(', ')}`);
  const status = quoteCheck(quote, text);
  if (LABELS.includes(label) && !allowedLabels(status).includes(label)) errors.push(`label "${label}" not allowed: quote is ${status}`);
  return { ok: errors.length === 0, errors, quote_status: status };
}
