#!/usr/bin/env node
// The JS2 loop (GATE.md): watch the boards in a config, within budgets, under the
// permission policy, and end in exactly one exit status.
//
//   node src/loop.mjs --config boards.json --label <label>
//     [--max-requests N] [--approve <path>]... [--replay out/raw/<file>] [--judge none]
//
// Exit codes: 0 finished, 10 incomplete, 11 budget-exhausted, 12 error.
//
// Everything the loop observes or decides goes into an append-only trace,
// out/traces/<run>.jsonl. Raw bodies go to out/raw/<run>/, pre- and post-run state
// snapshots to out/snapshots/<run>/, seen-id state to out/state/<board>.json, the
// consecutive-failure counter to out/failures.json, and the loop's own report to
// out/reports/<run>.json. src/check.mjs recomputes from raw bodies and snapshots; it
// never trusts the report.
//
// Seen-id state is read and written by JS1's src/state.mjs, unchanged. Its Lever UUID
// defect is the GATE.md finished-but-wrong demonstration and the review-packet target.
import { readFileSync, writeFileSync, appendFileSync, mkdirSync, renameSync, copyFileSync, chmodSync, existsSync } from 'node:fs';
import { join, dirname, resolve, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';
import { checkCliOptions, createNetSession, createFilePolicy, validToken, PolicyError } from './policy.mjs';
import { loadState, saveState, diffNew } from './state.mjs';
import * as greenhouse from './providers/greenhouse.mjs';
import * as lever from './providers/lever.mjs';

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PROVIDERS = { greenhouse, lever };
export const EXIT = { finished: 0, incomplete: 10, 'budget-exhausted': 11, error: 12 };
const PRECEDENCE = ['finished', 'incomplete', 'budget-exhausted', 'error'];
const BOARD_ID_RE = /^[a-z0-9-]{1,64}$/;

class RunError extends Error {}

function stampOf(ms) {
  return new Date(ms).toISOString().replace(/[-:]/g, '').replace(/\.(\d+)Z$/, '$1Z');
}

// Each attempt's outcome -> the board disposition GATE.md names.
function failureOf(o) {
  switch (o.kind) {
    case 'http': return o.status === 404 ? 'error: not found' : o.status === 429 ? 'rate-limited' : `error: http ${o.status}`;
    case 'redirect': return 'error: redirect refused';
    case 'timeout': return 'error: timeout';
    case 'transport': return 'error: transport';
    case 'denied': return `error: refused by policy (${o.reason})`;
    default: return `error: ${o.kind}`;
  }
}

export async function runLoop({
  argv = process.argv.slice(2),
  root = PROJECT_ROOT,
  cwd = process.cwd(),
  fetchImpl, // undefined -> createNetSession's default; this file never names fetch itself
  now = Date.now,
  sleep,
  setTimer,
  clearTimer,
  log = line => process.stdout.write(`${line}\n`),
} = {}) {
  const startMs = now();
  let args = {};
  let argError = null;
  try {
    args = parseArgs({
      args: argv,
      strict: true,
      allowPositionals: false,
      options: {
        config: { type: 'string' }, label: { type: 'string' }, 'max-requests': { type: 'string' },
        approve: { type: 'string', multiple: true }, replay: { type: 'string' }, judge: { type: 'string' },
      },
    }).values;
  } catch (e) {
    argError = e.message;
  }
  const labelOk = typeof args.label === 'string' && BOARD_ID_RE.test(args.label);

  let fp;
  try {
    fp = createFilePolicy({ root, approve: (args.approve ?? []).map(p => resolve(cwd, p)) });
  } catch (e) {
    log(`error: ${e.message}`);
    return { status: 'error', exitCode: EXIT.error, reason: e.message };
  }
  const rel = p => relative(fp.root, p).split('\\').join('/');
  const abs = p => join(fp.root, p);

  // Unique run id: the trace file name must not exist yet.
  const base = `${stampOf(startMs)}-${labelOk ? args.label : 'invalid-label'}`;
  let runId = base;
  for (let i = 2; existsSync(abs(`out/traces/${runId}.jsonl`)); i++) runId = `${base}-${i}`;
  const tracePath = `out/traces/${runId}.jsonl`;

  function ensureDir(p) {
    const d = fp.checkWrite(join(p, '.dir-probe'));
    if (d.decision !== 'allow') throw new RunError(`refused: mkdir ${p}: ${d.reason}`);
    mkdirSync(abs(p), { recursive: true });
  }
  function trace(event, data = {}) {
    const d = fp.checkWrite(tracePath);
    if (d.decision !== 'allow') throw new RunError(`refused: trace write: ${d.reason}`);
    appendFileSync(abs(tracePath), `${JSON.stringify({ at: new Date(now()).toISOString(), run: runId, event, ...data })}\n`);
  }
  function writeChecked(p, text) {
    const d = fp.checkWrite(p);
    if (d.decision !== 'allow') throw new RunError(`refused: write ${p}: ${d.reason}`);
    writeFileSync(abs(p), text);
  }
  function writeAtomic(p, text) {
    const tmp = `${p}.${runId}.tmp`;
    writeChecked(tmp, text);
    const d = fp.checkWrite(p);
    if (d.decision !== 'allow') throw new RunError(`refused: write ${p}: ${d.reason}`);
    renameSync(abs(tmp), abs(p));
  }
  function snapshot(statePath, boardId, which) {
    if (!existsSync(abs(statePath))) return null;
    const p = `out/snapshots/${runId}/${boardId}.${which}.json`;
    const d = fp.checkWrite(p);
    if (d.decision !== 'allow') throw new RunError(`refused: snapshot ${p}: ${d.reason}`);
    copyFileSync(abs(statePath), abs(p));
    chmodSync(abs(p), 0o444);
    return p;
  }

  const results = [];
  const unattempted = [];
  let status = 'finished';
  const raise = s => { if (PRECEDENCE.indexOf(s) > PRECEDENCE.indexOf(status)) status = s; };
  let reason = null;
  let session = null;
  const mode = args.replay !== undefined ? 'replay' : 'live';

  try {
    ensureDir('out/traces');
    trace('run_start', {
      mode, label: args.label ?? null, argv, node: process.version, root: fp.root,
      config: args.config ?? null, replay: args.replay ?? null, approve: args.approve ?? [],
    });

    // ---- everything below is checked before any network action ----
    if (argError) throw new RunError(`bad arguments: ${argError}`);
    if (!labelOk) throw new RunError('--label is required and must be kebab-case');
    const cli = checkCliOptions({ 'max-requests': args['max-requests'], judge: args.judge });
    if (cli.decision !== 'allow') throw new RunError(`refused: ${cli.reason}`);
    const limits = cli.limits;
    if (!args.config) throw new RunError('--config is required');

    const cfgPath = resolve(cwd, args.config);
    const cr = fp.checkRead(cfgPath);
    if (cr.decision !== 'allow') throw new RunError(`refused: read config: ${cr.reason}`);
    let config;
    try { config = JSON.parse(readFileSync(cr.path, 'utf8')); } catch (e) { throw new RunError(`config unreadable: ${e.message}`); }
    if (!Array.isArray(config) || config.length === 0) throw new RunError('config must be a nonempty array of boards');
    const boards = [];
    const seenKeys = new Map();
    for (const b of config) {
      if (!b || !BOARD_ID_RE.test(b.id ?? '') || !PROVIDERS[b.system] || !validToken(b.token)) {
        throw new RunError(`invalid board entry ${JSON.stringify(b)}`);
      }
      const key = `${b.system}:${b.token}`;
      if (seenKeys.has(key)) {
        trace('board_skipped', { board: b.id, disposition: 'skipped: duplicate', duplicate_of: seenKeys.get(key) });
        results.push({ board: b.id, system: b.system, disposition: 'skipped: duplicate', duplicate_of: seenKeys.get(key) });
        continue;
      }
      if (boards.some(x => x.id === b.id)) throw new RunError(`board id ${b.id} used for two different boards`);
      seenKeys.set(key, b.id);
      boards.push(b);
    }
    trace('config', { config: rel(cr.path), limits, boards: boards.map(b => ({ id: b.id, system: b.system, token: b.token })) });

    let replay = null;
    if (mode === 'replay') {
      if (boards.length !== 1) throw new RunError(`--replay needs a single-board config; this one has ${boards.length}`);
      const rp = fp.checkReplayPath(resolve(cwd, args.replay));
      if (rp.decision !== 'allow') throw new RunError(`refused: --replay ${args.replay}: ${rp.reason}`);
      replay = { path: rp.path, body: readFileSync(rp.path, 'utf8') };
    }

    const failuresPath = 'out/failures.json';
    let failures = {};
    if (existsSync(abs(failuresPath))) {
      try { failures = JSON.parse(readFileSync(abs(failuresPath), 'utf8')); } catch (e) { throw new RunError(`out/failures.json unreadable: ${e.message}`); }
    }

    const deadline = startMs + limits.wallSeconds * 1000;
    if (mode === 'live') {
      session = createNetSession({ maxRequests: limits.requests, deadline, now, fetchImpl, sleep, setTimer, clearTimer });
    }
    for (const p of ['out/state', `out/raw/${runId}`, `out/snapshots/${runId}`, 'out/reports']) ensureDir(p);

    let attemptedBoards = 0;
    let budgetHit = null; // once a budget is hit, no further board is attempted
    const hit = budget => { budgetHit ??= budget; raise('budget-exhausted'); };
    for (const b of boards) {
      if (budgetHit) { unattempted.push({ board: b.id, budget: budgetHit }); continue; }
      if (attemptedBoards >= limits.boards) { hit('boards'); unattempted.push({ board: b.id, budget: 'boards' }); continue; }
      if (deadline - now() <= 0) { hit('wall-clock'); unattempted.push({ board: b.id, budget: 'wall-clock' }); continue; }

      const provider = PROVIDERS[b.system];
      const statePath = `out/state/${b.id}.json`;
      trace('board_start', { board: b.id, system: b.system, token: b.token, remaining_ms: deadline - now(), requests_used: session?.requests ?? 0 });

      // Observe: one logical GET through the policy session, or the replayed body.
      let final;
      let rawPath = null;
      if (replay) {
        final = { kind: 'ok', body: replay.body };
        rawPath = rel(replay.path);
        trace('replay_read', { board: b.id, raw_path: rawPath, network_requests: 0 });
      } else {
        // Each attempt and the retry decision are written to the trace (and the raw body
        // to out/raw/) the moment they happen, not after the board is done.
        let k = 0;
        const onAttempt = a => {
          k += 1;
          if (a.request === undefined) {
            if (a.kind !== 'budget' || k > 1) trace('request_refused', { board: b.id, outcome: a.kind, reason: a.reason ?? a.budget });
            return;
          }
          let p = null;
          if (a.body !== undefined) { p = `out/raw/${runId}/${b.id}.attempt${k}.json`; writeChecked(p, a.body); rawPath = p; }
          trace('request', {
            at: a.at, completed_at: a.completedAt, board: b.id, request: a.request, method: 'GET', url: a.url, permission: 'allow',
            status: a.status ?? null, outcome: a.kind, error: a.error ?? null, location: a.location ?? null, timeout_ms: a.timeoutMs, raw_path: p,
          });
        };
        const onRetry = (d, first) => trace('retry', { board: b.id, after: first.kind, status: first.status ?? null, wait_ms: d.waitMs });
        const o = await provider.observe(session, b.token, { onAttempt, onRetry });
        if (o.attempts.length === 1 && o.attempts[0].kind === 'budget') {
          unattempted.push({ board: b.id, budget: o.attempts[0].budget });
          trace('board_not_attempted', { board: b.id, budget: o.attempts[0].budget });
          hit(o.attempts[0].budget);
          continue;
        }
        // The decision not to retry is recorded once the first attempt has failed, right here.
        if (!o.retry.retry && o.retry.reason !== 'not retryable' && o.attempts[0].kind !== 'ok') trace('no_retry', { board: b.id, reason: o.retry.reason });
        if (o.retry.budgetExhausted) hit(o.retry.budgetExhausted);
        final = o.kind === 'budget' ? o.attempts[0] : o; // a retry the budget refused: the board failed on its first attempt
        if (o.kind === 'budget') hit(o.budget);
      }
      attemptedBoards += 1;

      let state;
      try { state = loadState(abs(statePath)); } catch (e) { throw new RunError(`unreadable state ${statePath}: ${e.message}`); }
      const before = snapshot(statePath, b.id, 'before');

      let disposition;
      let jobs = null;
      let newIds = null;
      let updated = false;
      if (final.kind !== 'ok') {
        disposition = failureOf(final);
        if (final.kind === 'denied') { reason = disposition; raise('error'); }
      } else {
        const parsed = provider.parse(final.body);
        if (!parsed.ok) disposition = `error: malformed (${parsed.reason})`;
        else if (parsed.jobs.length === 0) disposition = state && state.ids.length > 0 ? 'suspect: empty' : 'empty (unverified)';
        else {
          jobs = parsed.jobs;
          const sBefore = state ?? { ids: [] };
          newIds = diffNew(jobs, sBefore).fresh.map(j => j.id);
          const nextIds = [...sBefore.ids, ...jobs.map(j => j.id)];
          if (deadline - now() <= 0) {
            disposition = 'not completed: wall-clock budget before state write';
            hit('wall-clock');
          } else {
            const tmp = `out/state/.${b.id}.json.${runId}.tmp`;
            const t = fp.checkWrite(tmp);
            if (t.decision !== 'allow') throw new RunError(`refused: write ${tmp}: ${t.reason}`);
            saveState(abs(tmp), { board: b.id, ids: nextIds, run: runId });
            const d = fp.checkWrite(statePath, { nextIds });
            if (d.decision === 'ask') throw new RunError(`refused: needs approval: ${statePath}: ${d.reason}`);
            if (d.decision !== 'allow') throw new RunError(`refused: write ${statePath}: ${d.reason}`);
            renameSync(abs(tmp), abs(statePath));
            updated = true;
            disposition = newIds.length ? 'observed' : 'unchanged (no new IDs)';
          }
        }
      }
      const after = snapshot(statePath, b.id, 'after');
      const failed = !(disposition === 'observed' || disposition === 'unchanged (no new IDs)');
      if (failed) raise('incomplete');

      const prev = failures[b.id] ?? { consecutive: 0 };
      failures[b.id] = failed
        ? { consecutive: prev.consecutive + 1, last_error: disposition, last_run: runId, escalate: prev.consecutive + 1 >= 2 }
        : { consecutive: 0, last_error: null, last_run: runId, escalate: false };

      const r = {
        board: b.id, system: b.system, token: b.token, disposition, raw_path: rawPath,
        raw_count: jobs ? jobs.length : null, new_count: newIds ? newIds.length : null, new_ids: newIds,
        state_path: statePath, state_before: before, state_after: after, state_updated: updated,
        escalate: failures[b.id].escalate,
      };
      results.push(r);
      trace('board_result', r);
    }

    writeAtomic(failuresPath, `${JSON.stringify(failures, null, 2)}\n`);
    trace('failures_written', { path: failuresPath });
  } catch (e) {
    if (!(e instanceof RunError) && !(e instanceof PolicyError)) throw e;
    reason = e.message;
    raise('error');
  }

  const exitCode = EXIT[status];
  const report = {
    run: runId, mode, status, exit_code: exitCode, reason, requests: session?.requests ?? 0,
    boards: results, unattempted, trace: tracePath,
  };
  try {
    ensureDir('out/reports');
    writeAtomic(`out/reports/${runId}.json`, `${JSON.stringify(report, null, 2)}\n`);
    trace('run_end', { status, exit_code: exitCode, reason, requests: report.requests, unattempted });
  } catch (e) {
    log(`error: could not record the run: ${e.message}`);
    return { ...report, status: 'error', exitCode: EXIT.error, reason: e.message };
  }

  for (const r of results) {
    const n = r.disposition === 'observed' || r.disposition === 'unchanged (no new IDs)' ? `, ${r.raw_count} jobs, ${r.new_count} new` : '';
    log(`${r.board}: ${r.disposition}${n}${r.escalate ? ' [escalate]' : ''}`);
  }
  for (const u of unattempted) log(`${u.board}: not attempted (${u.budget} budget)`);
  log(`${runId}: ${status} (exit ${exitCode})${mode === 'replay' ? ' [mode: replay]' : ''}${reason ? `: ${reason}` : ''} · ${report.requests} request(s) · ${tracePath}`);
  return { ...report, exitCode };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const r = await runLoop();
  process.exitCode = r.exitCode;
}
