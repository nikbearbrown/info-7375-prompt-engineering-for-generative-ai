#!/usr/bin/env node
// Mutation check for src/policy.mjs. Each mutant is one GATE.md "wrong implementation"
// built as a broken copy of policy.mjs in .mutants/<name>/ (gitignored). Three suites
// run against each copy: the policy tests, the loop tests and the wrong-version loop
// tests. A mutant is KILLED if at least one test in any suite fails, and SURVIVES if
// every test still passes. Kills are reported per suite; survivors are not hidden.
//
//   node tools/mutate-policy.mjs
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, '.mutants');

// [wrong version in GATE.md, mutant name, what it does, [[exact text, replacement], ...]]
const MUTANTS = [
  [1, 'wv01-host-includes', 'host matched with includes()',
    [['ROUTES.find(r => r.host === u.hostname)', 'ROUTES.find(r => u.hostname.includes(r.host))']]],
  [1, 'wv01-host-endsWith', 'host matched with endsWith()',
    [['ROUTES.find(r => r.host === u.hostname)', 'ROUTES.find(r => u.hostname.endsWith(r.host))']]],
  [2, 'wv02-prefix-startsWith', 'inside-check by raw string prefix',
    [['  const r = relative(base, target);\n', '  return target.startsWith(base);\n  const r = relative(base, target);\n']]],
  [3, 'wv03-no-realpath', 'paths resolved lexically, symlinks not resolved',
    [['return resolve(realpathSync(cur), ...tail);', 'return resolve(cur, ...tail);']]],
  [4, 'wv04-no-method-check', 'method not checked on an allow-listed host',
    [["  if (method !== 'GET') return deny(`method ${method} not allowed: GET only`);\n", '']]],
  [5, 'wv05-redirect-follow', "fetch left following redirects",
    [["redirect: 'manual'", "redirect: 'follow'"]]],
  [7, 'wv07-404-retried', '404 treated as transient and retried',
    [["(outcome.kind === 'http' && outcome.status >= 500)", "(outcome.kind === 'http' && (outcome.status >= 500 || outcome.status === 404))"]]],
  [7, 'wv07-no-retry-cap', 'retries until success or 5 attempts',
    [
      ["    if (n >= 1 + LIMITS.retriesPerBoard) return { kind: 'denied', reason: 'repeat: retry already used' };\n", ''],
      ['    await sleep(decision.waitMs);\n    const second = await attempt(req, { retry: true });\n    onAttempt(second);\n    return { ...second, attempts: [first, second], retry: decision };',
        '    const attempts = [first];\n    let last = first;\n    for (let d = decision; d.retry && attempts.length < 5; d = retryDecision(last, { nowMs: now(), deadline, requests, maxRequests })) {\n      await sleep(d.waitMs);\n      last = await attempt(req, { retry: true });\n      onAttempt(last);\n      attempts.push(last);\n    }\n    return { ...last, attempts, retry: decision };'],
    ]],
  [8, 'wv08-budget-after-request', 'request budget checked as if after sending (N + 1 sent)',
    [["    if (requests >= maxRequests) return { kind: 'budget', budget: 'requests' };", "    if (requests > maxRequests) return { kind: 'budget', budget: 'requests' };"]]],
  [13, 'wv13-no-raw-guard', 'no raw-string guard before new URL()',
    [["  if (/[^a-z0-9/-]/.test(rawPath)) return deny('raw path has encoded or forbidden characters');\n", '']]],
  [13, 'wv13-boardUrl-unvalidated', 'token interpolated into the URL without validation',
    [['  if (!validToken(token)) throw new PolicyError(`token ${JSON.stringify(token)} fails ${TOKEN_RE}`);\n  const r = ROUTES', '  const r = ROUTES']]],
  [14, 'wv14-blind-429', '429 retried after a fixed 2 s, Retry-After ignored',
    [["  } else if (outcome.kind === 'http' && outcome.status === 429) {\n", "  } else if (outcome.kind === 'http' && outcome.status === 429) {\n    waitMs = LIMITS.retryWaitMs;\n  } else if (false) {\n"]]],
  [15, 'wv15-cli-raise-accepted', 'a flag above the hard maximum is accepted',
    [['    if (Number(v) > LIMITS[key]) return { decision: \'deny\', reason: `--${flag} ${v} exceeds the hard maximum ${LIMITS[key]} (GATE.md)` };\n', '']]],
  [15, 'wv15-cli-raise-clamped', 'a flag above the hard maximum is silently clamped',
    [['    if (Number(v) > LIMITS[key]) return { decision: \'deny\', reason: `--${flag} ${v} exceeds the hard maximum ${LIMITS[key]} (GATE.md)` };\n', '    if (Number(v) > LIMITS[key]) { limits[key] = LIMITS[key]; continue; }\n']]],
  [18, 'wv18-approval-reusable', 'an approval is never consumed',
    [['      a.consumed = true;\n', '']]],
  [18, 'wv18-approval-any-path', 'an approval for one path authorizes another',
    [['    const a = approvals.get(real);', '    const a = [...approvals.values()].find(x => !x.consumed);']]],
  [19, 'wv19-full-timeout', 'every attempt gets the full 15 s timeout',
    [['Math.min(LIMITS.attemptTimeoutMs, remaining)', 'LIMITS.attemptTimeoutMs']]],
  [20, 'wv20-replay-anywhere', 'replay accepts any existing file, not only out/raw/',
    [["    if (!isInside(rawReal, real)) return { decision: 'deny', path: real, reason: 'replay file not under out/raw/' };\n", '']]],
  [20, 'wv20-replay-missing-ok', 'replay accepts a missing file',
    [["    if (!existsSync(real) || !statSync(real).isFile()) return { decision: 'deny', path: real, reason: 'replay file missing' };\n", '']]],
];

const SUITES = [['policy', 'test/policy.test.mjs'], ['loop', 'test/loop.test.mjs'], ['wrong-versions', 'test/wrong-versions.test.mjs']];

// Each copy's test files are spec/<suite>.mutant.mjs, names `node --test` with no
// arguments does not discover, so the project's own test run never picks up mutants.
function runTests(dir) {
  const out = { failed: [], total: 0, status: 0, bySuite: {} };
  for (const [suite] of SUITES) {
    const r = spawnSync(process.execPath, ['--test', `spec/${suite}.mutant.mjs`], { cwd: dir, encoding: 'utf8' });
    const failed = [...r.stdout.matchAll(/^not ok \d+ - (.+)$/gm)].map(m => `[${suite}] ${m[1]}`);
    const total = Number(/^# tests (\d+)/m.exec(r.stdout)?.[1] ?? 0);
    out.bySuite[suite] = { failed: failed.length, total };
    out.failed.push(...failed);
    out.total += total;
    out.status ||= r.status;
  }
  return out;
}
const suiteSummary = r => SUITES.map(([s]) => `${s} ${r.bySuite[s].failed}/${r.bySuite[s].total}`).join(', ');

function copy(name) {
  const dir = join(OUT, name);
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(join(dir, 'test'), { recursive: true });
  mkdirSync(join(dir, 'spec'), { recursive: true });
  cpSync(join(ROOT, 'src'), join(dir, 'src'), { recursive: true });
  cpSync(join(ROOT, 'GATE.md'), join(dir, 'GATE.md'));
  cpSync(join(ROOT, 'test/boundary-cases.md'), join(dir, 'test/boundary-cases.md'));
  for (const [suite, file] of SUITES) cpSync(join(ROOT, file), join(dir, `spec/${suite}.mutant.mjs`));
  return dir;
}

const original = readFileSync(join(ROOT, 'src/policy.mjs'), 'utf8');

// Control: the unmutated copy must pass, or the check means nothing.
const control = runTests(copy('control'));
console.log(`control (unmutated policy.mjs): ${control.failed.length} failed of ${control.total} (${suiteSummary(control)} failed)`);
if (control.failed.length || control.status !== 0) process.exit(2);

let survivors = 0;
for (const [wv, name, what, edits] of MUTANTS) {
  let src = original;
  for (const [from, to] of edits) {
    const hits = src.split(from).length - 1;
    if (hits !== 1) { console.error(`${name}: pattern found ${hits} times, expected 1:\n${from}`); process.exit(3); }
    src = src.replace(from, () => to);
  }
  const dir = copy(name);
  writeFileSync(join(dir, 'src/policy.mjs'), src);
  const r = runTests(dir);
  const verdict = r.failed.length ? 'KILLED' : 'SURVIVED';
  if (!r.failed.length) survivors += 1;
  console.log(`\nWV${String(wv).padStart(2, '0')} ${name} (${what}): ${verdict}, ${r.failed.length} of ${r.total} tests failed (${suiteSummary(r)} failed)`);
  for (const f of r.failed) console.log(`    not ok - ${f}`);
}
console.log(`\n${MUTANTS.length} mutants, ${MUTANTS.length - survivors} killed, ${survivors} survived`);
