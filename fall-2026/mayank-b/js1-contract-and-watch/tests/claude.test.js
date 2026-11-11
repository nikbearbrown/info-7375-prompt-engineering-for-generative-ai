// The Claude validator: the fixed output format, and nothing else, is accepted.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { PERSONA_PATH } from "../src/config.js";
import { buildPrompt, makeClaudeJudge, validateClaudeOutput } from "../src/claude.js";

const ID = 9000000004;
const good = {
  posting_id: ID,
  verdict: "relevant",
  resume_fields: ["search.target_titles", "personal.location"],
  posting_fields: ["title", "location.name"],
  justification: 'The title "AI Engineer, Internal Tools" fits search.target_titles, and location.name "Boston, MA" equals personal.location.',
};
const reply = (over = {}) => JSON.stringify({ ...good, ...over });

test("accepts a reply in the fixed format", () => {
  assert.equal(validateClaudeOutput(reply(), ID).ok, true);
  assert.equal(validateClaudeOutput(`\n${reply()}\n`, ID).ok, true);
});

test("rejects anything that is not exactly the fixed format", () => {
  const cases = {
    "code fences": "```json\n" + reply() + "\n```",
    "text before": "Here is my answer: " + reply(),
    "not JSON": "{relevant}",
    "extra key": reply({ confidence: 0.9 }),
    "missing key": JSON.stringify({ ...good, justification: undefined }),
    "wrong posting id": reply({ posting_id: 9000000005 }),
    "id as a string": reply({ posting_id: String(ID) }),
    "unknown verdict": reply({ verdict: "maybe" }),
    "no résumé fields": reply({ resume_fields: [] }),
    "a field that was not sent": reply({ resume_fields: ["experience.title"] }),
    "a posting field that was not sent": reply({ posting_fields: ["content"] }),
  };
  for (const [name, text] of Object.entries(cases)) assert.equal(validateClaudeOutput(text, ID).ok, false, name);
});

test("rejects a justification that cites nothing", () => {
  assert.equal(validateClaudeOutput(reply({ justification: "This matches the candidate's background well." }), ID).ok, false);
});

test("a rejected reply becomes no_verdict with the raw reply kept, never a guess", async () => {
  const judge = makeClaudeJudge({ template: "{{RESUME_FIELDS}} {{POSTING_FIELDS}}", version: "test", ask: async () => "I think it's relevant!" });
  const out = await judge({ id: ID, title: "AI Engineer", location: { name: "Boston, MA" } }, {});
  assert.equal(out.verdict, "no_verdict");
  assert.equal(out.kind, "judgment");
  assert.equal(out.raw_output, "I think it's relevant!");
  assert.match(out.reason, /validator rejected/);
});

test("the prompt sends only the listed résumé fields (no name, email or phone)", () => {
  const persona = JSON.parse(fs.readFileSync(PERSONA_PATH, "utf8"));
  const prompt = buildPrompt(fs.readFileSync(new URL("../prompts/judge-v1.md", import.meta.url), "utf8"), { id: ID, title: "AI Engineer", location: { name: "Boston, MA" } }, persona);
  for (const secret of [persona.personal.name, persona.personal.email, persona.personal.phone]) assert.ok(!prompt.includes(secret), secret);
  assert.ok(prompt.includes('"skills.languages"') && prompt.includes(String(ID)));
});
