// Greenhouse job board provider. The request goes through the policy session
// (src/policy.mjs: allow-list, redirect: 'manual', timeout = min(15 s, remaining)).
// IDs are passed through as the board returned them: ID canonicalization and
// validation belong to src/state.mjs (GATE.md, "State meaning and preservation").
import { boardUrl } from '../policy.mjs';

export const system = 'greenhouse';

export function url(token) {
  return boardUrl(system, token);
}

// hooks: { onAttempt, onRetry }, passed to the session so events are recorded as they happen.
export function observe(session, token, hooks) {
  return session.get({ method: 'GET', url: url(token), headers: { accept: 'application/json' } }, hooks);
}

// Raw body -> { ok: true, jobs } or { ok: false, error: 'malformed', reason }.
export function parse(body) {
  let j;
  try { j = JSON.parse(body); } catch { return { ok: false, error: 'malformed', reason: 'body is not JSON' }; }
  if (!j || typeof j !== 'object' || !Array.isArray(j.jobs)) return { ok: false, error: 'malformed', reason: 'no jobs array' };
  return {
    ok: true,
    jobs: j.jobs.map(p => ({ id: p?.id, title: p?.title, location: p?.location?.name ?? null, url: p?.absolute_url ?? null })),
  };
}
