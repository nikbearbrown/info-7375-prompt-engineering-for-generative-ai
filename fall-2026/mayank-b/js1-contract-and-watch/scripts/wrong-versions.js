// Proves the tests can fail: plants each wrong version from CONTRACT.md into a temporary copy of the code,
// runs the test suite there, and reports which tests caught it. The real code is never modified.
// Usage: node scripts/wrong-versions.js
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { ROOT } from "../src/config.js";

const WRONG = {
  "W1 substring matching": {
    file: "src/rule.js",
    find: /export function matchesTerm\(text, term\) \{[\s\S]*?\n\}/,
    replace: `export function matchesTerm(text, term) {\n  return collapse(text).toLowerCase().includes(collapse(term).toLowerCase());\n}`,
    mustFail: ["W1: 'Intern' must not exclude 'AI Engineer, Internal Tools'", "W1: 'Lead' must not exclude 'ML Engineer, Leadership Programs'"],
  },
  "W2 verdicts paired by position": {
    file: "src/watch.js",
    find: /  const postings = \[\];\n  for \(const job of fresh\) \{[\s\S]*?\n  \}\n/,
    replace: `  const settled = await Promise.allSettled(fresh.map((job) => judgeClaude(job, persona)));
  const judged = settled.filter((s) => s.status === "fulfilled").map((s) => s.value);
  const postings = fresh.map((job, i) => ({ posting_id: job.id, title: job.title, url: job.absolute_url ?? null, rule: judgeByRule(job, persona),
    claude: { posting_id: job.id, ...(judged[i] ?? { kind: "judgment", verdict: "no_verdict", reason: "missing" }) } }));
`,
    mustFail: ["W2: when the middle Claude call fails, every verdict stays with its own posting"],
  },
  "W5 baseline reports everything as new": {
    file: "src/watch.js",
    find: "const fresh = baseline ? [] : unique.filter((job) => !seen.has(job.id));",
    replace: "const fresh = unique.filter((job) => !seen.has(job.id));",
    mustFail: ["W5: run 1 with no state file reports 0 new and saves every fetched id"],
  },
};

function failingTests(dir) {
  try {
    execFileSync(process.execPath, ["--test", "--test-reporter=tap", "tests/*.test.js"], { cwd: dir, encoding: "utf8", stdio: "pipe" });
    return [];
  } catch (e) {
    return [...e.stdout.matchAll(/^not ok \d+ - (.+)$/gm)].map((m) => m[1].trim());
  }
}

let allCaught = true;
for (const [name, w] of Object.entries(WRONG)) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "js1-wrong-"));
  for (const sub of ["src", "tests", "persona", "prompts", "node_modules", "package.json"])
    fs.cpSync(path.join(ROOT, sub), path.join(dir, sub), { recursive: true });
  const file = path.join(dir, w.file);
  const before = fs.readFileSync(file, "utf8");
  const after = before.replace(w.find, w.replace);
  if (after === before) throw new Error(`${name}: could not plant the wrong version (pattern not found in ${w.file})`);
  fs.writeFileSync(file, after);

  const failed = failingTests(dir);
  const caught = w.mustFail.every((t) => failed.includes(t));
  allCaught &&= caught;
  console.log(`${caught ? "CAUGHT " : "MISSED "} ${name}`);
  for (const t of failed) console.log(`    failed: ${t}`);
  fs.rmSync(dir, { recursive: true, force: true });
}
console.log(allCaught ? "\nEvery wrong version was caught by its named test." : "\nAt least one wrong version was NOT caught.");
process.exitCode = allCaught ? 0 : 1;
