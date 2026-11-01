# Chapter 3: Action-surface comparison

**Task.** The same task done three ways with real `claude -p` sessions: (a) the posting pasted into the conversation on stdin with no tools; (b) the posting and résumé payload given as files Claude may read; (c) an agent that fetches the board itself and writes its own state file.

**What ran.** 2026-10-30 03:11–03:13 ET at clean commit `7188965`, recorded in `8fea85b`. Each surface ran once in its own sandbox directory under `data/experiments/surfaces/<a|b|c>/sandbox/`.

```bash
uv run jsa exp surfaces prepare
uv run jsa exp surfaces run a
uv run jsa exp surfaces run b
uv run jsa exp surfaces run c
uv run jsa exp surfaces capture
```

**Raw evidence.** Per surface in `data/experiments/surfaces/<a|b|c>/`: the exact argv and working directory (`run.json`), the prompt (`prompt.txt`), the full Claude Code transcript (`transcript.jsonl`), observed tool use and cost (`observed.json`), and the sandbox tree before and after (`before.tree.json`, `after.tree.json`, `diff.json`). For (c), `independent/raw.json` is our own allow-listed fetch used to check the agent's IDs. Absolute paths in the transcripts were replaced with `<repo>`; `REDACTIONS.json` records the SHA-256 of each file before and after. Generated table: `data/experiments/surfaces/ACTION_SURFACES.tables.md`.

## Results

| Surface | Can read | Can write | Can send | Authority granted | Authority observed | What could go wrong |
|---|---|---|---|---|---|---|
| (a) | nothing | nothing | nothing | tools: none | reads 0, writes 0, sends 0, denials 0 | Untrusted text in POSTING.content can attempt prompt injection to skew the label or summary, emit invalid JSON or nonexistent paths, or echo résumé values into free text (mitigated by keeping the deterministic rule separate, validating §8 schema/paths, and scanning for RESUME_VALUE_ECHO); also, the claude CLI's own connection to Anthropic's model host is outside our Python AllowListTransport (CONTRACT.md §11). |
| (b) | ./posting.json, ./resume.payload.json | nothing | nothing | tools: Read | reads 2, writes 0, sends 0, denials 0 | All risks of (a), plus file-read scoping relies on Claude Code's user-space flag rules (--restricted and Read(./...)) rather than an OS sandbox—a path/glob misconfiguration or symlink could expose adjacent files (state.json or unprojected résumé data)—while adding extra tool-call turns and cost ($0.0301 vs. $0.0234 in (a)) to read payloads the caller already has in memory. |
| (c) | ./state.json | ./state.json | boards-api.greenhouse.io (WebFetch) | tools: WebFetch, Read, Edit, Write | reads 1, writes 1, sends 5, denials 0 | Capability is not reliability or authorization: WebFetch truncated the Greenhouse response and routed 5 chunked fetches (sends 5, $0.1311) through a summarizing model that cut off one job mid-entry (making its ID invisible) and forced Claude to diff 700+ IDs against seen_ids "by eye" before editing state.json. This risks silent ID drops, invented IDs, non-atomic state corruption, loss of byte-for-byte raw SHA-256 evidence, and unmonitored outbound fetches inside WebFetch. |

Repository unchanged after the runs: (a) True, (b) True, (c) True.

## Least autonomy that suffices

**Choice: Surface `(a)` — chat on stdin with `--tools ""` (zero file-read, file-write, or network-fetch tools), running in a fresh empty working directory (`data/tmp/claude-<uuid>/`) with only the projected résumé and single-posting payloads passed on stdin.**

### Defense of Surface `(a)` over `(b)` and `(c)`

1. **Deterministic code should own I/O, state, and exact set math; the model should only judge text:** Under `CONTRACT.md`, fetching the Stripe Greenhouse endpoint over an allow-listed HTTPS client (`http.AllowListTransport`), saving the exact raw bytes and SHA-256 (`.meta.json`), parsing and deduplicating `seen_ids`, evaluating the four-gate deterministic rule, validating reply schema/paths/privacy (`§8` and `R10`), and atomically updating `state.json` via `os.replace` are exact, reproducible operations. None of them benefits from LLM autonomy. The only task that requires a language model is producing the separate qualitative opinion (`RELEVANT` / `NOT_RELEVANT`, `summary`, `evidence`, `uncertainties`) on one already-fetched posting.
2. **Why Surface `(b)` adds authority and cost for zero benefit:** In `(b)`, the Python caller already holds `posting_payload` and `resume_payload` in memory, writes them to `./posting.json` and `./resume.payload.json`, and grants `--tools Read` so the model can spend two extra tool calls reading them back (`reads 2`, `$0.0301` vs. `$0.0234` in `(a)`). That widens the authority surface from "no tools at all" (`--tools ""`) to user-space path-rule enforcement (`--restricted` and `--allowedTools "Read(./...)"`) without giving the model any information it did not already receive on stdin in `(a)`.
3. **Why Surface `(c)` fails the reliability and auditability requirements of `CONTRACT.md §§9–11`, even when its ID list happens to match:** In our recorded run of `(c)` (`data/experiments/surfaces/c/observed.json`), the 6 new IDs the agent wrote (`8316059`, `8330791`, `8330801`, `8330813`, `8330815`, `8336023`) matched our independent allow-listed fetch (`missing: 0, extra: 0, malformed: 0`). However, the transcript and the agent's own reply expose why `(c)` is unsafe:
   - **Lossy summarization and truncation inside `WebFetch`:** Because the Greenhouse JSON was too large for a single `WebFetch`, the agent made **5 separate `WebFetch` calls** (`sends 5`, costing `$0.1311`—nearly 5.6× the `$0.0234` cost of `(a)`) and received outputs from a summarizing model rather than a raw JSON parser. As the agent itself reported: *"The IDs in each chunk came from a summarizing model, not a raw parse. I compared them by eye against `seen_ids`, so I may have missed an ID. The last job in one chunk was cut off mid-entry and its ID wasn't visible."*
   - **Loss of atomic state guarantees and byte-for-byte evidence:** Letting the agent mutate `./state.json` via `Edit` bypasses `OutputRoot.write_json_atomic` and never saves the byte-for-byte raw API response with its SHA-256 metadata.
   - **Brittle user-space permission rules and unmonitored network paths:** As Plan Amendment `R2` records (`Write(./state.json)` permission rules never matched in Claude Code, requiring `Edit(./state.json)` while keeping `Write` in `--tools`), tool-permission syntax is a user-space CLI convention rather than an OS boundary, and `WebFetch`'s internal network requests cannot be constrained by our Python `AllowListTransport`.

Surface `(a)` (`--tools ""`) grants the minimum authority needed to produce `model_judgment` (`reads 0, writes 0, sends 0`), while Python owns all network, filesystem, and state invariants.
