# Job-Search Agent 3: The Filter, the Tool, and the Score

Atharva Hambir · INFO 7375 · Fall 2026 · built with Claude Code (see `SOURCES.md`)

The agent reads a frozen corpus of 4,240 public job postings and decides **keep** or **reject** for one fictional job seeker, Riley Navarro. Riley is an entry-level Data/BI/Business Analyst with 0–2 years of experience, working in the US, who needs H-1B sponsorship. For each kept posting, Claude writes claims backed by quotes, a checker tests the quotes, and the agent abstains when the evidence is missing. One read-only tool, `score_posting`, serves the filter over MCP.

## What happened, in one paragraph
- **The first corpus held nothing Riley could apply to.** It was 12 boards and 4,102 postings, chosen by a rule fixed before a 116-board probe. I labeled all 92 sampled postings "no", and the nearest misses all said they wouldn't sponsor.
- **A second fixed rule (FILTER.md v1.1) found more.** It ran over 196 new boards and found 2 with a candidate, FanDuel and Axios. I labeled 2 FanDuel postings "yes".
- **What the filter did:** v1.0 keeps 12 postings, including both "yes" labels (held-out precision 2/2, recall 2/2). That is a sample too small to praise it.
- **My reject audit:** all 10 kept postings outside held-out were wrong, and 0 of 40 rejects were.
- **The current version, v1.2:** it adopts three filter fixes and one prompt fix. It keeps 9, still 2/2 on held-out.
- **What the claims did:** the abstention rule abstains on both "yes" postings, and answers "keep" only on 3 postings I labeled "no".
- **Each change tried, one at a time:** one change (reject at 2+ years) loses a held-out "yes". One prompt "improvement" turned out to be run-to-run noise. One rule misreading in my own code was found and measured instead of quietly fixed.

## Files

| File | What it is |
|---|---|
| [`FILTER.md`](FILTER.md) | The filter, written before any code: rules with reasons, evidence rules, expected sources, wrong versions, the measurement plan, and the version history (v1.0, v1.1, v1.2) |
| [`AUDIT.md`](AUDIT.md) | The reject audit: my verdicts on 50 seeded postings, k/n with 95% intervals, the sample statement, the named false friend, and the changelog |
| [`SHORTLIST.md`](SHORTLIST.md) | The source-grounded shortlist: claim labels, a relevance-vs-entailment case, the abstention rule and its counterexamples |
| [`MCP_EVAL.md`](MCP_EVAL.md) | The tool server: transcripts, declared vs actual, what a client isn't entitled to, the trust decision, and an evaluation of the reference Fetch server |
| [`SCORE.md`](SCORE.md) | What moves the score: the origin of every number, one change at a time on held-out labels, and why persistence is not training |
| [`SIGNOFF.md`](SIGNOFF.md) | What I checked, didn't check, and don't claim; the signature; the driver's seat |
| [`SOURCES.md`](SOURCES.md) | What this builds on, and what Claude Code did and what I did |
| [`FRICTIONAL.md`](FRICTIONAL.md) | The dated log of every session |

| Code | What it does |
|---|---|
| `agent.py`, `loop.py`, `adapters.py`, `text.py`, `tools.py`, `policy.py` | The JS2 collector, extended to keep full posting text. Permission policy unchanged. |
| `corpus.py` | Loads the frozen corpus (the v1.0 run plus the v1.1 supplement) from saved raw responses |
| `labels.py` | Draws the seeded label sample |
| `filter.py` | The filter: v1.2 (current) and v1.0 (kept for the audit and the measurements), plus the two wrong versions (used only in tests) |
| `measure.py`, `measure_changes.py` | Precision and recall on the labels; one change at a time |
| `audit.py` | Draws the reject audit, and reports k/n with Wilson 95% intervals |
| `claims.py` | Claims through `claude -p`, the substring checker, and abstention |
| `mcp_server.py`, `mcp_client.py`, `.mcp.json` | The MCP server from scratch, a minimal client, and the Claude Code config |
| `mcp_eval_fetch.py` | The recorded session with the Fetch server |
| `probe/` | Both board probes and their summaries |

## Run it
All commands run from this folder, with Python 3.14 standard library only.

```bash
python3 -m unittest discover -s tests
```

```bash
python3 corpus.py
```

```bash
python3 filter.py show greenhouse/fanduel/8055746
```

```bash
python3 measure.py
```

```bash
python3 measure_changes.py
```

```bash
python3 audit.py report
```

```bash
python3 mcp_client.py greenhouse/fanduel/8055746
```

**Notes on the commands:**
- `measure_changes.py` writes `state/measure/changes.json`, and the policy refuses to overwrite it. Move the existing file before running it again.
- `claims.py run VARIANT` calls Claude through `claude -p`, so it needs Claude Code. Its outputs are already saved in `state/claims/`, so `claims.py check VARIANT` works offline.
- **Connecting Claude Code to the server:** run `claude` in this folder. `.mcp.json` starts `python3 mcp_server.py`.

## What the agent never does
It never applies, emails, messages, or logs in anywhere. The collector makes GET requests to three job-board hosts only (JS2's policy). The tool server has one read-only tool. Whether a posting is worth Riley's application stays with me (`SIGNOFF.md`, driver's seat).
