# CAPTURE.md: manual curl capture, 2026-11-25

Live capture, not SEEDED. Run by Claude Code (claude-opus-5-5) in Deepak's session on 2026-11-25 at 13:23 ET (18:23 UTC), before any JS3 code existed. Raw files committed in 3fe5a78 before this file was written.

- Folder: `evidence/manual-capture/20261125T182322Z/`
- Method: `curl -sS --proto '=https' --max-redirs 0 --max-time 30 -X GET -D <name>.headers.txt -o <name>.body <url>`, one GET per URL, at least 2 s apart, in the order below.
- Per-request log: `20261125T182322Z/curl_log.tsv` (start time UTC, HTTP code, content-type, bytes, curl exit code).
- sha256 of every body and header file: `20261125T182322Z/SHA256SUMS`.
- Posting count: the length of the top-level JSON list (Lever) or of the `jobs` list (Greenhouse, Ashby).
- Counting was done by a throwaway script run with `python3 -I` from the session scratchpad, outside this folder (no .py file exists in this folder before Gate 1). Its definitions are stated with each count below.

## Per URL

| # | URL | HTTP status | content-type | bytes | posting count | sha256 (body) |
|---|---|---|---|---|---|---|
| 01 | https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true | 200 | application/json | 6082469 | 771 | 3858ca0b8dd76aa14fca02f812368d428bb9070f83fd3ebed659f02ce48ad76e |
| 02 | https://api.eu.lever.co/v0/postings/lever?mode=json | 200 | application/json; charset=utf-8 | 111100 | 6 | 5179dcd2ca0165aeabc34f43670a1403874c19448e09d70fd7d281a6de3a4b92 |
| 03 | https://api.lever.co/v0/postings/palantir?mode=json | 200 | application/json; charset=utf-8 | 5923310 | 305 | c6fd3b3e9246a72b2ca348c347392090b7f270de7867b4d09c3e2dc388b2b4cf |
| 04 | https://api.ashbyhq.com/posting-api/job-board/linear | 200 | application/json; charset=utf-8 | 418959 | 30 | ffbe5745fc0c4a3e1e3105ffba661f7739590d711034b53907e94832bd03851b |
| 05 | https://api.ashbyhq.com/posting-api/job-board/notion | 200 | application/json; charset=utf-8 | 3181419 | 172 | f91029327049d7a44734e6065c1bd1e0280bfe70a11d630396359ade0ba3bf17 |

The sha256 column is copied from `20261125T182322Z/SHA256SUMS`, which also holds the header files' hashes.

All five curl exit codes were 0 and no response was a 3xx (`curl_log.tsv`). Every posting id within a body is unique (771, 6, 305, 30, 172 distinct ids). Rows 04 and 05 carried `cf-cache-status: HIT` with `age: 57` and `age: 55`.

Total postings across the five bodies: 1284.

## Keys of one posting object, exactly as they appear (the first posting in each body)

Every posting in a body has the same key set as its first posting (checked over all postings).

- 01 Greenhouse stripe (top level: `jobs`, `meta`): `absolute_url`, `data_compliance`, `education`, `internal_job_id`, `location`, `metadata`, `id`, `updated_at`, `requisition_id`, `title`, `company_name`, `first_published`, `language`, `application_deadline`, `content`, `departments`, `offices`, `ai_disclaimer`, `include_ai_disclaimer`, `ai_opt_out_request_url`
- 02 and 03 Lever (top level: a list): `additionalPlain`, `additional`, `categories`, `createdAt`, `descriptionPlain`, `description`, `id`, `lists`, `text`, `country`, `workplaceType`, `opening`, `openingPlain`, `descriptionBody`, `descriptionBodyPlain`, `hostedUrl`, `applyUrl`. `categories` keys over all postings: 02 has `commitment`, `department`, `location`, `team`, `allLocations` in 6/6 and `level` in 1/6; 03 has `commitment`, `location`, `team`, `allLocations` in 305/305.
- 04 and 05 Ashby (top level: `jobs`, `apiVersion`): `id`, `title`, `department`, `team`, `employmentType`, `location`, `secondaryLocations`, `publishedAt`, `isListed`, `isRemote`, `workplaceType`, `address`, `jobUrl`, `applyUrl`, `descriptionHtml`, `descriptionPlain`

## Which fields hold the title, description text and location

| System | Title | Description text | Location |
|---|---|---|---|
| Greenhouse (with `?content=true`) | `title` | `content`: HTML, escaped (the first posting's value starts `&lt;h2&gt;`) | `location.name` (a string inside an object); `offices` is a separate list |
| Lever | `text` | split across fields: `description` (HTML) and `descriptionPlain`; `opening`/`openingPlain` and `descriptionBody`/`descriptionBodyPlain`; `lists` (a list of `{"text", "content"}`, `content` is HTML `<li>` items); `additional` (HTML) and `additionalPlain` | `categories.location` (a string); also `categories.allLocations` (a list), `country`, `workplaceType` |
| Ashby | `title` | `descriptionHtml` (HTML) and `descriptionPlain` | `location` (a string); also `secondaryLocations` (a list), `address`, `isRemote`, `workplaceType` |

Facts about the Lever split, from the bodies:
- `description` equals the exact string `opening + descriptionBody` in 4 of 6 postings (02) and 1 of 305 (03).
- Of postings with non-empty `lists` content, the normalized `lists[].content` text was all found inside the normalized `description` in 0 of 6 (02) and 0 of 302 (03).
- The normalized `additional` text was found inside the normalized `description` in 0 of 6 (02) and 0 of 305 (03).

So in these captures, `description` alone does not contain the Lever requirement lists or the `additional` text.

## Non-empty description and location counts

Definitions: "non-empty string" = a JSON string with at least one non-whitespace character. "Normalized" = the JS1 `content_text` steps at JS2 b2ac533 (`jobwatch/postings.py:25-34`: `html.unescape`, tags replaced by a space, `html.unescape`, whitespace collapsed) without the 6000-character truncation. "Token" = the JS1 tokenization (`jobwatch/textmatch.py:10-20` at b2ac533: lowercase, maximal runs of `str.isalnum()` characters or `+#`).

| Body | Field | Non-empty string | ≥1 token after normalization | Normalized length > 6000 chars |
|---|---|---|---|---|
| 01 stripe | `content` | 771/771 | 771/771 | 90/771 |
| 02 lever EU | `description` | 6/6 | 6/6 | 0/6 |
| 02 lever EU | `descriptionPlain` | 6/6 | 6/6 | 0/6 |
| 02 lever EU | `opening` | 0/6 | 0/6 | 0/6 |
| 02 lever EU | `descriptionBody` | 6/6 | 6/6 | 0/6 |
| 02 lever EU | `lists` (non-empty list) | 6/6 | | |
| 02 lever EU | `additional` | 6/6 | 6/6 | 0/6 |
| 03 palantir | `description` | 305/305 | 305/305 | 1/305 |
| 03 palantir | `descriptionPlain` | 305/305 | 305/305 | 1/305 |
| 03 palantir | `opening` | 299/305 | 299/305 | 0/305 |
| 03 palantir | `descriptionBody` | 293/305 | 293/305 | 1/305 |
| 03 palantir | `descriptionBodyPlain` | 289/305 | 289/305 | 1/305 |
| 03 palantir | `lists` (non-empty list) | 302/305 | | |
| 03 palantir | `additional` | 305/305 | 305/305 | 3/305 |
| 04 linear | `descriptionHtml` | 30/30 | 30/30 | 0/30 |
| 04 linear | `descriptionPlain` | 30/30 | 30/30 | 1/30 |
| 05 notion | `descriptionHtml` | 172/172 | 172/172 | 147/172 |
| 05 notion | `descriptionPlain` | 172/172 | 172/172 | 156/172 |

JS1 `content_text` truncates to 6000 characters (`jobwatch/postings.py:10,34` at b2ac533). The last column counts the postings that truncation would cut.

| Body | Location field | Non-empty string | ≥1 token | Missing or null |
|---|---|---|---|---|
| 01 stripe | `location.name` | 771/771 | 771/771 | 0/771 |
| 02 lever EU | `categories.location` | 6/6 | 6/6 | 0/6 |
| 03 palantir | `categories.location` | 305/305 | 305/305 | 0/305 |
| 04 linear | `location` | 30/30 | 30/30 | 0/30 |
| 05 notion | `location` | 172/172 | 172/172 | 0/172 |

Other location-related fields: 03 `workplaceType` values are `hybrid`, `onsite`, `remote`; 02 has only `unspecified`. 04 `isRemote` is true in 30/30 and `workplaceType` is `Hybrid` or `Remote`; 05 `isRemote` is true in 99/172 and `workplaceType` is `Hybrid`, `Remote` or null. `secondaryLocations` is non-empty in 7/30 (04) and 45/172 (05). `isListed` is true in every Ashby posting.

## Titles containing at least one broad word

Words: engineer, engineering, scientist, science, data, machine, learning, ml, ai, software, research, researcher, developer, analyst. Matching: whole JS1 tokens of the title field (`title` for Greenhouse and Ashby, `text` for Lever), case-insensitive. No stemming, so "Engineers" does not count as "engineer".

| Body | Titles with ≥1 word | engineer | engineering | scientist | science | data | machine | learning | ml | ai | software | research | researcher | developer | analyst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 stripe | 240/771 | 152 | 30 | 6 | 1 | 23 | 12 | 12 | 1 | 25 | 56 | 1 | 0 | 7 | 26 |
| 02 lever EU | 3/6 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 03 palantir | 208/305 | 184 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 7 | 138 | 0 | 0 | 6 | 20 |
| 04 linear | 9/30 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 2 | 0 |
| 05 notion | 37/172 | 29 | 4 | 0 | 0 | 2 | 0 | 0 | 0 | 5 | 19 | 0 | 1 | 2 | 2 |
| All five | 497/1284 | | | | | | | | | | | | | | |

The per-word columns count titles containing that word; a title can count under several words, so a row's per-word counts can sum to more than its first column.

## Compared with the JS2 capture of 2026-11-10 (`js2-loop-tools-diff/evidence/manual-capture/CAPTURE.md` at b2ac533)

Posting counts then and now: stripe 776 then (without `?content=true`), 771 now (with it); lever EU 6 and 6; palantir 304 and 305; linear 33 and 30; notion 152 and 172.
