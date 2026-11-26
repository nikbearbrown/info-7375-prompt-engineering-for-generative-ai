# Job-Search Agent 3: The Filter, the Tool, and the Score

Arundhati K · INFO 7375 · Fall 2026 · persona: Rohan Desai (fictional, `persona/rohan-desai.resume.example.json`)

**Started from** my JS2 agent (`../js2-loop-tools-diff/`). It uses the same three boards (Stripe and Figma on
Greenhouse, Notion on Ashby), the same allow-list idea, and the same persona. The Claude judge prompt is inherited
from my JS1 (`../js1-contract-and-watch/prompts/baseline.txt`). No Reallocation Engine or Lectern code was used. No
classmate's JS3 folder was read.

## Order of work (each step committed before the next)

The hashes in these files are the ones on GitHub. My 24 commits were rebased onto 1 newer classmate commit before pushing (author dates and order unchanged), so commit *messages* may still quote the old hashes:

<details><summary>old → new hash map</summary>

| before rebase | on GitHub |
|---|---|
| `a3e574da` | `e436212d` |
| `aca05b4b` | `591bba1b` |
| `e40e9b17` | `3ed49fc1` |
| `fab69d83` | `01120f35` |
| `37687242` | `d190b97e` |
| `76e79e90` | `d39c2046` |
| `49bebaab` | `8432d6fe` |
| `81e4bcf1` | `5d2271b7` |
| `ab371658` | `3eaf12a6` |
| `5246ca26` | `c10a9ff3` |
| `b4729c8e` | `fb9e0d0f` |
| `0bf418c1` | `7286c818` |
| `d47f0a32` | `d33137fc` |
| `5e54bac0` | `ac89bb68` |
| `3b091c23` | `401cacdb` |
| `49191b37` | `0e23460c` |
| `8a6b77e4` | `8c02746e` |
| `9ee00800` | `7521ea81` |
| `5c9c8b28` | `df7f606b` |
| `771a61a9` | `69450ad8` |
| `58a220b7` | `a2a4f120` |
| `63941b01` | `fc924774` |
| `18977838` | `0b607fc5` |
| `a725b4a4` | `1b468cf7` |

</details>

| step | commit | what |
|---|---|---|
| gate | `1b468cf7` | [FILTER.md](FILTER.md) v1: my rules, reasons, evidence rules, sources and wrong versions, before any code |
| tests first | `0b607fc5` | 31 filter/evidence tests and 11 server tests, all failing on import ([log 00](evidence/logs/00-tests-before-code.txt)); collector and live snapshot |
| code | `fc924774` | `jsagent3/filter.py`, `evidence.py`, `mcp_server.py`; the same 42 tests pass ([log 01](evidence/logs/01-tests-after-code.txt)) |
| run + blind sample | `a2a4f120` | v1 on 1,088 postings, 25 kept; audit sample and held-out sheets, filter verdict hidden |
| tool server transcripts | `69450ad8`, `df7f606b` | real transcripts with my client, Claude Code, and `claude mcp serve`; [TOOL-EVALUATIONS.md](TOOL-EVALUATIONS.md) |
| my audit verdicts | `7521ea81` | 54 blind verdicts; optional rule keys (off in v1) + tests |
| my rule decisions | `8c02746e` | FILTER.md v1.1: A rejected, B added, C rejected, D added; held-out labels |
| parser fixes, test first | `0e23460c`, `401cacdb` | curly-apostrophe headings; "four (4) years"; live Claude runs P1/P2/C2 |
| write-ups | (later commits) | [AUDIT.md](AUDIT.md), [SHORTLIST.md](SHORTLIST.md), [SCORE-CHANGES.md](SCORE-CHANGES.md), SIGNOFF, SOURCES, FRICTIONAL |
| labeler fix, test first | `ed344260`, `124eca29` | dev set 10/16 → 16/16; logs 14–18; SHORTLIST.md "Improvement" |

## Language and toolchain

- Python 3, **standard library only**. Developed on Python 3.15.0 on macOS. Nothing to install.
- Network (collector only): `boards-api.greenhouse.io` and `api.ashbyhq.com`, GET only, allow-listed in
  `jsagent3/collect.py`. Everything else runs offline from `data/raw/2026-11-25/`.
- Claude Code CLI 2.1.316 (`claude`). It is used by `claude_score.py` (live scorer runs), by `mcp-config.json` (Claude
  as an MCP client), and for `claude mcp serve` (the other server). Claude Code also wrote most of the code and docs
  (see SOURCES.md).

## Exact commands (from this folder)

```bash
python3 -m unittest discover -s tests -t .
```

```bash
python3 run_filter.py --version v1 --no-sample
```

```bash
python3 run_filter.py --version v1.1 --no-sample
```

```bash
python3 make_shortlist.py v1.1
```

```bash
python3 measure_claims.py
```

```bash
python3 mcp_client.py own
```

```bash
claude -p --mcp-config mcp-config.json --strict-mcp-config --allowedTools mcp__js3__score_posting "Use the score_posting tool on posting stripe:8128744 and report keep/reject and which claims are supported."
```

```bash
python3 claude_score.py P1 P2 C2
```

- The first command runs the 57 tests. They are offline and deterministic.
- The `run_filter.py` and `make_shortlist.py` commands run offline on the saved snapshot.
- `mcp_client.py own` records a fresh transcript to `transcripts/01-own-client.*`.
- The `claude -p` and `claude_score.py` commands are **live** Claude calls, need a logged-in Claude Code, and
  overwrite the saved evidence.
- To refetch the boards (live, GET only), run `python3 -c "from pathlib import Path; from jsagent3.collect import collect; print(collect(Path('data/raw/NEW-DATE'))[1])"`.

## What ran (all on 2026-11-25)

- **Collection:** 1,088 postings (Stripe 772, Figma 142, Notion 174), 0 with a missing body.
- **Filter v1:** 25 kept. **Filter v1.1:** 4 kept ([log 04](evidence/logs/04-run-v1.1.txt)).
- **Audit:** 54 blind hand verdicts, and 0 of 32 random rejects wrong. That is a sample result, consistent with up to
  about 9% of rejects being wrong. 8 of 10 sampled keeps were wrong ([AUDIT.md](AUDIT.md)).
- **Held-out (20, 2 Y):** filter v1 16/20, v1.1 18/20 (TP 0). The LIVE Claude scorer gave 17/20 under every
  prompt and context tried ([SCORE-CHANGES.md](SCORE-CHANGES.md)).
- **Claim labeler fix (dev set):** agreement with my checked labels went from 10/16 to 16/16, test-first (SHORTLIST.md, logs 14–18).
- **Tool server:** 11 server tests (57 in total), and 3 real transcripts. One of them is a live `claude -p` session that called the tool
  twice.

**Known gap:** the tool server scores with **filter v1**, the version it was built and recorded with. Every result
reports `"filter_version": "v1"`. It was not switched to v1.1, so the transcripts stay true to what ran.

## Files

[FILTER.md](FILTER.md) · [AUDIT.md](AUDIT.md) (+ `audit/`) · [SHORTLIST.md](SHORTLIST.md) ·
[TOOL-EVALUATIONS.md](TOOL-EVALUATIONS.md) (+ `transcripts/`) · [SCORE-CHANGES.md](SCORE-CHANGES.md) (+ `labels/`,
`prompts/`, `evidence/claude-runs/`) · [SIGNOFF.md](SIGNOFF.md) · [SOURCES.md](SOURCES.md) ·
[FRICTIONAL.md](FRICTIONAL.md)

Left out: `out/` (regenerated), `data/postings.json` (regenerated from raw), caches, credentials, and my real
résumé. The agent never applies, emails, messages or logs in. The tool server exposes one read-only tool.
