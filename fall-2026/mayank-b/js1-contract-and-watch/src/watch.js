// The watch (brief Step 2): fetch one board, save the raw response, report only ids not seen before.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { BOARD } from "./config.js";
import { validatePersona } from "./persona.js";
import { judgeByRule } from "./rule.js";

export class OutsideFolderError extends Error {
  constructor(target, root) {
    super(`refused: ${target} is outside ${path.join(root, "state")} and ${path.join(root, "runs")}`);
    this.name = "OutsideFolderError";
  }
}

// CONTRACT.md, Refuses, row 6: writes go only into <root>/state and <root>/runs.
export function safeWrite(root, target, text) {
  const resolved = path.resolve(target);
  const inside = ["state", "runs"].some((d) => resolved.startsWith(path.join(path.resolve(root), d) + path.sep));
  if (!inside) throw new OutsideFolderError(resolved, root);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const tmp = `${resolved}.tmp`;
  fs.writeFileSync(tmp, text);
  fs.renameSync(tmp, resolved);
}

export function localDate(d) {
  return d.toLocaleDateString("en-CA", { timeZone: "America/New_York" }); // YYYY-MM-DD in Boston time
}

export function loadState(statePath) {
  if (!fs.existsSync(statePath)) return null;
  return JSON.parse(fs.readFileSync(statePath, "utf8"));
}

// Keeps the first copy of each id. Returns the unique postings and how many duplicates were dropped.
export function dedupeById(jobs) {
  const seen = new Set();
  const unique = [];
  for (const job of jobs) {
    if (seen.has(job.id)) continue;
    seen.add(job.id);
    unique.push(job);
  }
  return { unique, duplicates: jobs.length - unique.length };
}

export async function fetchBoardText(fetchFn) {
  const res = await fetchFn(BOARD.url, { headers: { accept: "application/json" } });
  if (!res.ok) throw new Error(`board fetch failed: HTTP ${res.status}`);
  return res.text();
}

/**
 * One run of the watch.
 *  root        folder that holds state/ and runs/
 *  persona     the résumé JSON (validated again here, before any fetch)
 *  getRawText  async () => the board response body, exactly as received
 *  judgeClaude async (posting, persona) => claude block
 *  seededFrom  path of a saved response, if this run is seeded instead of live
 */
export async function runWatch({ root, persona, getRawText, judgeClaude, now = () => new Date(), seededFrom = null }) {
  validatePersona(persona);
  const startedAt = now();
  const statePath = path.join(root, "state", "seen-ids.json");
  const state = loadState(statePath);
  const baseline = state === null;
  const runNumber = (state?.runs?.length ?? 0) + 1;
  const runDir = path.join(root, "runs", `run-${String(runNumber).padStart(2, "0")}-${localDate(startedAt)}${seededFrom ? "-seeded" : ""}`);

  const rawText = await getRawText();
  safeWrite(root, path.join(runDir, "raw-response.json"), rawText);
  const sha256 = crypto.createHash("sha256").update(rawText).digest("hex");

  const data = JSON.parse(rawText);
  if (!Array.isArray(data?.jobs)) throw new Error("board response has no jobs array");
  for (const job of data.jobs)
    if (!Number.isInteger(job?.id) || typeof job.title !== "string") throw new Error(`posting without an integer id and a title: ${JSON.stringify(job).slice(0, 200)}`);
  const { unique, duplicates } = dedupeById(data.jobs);

  const seen = new Set(state?.ids ?? []);
  const fresh = baseline ? [] : unique.filter((job) => !seen.has(job.id));

  // Each result is built from its own posting, never matched up by position afterwards (W2).
  const postings = [];
  for (const job of fresh) {
    const rule = judgeByRule(job, persona);
    let claude;
    try {
      claude = await judgeClaude(job, persona);
    } catch (e) {
      claude = { kind: "judgment", verdict: "no_verdict", reason: `judge crashed: ${e.message}` };
    }
    postings.push({ posting_id: job.id, title: job.title, url: job.absolute_url ?? null, rule, claude: { posting_id: job.id, ...claude } });
  }

  const report = {
    run: runNumber,
    started_at: startedAt.toISOString(),
    board: BOARD.name,
    host: BOARD.host,
    url: BOARD.url,
    seeded: Boolean(seededFrom),
    seeded_from: seededFrom,
    baseline,
    postings_fetched: data.jobs.length,
    duplicate_ids_removed: duplicates,
    new_count: fresh.length,
    raw_response: path.relative(root, path.join(runDir, "raw-response.json")),
    raw_sha256: sha256,
    state_file: path.relative(root, statePath),
    postings,
  };
  safeWrite(root, path.join(runDir, "report.json"), JSON.stringify(report, null, 2) + "\n");

  const ids = [...new Set([...seen, ...unique.map((j) => j.id)])].sort((a, b) => a - b);
  const runs = [...(state?.runs ?? []), { run: runNumber, at: report.started_at, seeded: report.seeded, fetched: data.jobs.length, new: fresh.length, raw_response: report.raw_response }];
  safeWrite(root, statePath, JSON.stringify({ board: BOARD.url, updated_at: report.started_at, count: ids.length, runs, ids }, null, 2) + "\n");

  return { report, runDir };
}
