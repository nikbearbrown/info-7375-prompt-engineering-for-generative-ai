// Lever postings provider. The request goes through the policy session
// (src/policy.mjs: allow-list, redirect: 'manual', timeout = min(15 s, remaining)).
// IDs are passed through as the board returned them (UUID strings): ID
// canonicalization and validation belong to src/state.mjs. A posting's applyUrl is
// never kept or requested.
import { boardUrl } from '../policy.mjs';

export const system = 'lever';

export function url(token) {
  return boardUrl(system, token);
}

// hooks: { onAttempt, onRetry }, passed to the session so events are recorded as they happen.
export function observe(session, token, hooks) {
  return session.get({ method: 'GET', url: url(token), headers: { accept: 'application/json' } }, hooks);
}

// Raw body -> { ok: true, jobs } or { ok: false, error: 'malformed', reason }.
// Lever answers a postings request with a bare JSON array.
export function parse(body) {
  let j;
  try { j = JSON.parse(body); } catch { return { ok: false, error: 'malformed', reason: 'body is not JSON' }; }
  if (!Array.isArray(j)) return { ok: false, error: 'malformed', reason: 'no postings array' };
  return {
    ok: true,
    jobs: j.map(p => ({ id: p?.id, title: p?.text, location: p?.categories?.location ?? null, url: p?.hostedUrl ?? null })),
  };
}
