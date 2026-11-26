# TOOL-SERVER.md — my agent as a tool, and two evaluations

## 1. The server

`js3/mcp_server.py` speaks the Model Context Protocol from scratch: JSON-RPC 2.0, one JSON message per line on stdin and stdout. It uses the Python standard library only (no MCP SDK). It answers `initialize`, `ping`, `tools/list` and `tools/call`, ignores notifications such as `notifications/initialized`, and returns JSON-RPC errors for everything else.

**The one capability:** `score_posting(posting_id)`. It runs FILTER.md v1 on one posting saved from the 2026-11-10 run and returns:
- the score out of 5 and the rules that failed;
- each claim, labeled supported / contradicted / insufficient with the quote that decides it;
- the answer ("fits by the evidence rules", "does not fit" or "I cannot tell").

How to start it (a client does this; `mcp.json` is the configuration Claude Code used):

```bash
python3 -m js3.mcp_server     # from this folder; the client talks to it over stdin/stdout
```

## 2. The real transcript

**Session 1, 2026-11-25 15:52 UTC.** The client was **Claude Code 2.1.283**. Its usage record lists `claude-opus-5-5` and also `claude-haiku-4-5-20251001`, which Claude Code uses for small steps of its own; I did not check which model wrote which part. It was started like this:

```bash
claude -p "<the prompt below>" --mcp-config mcp.json --strict-mcp-config --tools "" \
  --allowedTools "mcp__js3__score_posting" --no-session-persistence --output-format json
```

The options mean:
- `--strict-mcp-config`: only this server, none of my other MCP servers;
- `--tools ""`: no built-in tools;
- `--allowedTools`: only this one tool may run without asking.

- **Both directions, as the server saw them:** [transcripts/claude-code-session-1.server.jsonl](transcripts/claude-code-session-1.server.jsonl). That is 9 lines, each with a time, a direction and the exact message.
- **Claude's side:** [transcripts/claude-code-session-1.client-output.json](transcripts/claude-code-session-1.client-output.json). It holds Claude Code's final reply, the model, the 3 turns and the $0.07 cost.

What happened, message by message:

| # | Direction | Message |
|---|---|---|
| 1 | client → server | `initialize`, asking for protocol `2025-11-25`. The client declares `roots` and `elicitation`, and `clientInfo` says `claude-code` 2.1.283 |
| 2 | server → client | agrees to `2025-11-25`; capabilities `tools` only; `serverInfo` `js3-job-filter` 1.0.0 |
| 3 | client → server | `notifications/initialized` (no reply, as the protocol says) |
| 4–5 | client → server → client | `tools/list` → one tool, `score_posting`, with its schema and hints |
| 6–7 | client → server → client | `tools/call` for `lever/palantir/ab7e3425-…` → score 5, outcome `keep`, 9 claims, answer "I cannot tell" (no years stated) |
| 8–9 | client → server → client | `tools/call` for `does-not-exist` → `isError: true`, "No saved posting has the id 'does-not-exist'." |

The prompt was: *"You have one tool, score_posting, from a server named js3. Call it for posting_id lever/palantir/ab7e3425-81d5-4705-a7b5-cd60c8a45cdb, then call it once more for posting_id does-not-exist. Then answer in at most 5 sentences: does the first posting fit, according to the tool, and which claims did the tool label insufficient? Quote the tool; do not add your own judgment of fit."*

**Claude's reply (received 2026-11-25, as returned, not edited):**

> 1. The tool doesn't say this posting fits: its answer is **"I cannot tell"**, and the only reason it gives is "no evidence: It asks for 3 years or fewer".
> 2. That answer doesn't match the rest of the tool's output for the same posting, which shows `"score": 5`, `"outcome": "keep"` and `"failed_rules": []`.
> 3. The tool labeled five claims insufficient, starting with C2 "It is open to an early-career engineer" ("no early-career wording and no years phrase") and C4 "It asks for 3 years or fewer" ("no years phrase anywhere: nothing shows that 29 months is enough").
> 4. The other three are C5 claims, "It asks for Kafka", "It asks for Kubernetes" and "It asks for Docker", each with the reason "the word appears, but not as something the job asks for", yet all three are still listed in `skills_matched`.
> 5. The second call returned an error instead of a score: "No saved posting has the id 'does-not-exist'."

## 3. Evaluating my own server as if someone else wrote it

**Declared versus actual:**

| What it declares | What it actually does | Gap? |
|---|---|---|
| "Read-only" (description, and the `readOnlyHint: true` annotation) | Reads `data/` and `persona/`. It also **writes** one file per session: its transcript in `transcripts/`. | **Yes, a small one.** It never changes the postings, but "read-only" is not literally true. The transcript stays inside my folder. |
| `openWorldHint: false`, meaning nothing outside | No network code at all. `tests/test_claims_and_server.py::test_the_server_writes_nothing_but_its_transcript` checks that the source has no `urllib`, `socket`, `subprocess`, `requests` or `http.client`, and exactly one `open(`. | No |
| Input `{posting_id: string, max 200}`, no other fields | The server checks this itself and refuses anything else with JSON-RPC error −32602, whatever the client sent (`test_extra_or_wrong_arguments_are_refused`) | No |
| It returns "the answer ('fits', 'does not fit' or 'I cannot tell')" | It returns **two** verdicts that can disagree: `outcome` (the keyword filter: `keep`) and `answer` (the evidence rules: "I cannot tell"). Nothing in the output says which one counts. | **Yes.** In session 1, Claude read them as a contradiction ("That answer doesn't match the rest of the tool's output"). |
| The claims are "labeled … with the quote that decides it" | They are labeled by fixed word patterns (FILTER.md section 2), not by understanding. "*3+ years*" is quoted as **support** for "asks for 3 years or fewer", although 3+ years is more than his 29 months (SHORTLIST.md, job 5). "*such as Java, C++, Python, Rust, or similar*" is quoted as support for "asks for Python", although Python is only one option. | **Yes.** The quotes make the labels look more certain than they are. |
| Protocol versions | It agrees to the client's version if it knows it, otherwise offers `2025-11-25`. It ignores the client's `roots`, `elicitation` and `progressToken`. | No: these are optional |

**What a compatible client is not entitled to assume:**
1. **That the hints are true.** `readOnlyHint` and `openWorldHint` are the server's own claims. The protocol does not enforce them, and here "read-only" is not even literally true.
2. **That `answer` is a fact about the job.** It is the output of my rules, on a snapshot from 2026-11-10. Postings may have closed since.
3. **That quoted posting text is safe to obey.** Quotes are third-party text from job boards. A client must treat them as data, never as instructions.
4. **That it can reach anything else.** The server gives no file paths, makes no fetches, and has no other tools, whatever a client asks for (`test_a_tool_it_does_not_offer_is_an_error`).

**My trust decision:**
- **Trusted** for read-only scoring of my saved postings, run by Claude without asking each time, because:
  - it has one tool;
  - it has no network code and writes nothing outside its own transcript;
  - it checks its own input;
  - it has tests;
  - I can read all ~150 lines.
- **Not trusted** to decide whether a posting is worth my time. Its "fits" can be wrong in exactly the ways above.
- **Fix noted, not made:** the description should say that `outcome` is the keyword filter and `answer` is the evidence check. It is not changed in v1, because the tool list is one of the objects in the one-change-at-a-time measurements, and changing it now would mix two changes.

## 4. Evaluating a server someone else wrote: the reference `fetch` server

**Source:** the Model Context Protocol project's reference server `fetch`, at [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/97ed9ec74f370222d4ceec50380d06dff36ac4e5/src/fetch). It was read at commit `97ed9ec74f370222d4ceec50380d06dff36ac4e5` (2026-11-18, "chore: stamp Python CalVer versions for 2026.11.18"), downloaded on 2026-11-25.

| File | SHA-256 |
|---|---|
| `src/fetch/src/mcp_server_fetch/server.py` (1,178 lines) | `dc6de86f…` |
| `src/fetch/README.md` | `028743a4…` |

It is not copied into this folder.

**How it was evaluated:** by **reading** its source. It was **not run**: it needs packages I do not have, and running it would mean letting it fetch from the internet. A separate Claude reviewer read `server.py`, the README and `pyproject.toml` and reported with line numbers. I then **checked these lines myself** against the file:
- the tool description (`server.py:945-949`);
- the four hints (`server.py:1019-1030`);
- that a host that cannot be resolved is let through (`server.py:192-203`);
- the README's CAUTION box (`README.md:10-14`);
- the truncation note (`server.py:1100-1106`);
- the six helper modules it imports but I did not download (`server.py:51-61`).

Other line references below come from the reviewer and are marked *(reviewer)*.

**Declared versus actual:**

| What it declares | What the code does | Gap? |
|---|---|---|
| **Tool description:** *"Fetches a URL from the internet … Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access."* (`server.py:945-949`, checked) | Fetches with GET. It refuses non-public addresses by default and obeys robots.txt for the tool, and it has a size cap and a host allow-list option. | **Yes.** The description promises internet access and **tells the model to change its earlier behavior**. It mentions none of the refusals, so a model is not told when or why a fetch will be refused. |
| **Hints:** `read_only_hint=True`, `destructive_hint=False`, `idempotent_hint=True`, `open_world_hint=True` (`server.py:1024-1029`, checked) | A GET to an arbitrary URL can trigger actions on the remote site, and the page can change between calls. | **Yes, in part.** "Idempotent" and "read-only" are claims about other people's websites, which the server cannot know. `open_world_hint=True` is honest. |
| **README CAUTION:** *"This server can access local/internal IP addresses and may represent a security risk"* (`README.md:12`, checked) | The next paragraph and the code refuse private, loopback, link-local and metadata addresses by default, on every redirect hop. | **Contradictory**, but the warning is still true in three cases: with `--allow-private-ips`, behind a proxy, and for a hostname the server cannot resolve, which is let through unchecked (`server.py:200-203`, checked). |
| **`max_length`:** "Maximum number of characters to return" *(reviewer: `server.py:1040`)* | A prefix and a truncation note are added around the page text (`server.py:1105-1106`, checked). The reviewer also reports that a robots.txt refusal can repeat up to 5 MiB of robots.txt in the error. | **Yes:** the result can be longer than `max_length`. |
| **Errors** come back as `isError` results *(reviewer)* | Some problems come back as ordinary text inside `<error>…</error>` tags, e.g. "Content truncated" (`server.py:1105`, checked). A page can contain the same tags. | **Yes:** `isError: false` does not mean the fetch worked, and the server's tags cannot be told apart from page text. |
| **Size:** a 5 MiB body cap (README) | Enforced, by Content-Length and while streaming *(reviewer: `server.py:576-609`)* | No |

**What a compatible client is not entitled to assume about it:**
1. **That the hints are true or enforced.** The server says them about itself.
2. **That the result is the page.** It is an extraction, possibly negotiated as markdown, with hidden text possibly revealed *(reviewer)*.
3. **That the text is free of prompt injection.** Page text, untrusted robots.txt text and the server's own instructions to the assistant arrive in one string *(reviewer)*.
4. **That a guard was applied.** robots.txt and the private-address guard depend on server flags. The prompt (as opposed to the tool) skips robots.txt *(reviewer)*.
5. **That only the requested host was contacted.** Each redirect hop's robots.txt is fetched too *(reviewer)*. The README says npm packages may be installed on first use, and that code is in a module I did not read.
6. **That I know everything it does.** Six helper modules (`allowlist`, `pinning`, `readability_js`, `timeout`, `title`, `transport`) were not part of what I read (`server.py:51-61`, checked). The connection-time pinning that the README's DNS-rebinding claim depends on lives in one of them.

**My trust decision:** **not for my agent.**
- My permission policy (JS2 `GATE.md` section 5) allows exactly three job-board hosts, GET only. This server's whole purpose is an open world. Even with its host allow-list option, the description it sends to the model tells the model it now has internet access.
- I would use it only by hand, in a separate session, with `--allowed-hosts` set and Claude Code asking me before each call. Never under `--allowedTools` as an automatic tool.
- Compared with my own server, its code is far more careful about networks (the address guard, redirect re-checks, size caps). But it does far more, and more of it happens in code I did not read.
