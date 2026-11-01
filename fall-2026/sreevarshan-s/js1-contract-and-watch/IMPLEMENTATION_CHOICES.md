# Implementation choices: rule judge (phase 2)

The rule judge (`js1/rule_judge.py`) implements the Final section of `CONTRACT.md`. This file lists every point the contract leaves open and how the code handles it, so a reader can recompute any verdict by hand.

## Defaults set by me (2026-10-29)

1. **Seeded state.** Deferred. The real second run is tomorrow, so no seeded run or separate seeded state file exists yet.
2. **Location words.** "remote" = remote; "hybrid" = hybrid; "on-site", "onsite", "in office", "in-office" = onsite. Complete words, case-insensitive, searched in `location.name` and in the description.
3. **Sentences.** Each HTML list item (`<li>…</li>`) is its own sentence. All other text is split on `.`, `!` or `?` followed by whitespace.
4. **Claude's "experience requirements" input.** `profile.yml` has no such field. To be resolved in the Claude judge phase.
5. **Slashes in titles.** "/" is a separator everywhere, like commas, hyphens and parentheses.
6. **Number words.** one through ten.
7. **Skill citations.** A skill counts once, but cites every résumé field it appears in.

## Rules added after the first rule-judge tests (2026-10-29)

### "Databricks" counts only in a skill context (D8§1)

"Databricks" counts as a matched skill only if it appears in a skill context in the posting title or in one description sentence. A skill context is either of these, case-insensitive:

- **A skill cue directly before it,** with an optional "the" in between. The cues are:
  - experience with, experience in, experience using, experience on
  - knowledge of
  - proficiency in, proficiency with, proficient in, proficient with
  - familiarity with, familiar with
  - expertise in, expertise with
  - skills in

  Example: "experience with the Databricks platform".
- **A product word directly after it.** The words are: platform, lakehouse, notebooks, notebook, workflows, jobs, sql, runtime, clusters, cluster, certification, certified.

  Example: "Databricks SQL".

Anything else is treated as the company name and does not count, for example "Databricks is the Data and AI company", "Join Databricks" or "build pipelines on Databricks".

Known limits:
- **Boilerplate false positives:** company boilerplate that happens to say "the Databricks platform" will still count.
- **Missed skill uses:** a real skill use worded outside these cues, like "on Databricks", will not count.
- **Genie API:** "Databricks Genie API" is still matched separately, as its own skill (D7§b).

### Bullets under a preferred heading count as preferred

- **What counts as a heading:** an `<h1>`–`<h6>`, or a `<p>` whose whole text is one `<strong>` or `<b>`.
- **When it switches on:** after a heading whose text contains "preferred", "nice to have", "nice-to-have" or "bonus".
- **What it covers:** every list item from that heading up to the next heading is treated as if it contained a preferred word. Paragraph text under the heading is not affected.
- **How it combines with D6-B§2:** the "required" / "must have" override still applies. A bullet like "Active security clearance required" under "Preferred Qualifications" stays mandatory.
- **Headings as sentences:** each heading is now its own sentence.

## Further choices made in the code (not yet reviewed by me)

- **Title separators.** The en dash (–) and em dash (—) are treated like hyphens.
- **Other HTML.** Paragraph tags are not sentence boundaries; they become spaces. So a paragraph without end punctuation joins the next one. Headings are separate sentences (see above).
- **Where skills are cited from.** The résumé `skills` arrays (except `familiar_with_not_shipped` and `agent_note`), plus every string in `experience` and `projects`.
- **The two experience tools.** "Databricks Genie API" and "MLflow" must appear in `experience` or `projects` with exactly that capitalization to be added.
- **Where postings are searched for skills.** The posting `title` and the full description text.
- **Years forms.**
  - Ranges may use "-", "–" or "—".
  - "year", "years", "yr" and "yrs" are all accepted.
  - A bare "N years" counts (the contract lists "five years"), with no requirement that the word "experience" be nearby. Every minimum the judge finds is shown in the record's evidence, so false matches are visible.
- **Where clearance and sponsorship are searched.** Description sentences only, not the title.
- **Offered and denied together.** If a posting matches both, the value is "denied", and both matches are kept in the evidence. Example: "no visa sponsorship available" contains both "no visa sponsorship" and "visa sponsorship available".
- **Conflicting work arrangements.** If more than one arrangement is found, across the location field and the description, `work_arrangement` is "conflict" and `work_arrangement_conflict` shows which field gave which.

## Watch run (`python3 -m js1`, no flags), 2026-10-30

- **Order:**
  1. Check the persona.
  2. Refuse if `state/seen_ids.json` does not exist (exit 5).
  3. Fetch once through the allow-list. A fetch error exits 6, with nothing written.
  4. Save the raw response byte for byte to `evidence/raw/<UTC stamp>.json`. If it is not a Greenhouse jobs list, exit 6; the raw file is kept as evidence and state is unchanged.
  5. Compare by posting id.
  6. Run the rule judge on new postings only.
  7. Save `evidence/rule/<UTC stamp>.json`.
  8. Print the report.
  9. Only then copy the previous state to `state/seen_ids.<previous stamp>.json` and write the new state.

  A failure at any step before 9 leaves state unchanged. The Claude judge is not called.
- **What's counted:**
  - **New:** ids in this fetch that were never seen (`seen_ids`).
  - **Removed:** ids in the previous fetch that are not in this one.
  - **Why two lists:** `seen_ids` keeps every id ever seen, so it would count an old removal again on every run. State therefore also stores `last_fetched_ids` and `last_run`.
- **Older state files:** the baseline state committed on 2026-10-29 has only `seen_ids`. In that case the previous fetch is taken to be `seen_ids`, which is exactly the baseline fetch. The previous stamp is taken from the newest earlier file in `evidence/raw/`, which is `2026-10-29T22-15-02Z`.
- **Previous-state backup:** it is written once and never overwritten.
- **The rule evidence file:** holds `{"run": {...counts, removed_ids, raw_evidence, previous_run, previous_state_backup}, "records": [...]}`.
- **Exit codes:**
  - 0: success
  - 1: persona refused
  - 2: seeded run deferred
  - 3: baseline refused, state exists
  - 5: watch refused, no state
  - 6: fetch failed, state unchanged

## Claude judge (phase 3, `js1/claude_judge.py`)

### What Claude receives

- **The posting:** `id`, `title`, `location` (the Greenhouse `location.name`) and `description`. The description is plain text, made by the rule judge's own sentence splitter so both judges read the same text.
- **Priya's fields:**
  - `resume_skill_fields`: the `skills.*` arrays, except `familiar_with_not_shipped` and `agent_note`.
  - `resume_experience_tools`: "Databricks Genie API" with the résumé fields it appears in.
  - `skills.familiar_with_not_shipped`
  - `profile.target_role.primary` and `profile.target_role.secondary`
  - `profile.needs_sponsorship`
  - `profile.target_role.excluded`
- **Never sent:** name, email, phone, LinkedIn, GitHub, or anything from the rule judge's record.
- **"Experience requirements":** `profile.yml` has no such field (D6-C§14 names one). Sent instead: `experience_cap: {"max_required_years": 3, "source": "CONTRACT.md D4§2, not a profile field"}`.

### The exact call

Python makes no network call itself. It runs the claude CLI (v2.1.117) once per attempt, as a subprocess:

```
claude -p --model claude-sonnet-4-6 --tools "" --strict-mcp-config --mcp-config '{"mcpServers": {}}' --disable-slash-commands --no-session-persistence --output-format text
```

**Model, pinned 2026-10-29: `claude-sonnet-4-6`.**
- **Where the id comes from:** this is the claude CLI's full id for Sonnet 4.6, the model the CLI was using. I confirmed the id without a Claude call, by reading the installed CLI (v2.1.117). Its alias table maps "sonnet 4.6" to `claude-sonnet-4-6`, there is no dated variant, and `claude --help` uses the same id as its `--model` example.
- **Where it's recorded:** every saved result, valid or invalid, has a `model` field.
- **Before pinning:** the smoke test results from 2026-10-30T00-43-34Z and 00-46-34Z ran before the model was pinned, so they have no `model` field.

**Personal Claude settings (checked 2026-10-29, read-only):**
- `~/.claude/CLAUDE.md` does not exist.
- `~/.claude/settings.json` contains only `"theme": "dark-daltonized"`, which affects display, not judging.
- No `ANTHROPIC_MODEL`-style environment variable is set.

So nothing personal currently reaches the judge. If a `~/.claude/CLAUDE.md` or a hook is added later, it would load into judge calls, and the cleanest guard is to add a check that refuses to run while one exists.

- **Prompt:** sent on stdin, not as an argument.
- **Working directory:** a fresh empty temporary directory, removed after the call.
- **Timeout:** 180 seconds.

What each flag does, per `claude --help`:
- `--tools ""` disables all built-in tools.
- `--strict-mcp-config` with an empty `--mcp-config` loads no MCP servers.
- `--disable-slash-commands` disables skills.
- `--no-session-persistence` means the session is not saved.

Known limits:
- **Personal settings can still load.** `--bare` is not used, because it accepts only `ANTHROPIC_API_KEY` auth, not a normal login. So user-level settings such as `~/.claude/CLAUDE.md` can still load.
- **Tried for real since.** This flag combination has run against real Claude calls: the smoke tests (`bb1f877`, which failed with "Not logged in", then `c047608`, valid) and the dev experiment (`d7411f4`, 23 calls). The live watch run (`0dd01ab`) ran only the rule judge and made no Claude call.

### The prompts

- **`prompts/baseline.txt`:** review the posting against Priya's fields; return the verdict and explanation in the fixed JSON.
- **`prompts/revised.txt`:** identical, plus one added line: "Check every mandatory eligibility condition before giving the verdict."
- **Building the prompt:** the code appends `INPUT:` and the input JSON after the prompt text.

### The validator (D5§2)

The whole reply, stripped of surrounding whitespace, must parse as one JSON object. A reply wrapped in code fences is rejected. The object must have exactly four keys, `posting_id`, `verdict`, `skills_cited` and `explanation`, with these rules:

- **`posting_id`:** an integer equal to the input id.
- **`verdict`:** "relevant" or "not relevant".
- **`skills_cited`:** a list of `{"skill", "resume_field"}` objects.
  - `resume_field` must be a field name given in the input.
  - Citing `skills.familiar_with_not_shipped` is rejected (D3§2).
- **`explanation`:** a non-empty string that names at least one posting field: "title", "location" or "description".

### Failures (D6-C§15)

- **Retry:** an invalid reply, a non-zero exit, a timeout or a missing `claude` binary each count as a failed attempt. The agent retries exactly once with the same prompt.
- **After two failures:** the result is `{"label": "judgment", "status": "invalid", "validation_errors": [...]}`, with no verdict, and the next posting is processed.
- **What each failure records:** each entry in `validation_errors` holds the attempt number, the error, the exit code, and the first 2,000 characters of both stdout and stderr. The CLI prints some failures on stdout, for example "Not logged in · Please run /login".

### Evidence

- **Raw replies:** every attempt's reply is saved as `evidence/claude/<UTC stamp>-<prompt>-<posting id>-attempt<n>.txt`.
- **Results:** the parsed or invalid result is saved as `…-result.json`.

## APPROVED by me, Sreevarshan Sathiyamurthy, 2026-10-29 (my own approval step, not a contract requirement): sponsorship denial phrases

The contract's three phrases (D6-B§6) are used as written. Draft 7 §a says any explicit denial counts, so the code also uses the added phrases below. All are complete-phrase and case-insensitive.

Checked against the live baseline evidence/raw/2026-10-29T22-15-02Z.json: 0 of 905 postings contain any denial phrase, and all 38 'sponsor' matches are business usage (executive sponsor, sponsored by the CEO, conference sponsorships). On this board, check 6 returns 'unknown' for every posting.

Contract:
- "no visa sponsorship"
- "sponsorship is not available"
- "must not require sponsorship now or in the future"

Added (approved):
- "visa sponsorship is not available"
- "not able to sponsor"
- "unable to sponsor"
- "will not sponsor"
- "does not sponsor"
- "do not sponsor"
- "cannot sponsor"
- "can't sponsor"
- "does not offer visa sponsorship"
- "do not offer visa sponsorship"
- "not eligible for visa sponsorship"
- "not eligible for sponsorship"
- "sponsorship will not be provided"
- "without the need for sponsorship"
- "without the need for visa sponsorship"
- "without sponsorship"
- "without visa sponsorship"
- "will not require sponsorship"
- "not require visa sponsorship now or in the future"
- "will not provide sponsorship"
- "does not provide sponsorship"
