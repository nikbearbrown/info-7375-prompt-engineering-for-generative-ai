# CONTRACT: Job-Search Agent 1

Author: Deepak Kumaran T S
Date written: 2026-10-29
Board host: boards-api.greenhouse.io (Greenhouse Job Board API, public, read-only, no key), board token `stripe`

## In
- `--board <token>`: must fully match `^[a-z0-9][a-z0-9_-]{0,62}$`. Anything else is refused
  before any request.
- `--resume <path>`: JSON that validates against `schema/resume.schema.json`. Required:
  `"fictional": true`; `basics.name`, `basics.email`, `basics.phone` (strings);
  `targets.roles` (non-empty array of non-empty strings); `targets.locations` and
  `targets.exclude_title_terms` (arrays of non-empty strings); `skills` (array of strings).
  Other fields are allowed. Every `targets.roles`, `targets.locations` and
  `targets.exclude_title_terms` entry must have at least one token (as defined in The rule);
  otherwise the résumé is refused at load with exit code 2.
- Network: two requests, each with one purpose. Nothing else is ever requested.
  - Board fetch: `GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`,
    built by the code from the validated token. Timeout 20 s.
  - Judge: the Claude Messages API at `api.anthropic.com`, through the `anthropic` SDK. No URL
    found in posting data is ever requested.
- Writes: only under `evidence/` and `state/`.
- `ANTHROPIC_API_KEY`: used by the judge only. If it is absent, every judgment has status `not_run`.

## Out
**Baseline run** (no state file for this board): zero posting records. The report gives counts only.
**Any other run:** one record per posting whose id was not in the state file before this run.

| field | meaning |
|---|---|
| `posting_id` | Greenhouse `id`, as a string |
| `title`, `absolute_url` | copied from the posting |
| `location` | `location.name`, or `null` if absent |
| `record` | rule verdict: `{verdict, citations}` |
| `judgment` | always an object: `{status, reason, verdict, citations, model, called_at, raw_path}` |
| `agreement` | `agree`, `disagree`, or `n/a` (any judgment not `accepted`) |

`judgment.status` is one of:
- `accepted`: passed the validator; `verdict` and `citations` are filled.
- `rejected`: `reason` is the validator's named reason, or `truncated` (stop_reason max_tokens). `verdict` is null.
- `error`: `reason` is `api_error:<type>` (timeout, rate limit, 5xx, auth). `verdict` is null.
- `not_run`: `reason` is `no_api_key`. `verdict` is null.
Whenever a call was made, the exact raw response text is saved at `raw_path`.

**Citations.** A citation is `{source: "resume" | "posting", path, value}`.
- `path` is a JSON Pointer (RFC 6901) into the résumé, or into the posting document.
- The posting document that citations resolve against is exactly `POSTING_JSON` (Interfaces ›
  Prompt file): `id`, `title`, `location`, `absolute_url`, `departments`, and `content_text`.
  `content_text` is `content` after `html.unescape`, tag stripping and whitespace normalisation,
  truncated to the first 6000 characters. That is exactly the text the judge is sent. Fields
  outside that set, such as `/content`, `/updated_at` and `/offices`, are not citable; the
  validator rejects them as `path_unresolved`.
- `path` must resolve to a string or a number (numbers compared as their decimal string).
- `value` must be non-empty and must appear at that path as a whole-word match (the same matching
  the rule uses), case-insensitive, with all Unicode whitespace normalised to single spaces.
- Every verdict, the rule's and Claude's, needs at least one résumé citation and one posting citation.

**Claude's output format.** Exactly one JSON object, nothing before or after it, no code fences:
`{"posting_id": "<string>", "verdict": "relevant" | "not_relevant", "citations": [...], "reason": "<string, at most 400 characters>"}`.
No other keys. An integer `posting_id` is rejected.

**Files written by each run:** `evidence/raw/<run_id>.raw` (body bytes exactly as received);
`evidence/runs/<run_id>/manifest.json`; `state_before.json` (a byte copy, absent on baseline);
`claude/<posting_id>.request.json` and `.response.txt`; `report.json` and `report.txt` (also printed
to stdout); then `state/<token>.json`.

**run_id:** `YYYYMMDDTHHMMSSZ_<token>`, from the injected or real UTC now. On a collision, append
`-2`, `-3` and so on.

**report.json:**
```
{"run_id", "label", "board", "generated_at",
 "counts": {"postings", "unique", "previously_seen", "new", "agree", "disagree"},
 "duplicates_dropped": <int>, "skipped_bad_id": [<raw id as received>...], "skipped_bad_title": [<id>...],
 "judge": {"status": "run" | "not_run", "model", "prompt_sha256"},
 "records": [<Out record>, ...]}
```
`records` are in response order. On a baseline run, `records` is `[]`.
- `postings`: jobs as received.
- `unique`: distinct valid ids, after `skipped_bad_id` and `duplicates_dropped`. Postings with a
  bad title have valid ids, so they are counted in `unique`.
- `previously_seen`: unique ids already in `seen_ids` before this run.
- `new`: unique ids not previously seen, excluding `skipped_bad_title`. So `new` always equals the
  number of records.
- `agree` / `disagree`: the number of records with that agreement.
- `skipped_bad_id` and `skipped_bad_title` are listed on every run, at parse time, whether or not
  the ids are new.
- Every unique id, including bad-title ones, is added to `seen_ids`.

**manifest.json:**
- `run_id`, `label`, `board`, `source` (`"network"` | `"file"`);
- `url` (null if seeded), `from_file` and `from_file_sha256` (null if live);
- `method` `"GET"`, `http_status` (null if seeded), `location_header` (only on a 3xx);
- `fetched_at` (UTC), `sha256`, `byte_length`, `raw_path`;
- `resume_path`, `resume_sha256`, `state_before_sha256` (null on baseline);
- `prompt_path`, `prompt_sha256` (both null if no prompt was loaded), `model`.

**State file** (`state/<token>.json`): `{"schema_version": 1, "board": "<token>", "seen_ids": [unique
digit strings, sorted by integer value], "updated_at": "<UTC ISO 8601 with Z>", "last_run_id":
"<run_id>"}`. The only known `schema_version` is 1.

## Refuses
1. Any request other than the two listed in In. Redirects (any 3xx) are never followed, and the run
   stops. The URL check requires: https only, an exact hostname match (case-insensitive), no
   userinfo, no explicit port, no trailing dot.
2. A résumé that lacks `"fictional": true`. Also a résumé where any string contains an email address
   not ending exactly in `@example.com` (case-insensitive, no subdomains). Also a résumé where any
   string contains a phone number outside 555-01xx: after an optional leading country code 1, the
   exchange must be 555 and the line 0100 to 0199, in any written format. Refusal messages name the
   field path, never the value.
3. Presenting a model's judgment as a fact. It is printed as `JUDGMENT (<model>, <UTC date>)`, on a
   separate line from `RECORD (rule)`, and is never merged into the rule verdict. A disagreement is
   shown per posting as `DISAGREE` and never resolved. There is no combined verdict.
4. Applying, emailing, messaging, logging in, or POSTing to the job board or to any host. The single
   exception is the judge's API call in In.
5. Reporting any posting as new on the baseline run.
6. Running on a corrupt state file. Corrupt means any of: unreadable, empty, invalid JSON, not an
   object, unknown `schema_version`, a board that doesn't match, or `seen_ids` that is not a list of
   unique digit strings. The run stops before any request, and nothing is written.

## Order of operations (one `run`)
1. Validate the token.
2. Load the résumé; check it against the schema, then run the privacy check.
2b. Only when `ANTHROPIC_API_KEY` is set: load and check the prompt, before any request. If it is
    missing, a section is missing or extra, or a placeholder is missing or repeated, the run is
    refused with exit code 2. With no key, no prompt is needed, and every judgment is `not_run`.
3. Load the state. Missing means a baseline run; corrupt means stop.
4. Check the URL, then GET it (or, in a seeded run, read the `--from-file` instead).
5. Write the raw bytes and the manifest.
6. On any 3xx or non-200 status: stop with exit code 3, state unchanged.
7. Parse the body, which must be `{"jobs": [...]}`; otherwise stop.
   - A valid id is a positive integer (not a bool) or a string matching `^[1-9][0-9]*$`. It is
     normalised to a string.
   - A posting with any other id is skipped and listed under `skipped_bad_id`.
   - A posting whose `title` is missing, not a string, or has zero tokens is not judged. It is
     listed under `skipped_bad_title`, and its id is still added to `seen_ids`.
   - For duplicate ids, the first occurrence is kept and `duplicates_dropped` is reported.
8. Compute new = ids not in `seen_ids`. On a baseline run, new is empty.
9. For each new posting:
   - Run the rule, then the validator. An invalid rule verdict is a bug: stop with exit code 5,
     state unchanged.
   - Then run the judge, then the validator.
10. Write the report.
11. Write the state atomically (temp file, then rename). `seen_ids` becomes `seen_ids` ∪ ids: every
    id ever seen. An id that disappears and later returns is not new. A judge error does not block
    this step: the posting is marked seen, and its error stays in the report.

## Run labels
- `baseline`: no state file for this board existed before the run.
- `live`: state existed, and the body came from a network fetch.
- `seeded`: the body came from `--from-file <saved raw file>`. The manifest records that file and its
  sha256, and `url` is null.

## Interfaces
- `python -m jobwatch run --board T --resume P [--from-file F] [--prompt prompts/v1.md] [--model M]`
- `python -m jobwatch replay RUN_DIR`: offline, needs no key, and writes nothing. It rebuilds the
  report from the saved raw response, `state_before.json` and the saved Claude responses, re-validates
  the responses, and exits 1 on any difference or sha256 mismatch.
- `python -m jobwatch sample --run RUN_DIR --posting-id ID ... --resume P --prompt F [--n 4]`:
  every call is a separate request with no prior messages.
- `python -m jobwatch experiment --set development|held-out --resume P --prompt-a F --prompt-b F`:
  - Scores each prompt against `labels/labels.csv`, counting rejections separately from wrong
    verdicts.
  - `held-out` refuses to run if results already exist for that prompt's sha256, or if either prompt
    file has uncommitted changes.
  - `labels/split.json` is made by `labels/make_split.py --seed S`, and the seed is stored in it.
- Prompt file:
  - The file has exactly two sections, headed `## System` and `## User`.
  - The User section contains each of `{{RESUME_JSON}}`, `{{POSTING_ID}}` and `{{POSTING_JSON}}`
    exactly once. They are replaced literally.
  - `POSTING_JSON` is the posting document the validator resolves citations against: `id`,
    `title`, `location`, `absolute_url`, `departments`, and `content_text` (truncated to 6000
    characters) instead of `content`.
  - The request is: `system` = the System section; `messages` = `[{"role": "user", "content": the
    filled User section}]`; model; temperature 1.0; `max_tokens` 600; no tools.
- Judge defaults: model `claude-sonnet-5-5` (pinned and recorded in every call file); temperature 1.0,
  sent explicitly; `max_tokens` 600; no tools; no retries.
- Test seam: `cli.main(argv, *, opener=None, anthropic_client=None, now=None) -> int`.
- Exit codes:

  | code | meaning |
  |---|---|
  | 0 | ok |
  | 2 | refused input (token, résumé, prompt or URL) |
  | 3 | network error, HTTP error or redirect |
  | 4 | corrupt state |
  | 5 | rule produced an invalid verdict |
  | 1 | anything else |

## The rule
**Fields read.** Nothing else is used.
- Posting: `/title` decides the role and the exclusion; `/location/name` decides the location.
  `/content_text` and `/departments` are not used by the rule.
- Résumé: `/targets/exclude_title_terms/N`, `/targets/roles/N`, `/targets/locations/N`.
  `/skills` is not used.

**Whole-word match.** Lowercase both texts with Python `str.lower()` (not `str.casefold()`). A
token is a maximal run of characters that are `str.isalnum()` or one of `+#`. A term matches when
its token sequence appears contiguously in the text's token sequence. So "ML" matches "ML-Ops" and "Senior ML Engineer" but not "HTML"; "C++"
matches "C++"; "Node.js" is the tokens node, js; there is no stemming, so "Engineers" does not
match "Engineer"; "New York" matches "New York City" but not "NYC".

**Order of checks.** The first step that applies decides the verdict.
1. If `/title` contains any `exclude_title_terms` term: `not_relevant`.
2. Else, if `/title` contains no `roles` term: `not_relevant`.
3. Else, if `/location/name` contains no `locations` term: `not_relevant`. A null, missing or
   zero-token location never matches. "Remote" is an ordinary term and counts wherever it
   appears, so "Remote in the US, Canada" matches.
4. Else: `relevant`.

When several terms in one array match, the rule uses the one with the lowest index in that array.

**Citations**, by the deciding step. `i` and `j` are those lowest matching indexes, and "the term"
is the résumé string exactly as written at that index. The order of the list is part of the
verdict: citations appear exactly in the order below.
- Step 1 (excluded):
  1. résumé `/targets/exclude_title_terms/i` = the term
  2. posting `/title` = the same term
- Step 2 (no role):
  1. résumé `/targets/roles/0` = its value
  2. posting `/title` = the full title
- Step 3 (no location):
  1. résumé `/targets/roles/i` = the term
  2. posting `/title` = the same term
  3. posting `/location/name` = its full value, only if it has at least one token
- Step 4 (relevant):
  1. résumé `/targets/roles/i` = the term
  2. posting `/title` = the same term
  3. résumé `/targets/locations/j` = the term
  4. posting `/location/name` = the same term

**Worked example** (Stripe posting 8197886, from `evidence/manual/stripe_20261030T000804Z.raw`,
with the persona in `examples/persona_resume.json`).
- Fields read: `/title` = `"Machine Learning Engineer, Link"`, tokens [machine, learning, engineer,
  link]; `/location/name` = `"New York City "` (trailing space as in the raw file), tokens [new,
  york, city].
- Step 1: no `exclude_title_terms` entry (Senior Staff, Principal, Director, Intern, Manager,
  Staff) appears in the title tokens.
- Step 2: `roles/0` "Machine Learning Engineer" = [machine, learning, engineer] appears at the start
  of the title, so i = 0.
- Step 3: `locations/0` "Boston" does not appear; `locations/1` "New York" = [new, york] does, so
  j = 1.
- Verdict: `relevant`. Citations, in order:
  1. `{"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"}`
  2. `{"source": "posting", "path": "/title", "value": "Machine Learning Engineer"}`
  3. `{"source": "resume", "path": "/targets/locations/1", "value": "New York"}`
  4. `{"source": "posting", "path": "/location/name", "value": "New York"}`

## Wrong versions
1. Verdicts paired with the wrong posting after a sort or dedupe. When every new posting gets the
   same verdict, or there is only one new posting, wrongly paired output looks identical to correct
   output. It only shows when two new postings get different verdicts and their order changes.
   Caught by `test_ac09_shuffle_keeps_each_verdict_with_its_posting`.
2. A justification that cites nothing, or cites a path or value not in the document. The verdict
   word can still be right, and the reason text reads as plausible. Empty citations, or citations
   to a field that isn't there, go unnoticed unless something checks them. Caught by
   `test_ac10_uncited_or_miscited_verdict_is_rejected`.

## What a failure looks like
2026-10-29: A failure is any run that reports as new a posting id already in the state file, misses
one that wasn't, or shows a verdict whose citations don't resolve to that posting and the résumé.

## Amendments
- 2026-10-29 A1 (Run labels): a run with no state file is `baseline` even when its body comes from `--from-file`; a run with state and `--from-file` is `seeded`. `report.json` and the `report.txt` header always show `source` (network or file), and for a file also its path and sha256. Why: Run labels did not say which label wins when both apply, and the report did not say where its body came from.
- 2026-10-29 A2 (Out): records are exactly the postings counted in `new`, so `skipped_bad_title` postings get no record. Why: this reconciles Out's record sentence with the `counts` definitions.
- 2026-10-29 A3 (Out › Citations, `content_text`): `html.unescape`, then strip tags, then `html.unescape` again, then whitespace normalisation, then truncation to 6000 characters. Why: Greenhouse content is escaped HTML, so one unescape leaves entities such as `&nbsp;` in the text the judge is sent and citations resolve against.
- 2026-10-29 A4 (Order of operations): when a run stops at step 6, 7 or 9, no report is written; the manifest, and the raw file if one exists, stay as evidence. Why: the contract did not say what a stopped run leaves behind.
- 2026-10-29 A5 (Out, manifest.json): a network failure with no response writes a manifest with null `raw_path`, `sha256` and `byte_length`, plus an `error` field. Why: the contract did not say what is recorded when there is no response at all.
- 2026-10-29 A6 (Interfaces, Judge defaults; Out, files written): the judge client uses an SDK timeout of 60 s and `max_retries` 0, and each call also writes `claude/<id>.response.meta.json`. Why: "no retries" needed a stated client setting, and the response's id, model and stop_reason were not saved anywhere.
- 2026-10-30 A7 (Interfaces, sample and experiment): `experiment` also takes `--run RUN_DIR`. Postings are read from that run's saved raw response, never fetched. Same for `sample`. Why: the experiment and the sampling must judge exactly the postings that were labelled, from the run 1 response they were chosen from.
- 2026-10-30 A8 (Interfaces, output locations): `sample` writes `evidence/sampling/<UTC stamp>/`. `experiment` writes `evidence/experiments/<set>/<prompt sha256[:12]>/`. Each call saves request.json, response.txt, response.meta.json and the validator result, exactly like `run`, and each directory gets a `results.json` summary. `held-out` refuses if its target directory already exists, or if `prompts/` has uncommitted changes (`git status --porcelain`). Why: Interfaces did not say where these subcommands write, and "results already exist" needed a checkable definition.
- 2026-10-30 A9 (Interfaces, replay): for a run made before A1, if the saved report.json has no source fields, `replay` takes source from manifest.json, compares every other field, and prints one line saying the A1 fields were not compared. Why: run 1 was produced by the code before A1, and its report has no source fields.
- 2026-10-30 A10 (Interfaces, experiment): `--prompt-b` is optional on `--set development`; without it, only `--prompt-a` is run and scored. `held-out` requires both, with different sha256s. Why: v2 is written only after reading v1's development failures, so v1 must be runnable alone.
- 2026-10-30 A11 (Interfaces, experiment): on `development`, a prompt whose target directory already exists is not called again; its saved responses are re-validated and re-scored, and its results.json is rewritten (keeping `created_at`, adding `rescored_at`). It is refused if that results.json was made from a different run, résumé, model or set. Why: running v1 against v2 after v1 has run would otherwise either fail or re-run v1 on new samples.
- 2026-10-30 A12 (Interfaces, experiment): an `error` judgment (an API failure) is counted separately from `rejected`, so the counts are accepted-and-correct, accepted-and-wrong, rejected and error. Pass rate is accepted-and-correct / n either way. Why: an API failure is not a validator rejection.
- 2026-10-30 A13 (Interfaces, sample): once labels/split.json exists, `sample` refuses any `--posting-id` in `held_out`, before any call. Why: no Claude call is made on a held-out posting until the final held-out run (labels/LABELING_RULE.md).
- 2026-10-30 A14 (In › Network; Interfaces): In (Network) and Interfaces now allow a judge via the local Claude Code CLI subprocess. `run`, `sample` and `experiment` take `--judge sdk|claude-cli` (default `sdk`). Each claude-cli call runs `claude -p --output-format json --system-prompt <System section> --tools "" --strict-mcp-config --safe-mode --disable-slash-commands --no-session-persistence --model <model>` with the filled User section on stdin, from a new empty temporary directory, with ANTHROPIC_API_KEY removed from its environment and a 120 s timeout. It saves request.json, the raw stdout as response.txt, response.meta.json (CLI version, the models the JSON reports, session id, usage, exit code, error) and, in sample and experiment, the validator result. A non-zero exit, a timeout or a usage-limit message gives status `error` with reason `cli_<kind>` (`cli_nonzero_exit`, `cli_timeout`, `cli_usage_limit`, `cli_error_result`, `cli_bad_output`, `cli_exec_failed`); it is never retried, and the command makes no further calls. In `run`, later new postings get `not_run` with reason `judge_stopped`, the report and state are written as usual, and the exit code is 1. In `sample` and `experiment`, results.json is written with `"complete": false` and the exit code is 1; rerunning the same `experiment` calls only the postings with no saved response, on development and held-out alike, so no held-out posting gets two responses. `held-out` refuses once every target is complete, or if an existing target was run with a different pair of prompts (this replaces A8's "refuses if its target directory already exists"). `not_run` means no backend is available: `no_api_key` (sdk) or `claude_cli_not_found` (claude-cli). The manifest records `judge_backend`, and the report's `judge` block records `backend`. Why: there is no API key; the CLI uses my subscription. Limits: the temperature isn't controllable (nor is max_tokens), and the CLI is an agent wrapped around the model, constrained here by a replaced system prompt, no tools and an empty working directory.
- 2026-10-30 A15 (Interfaces, experiment; corrects A14): on `held-out`, a resume sends only the postings that have no saved call (no `claude/<id>.request.json`). A posting whose call was saved, including one that ended in `error`, is never sent again under the same prompt sha256; its saved judgment is scored as it is (an error counts as `error`, A12), and a saved request with no recoverable response counts as `error` with reason `no_saved_response`. On `development`, a resume still re-sends postings whose saved call ended in `error`. Why: A14 let a held-out resume re-send a posting whose call had failed, even one that had already reached the model (a timeout), so a held-out posting could be sent twice under the same prompt.
