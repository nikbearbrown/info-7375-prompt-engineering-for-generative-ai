// The watch: W5 (baseline), the failure sentence (no old id reported as new, no duplicates), W2 (pairing).
// Uses constructed fixtures and a fake Claude judge, so nothing here touches the network.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PERSONA_PATH } from "../src/config.js";
import { runWatch } from "../src/watch.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixture = (name) => fs.readFileSync(path.join(here, "fixtures", name), "utf8");
const persona = JSON.parse(fs.readFileSync(PERSONA_PATH, "utf8"));
const tempRoot = () => fs.mkdtempSync(path.join(os.tmpdir(), "js1-"));
const day = (d) => () => new Date(`2026-10-${d}T15:00:00Z`);

// A judge whose answer carries the posting it was asked about, so a mismatch is visible.
const echoJudge = async (job) => ({ kind: "judgment", model: "fake", judged_at: "2026-10-28T00:00:00.000Z", verdict: "relevant", justification: `about ${job.id}` });
const neverCalled = async () => assert.fail("Claude must not be called on a baseline run");

test("W5: run 1 with no state file reports 0 new and saves every fetched id", async () => {
  const root = tempRoot();
  const { report, runDir } = await runWatch({ root, persona, getRawText: async () => fixture("board-run1.json"), judgeClaude: neverCalled, now: day(28) });
  assert.equal(report.baseline, true);
  assert.equal(report.new_count, 0);
  assert.deepEqual(report.postings, []);
  const state = JSON.parse(fs.readFileSync(path.join(root, "state", "seen-ids.json"), "utf8"));
  assert.deepEqual(state.ids, [9000000001, 9000000002, 9000000003]);
  assert.equal(fs.readFileSync(path.join(runDir, "raw-response.json"), "utf8"), fixture("board-run1.json"), "raw response saved byte for byte");
});

test("failure sentence: run 2 reports no id saved in run 1, and each new id once", async () => {
  const root = tempRoot();
  await runWatch({ root, persona, getRawText: async () => fixture("board-run1.json"), judgeClaude: neverCalled, now: day(28) });
  const run1Ids = JSON.parse(fs.readFileSync(path.join(root, "state", "seen-ids.json"), "utf8")).ids;
  const { report } = await runWatch({ root, persona, getRawText: async () => fixture("board-run2.json"), judgeClaude: echoJudge, now: day(29) });

  const reported = report.postings.map((p) => p.posting_id);
  assert.equal(report.baseline, false);
  assert.deepEqual(reported.filter((id) => run1Ids.includes(id)), [], "an id saved in run 1 was reported as new");
  assert.equal(new Set(reported).size, reported.length, "an id was reported twice");
  assert.deepEqual(reported, [9000000004, 9000000005, 9000000006]);
  assert.equal(report.duplicate_ids_removed, 1);
  assert.equal(report.run, 2);
  assert.match(report.raw_response, /^runs\/run-02-2026-10-29\/raw-response\.json$/);
});

test("W2: when the middle Claude call fails, every verdict stays with its own posting", async () => {
  const root = tempRoot();
  await runWatch({ root, persona, getRawText: async () => fixture("board-run1.json"), judgeClaude: neverCalled, now: day(28) });
  const judge = async (job) => {
    if (job.id === 9000000005) throw new Error("simulated API failure");
    return echoJudge(job);
  };
  // The judge also returns no_verdict blocks the normal way; here it throws, the harder case.
  const { report } = await runWatch({ root, persona, getRawText: async () => fixture("board-run2.json"), judgeClaude: judge, now: day(29) });

  const [first, middle, last] = report.postings;
  for (const p of report.postings) assert.equal(p.claude.posting_id, p.posting_id);
  assert.equal(first.claude.justification, "about 9000000004");
  assert.equal(middle.claude.verdict, "no_verdict");
  assert.match(middle.claude.reason, /simulated API failure/);
  assert.equal(last.claude.justification, "about 9000000006");
  assert.equal(last.claude.verdict, "relevant");
});

test("every Claude block is labeled a judgment, every rule block a record", async () => {
  const root = tempRoot();
  await runWatch({ root, persona, getRawText: async () => fixture("board-run1.json"), judgeClaude: neverCalled, now: day(28) });
  const { report } = await runWatch({ root, persona, getRawText: async () => fixture("board-run2.json"), judgeClaude: echoJudge, now: day(29) });
  for (const p of report.postings) {
    assert.equal(p.rule.kind, "record");
    assert.equal(p.claude.kind, "judgment");
  }
});

test("a rejected persona stops the run before anything is fetched", async () => {
  const root = tempRoot();
  const real = structuredClone(persona);
  real.personal.email = "someone@northeastern.edu";
  let fetched = false;
  await assert.rejects(
    runWatch({ root, persona: real, getRawText: async () => { fetched = true; return "{}"; }, judgeClaude: neverCalled }),
    /persona résumé rejected/,
  );
  assert.equal(fetched, false);
  assert.equal(fs.existsSync(path.join(root, "runs")), false);
});
