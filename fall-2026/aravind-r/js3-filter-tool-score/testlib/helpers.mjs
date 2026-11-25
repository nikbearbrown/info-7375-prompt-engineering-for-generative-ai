// Shared test fixtures. Every posting built here is SYNTHETIC (made up for a test),
// not from the snapshot, unless a test says it reads data/.
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
export const FILTER_MD = join(ROOT, 'FILTER.md');
export const SNAPSHOT = join(ROOT, 'data', 'raw', '20261110T225032086Z-post-patch-2');

// Same values as persona/persona-prefs.json (fictional persona Maya Sehgal).
export const PREFS = Object.freeze({
  years_pm: 2,
  locations: ['San Francisco', 'Los Angeles', 'San Jose', 'Remote'],
  needs_sponsorship: true,
  domains: ['payments', 'fintech', 'data', 'e-commerce', 'mobile'],
});

// Neutral padding: contains no topic term, no veto phrase, no "experience", no years.
const FILLER = 'You will work with a cross-functional team to shape the roadmap and talk to customers every week. ';

export function mk({ id = 'syn-1', board = 'syn', title = 'Product Manager', location = 'San Francisco, CA',
  department = 'Product', text = '', url = 'https://example.com/job/1', pad = true } = {}) {
  const body = pad ? `${text}\n${FILLER.repeat(3)}` : text;
  return { id, board, title, location, department, text: body, url };
}

export const clone = o => JSON.parse(JSON.stringify(o));
