// Persona validator (CONTRACT.md, Refuses, row 2). Runs before any fetch.
import fs from "node:fs";

export class PersonaRejectedError extends Error {
  constructor(problems) {
    super(`refused: persona résumé rejected:\n  - ${problems.join("\n  - ")}`);
    this.name = "PersonaRejectedError";
    this.problems = problems;
  }
}

const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;

function allStrings(value, out = []) {
  if (typeof value === "string") out.push(value);
  else if (Array.isArray(value)) value.forEach((v) => allStrings(v, out));
  else if (value && typeof value === "object") Object.values(value).forEach((v) => allStrings(v, out));
  return out;
}

const isStringList = (v) => Array.isArray(v) && v.length > 0 && v.every((s) => typeof s === "string" && s.trim());

export function validatePersona(persona) {
  const problems = [];
  const personal = persona?.personal ?? {};

  if (typeof personal.email !== "string" || !personal.email.toLowerCase().endsWith("@example.com"))
    problems.push(`personal.email must end in @example.com (got ${JSON.stringify(personal.email ?? null)})`);
  if (typeof personal.phone !== "string" || !personal.phone.includes("555"))
    problems.push(`personal.phone must contain 555 (got ${JSON.stringify(personal.phone ?? null)})`);
  for (const s of allStrings(persona))
    for (const email of s.match(EMAIL) ?? [])
      if (!email.toLowerCase().endsWith("@example.com")) problems.push(`email "${email}" anywhere in the file must end in @example.com`);

  if (typeof personal.location !== "string" || !personal.location.trim()) problems.push("personal.location is missing");
  const search = persona?.search ?? {};
  if (!isStringList(search.target_titles)) problems.push("search.target_titles must be a non-empty list of strings");
  if (!isStringList(search.exclude_titles)) problems.push("search.exclude_titles must be a non-empty list of strings");
  if (typeof search.open_to_remote !== "boolean") problems.push("search.open_to_remote must be true or false");
  if (!Array.isArray(search.open_to_relocate) || !search.open_to_relocate.every((s) => typeof s === "string"))
    problems.push("search.open_to_relocate must be a list of strings");

  if (problems.length) throw new PersonaRejectedError(problems);
  return persona;
}

export function loadPersona(file) {
  return validatePersona(JSON.parse(fs.readFileSync(file, "utf8")));
}
