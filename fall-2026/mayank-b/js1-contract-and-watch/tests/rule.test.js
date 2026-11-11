// THE RULE, including W1 (substring matching). Cases come from CONTRACT.md.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { PERSONA_PATH } from "../src/config.js";
import { judgeByRule, matchesTerm, splitLocations } from "../src/rule.js";

const persona = JSON.parse(fs.readFileSync(PERSONA_PATH, "utf8"));
const posting = (title, location) => ({ id: 1, title, location: { name: location } });
const verdict = (title, location) => judgeByRule(posting(title, location), persona).verdict;

test("W1: 'Intern' must not exclude 'AI Engineer, Internal Tools'", () => {
  assert.equal(verdict("AI Engineer, Internal Tools", "Boston, MA"), "relevant");
});

test("W1: 'Lead' must not exclude 'ML Engineer, Leadership Programs'", () => {
  assert.equal(verdict("ML Engineer, Leadership Programs", "Boston, MA"), "relevant");
});

test("whole-word matching still catches the real words", () => {
  assert.equal(verdict("AI Engineer Intern", "Boston, MA"), "not_relevant");
  assert.equal(verdict("Lead ML Engineer", "Boston, MA"), "not_relevant");
  assert.equal(verdict("Staff+ Software Engineer (Machine Learning)", "San Francisco, CA"), "not_relevant");
  assert.equal(matchesTerm("Head  of   Data", "Head of"), true); // spaces collapsed
  assert.equal(matchesTerm("LLMs Platform", "LLM"), false); // whole words only, no plural
});

test("location is split on | and ; (both appear on the Anthropic board)", () => {
  assert.deepEqual(splitLocations("New York City, NY; San Francisco, CA | Seattle, WA"), ["New York City, NY", "San Francisco, CA", "Seattle, WA"]);
  assert.equal(verdict("Data Engineer, GTM", "Seattle, WA; New York City, NY"), "relevant");
});

test("location: Boston, relocation cities, remote US only", () => {
  assert.equal(verdict("Data Engineer", "Boston, MA; San Francisco, CA"), "relevant");
  assert.equal(verdict("Data Engineer", "Remote-Friendly, United States"), "relevant");
  assert.equal(verdict("Data Engineer", "Remote-Friendly (Travel-Required)"), "not_relevant");
  assert.equal(verdict("Data Engineer", "Seattle, WA"), "not_relevant");
  assert.equal(verdict("Data Engineer", "London, UK"), "not_relevant");
});

test("worked examples in CONTRACT.md come out as written", () => {
  assert.equal(verdict("Data Engineer, Product", "San Francisco, CA | New York City, NY | Seattle, WA"), "relevant");
  assert.equal(verdict("Manager, Applied AI Architect", "Seoul, South Korea"), "not_relevant");
  assert.equal(verdict("Applied AI Architect", "Mumbai, India"), "not_relevant");
  assert.equal(verdict("Research Engineer, Machine Learning (RL Velocity)", "Remote-Friendly (Travel-Required) | San Francisco, CA | New York City, NY"), "relevant");
  assert.equal(verdict("Recruiter, Applied AI", "San Francisco, CA | New York City, NY"), "relevant"); // the known weakness
});

test("the justification names résumé fields and posting fields with their values", () => {
  const { justification } = judgeByRule(posting("Data Engineer, Product", "Seattle, WA"), persona);
  for (const field of ["search.target_titles", "search.exclude_titles", "personal.location", "title", "location.name"])
    assert.ok(justification.includes(field), `missing ${field}: ${justification}`);
  assert.ok(justification.includes('"Data Engineer"') && justification.includes('"Seattle, WA"'));
});
