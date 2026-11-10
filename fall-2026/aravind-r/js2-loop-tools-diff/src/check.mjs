#!/usr/bin/env node
// The independent check (GATE.md, "Independent check"). Separate from the loop: it
// imports nothing from src/loop.mjs, src/state.mjs or src/providers/. It reads only
// files under out/: saved raw ATS bodies, the pre-/post-run state snapshots, and the
// trace, which it uses to locate those files and to read the claim under test. It never
// reads the loop's report (out/reports/) and never uses the trace's counts as truth.
//
//   node src/check.mjs --trace out/traces/<run>.jsonl [--trace ...]
//
// Rules, per board in each trace:
//   1 raw validity    every raw job has a valid ATS-native id; unique count recomputed;
//                     an empty response cannot back a success
//   2 delta           expectedNew = rawUniqueIds \ preRunSeenIds, against the claim
//   3 state integrity persisted ids are valid non-null strings; post = pre ∪ raw for a
//                     success, post = pre for a failure; first observation count check
// A trace with no board observations never passes: it prints NO OBSERVATIONS (run
// status: <status>) and exits 1. Exit 0 if every rule passes for every trace, 1 if any
// rule fails or a run observed nothing, 2 for a usage or evidence error.
import { readFileSync, realpathSync } from 'node:fs';
import { join, dirname, resolve, relative, isAbsolute, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DECIMAL = /^(0|[1-9]\d*)$/;
const SUCCESS = new Set(['observed', 'unchanged (no new IDs)']);

class EvidenceError extends Error {}

// The checker's own id canonicalization (GATE.md rule 1): Greenhouse numeric (safe
// integer) or decimal-string ids -> decimal string; Lever ids must be UUID strings.
export function canonicalRawId(system, id) {
  if (system === 'greenhouse') {
    if (Number.isSafeInteger(id) && id >= 0) return String(id);
    if (typeof id === 'string' && DECIMAL.test(id)) return id;
    return null;
  }
  if (system === 'lever') return typeof id === 'string' && UUID.test(id) ? id : null;
  return null;
}

// A persisted id must already be a canonical string (rule 3); a number does not qualify.
export function validPersistedId(system, id) {
  return typeof id === 'string' && canonicalRawId(system, id) === id;
}

function rawJobs(system, body) {
  let j;
  try { j = JSON.parse(body); } catch { return { error: 'raw body is not JSON' }; }
  if (system === 'greenhouse') return j && Array.isArray(j.jobs) ? { jobs: j.jobs } : { error: 'no jobs array' };
  if (system === 'lever') return Array.isArray(j) ? { jobs: j } : { error: 'no postings array' };
  return { error: `unknown system ${system}` };
}

export function checkTrace(tracePath, { root = PROJECT_ROOT } = {}) {
  const rootReal = realpathSync(root);
  const outReal = realpathSync(join(rootReal, 'out'));
  const underOut = p => {
    const real = realpathSync(resolve(rootReal, p));
    const r = relative(outReal, real);
    if (r === '' || r === '..' || r.startsWith(`..${sep}`) || isAbsolute(r)) throw new EvidenceError(`${p} is not under out/`);
    if (relative(join(outReal, 'reports'), real).split(sep)[0] !== '..') throw new EvidenceError(`${p} is a loop report; the checker does not read reports`);
    return real;
  };
  const read = p => readFileSync(underOut(p), 'utf8');
  const stateIds = p => {
    if (p === null || p === undefined) return { absent: true, ids: [] };
    const s = JSON.parse(read(p));
    if (!Array.isArray(s.ids)) throw new EvidenceError(`${p} has no ids list`);
    return { absent: false, ids: s.ids };
  };

  const events = read(tracePath).trim().split('\n').map(l => JSON.parse(l));
  const start = events.find(e => e.event === 'run_start');
  const out = { trace: tracePath, run: start?.run ?? null, mode: start?.mode ?? null, boards: [] };

  for (const b of events.filter(e => e.event === 'board_result')) {
    const rules = [];
    const success = SUCCESS.has(b.disposition);
    const pre = stateIds(b.state_before);
    const post = stateIds(b.state_after);

    // Rule 1: raw validity, from the raw bytes.
    let rawUnique = null;
    if (!b.raw_path) {
      rules.push({ rule: 1, pass: !success, detail: success ? 'success claimed with no raw body' : 'no raw body (failed board)' });
    } else {
      const parsed = rawJobs(b.system, read(b.raw_path));
      if (parsed.error) {
        rules.push({ rule: 1, pass: !success, detail: `${parsed.error}${success ? ', yet success claimed' : ''}` });
      } else {
        const canon = parsed.jobs.map(j => canonicalRawId(b.system, j?.id));
        const invalid = canon.filter(c => c === null).length;
        const unique = new Set(canon.filter(c => c !== null));
        const dupes = canon.length - invalid - unique.size;
        const problems = [];
        if (invalid) problems.push(`${invalid} invalid id(s)`);
        if (dupes) problems.push(`${dupes} duplicate id(s)`);
        if (parsed.jobs.length === 0 && success) problems.push('empty response cannot prove "no new jobs"');
        if (!problems.length) rawUnique = unique;
        rules.push({ rule: 1, pass: !success || problems.length === 0, detail: `${parsed.jobs.length} raw job(s), ${unique.size} unique valid id(s)${problems.length ? `; ${problems.join('; ')}` : ''}` });
      }
    }

    // Rule 2: delta, recomputed against the pre-run seen set as persisted (String() only,
    // no validation; a corrupt pre-run set is rule 3's job).
    const claim = b.new_ids === null || b.new_ids === undefined ? null : b.new_ids.map(String);
    if (!success) {
      rules.push({ rule: 2, pass: claim === null, detail: claim === null ? 'failed board, no new-id claim' : `failed board, yet ${claim.length} new id(s) claimed` });
    } else if (!rawUnique) {
      rules.push({ rule: 2, pass: false, detail: 'cannot recompute: raw response invalid' });
    } else {
      const seen = new Set(pre.ids.map(String));
      const expected = [...rawUnique].filter(id => !seen.has(id));
      const claimed = new Set(claim ?? []);
      const missing = expected.filter(id => !claimed.has(id));
      const extra = [...claimed].filter(id => !expected.includes(id));
      const pass = claim !== null && missing.length === 0 && extra.length === 0 && claim.length === expected.length;
      rules.push({ rule: 2, pass, detail: `expected ${expected.length} new, claimed ${claim?.length ?? 'none'}${missing.length ? `; ${missing.length} expected id(s) not claimed` : ''}${extra.length ? `; ${extra.length} claimed id(s) not expected` : ''}` });
    }

    // Rule 3: state integrity.
    const problems = [];
    const badPre = pre.ids.filter(id => !validPersistedId(b.system, id));
    const badPost = post.ids.filter(id => !validPersistedId(b.system, id));
    if (badPre.length) problems.push(`pre-run state has ${badPre.length} invalid id(s), e.g. ${JSON.stringify(badPre[0])}`);
    if (badPost.length) problems.push(`post-run state has ${badPost.length} invalid id(s), e.g. ${JSON.stringify(badPost[0])}`);
    const preSet = new Set(pre.ids.map(String));
    const postSet = new Set(post.ids.map(String));
    if (post.ids.length !== postSet.size) problems.push(`post-run state has ${post.ids.length - postSet.size} duplicate id(s)`);
    const lost = [...preSet].filter(id => !postSet.has(id));
    if (lost.length) problems.push(`post-run state dropped ${lost.length} pre-run id(s)`);
    if (success && rawUnique) {
      const want = new Set([...preSet, ...rawUnique]);
      const absentFromPost = [...want].filter(id => !postSet.has(id));
      const extraInPost = [...postSet].filter(id => !want.has(id));
      if (absentFromPost.length) problems.push(`post ≠ pre ∪ raw: ${absentFromPost.length} id(s) missing from post-run state`);
      if (extraInPost.length) problems.push(`post ≠ pre ∪ raw: ${extraInPost.length} id(s) in post-run state not in pre ∪ raw`);
      if (pre.absent || pre.ids.length === 0) {
        const validPost = post.ids.filter(id => validPersistedId(b.system, id)).length;
        if (validPost !== rawUnique.size) problems.push(`first observation: ${validPost} valid persisted id(s), raw has ${rawUnique.size}`);
      }
    } else if (!success) {
      const same = pre.absent === post.absent && preSet.size === postSet.size && [...preSet].every(id => postSet.has(id));
      if (!same) problems.push('failed board, yet state changed');
    }
    rules.push({ rule: 3, pass: problems.length === 0, detail: problems.length ? problems.join('; ') : `${post.ids.length} persisted id(s), all valid` });

    out.boards.push({ board: b.board, system: b.system, disposition: b.disposition, rules, pass: rules.every(r => r.pass) });
  }
  // A run that observed no board proves nothing: it never passes.
  out.runStatus = events.find(e => e.event === 'run_end')?.status ?? null;
  out.observations = out.boards.length;
  out.pass = out.observations > 0 && out.boards.every(b => b.pass);
  return out;
}

export function formatResult(r, tracePath) {
  const lines = [`# ${r.run} (mode: ${r.mode}) — ${tracePath}`];
  for (const b of r.boards) {
    for (const x of b.rules) lines.push(`${b.board} rule ${x.rule}: ${x.pass ? 'PASS' : 'FAIL'} — ${x.detail}`);
  }
  if (r.observations === 0) lines.push(`${r.run}: NO OBSERVATIONS (run status: ${r.runStatus ?? 'unknown'})`);
  else lines.push(`${r.run}: ${r.pass ? 'PASS' : 'FAIL'}`);
  return lines;
}

// 0 only if every trace passed; a FAIL or a run with no observations gives 1.
export function exitCodeFor(results) {
  return results.length > 0 && results.every(r => r.pass) ? 0 : 1;
}

function main() {
  let traces;
  try {
    traces = parseArgs({ strict: true, options: { trace: { type: 'string', multiple: true } } }).values.trace;
  } catch (e) {
    console.error(`usage: node src/check.mjs --trace out/traces/<run>.jsonl [--trace ...]\n${e.message}`);
    return 2;
  }
  if (!traces?.length) { console.error('usage: node src/check.mjs --trace out/traces/<run>.jsonl [--trace ...]'); return 2; }
  const results = [];
  for (const t of traces) {
    let r;
    try { r = checkTrace(resolve(process.cwd(), t)); } catch (e) {
      console.error(`${t}: evidence error: ${e.message}`);
      return 2;
    }
    for (const line of formatResult(r, t)) console.log(line);
    results.push(r);
  }
  return exitCodeFor(results);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  process.exitCode = main();
}
