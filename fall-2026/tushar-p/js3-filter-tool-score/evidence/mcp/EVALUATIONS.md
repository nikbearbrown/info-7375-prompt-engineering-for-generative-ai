# Trust decisions by Tushar, 2026-11-24; facts in EVAL-FACTS.md (drafted by Claude Code)

The decisions below are Tushar's. Each point links to the line of [EVAL-FACTS.md](EVAL-FACTS.md) it rests on.
Lines 1-148 of EVAL-FACTS.md describe the servers as first evaluated. Lines 152 onward are the addendum written after the fix.

## a. My server (`tools/mcp_server.py`): trusted, with limits

**Trusted for:** local, read-only scoring of saved postings, with Claude Code as the client and the tool explicitly allow-listed per run.
- Reads are limited to the corpus, FILTER.md and the persona file: [EVAL-FACTS.md](EVAL-FACTS.md) (line 33).
- The only write is the transcript in `evidence/mcp/`: [EVAL-FACTS.md](EVAL-FACTS.md) (line 34).
- No socket or subprocess activity: [EVAL-FACTS.md](EVAL-FACTS.md) (line 35).
- In the recorded runs, approval came from `--allowedTools` in the command, per run: [EVAL-FACTS.md](EVAL-FACTS.md) (line 66).

**Not trusted for:**
- **Auto-approval in other clients.**
  - The description and annotations are not enforced by MCP: [EVAL-FACTS.md](EVAL-FACTS.md) (line 63).
  - The spec asks for a human able to deny tool calls: [EVAL-FACTS.md](EVAL-FACTS.md) (line 66).
- **Treating verdicts as facts about jobs.** They are filter output on text saved 2026-11-22:
  - [EVAL-FACTS.md](EVAL-FACTS.md) (line 64)
  - `isError: false` means only that the rules ran: [EVAL-FACTS.md](EVAL-FACTS.md) (line 65).

**Required fixes before relying on it:**
- **The description must state the persona-file read.** Mismatch 1: [EVAL-FACTS.md](EVAL-FACTS.md) (line 54).
- **The description must state that every call's arguments are logged to `evidence/mcp/`.**
  - Mismatch 2: [EVAL-FACTS.md](EVAL-FACTS.md) (line 55).
  - Arguments are logged verbatim to a committed folder: [EVAL-FACTS.md](EVAL-FACTS.md) (line 67).
- **Declare `readOnlyHint: true` and `openWorldHint: false`.** With no annotations, the spec's defaults say "possibly destructive, open world" (mismatch 6): [EVAL-FACTS.md](EVAL-FACTS.md) (line 59).

Fixes made in the same commit as this file:
- New description: [EVAL-FACTS.md](EVAL-FACTS.md) (line 157).
- Annotations, with `destructiveHint: false` and `idempotentHint: true` added: [EVAL-FACTS.md](EVAL-FACTS.md) (line 158).
- How the annotations treat the transcript log: [EVAL-FACTS.md](EVAL-FACTS.md) (line 160).

**Transcripts:**
- **Pre-fix declaration** (no annotations, original description): `transcript-run-20261125T040140Z-bfa84e.jsonl`, the first run.
- **Fixed declaration:** `transcript-run-20261125T044128Z-5fd246.jsonl`, the second run with the same command. Its `tools/list` equals the fixed declaration: [EVAL-FACTS.md](EVAL-FACTS.md) (line 162).
- Replies: `claude-client-reply-2026-11-24.txt` (pre-fix) and `claude-client-reply-2026-11-24-postfix.txt` (fixed).

## b. Reference filesystem server (`modelcontextprotocol/servers` at commit c799c855): not trusted on my repos

**Not used against the course repo or the APG repo.**
- Six tools write: [EVAL-FACTS.md](EVAL-FACTS.md) (line 105).
- `edit_file` applies by default (`dryRun` is false): [EVAL-FACTS.md](EVAL-FACTS.md) (line 94).
- Hard links bypass its path check: [EVAL-FACTS.md](EVAL-FACTS.md) (line 134).

**If ever used:** only with all four of these restrictions:
- `--read-only`: [EVAL-FACTS.md](EVAL-FACTS.md) (line 125).
- `--confine-roots`: [EVAL-FACTS.md](EVAL-FACTS.md) (line 127).
- A single scratch directory: [EVAL-FACTS.md](EVAL-FACTS.md) (line 114) and [EVAL-FACTS.md](EVAL-FACTS.md) (line 133).
- stdio, never its unauthenticated HTTP transport: [EVAL-FACTS.md](EVAL-FACTS.md) (line 140).

**Reason:** its declarations understate what it can reach.
- Roots can widen access: [EVAL-FACTS.md](EVAL-FACTS.md) (line 133).
- Error messages reveal absolute paths: [EVAL-FACTS.md](EVAL-FACTS.md) (line 139).

2026-11-25: idempotentHint was later removed; see the EVAL-FACTS.md addendum
