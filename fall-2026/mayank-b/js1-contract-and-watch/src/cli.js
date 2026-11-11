#!/usr/bin/env node
// Usage:
//   node src/cli.js check-persona
//   node --env-file-if-exists=.env src/cli.js watch [--seeded-from runs/<run>/raw-response.json]
//   node src/cli.js rule <posting_id> --raw runs/<run>/raw-response.json   (recompute one rule verdict by hand-check)
import fs from "node:fs";
import path from "node:path";
import { allowedFetch } from "./allowlist.js";
import { makeClaudeJudge, makeLiveAsk, loadPromptTemplate } from "./claude.js";
import { MODEL, PERSONA_PATH, PROMPT_PATH, ROOT } from "./config.js";
import { loadPersona } from "./persona.js";
import { judgeByRule } from "./rule.js";
import { fetchBoardText, runWatch } from "./watch.js";

function flag(args, name) {
  const i = args.indexOf(name);
  return i === -1 ? null : args[i + 1];
}

function printReport(report, runDir) {
  const kind = report.seeded ? "SEEDED run (against a saved response, not a live fetch)" : "live run";
  console.log(`Run ${report.run} (${kind}) at ${report.started_at}`);
  console.log(`  board: ${report.url}`);
  console.log(`  fetched ${report.postings_fetched} postings, removed ${report.duplicate_ids_removed} duplicate ids`);
  console.log(`  raw response: ${report.raw_response} (sha256 ${report.raw_sha256.slice(0, 12)}...)`);
  if (report.baseline) console.log(`  BASELINE: no earlier state, so 0 reported as new; ${report.postings_fetched} ids saved to ${report.state_file}`);
  else console.log(`  new since last run: ${report.new_count}`);
  for (const p of report.postings) {
    console.log(`\n  [${p.posting_id}] ${p.title}`);
    console.log(`    rule (record):   ${p.rule.verdict}: ${p.rule.justification}`);
    const c = p.claude;
    const when = c.judged_at ? `, ${c.judged_at.slice(0, 10)}` : "";
    console.log(`    Claude (judgment, ${c.model ?? MODEL}${when}): ${c.verdict}: ${c.justification ?? c.reason}`);
  }
  console.log(`\n  report: ${path.relative(ROOT, path.join(runDir, "report.json"))}`);
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (command === "check-persona") {
    loadPersona(PERSONA_PATH);
    console.log(`persona OK: ${path.relative(ROOT, PERSONA_PATH)} (fictional, @example.com email, 555 phone)`);
    return;
  }
  if (command === "watch") {
    const persona = loadPersona(PERSONA_PATH);
    const seededFrom = flag(args, "--seeded-from");
    const getRawText = seededFrom ? async () => fs.readFileSync(path.resolve(seededFrom), "utf8") : () => fetchBoardText(allowedFetch);
    const { template, version } = loadPromptTemplate(PROMPT_PATH);
    const judgeClaude = makeClaudeJudge({ template, version, ask: makeLiveAsk() });
    const { report, runDir } = await runWatch({ root: ROOT, persona, getRawText, judgeClaude, seededFrom: seededFrom && path.relative(ROOT, path.resolve(seededFrom)) });
    printReport(report, runDir);
    return;
  }
  if (command === "rule") {
    const id = Number(args[0]);
    const raw = flag(args, "--raw");
    if (!Number.isInteger(id) || !raw) throw new Error("usage: node src/cli.js rule <posting_id> --raw <raw-response.json>");
    const job = JSON.parse(fs.readFileSync(raw, "utf8")).jobs.find((j) => j.id === id);
    if (!job) throw new Error(`posting ${id} is not in ${raw}`);
    const result = judgeByRule(job, loadPersona(PERSONA_PATH));
    console.log(JSON.stringify({ posting_id: id, title: job.title, location: job.location?.name, ...result }, null, 2));
    return;
  }
  console.error("commands: check-persona | watch [--seeded-from <raw-response.json>] | rule <posting_id> --raw <raw-response.json>");
  process.exitCode = 2;
}

main().catch((e) => {
  console.error(e.message);
  process.exitCode = 1;
});
