// The permission policy (GATE.md, "Permission policy", "Budgets and limits", "Repeat rule",
// "Error and escalation policy" retry rows). Every network request and every file
// read, write, delete or replay the agent makes is decided here, in code.
//
//   checkRequest(req)          one HTTP request: allow | deny
//   createNetSession(opts)     the only fetch path: policy, request budget, wall clock,
//                              per-attempt timeout, repeat rule, one counted retry
//   retryDecision(outcome, …)  whether a failed attempt may be retried
//   createFilePolicy(opts)     checkRead / checkWrite / checkDelete / checkReplayPath
//   checkCliOptions(opts)      flags may lower a budget, never raise one; --judge none only
import { realpathSync, lstatSync, readlinkSync, readFileSync, existsSync, statSync } from 'node:fs';
import { resolve, relative, isAbsolute, sep, dirname, basename, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// GATE.md "Budgets and limits" and the 429 row of the error policy. A test checks these
// against the table in GATE.md; changing one needs a dated Decision there first.
export const LIMITS = Object.freeze({
  boards: 5,
  requests: 8,
  wallSeconds: 60,
  attemptTimeoutMs: 15_000,
  retriesPerBoard: 1,
  retryWaitMs: 2_000,
  retryAfterMaxSeconds: 5,
});

export const TOKEN_RE = /^[a-z0-9-]{1,64}$/;
const TOKEN = Symbol('token');
const ROUTES = [
  { system: 'greenhouse', host: 'boards-api.greenhouse.io', segments: ['v1', 'boards', TOKEN, 'jobs'], query: 'content=true' },
  { system: 'lever', host: 'api.lever.co', segments: ['v0', 'postings', TOKEN], query: 'mode=json' },
];
// Header allow-list. Anything else (Authorization, Cookie, Proxy-Authorization, API-key
// headers) is refused, so no credential-bearing header can be sent.
const ALLOWED_HEADERS = new Set(['accept', 'user-agent']);

export class PolicyError extends Error {}

const deny = reason => ({ decision: 'deny', reason });

export function validToken(t) {
  return typeof t === 'string' && TOKEN_RE.test(t);
}

// Validate the token before building the URL (wrong version 13).
export function boardUrl(system, token) {
  if (!validToken(token)) throw new PolicyError(`token ${JSON.stringify(token)} fails ${TOKEN_RE}`);
  const r = ROUTES.find(x => x.system === system);
  if (!r) throw new PolicyError(`unknown system ${JSON.stringify(system)}`);
  return `https://${r.host}/${r.segments.map(s => (s === TOKEN ? token : s)).join('/')}?${r.query}`;
}

// One HTTP request. The raw string is checked before new URL() can normalize it
// (new URL turns /v1/boards/%2e%2e/jobs into /v1/jobs).
export function checkRequest({ method, url, headers = {} } = {}) {
  if (method !== 'GET') return deny(`method ${method} not allowed: GET only`);
  if (typeof url !== 'string') return deny('url is not a string');
  const m = /^https:\/\/([^/?#]*)([^?#]*)(?:\?([^#]*))?(#.*)?$/i.exec(url);
  if (!m) return deny('scheme not https');
  const [, authority, rawPath, rawQuery, fragment] = m;
  if (fragment !== undefined) return deny('fragment not allowed');
  if (authority.includes('@')) return deny('credentials in URL');
  if (/[^a-z0-9/-]/.test(rawPath)) return deny('raw path has encoded or forbidden characters');

  let u;
  try { u = new URL(url); } catch { return deny('unparseable URL'); }
  if (u.protocol !== 'https:') return deny('scheme not https');
  if (u.username || u.password) return deny('credentials in URL');
  if (u.port !== '') return deny(`non-default port ${u.port}`);
  if (u.hostname.endsWith('.')) return deny('trailing-dot hostname');
  const route = ROUTES.find(r => r.host === u.hostname); // u.hostname is DNS-lowercased
  if (!route) return deny(`host ${u.hostname} not on the allow-list`);

  const segs = rawPath.split('/');
  if (segs[0] !== '' || segs.length !== route.segments.length + 1) return deny('path not on the allow-list');
  let token;
  for (let i = 0; i < route.segments.length; i++) {
    const want = route.segments[i];
    const got = segs[i + 1];
    if (want === TOKEN) {
      if (!validToken(got)) return deny(`token ${JSON.stringify(got)} fails ${TOKEN_RE}`);
      token = got;
    } else if (got !== want) return deny('path not on the allow-list');
  }
  if (rawQuery !== undefined && rawQuery !== route.query) return deny(`query ${JSON.stringify(rawQuery)} not allowed`);

  for (const name of Object.keys(headers)) {
    if (!ALLOWED_HEADERS.has(name.toLowerCase())) return deny(`header ${name} not allowed`);
  }
  const canonical = `https://${route.host}${rawPath}${rawQuery !== undefined ? `?${rawQuery}` : ''}`;
  return { decision: 'allow', canonical, system: route.system, token };
}

// Retry-After: delta seconds or an HTTP date. Returns whole seconds, or null when the
// header is missing, invalid, or a date already in the past (not a nonnegative wait).
export function parseRetryAfter(value, nowMs) {
  if (value == null) return null;
  const v = String(value).trim();
  if (/^\d+$/.test(v)) return Number(v);
  const at = Date.parse(v);
  if (Number.isNaN(at)) return null;
  const s = Math.ceil((at - nowMs) / 1000);
  return s >= 0 ? s : null;
}

// GATE.md error policy: transport failure, timeout, 5xx -> one retry after 2 s;
// 429 -> one retry only if Retry-After parses to <= 5 s; 404, other 4xx, 3xx,
// denied -> never. Either way the wait and the next request must fit the budgets.
export function retryDecision(outcome, { nowMs, deadline, requests, maxRequests, retriesUsed = 0 }) {
  if (retriesUsed >= LIMITS.retriesPerBoard) return { retry: false, reason: 'retry limit reached' };
  let waitMs;
  if (outcome.kind === 'transport' || outcome.kind === 'timeout' || (outcome.kind === 'http' && outcome.status >= 500)) {
    waitMs = LIMITS.retryWaitMs;
  } else if (outcome.kind === 'http' && outcome.status === 429) {
    const s = parseRetryAfter(outcome.retryAfter, nowMs);
    if (s === null || s > LIMITS.retryAfterMaxSeconds) return { retry: false, reason: 'rate-limited' };
    waitMs = s * 1000;
  } else {
    return { retry: false, reason: 'not retryable' };
  }
  if (requests >= maxRequests) return { retry: false, reason: 'budget: requests', budgetExhausted: 'requests' };
  if (deadline - nowMs - waitMs <= 0) return { retry: false, reason: 'budget: wall-clock', budgetExhausted: 'wall-clock' };
  return { retry: true, waitMs };
}

const realSleep = ms => new Promise(r => setTimeout(r, ms));

// The only path to the network. Each attempt is checked before it is sent: policy,
// repeat rule, request budget, wall clock. Timeout = min(15 s, wall clock remaining),
// and it aborts the in-flight fetch. Redirects are never followed.
export function createNetSession({
  maxRequests = LIMITS.requests,
  deadline,
  now = Date.now,
  fetchImpl = globalThis.fetch,
  sleep = realSleep,
  setTimer = setTimeout,
  clearTimer = clearTimeout,
} = {}) {
  if (!Number.isInteger(maxRequests) || maxRequests < 1 || maxRequests > LIMITS.requests) {
    throw new PolicyError(`maxRequests ${maxRequests} outside 1..${LIMITS.requests}`);
  }
  if (!Number.isFinite(deadline)) throw new PolicyError('deadline (epoch ms) is required');
  const sent = new Map(); // "GET <canonical url>" -> attempts sent this run
  let requests = 0;

  async function attempt(req, { retry = false } = {}) {
    const p = checkRequest(req);
    if (p.decision !== 'allow') return { kind: 'denied', reason: p.reason };
    const key = `GET ${p.canonical}`;
    const n = sent.get(key) ?? 0;
    if (n >= 1 && !retry) return { kind: 'denied', reason: 'repeat: same request already sent this run' };
    if (n >= 1 + LIMITS.retriesPerBoard) return { kind: 'denied', reason: 'repeat: retry already used' };
    if (requests >= maxRequests) return { kind: 'budget', budget: 'requests' };
    const remaining = deadline - now();
    if (remaining <= 0) return { kind: 'budget', budget: 'wall-clock' };

    const timeoutMs = Math.min(LIMITS.attemptTimeoutMs, remaining);
    requests += 1;
    sent.set(key, n + 1);
    const base = { url: p.canonical, request: requests, timeoutMs, at: new Date(now()).toISOString() };
    const controller = new AbortController();
    let timedOut = false;
    const timer = setTimer(() => { timedOut = true; controller.abort(); }, timeoutMs);
    try {
      const res = await fetchImpl(p.canonical, { method: 'GET', redirect: 'manual', headers: req.headers ?? {}, signal: controller.signal });
      const body = await res.text();
      if (res.status >= 300 && res.status < 400) return { ...base, kind: 'redirect', status: res.status, location: res.headers.get('location'), body };
      if (res.status >= 200 && res.status < 300) return { ...base, kind: 'ok', status: res.status, body };
      return { ...base, kind: 'http', status: res.status, retryAfter: res.headers.get('retry-after'), body };
    } catch (e) {
      return timedOut ? { ...base, kind: 'timeout' } : { ...base, kind: 'transport', error: String(e?.message ?? e) };
    } finally {
      clearTimer(timer);
    }
  }

  // One logical GET: first attempt, plus at most the one retry the error policy allows.
  async function get(req) {
    const first = await attempt(req);
    const decision = retryDecision(first, { nowMs: now(), deadline, requests, maxRequests });
    if (!decision.retry) return { ...first, attempts: [first], retry: decision };
    await sleep(decision.waitMs);
    const second = await attempt(req, { retry: true });
    return { ...second, attempts: [first, second], retry: decision };
  }

  return {
    get,
    get requests() { return requests; },
    remainingMs: () => deadline - now(),
  };
}

// ---- Files ----------------------------------------------------------------

// Real path of `abs`: realpath of the nearest existing ancestor, plus the rest.
// A dangling symlink is followed through its target, so it cannot point a new
// file outside the tree.
function canonicalPath(abs, depth = 0) {
  if (depth > 40) throw new PolicyError(`too many symlinks resolving ${abs}`);
  const tail = [];
  let cur = abs;
  for (;;) {
    try {
      return resolve(realpathSync(cur), ...tail);
    } catch (e) {
      if (e.code !== 'ENOENT' && e.code !== 'ENOTDIR') throw e;
      let link = null;
      try { if (lstatSync(cur).isSymbolicLink()) link = readlinkSync(cur); } catch { /* does not exist */ }
      if (link !== null) return resolve(canonicalPath(resolve(dirname(cur), link), depth + 1), ...tail);
      const parent = dirname(cur);
      if (parent === cur) throw e;
      tail.unshift(basename(cur));
      cur = parent;
    }
  }
}

// Segment comparison, not a string prefix: out-evil/x is not inside out/.
function isInside(base, target) {
  const r = relative(base, target);
  return r !== '' && r !== '..' && !r.startsWith(`..${sep}`) && !isAbsolute(r);
}

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// root: the project folder (default: this file's parent's parent). Relative paths are
// resolved against root, never the shell's cwd, and "~" is never expanded.
// approve: the --approve paths for this run; each authorizes one guarded mutation of
// that one canonical path, and is consumed when used.
export function createFilePolicy({ root = PROJECT_ROOT, approve = [] } = {}) {
  const rootReal = realpathSync(root);
  const outReal = canonicalPath(join(rootReal, 'out'));
  const rawReal = canonicalPath(join(rootReal, 'out', 'raw'));
  const stateReal = canonicalPath(join(rootReal, 'out', 'state'));
  const where = p => canonicalPath(resolve(rootReal, p));
  const approvals = new Map(approve.map(p => [where(p), { consumed: false }]));

  function guarded(real, reason) {
    const a = approvals.get(real);
    if (a && !a.consumed) {
      a.consumed = true;
      return { decision: 'allow', path: real, approved: true, reason: `approved once: ${reason}` };
    }
    return { decision: 'ask', path: real, reason: `needs approval: ${reason}${a ? ' (approval already used)' : ''}` };
  }

  function checkRead(p) {
    const real = where(p);
    if (!isInside(rootReal, real)) return { decision: 'deny', path: real, reason: 'read outside the project' };
    return { decision: 'allow', path: real };
  }

  // Create or overwrite. Whether the file exists is read from disk here, so a caller
  // cannot call an overwrite a "create". nextIds is required when overwriting a state file.
  function checkWrite(p, { nextIds } = {}) {
    const real = where(p);
    if (!isInside(outReal, real)) return { decision: 'deny', path: real, reason: 'write outside out/' };
    if (!existsSync(real) || !isInside(stateReal, real)) return { decision: 'allow', path: real };
    if (!Array.isArray(nextIds)) return { decision: 'deny', path: real, reason: 'state overwrite without its new id set' };
    let before;
    try {
      before = JSON.parse(readFileSync(real, 'utf8')).ids;
      if (!Array.isArray(before)) throw new Error('no ids list');
    } catch (e) {
      return { decision: 'deny', path: real, reason: `existing state unreadable: ${e.message}` };
    }
    const next = new Set(nextIds.map(String));
    const lost = before.filter(id => !next.has(String(id)));
    if (lost.length) return guarded(real, `overwrite would remove ${lost.length} seen id(s)`);
    return { decision: 'allow', path: real };
  }

  function checkDelete(p) {
    const real = where(p);
    if (!isInside(outReal, real)) return { decision: 'deny', path: real, reason: 'delete outside out/' };
    return guarded(real, 'delete under out/');
  }

  // --replay: the file must really be under out/raw/ and must exist. No fallback.
  function checkReplayPath(p) {
    const real = where(p);
    if (!isInside(rawReal, real)) return { decision: 'deny', path: real, reason: 'replay file not under out/raw/' };
    if (!existsSync(real) || !statSync(real).isFile()) return { decision: 'deny', path: real, reason: 'replay file missing' };
    return { decision: 'allow', path: real };
  }

  return { root: rootReal, out: outReal, checkRead, checkWrite, checkDelete, checkReplayPath };
}

// ---- CLI -------------------------------------------------------------------

// Budget flags may lower a limit, never raise it (raising is rejected, not clamped).
// --judge none is the only judge mode. Returns the effective limits for the run.
export function checkCliOptions(opts = {}) {
  const limits = { boards: LIMITS.boards, requests: LIMITS.requests, wallSeconds: LIMITS.wallSeconds };
  const flags = { 'max-boards': 'boards', 'max-requests': 'requests', 'max-seconds': 'wallSeconds' };
  for (const [flag, key] of Object.entries(flags)) {
    if (opts[flag] === undefined) continue;
    const v = String(opts[flag]);
    if (!/^\d+$/.test(v) || Number(v) < 1) return { decision: 'deny', reason: `--${flag} ${v} is not a positive integer` };
    if (Number(v) > LIMITS[key]) return { decision: 'deny', reason: `--${flag} ${v} exceeds the hard maximum ${LIMITS[key]} (GATE.md)` };
    limits[key] = Number(v);
  }
  if (opts.judge !== undefined && opts.judge !== 'none') return { decision: 'deny', reason: `--judge ${opts.judge} not allowed: --judge none only` };
  return { decision: 'allow', limits };
}
