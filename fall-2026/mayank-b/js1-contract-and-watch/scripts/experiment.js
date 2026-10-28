// Prompt experiment (brief Step 4, Chapter 2): pass rate of one prompt contract against my hand labels.
// Run the baseline and the revision on dev first. The held-out set needs --final, so it can't be run by accident.
// Usage: npm run experiment -- --prompt prompts/judge-v1.md --set dev [--labels labels/labels.json]
//        npm run experiment -- --prompt prompts/judge-v2.md --set heldout --final
import { loadPromptTemplate, makeClaudeJudge, makeLiveAsk } from "../src/claude.js";
import { PERSONA_PATH } from "../src/config.js";
import { loadPersona } from "../src/persona.js";
import { arg, hasFlag, loadLabels, postingsById, writeReport } from "./common.js";

const promptFile = arg("--prompt");
const set = arg("--set");
const labels = loadLabels(arg("--labels", "labels/labels.json"));
if (!promptFile || !["dev", "heldout"].includes(set) || !labels) {
  console.error("usage: npm run experiment -- --prompt <prompts/x.md> --set dev|heldout [--final] (needs labels/labels.json)");
  process.exit(2);
}
if (set === "heldout" && !hasFlag("--final")) {
  console.error("refused: the held-out set is for the very end. Re-run with --final once the dev work is finished.");
  process.exit(2);
}

const persona = loadPersona(PERSONA_PATH);
const byId = postingsById(labels.raw_response);
const { template, version } = loadPromptTemplate(promptFile);
const judge = makeClaudeJudge({ template, version, ask: makeLiveAsk() });

const cases = labels.labels.filter((l) => l.set === set);
const results = [];
for (const l of cases) {
  const posting = byId.get(l.posting_id);
  if (!posting) throw new Error(`labeled posting ${l.posting_id} is not in ${labels.raw_response}`);
  const claude = await judge(posting, persona);
  const pass = claude.verdict === l.label; // no_verdict counts as a fail
  results.push({ posting_id: l.posting_id, title: posting.title, hand_label: l.label, claude_verdict: claude.verdict, pass, claude });
  console.log(`${pass ? "PASS" : "FAIL"} [${l.posting_id}] ${posting.title}: hand ${l.label}, Claude ${claude.verdict}`);
}

const passed = results.filter((r) => r.pass).length;
console.log(`\n${version} on ${set}: ${passed}/${results.length} passed`);
const file = writeReport(`experiment-${version}-${set}`, { prompt_version: version, set, ran_at: new Date().toISOString(), passed, total: results.length, results });
console.log(`saved ${file}`);
