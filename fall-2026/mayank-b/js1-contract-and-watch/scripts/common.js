// Shared helpers for the Step 4 scripts. They read saved raw responses only; they never fetch the board.
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "../src/config.js";
import { localDate } from "../src/watch.js";

export function arg(name, fallback = null) {
  const i = process.argv.indexOf(name);
  return i === -1 ? fallback : process.argv[i + 1];
}

export const hasFlag = (name) => process.argv.includes(name);

export function postingsById(rawFile) {
  const jobs = JSON.parse(fs.readFileSync(path.resolve(ROOT, rawFile), "utf8")).jobs;
  return new Map(jobs.map((j) => [j.id, j]));
}

export function writeReport(name, data) {
  const file = path.join(ROOT, "reports", `${name}-${localDate(new Date())}.json`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
  return path.relative(ROOT, file);
}

export function loadLabels(file) {
  if (!file || !fs.existsSync(path.resolve(ROOT, file))) return null;
  return JSON.parse(fs.readFileSync(path.resolve(ROOT, file), "utf8"));
}
