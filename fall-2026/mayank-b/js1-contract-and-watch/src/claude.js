// The Claude judge (CONTRACT.md, Out; brief Step 3). A judgment: always labeled as one, never mixed into the record.
import fs from "node:fs";
import path from "node:path";
import Anthropic from "@anthropic-ai/sdk";
import { allowedFetch } from "./allowlist.js";
import { MODEL } from "./config.js";

export const RESUME_FIELDS = [
  "personal.location",
  "search.target_titles",
  "search.exclude_titles",
  "search.open_to_remote",
  "search.open_to_relocate",
  "skills.languages",
];
export const POSTING_FIELDS = ["title", "location.name"];
const OUTPUT_KEYS = ["posting_id", "verdict", "resume_fields", "posting_fields", "justification"];
const VERDICTS = ["relevant", "not_relevant"];

const get = (obj, dotted) => dotted.split(".").reduce((o, k) => o?.[k], obj);

export function resumeFieldsFor(persona) {
  return Object.fromEntries(RESUME_FIELDS.map((f) => [f, get(persona, f)]));
}

export function postingFieldsFor(posting) {
  return { id: posting.id, title: posting.title, "location.name": posting.location?.name ?? null };
}

export function buildPrompt(template, posting, persona) {
  return template
    .replace("{{RESUME_FIELDS}}", () => JSON.stringify(resumeFieldsFor(persona), null, 2))
    .replace("{{POSTING_FIELDS}}", () => JSON.stringify(postingFieldsFor(posting), null, 2));
}

// The validator: accepts exactly one JSON object in the fixed format and rejects anything else.
export function validateClaudeOutput(text, postingId) {
  const reject = (reason) => ({ ok: false, reason });
  const trimmed = String(text ?? "").trim();
  if (!trimmed.startsWith("{") || !trimmed.endsWith("}")) return reject("reply is not a bare JSON object (text or code fences around it)");
  let out;
  try {
    out = JSON.parse(trimmed);
  } catch (e) {
    return reject(`reply is not valid JSON: ${e.message}`);
  }
  if (!out || typeof out !== "object" || Array.isArray(out)) return reject("reply is not a JSON object");
  const keys = Object.keys(out).sort();
  if (keys.join() !== [...OUTPUT_KEYS].sort().join()) return reject(`keys must be exactly ${OUTPUT_KEYS.join(", ")} (got ${keys.join(", ")})`);
  if (out.posting_id !== postingId) return reject(`posting_id ${JSON.stringify(out.posting_id)} does not match the posting sent (${postingId})`);
  if (!VERDICTS.includes(out.verdict)) return reject(`verdict must be one of ${VERDICTS.join(", ")} (got ${JSON.stringify(out.verdict)})`);
  for (const [key, allowed] of [["resume_fields", RESUME_FIELDS], ["posting_fields", POSTING_FIELDS]]) {
    const list = out[key];
    if (!Array.isArray(list) || list.length === 0) return reject(`${key} must be a non-empty list`);
    const unknown = list.filter((f) => !allowed.includes(f));
    if (unknown.length) return reject(`${key} cites fields that were not sent: ${unknown.join(", ")}`);
  }
  const j = out.justification;
  if (typeof j !== "string" || j.trim().length < 20) return reject("justification must be a sentence of at least 20 characters");
  if (!out.resume_fields.some((f) => j.includes(f))) return reject("justification names none of the résumé fields it cites");
  if (!out.posting_fields.some((f) => j.includes(f))) return reject("justification names none of the posting fields it cites");
  return { ok: true, value: out };
}

export function loadPromptTemplate(file) {
  return { template: fs.readFileSync(file, "utf8"), version: path.basename(file, ".md") };
}

// One fresh API call per verdict: no conversation history is shared between postings.
export async function askClaude(client, prompt, model = MODEL) {
  const response = await client.messages.create({
    model,
    max_tokens: 2000,
    output_config: { effort: "low" },
    messages: [{ role: "user", content: prompt }],
  });
  if (response.stop_reason === "refusal") throw new Error("model refused (stop_reason: refusal)");
  if (response.stop_reason === "max_tokens") throw new Error("reply was cut off (stop_reason: max_tokens)");
  return response.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

// Returns a judge: (posting, persona) -> claude block. `ask` is injectable so tests never call the API.
export function makeClaudeJudge({ template, version, ask, model = MODEL, now = () => new Date() }) {
  return async function judgeByClaude(posting, persona) {
    const base = { kind: "judgment", model, prompt_version: version };
    let raw;
    try {
      raw = await ask(buildPrompt(template, posting, persona));
    } catch (e) {
      return { ...base, judged_at: now().toISOString(), verdict: "no_verdict", reason: `call failed: ${e.message}`, raw_output: null };
    }
    const judged_at = now().toISOString();
    const checked = validateClaudeOutput(raw, posting.id);
    if (!checked.ok) return { ...base, judged_at, verdict: "no_verdict", reason: `validator rejected the reply: ${checked.reason}`, raw_output: raw };
    const { verdict, justification, resume_fields, posting_fields } = checked.value;
    return { ...base, judged_at, verdict, justification, resume_fields, posting_fields, raw_output: raw };
  };
}

export function makeLiveAsk(model = MODEL) {
  if (!process.env.ANTHROPIC_API_KEY) return async () => { throw new Error("ANTHROPIC_API_KEY is not set (see README, Setup)"); };
  const client = new Anthropic({ fetch: allowedFetch });
  return (prompt) => askClaude(client, prompt, model);
}
