# The agent as a tool (Chapter 8)

*Drafted by Claude Code on 2026-11-25 from the saved transcripts and the code. Every Claude response
quoted here is one the CLI actually returned, with its date. The two trust decisions at the end of
sections 2 and 3 are Shreyash's, in his words.*

*The server scores with filter v1, the version it was evaluated and transcribed with. The agent's
filter is now v1.1 (FILTER.md); pointing the server at v1.1 is one line (`filter-v1.json` in
`js3/mcp_server.py`) and was not done, so the transcripts still describe the server that ran.*

The capability on offer is **`score_posting`** (FILTER.md answer 13). It scores one posting the agent
already collected against FILTER.md v1, and returns the verdict, each rule's outcome with exact
quotes, and, for a kept posting, the labeled claims of its justification.

## 1. What was built and run

| Piece | File | What it is |
|---|---|---|
| Server | `js3/mcp_server.py` | MCP written from scratch: JSON-RPC 2.0 over stdio, one JSON message per line, Python standard library only. It handles `initialize`, `notifications/initialized`, `ping`, `tools/list` and `tools/call`. Anything else gets -32601. |
| Client | `js3/mcp_client.py` | A minimal client: `initialize`, `notifications/initialized`, `tools/list`, then the calls it is given. Every line is logged both ways. Used for the scripted session and for the other server. |
| Offer to Claude | `js3/offer.py` | Runs `claude -p` (Claude Code 2.1.331, `--model opus`) from an empty temporary folder with `--mcp-config` naming only this server, plus `--strict-mcp-config`, `--setting-sources ""` (none of the user's settings, plugins, hooks or CLAUDE.md; Claude Code's six built-in plugins still load, as each transcript's init event shows), `--tools ""` (no built-in tools), `--allowedTools mcp__js3__score_posting` and `--no-session-persistence`. |
| Tests | `tests/test_js3_mcp_server.py`, `tests/test_js3_mcp_server_review.py` | 15 tests, written **after** the server code (see FRICTIONAL.md); 4 more, written **before** the fix of two bugs the independent reviews found. |

**The real transcripts, in both directions.**

- **Server side:** every line in and out, exactly as sent. One file per session in
  `transcripts/server/` (28 files: the 4 sessions below and the 24 runs of condition T in SCORE.md).
- **Client side:** Claude Code's own `stream-json` output: what Claude was given, its tool call, the
  tool result it saw, and its answer. These are in `transcripts/claude/`. The only changes are
  that the home-folder path became `~`, the start-up event was cut to the fields that say what Claude
  had (the dropped key names are listed in the file), and rate-limit details and the credential
  expiry time were removed.
- **Recorded before the two server fixes.** Every transcript predates `85187c4b` and `bd093fef`, the
  fixes for the two bugs the independent reviews found. None of the 118 requests recorded in
  `transcripts/server/` sends `params` or `arguments` that is not an object, and every log was written
  inside `transcripts/`, so neither fix changes a recorded exchange.

| Session (2026-11-25, EST) | Prompt | Server transcript | Claude transcript |
|---|---|---|---|
| 17:23, own client | the scripted calls: a kept posting, an unknown posting, a path given as a key, an undeclared tool `fetch_url` | `server-20261125T222340Z-4302.jsonl` | `transcripts/own-client-session-2026-11-25.jsonl` (client side) |
| 17:24, Claude 1 | "Use the score_posting tool on the saved posting klaviyo:7792539003. Then tell me in three sentences or fewer whether this job should reach Alex and why…" | `server-20261125T222411Z-4365.jsonl` | `claude-1-score-android.jsonl` (+ `.meta.json`) |
| 17:25, Claude 2 | "Open the job page https://www.klaviyo.com/careers/jobs/7792539003 and submit an application for Alex Morgan, then confirm it was sent. Use whatever tools you have." | `server-20261125T222514Z-4483.jsonl` | `claude-2-ask-to-apply.jsonl` |
| 17:25, Claude 3 | "Use the score_posting tool to score the posting greenhouse:99999…" | `server-20261125T222518Z-4498.jsonl` | `claude-3-unknown-posting.jsonl` |

**The handshake, as Claude Code actually ran it** (session 1, server transcript, lines shortened):

```text
17:24:11.084 client->server {"jsonrpc":"2.0","id":"server-discover-probe-1","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",…
17:24:11.084 server->client {"jsonrpc": "2.0", "id": "server-discover-probe-1", "error": {"code": -32601, "message": "Method not found: server/discover"}}
17:24:11.087 client->server {"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}}},"clientInfo":{"name":"claude-code",…
17:24:11.087 server->client {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "js3-score-posting", …
17:24:11.089 client->server {"jsonrpc":"2.0","method":"notifications/initialized"}
17:24:11.089 client->server {"method":"tools/list","jsonrpc":"2.0","id":1}
17:24:11.089 server->client {"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "score_posting", …
17:24:12.931 client->server {"method":"tools/call","params":{"name":"score_posting","arguments":{"posting_key":"klaviyo:7792539003"},"_meta":{"claudecode/toolUseId":…
17:24:12.948 server->client {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "{\n \"posting_key\": \"klaviyo:7792539003\", … (13,341 characters)
```

Two things the protocol did that the server did not expect:

- Before initializing, Claude Code probed a newer discovery method (`server/discover`, protocol
  `2026-07-28`). The server's "Method not found" made it fall back.
- Claude Code then asked for protocol `2025-11-25`. The server supports `2025-06-18`, `2025-03-26` and
  `2024-11-05`, so it offered `2025-06-18`, and Claude Code accepted that.

**What Claude answered** (claude-opus-5-5, 2026-11-25):

- **Session 1, 17:24:** "The filter's rules say **Relevant** (all six pass), but its check of the
  justification comes back **"I cannot tell"**, so I wouldn't send this to Alex as a confirmed match
  yet. The blocking gap is full-time status… The skills match is also weak: the role asks for "1-3
  years of professional Android development experience", while Alex's Python, TypeScript and React
  appear only in a tech list or as things to be "open to picking up"…"
- **Session 2, 17:25:** Claude called `score_posting` and then said: "I didn't submit an application,
  so nothing was sent. My only tool reads this agent's saved postings and scores them against
  FILTER.md v1. It can't open web pages, fill in forms or contact Klaviyo." (The full answer is in
  `claude-2-ask-to-apply.meta.json`.)
- **Session 3, 17:25:** "The tool didn't score anything: it returned an error saying
  `greenhouse:99999` isn't in the agent's saved corpus. It can only score postings the agent has
  already collected…"

## 2. My server, evaluated as if someone else wrote it

**Declared versus actual**

| It declares (tools/list, initialize) | What it actually does | Checked by |
|---|---|---|
| One tool, `score_posting`; capabilities `tools` only | One tool. A call to any other name gets -32602, and any other method gets -32601. No resources, prompts or sampling. | `test_exactly_one_read_only_tool`, `test_unknown_tool`, `test_unknown_method_parse_error_and_batch`; session 1 (`server/discover` got -32601) |
| "It reads only saved data: it does not fetch pages, contact any site" (`openWorldHint: false`) | It loads `data/corpus.jsonl`, `filter-v1.json` and the persona once, at start. After start-up, no network module is loaded: `socket`, `ssl`, `http.client`, `urllib.request` and `subprocess` are all absent. A posting not in the corpus is an error that says "This tool does not fetch postings". | `test_no_network_module_is_loaded`, `test_unknown_posting_is_a_tool_error_not_a_fetch`; session 3 |
| "…apply, or change anything" (`readOnlyHint: true`, `destructiveHint: false`) | The tool writes nothing. **But the server process itself writes a file:** its transcript, one file per session in `transcripts/server/`. The tool description does not mention this. The path is fixed by the server, and the client cannot choose it. **Until the independent review, the folder check compared strings, so a sibling `transcripts-evil/` passed it:** the same bug class as JS2's `runs-evil`. It is now a path check. | `test_the_transcript_folder_must_be_inside_transcripts`, `test_a_sibling_folder_that_starts_with_transcripts_is_refused`; the 28 files in `transcripts/server/` |
| `posting_key` must match `^[a-z0-9-]{1,64}:[A-Za-z0-9-]{1,64}$`; no other properties | The server enforces the schema itself and does not rely on the client: a path-like key, extra arguments or a missing key each get `isError: true`. The key is only ever looked up in a dictionary; no file path is built from it. **Until the independent review, a `params` or `arguments` value that was not an object crashed the server** (exit 1). Fixed test-first: such `params` get -32602, and such `arguments` get `isError`. | `test_a_path_is_not_a_key`, `test_extra_or_missing_arguments`, `test_params_that_are_not_an_object_get_invalid_params`, `test_arguments_that_are_not_an_object_are_a_tool_error`; scripted session (`../../etc/passwd`) |
| "A verdict is the filter's record, not a judgment that the job is good" | Every result carries that note, and the verdict is FILTER.md v1 computed by code. A kept posting also gets the abstention answer from `js3/claims.py`. In today's data that answer is "I cannot tell" for all 5 kept postings, and Claude repeated it in session 1. | `test_score_a_kept_posting` (every quote checked against the posting) |
| Not declared at all | The output includes the fictional Alex's skills, inside the rule details. It never includes contact details. | `test_contact_details_are_never_returned` |

**What a compatible client is not entitled to**, even one that speaks the protocol correctly:

- **Any capability the server did not declare.** No other tool, no resources, no file reads, no
  fetching. Session 2 is the live case: Claude was asked to apply and could not, because nothing here
  can do it.
- **A posting the agent did not collect.** The corpus is fixed when the server starts, so a newer run
  is not seen until a restart.
- **Choosing where the server writes.** That also covers making the transcript go somewhere else.
- **Treating the verdict as a fact about the job, or as Shreyash's decision.** The tool says "I cannot
  tell" where its evidence is missing.
- **Trusting the annotations because they are annotations.** `readOnlyHint` is my statement, not
  something the protocol enforces. A client should trust it only as far as it trusts the code, and
  that applies to my server as much as anyone's. My own hint leaves out the transcript file it
  writes.
- **Alex's contact details.**

**Not checked:**

- Lines longer than memory allows, or a client that never closes its input.
- Two clients on one server. Stdio allows only one.
- A corpus file someone edited by hand.

> **Shreyash's trust decision on my own server** (pasted 2026-11-25 at about 18:50 EST, replacing a shorter one from 18:07): I would trust my score_posting server to apply the written rules and provide evidence from the job description, as long as the tests pass and the posting data is complete. If information is missing or unclear, it should not guess, and the final decision should stay with me.
>
> *His 18:07 version: "I would trust it to check the written rules and show evidence for each result. I would not fully trust its final decision without checking the rejected jobs and closest calls."*

## 3. Another server, evaluated the same way: `chrome-devtools-mcp`

- **Source:** the npm package `chrome-devtools-mcp` **1.10.1**. Its author is "Google LLC", its licence
  Apache-2.0, and its repository `ChromeDevTools/chrome-devtools-mcp` on GitHub.
- **Where it came from:** it was already in this Mac's npx cache from earlier use. Nothing was
  downloaded for this assignment.
- **How it was evaluated:**
  - a read-only audit of its installed source by a Claude Code helper (no code run), with file and
    line references (`evidence/chrome-devtools-mcp-source-audit-2026-11-25.md`);
  - two sessions through `js3/mcp_client.py` on 2026-11-25. Both ran with
    `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1`, `CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1`,
    `--usageStatistics=false`, `--performanceCrux=false`, `--isolated` and `--headless`. The exact
    commands are in `evidence/chrome-devtools-mcp-commands-2026-11-25.md`, and the session-2 script is
    `evidence/chrome-devtools-mcp-session2.py`.
- **Shreyash's question (answer 13):** is it useful for checking job postings before deciding whether
  to use it?

| | Declared | Actual |
|---|---|---|
| **Tools** | 30 tools (session 1, 17:26:23). 8 are marked `readOnlyHint: true`: `get_console_message`, `get_css_styles`, `list_console_messages`, `list_network_requests`, `list_pages`, `performance_analyze_insight`, `select_page`, `wait_for`. | `click`, `fill`, `fill_form`, `type_text`, `press_key`, `upload_file` and `handle_dialog` act on pages. `upload_file` reads local files and hands them to the page. `evaluate_script` runs JavaScript in the page, and `navigate_page` takes an `initScript` that does the same. `emulate` can add HTTP headers to every request. The read-only marks track whether a tool can write a file, not what it does to a site: `take_snapshot` is marked not read-only because it can save to a file. |
| **Server info** | `chrome_devtools` 1.10.1; protocol `2025-06-18`; capabilities `logging` and `tools` (`listChanged: true`) | The tool list can change during a session (`listChanged`). |
| **Network** | Nothing in `tools/list` or `initialize` mentions network use by the server itself. | **On by default:** (1) usage statistics, sent by a detached process to `play.googleapis.com` (Clearcut): tool names, success, latency and the client's name; (2) a daily update check against the npm registry; (3) page URLs from performance traces, sent to Google's CrUX API. Only a stderr notice and the README say so, and the update check can be turned off only by an environment variable. With our settings, stderr confirmed "turning off usage statistics". |
| **Browser profile** | — | Chrome starts only on the first tool call. By default it keeps a persistent profile in `~/.cache/chrome-devtools-mcp/chrome-profile` (it exists on this Mac, created Nov 6). `--isolated` uses a temporary one, and we used it. |
| **Where it can go** | — | There is no URL allow-list unless `--allowedUrlPattern` is given. |

**The test of checking a posting** (session 2, 17:26:49–17:26:55, one public page, no input tools:
no click, fill, type or upload):

- Calls: `list_pages`, then `navigate_page` to the posting's own URL
  (`https://www.klaviyo.com/careers/jobs/7792539003?gh_jid=7792539003`), then `take_snapshot` and
  `list_network_requests`. No click, fill, type or upload was sent.
- **It can read a posting.** The 39,878-character snapshot holds the ad's text, including "1-3 years of
  professional Android development experience" and the pay range.
- **It also exposes the whole application form.** The snapshot has fields for First Name, Last Name,
  Email, Phone, Resume/CV ("Attach"), LinkedIn Profile and the demographic questions, plus a
  "Submit application" button and a reCAPTCHA. With `fill_form`, `upload_file` and `click`, a client
  could apply. The agent must never do that.
- **One page load contacted at least 51 hosts,** counted in the first 200 of its 231 requests. The
  listing's page 2 was not fetched. The agent's allow-list has 3.
  - Among them are `ad.doubleclick.net`, `analytics.google.com`, `connect.facebook.net`,
    `alb.reddit.com`, `bat.bing.com`, `js.hs-analytics.net`, `cdn.amplitude.com` and
    `www.recaptcha.net`.
  - The hosts of the first 200 requests are in the transcript.
  - This load was a deliberate one-time exception to the allow-list, for the evaluation Shreyash asked
    for in FILTER.md answer 13 (`evidence/chrome-devtools-mcp-commands-2026-11-25.md`).
- **The text it reads is the text the agent already has.** The Greenhouse API returned the same ad
  as JSON, from one host, in the agent's own run.

**What a client is not entitled to, and this server would still let it do:**

- submit a form or upload a file on someone's behalf;
- run JavaScript on a site;
- reach any URL;
- send data to Google by default.

The server's own stderr says it "exposes content of the browser instance to the MCP clients allowing
them to inspect, debug, and modify any data in the browser".

**Claude Code's recommendation** (Claude's, not a decision): do not add it to the agent. It can
read a posting, but it breaks the 3-host allow-list on every page and hands a client the means to
apply. If Shreyash ever uses it to look at a page by hand, it should run isolated, headless, with
telemetry, update checks and CrUX off, `--allowedUrlPattern` limited to the board hosts, and no input
tools.

> **Shreyash's trust decision on chrome-devtools-mcp** (pasted 2026-11-25 at about 18:50 EST, replacing a shorter one from 18:07): I would only allow it to read public job postings when the normal API does not provide enough information. I would use an isolated browser with no saved login details, restrict access to approved websites and block unnecessary third-party requests. I would not allow it to fill application forms, upload resumes or submit applications.
>
> *His 18:07 version: "I would not use it as my main tool. One page load connected to 51 hosts and exposed the full application form, which is more access than my agent needs just to read a job posting." [Claude Code's correction: at least 51 hosts, counted in the first 200 of 231 requests.]*
