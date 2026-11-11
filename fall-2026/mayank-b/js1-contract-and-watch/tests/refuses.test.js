// CONTRACT.md, Refuses: the allow-list, the persona validator, and writes outside the folder.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { makeAllowedFetch } from "../src/allowlist.js";
import { PERSONA_PATH } from "../src/config.js";
import { validatePersona } from "../src/persona.js";

const persona = () => JSON.parse(fs.readFileSync(PERSONA_PATH, "utf8"));

test("a host not on the allow-list is refused and nothing is fetched", async () => {
  let calls = 0;
  const fetchSpy = async () => { calls++; return new Response("{}"); };
  const allowed = makeAllowedFetch(fetchSpy);
  for (const url of ["https://api.lever.co/v0/postings/x", "https://boards-api.greenhouse.io.evil.com/x", "http://boards-api.greenhouse.io/v1/boards/anthropic/jobs"])
    await assert.rejects(allowed(url), /not on the allow-list/, url);
  assert.equal(calls, 0);
  await allowed("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs");
  assert.equal(calls, 1);
});

test("Priya's persona passes the validator", () => {
  assert.doesNotThrow(() => validatePersona(persona()));
});

test("a real-looking résumé is rejected", () => {
  const edits = [
    (p) => { p.personal.email = "someone@northeastern.edu"; },
    (p) => { p.personal.phone = "(617) 373-2000"; },
    (p) => { p.experience[0].bullets.push("Contact my manager at boss@company.com"); },
    (p) => { delete p.search; },
  ];
  for (const edit of edits) {
    const p = persona();
    edit(p);
    assert.throws(() => validatePersona(p), /persona résumé rejected/);
  }
});

test("writes outside state/ and runs/ are refused", async () => {
  const { safeWrite } = await import("../src/watch.js");
  const os = await import("node:os");
  const path = await import("node:path");
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "js1-"));
  assert.throws(() => safeWrite(root, path.join(root, "notes.txt"), "x"), /outside/);
  assert.throws(() => safeWrite(root, path.join(root, "state", "..", "..", "escape.json"), "x"), /outside/);
  assert.throws(() => safeWrite(root, path.join(root, "runs-evil", "x.json"), "x"), /outside/);
  safeWrite(root, path.join(root, "runs", "run-01", "ok.json"), "x");
  assert.equal(fs.readFileSync(path.join(root, "runs", "run-01", "ok.json"), "utf8"), "x");
});
