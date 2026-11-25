// Loads the filter from FILTER.md (§6, the ```json filter-spec block). The document is
// the filter: nothing else in src/ holds a weight, word, or threshold.
import { readFileSync } from 'node:fs';

const BLOCK = /```json filter-spec\n([\s\S]*?)\n```/g;

export function parseFilterSpec(markdown) {
  const blocks = [...String(markdown).matchAll(BLOCK)];
  if (blocks.length !== 1) throw new Error(`FILTER.md must contain exactly one \`\`\`json filter-spec block (found ${blocks.length})`);
  const spec = JSON.parse(blocks[0][1]);
  const errors = validateSpec(spec);
  if (errors.length) throw new Error(`filter-spec invalid: ${errors.join('; ')}`);
  return spec;
}

export function loadFilterSpec(path) {
  return parseFilterSpec(readFileSync(path, 'utf8'));
}

export function validateSpec(s) {
  const e = [];
  const num01 = (v, name) => { if (typeof v !== 'number' || v < 0 || v > 1) e.push(`${name} must be a number in [0,1]`); };
  if (!/^\d+\.\d+\.\d+(-[a-z0-9.]+)?$/.test(s?.version ?? '')) e.push('version must be semver');
  for (const k of ['title', 'location', 'experience', 'topic']) num01(s?.weights?.[k], `weights.${k}`);
  num01(s?.threshold, 'threshold');
  num01(s?.near_band, 'near_band');
  for (const t of ['core', 'adjacent']) {
    num01(s?.title?.tiers?.[t]?.value, `title.tiers.${t}.value`);
    if (!Array.isArray(s?.title?.tiers?.[t]?.titles)) e.push(`title.tiers.${t}.titles must be a list`);
  }
  for (const k of ['cut_chars', 'junior_terms']) if (!Array.isArray(s?.title?.[k])) e.push(`title.${k} must be a list`);
  if (!Array.isArray(s?.topic?.terms) || !(s.topic.saturate_at > 0)) e.push('topic.terms list and topic.saturate_at > 0 required');
  if (!Number.isInteger(s?.experience?.junior_upper_max)) e.push('experience.junior_upper_max must be an integer');
  num01(s?.experience?.stretch_value, 'experience.stretch_value');
  num01(s?.experience?.impute, 'experience.impute');
  num01(s?.location?.impute, 'location.impute');
  if (!s?.location?.aliases || typeof s.location.aliases !== 'object') e.push('location.aliases must be an object');
  for (const k of ['sponsorship', 'citizenship']) if (!Array.isArray(s?.vetoes?.[k])) e.push(`vetoes.${k} must be a list`);
  if (!Number.isInteger(s?.min_text_chars)) e.push('min_text_chars must be an integer');
  return e;
}
