// Sampling report (brief Step 4, Chapter 1): ask Claude the same prompt contract about each posting
// N times, each in a fresh call, and record every verdict.
// Usage: npm run sample -- --raw runs/<run>/raw-response.json --ids 1,2,3,4,5 [--n 4] [--prompt prompts/judge-v1.md] [--labels labels/labels.json]
import { loadPromptTemplate, makeClaudeJudge, makeLiveAsk } from "../src/claude.js";
import { PERSONA_PATH, PROMPT_PATH } from "../src/config.js";
import { loadPersona } from "../src/persona.js";
import { judgeByRule } from "../src/rule.js";
import { arg, loadLabels, postingsById, writeReport } from "./common.js";

const raw = arg("--raw");
const ids = (arg("--ids") ?? "").split(",").filter(Boolean).map(Number);
const n = Number(arg("--n", "4"));
if (!raw || ids.length === 0 || !(n >= 1)) {
  console.error("usage: npm run sample -- --raw <raw-response.json> --ids <id,id,...> [--n 4]");
  process.exit(2);
}

const persona = loadPersona(PERSONA_PATH);
const byId = postingsById(raw);
const { template, version } = loadPromptTemplate(arg("--prompt", PROMPT_PATH));
const judge = makeClaudeJudge({ template, version, ask: makeLiveAsk() });
const hand = new Map((loadLabels(arg("--labels", "labels/labels.json"))?.labels ?? []).map((l) => [l.posting_id, l.label]));

const results = [];
for (const id of ids) {
  const posting = byId.get(id);
  if (!posting) throw new Error(`posting ${id} is not in ${raw}`);
  const calls = [];
  for (let i = 0; i < n; i++) calls.push(await judge(posting, persona)); // one fresh call each time
  const counts = { relevant: 0, not_relevant: 0, no_verdict: 0 };
  for (const c of calls) counts[c.verdict]++;
  const row = { posting_id: id, title: posting.title, location: posting.location?.name, rule_verdict: judgeByRule(posting, persona).verdict, hand_label: hand.get(id) ?? null, counts, calls };
  results.push(row);
  console.log(`[${id}] ${posting.title}: relevant ${counts.relevant}, not_relevant ${counts.not_relevant}, no_verdict ${counts.no_verdict} | rule ${row.rule_verdict} | hand ${row.hand_label ?? "-"}`);
}

const file = writeReport(`sampling-${version}`, { prompt_version: version, raw_response: raw, calls_per_posting: n, ran_at: new Date().toISOString(), results });
console.log(`\nsaved ${file}`);
