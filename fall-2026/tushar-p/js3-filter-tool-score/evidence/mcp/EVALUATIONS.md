# Trust decisions by Tushar, 2026-11-24; facts in EVAL-FACTS.md (drafted by Claude Code)

The decisions below are Tushar's. Each point links to the line of [EVAL-FACTS.md](EVAL-FACTS.md) it rests on.
Lines 1-148 of EVAL-FACTS.md describe the servers as first evaluated. Lines 152 onward are the addendum written after the fix.

## a. My server (`tools/mcp_server.py`): trusted, with limits

**Trusted for:** local, read-only scoring of saved postings, with Claude Code as the client and the tool explicitly allow-listed per run.
- Reads are limited to the corpus, FILTER.md and the persona file: [EVAL-FACTS.md L33](EVAL-FACTS.md?plain=1#L33).
- The only write is the transcript in `evidence/mcp/`: [L34](EVAL-FACTS.md?plain=1#L34).
- No socket or subprocess activity: [L35](EVAL-FACTS.md?plain=1#L35).
- In the recorded runs, approval came from `--allowedTools` in the command, per run: [L66](EVAL-FACTS.md?plain=1#L66).

**Not trusted for:**
- **Auto-approval in other clients.**
  - The description and annotations are not enforced by MCP: [L63](EVAL-FACTS.md?plain=1#L63).
  - The spec asks for a human able to deny tool calls: [L66](EVAL-FACTS.md?plain=1#L66).
- **Treating verdicts as facts about jobs.** They are filter output on text saved 2026-11-22:
  - [L64](EVAL-FACTS.md?plain=1#L64)
  - `isError: false` means only that the rules ran: [L65](EVAL-FACTS.md?plain=1#L65).

**Required fixes before relying on it:**
- **The description must state the persona-file read.** Mismatch 1: [L54](EVAL-FACTS.md?plain=1#L54).
- **The description must state that every call's arguments are logged to `evidence/mcp/`.**
  - Mismatch 2: [L55](EVAL-FACTS.md?plain=1#L55).
  - Arguments are logged verbatim to a committed folder: [L67](EVAL-FACTS.md?plain=1#L67).
- **Declare `readOnlyHint: true` and `openWorldHint: false`.** With no annotations, the spec's defaults say "possibly destructive, open world" (mismatch 6): [L59](EVAL-FACTS.md?plain=1#L59).

Fixes made in the same commit as this file:
- New description: [L157](EVAL-FACTS.md?plain=1#L157).
- Annotations, with `destructiveHint: false` and `idempotentHint: true` added: [L158](EVAL-FACTS.md?plain=1#L158).
- How the annotations treat the transcript log: [L160](EVAL-FACTS.md?plain=1#L160).

**Transcripts:**
- **Pre-fix declaration** (no annotations, original description): `transcript-run-20261125T040140Z-bfa84e.jsonl`, the first run.
- **Fixed declaration:** `transcript-run-20261125T044128Z-5fd246.jsonl`, the second run with the same command. Its `tools/list` equals the fixed declaration: [L162](EVAL-FACTS.md?plain=1#L162).
- Replies: `claude-client-reply-2026-11-24.txt` (pre-fix) and `claude-client-reply-2026-11-24-postfix.txt` (fixed).

## b. Reference filesystem server (`modelcontextprotocol/servers` at commit c799c855): not trusted on my repos

**Not used against the course repo or the APG repo.**
- Six tools write: [L105](EVAL-FACTS.md?plain=1#L105).
- `edit_file` applies by default (`dryRun` is false): [L94](EVAL-FACTS.md?plain=1#L94).
- Hard links bypass its path check: [L134](EVAL-FACTS.md?plain=1#L134).

**If ever used:** only with all four of these restrictions:
- `--read-only`: [L125](EVAL-FACTS.md?plain=1#L125).
- `--confine-roots`: [L127](EVAL-FACTS.md?plain=1#L127).
- A single scratch directory: [L114](EVAL-FACTS.md?plain=1#L114) and [L133](EVAL-FACTS.md?plain=1#L133).
- stdio, never its unauthenticated HTTP transport: [L140](EVAL-FACTS.md?plain=1#L140).

**Reason:** its declarations understate what it can reach.
- Roots can widen access: [L133](EVAL-FACTS.md?plain=1#L133).
- Error messages reveal absolute paths: [L139](EVAL-FACTS.md?plain=1#L139).
