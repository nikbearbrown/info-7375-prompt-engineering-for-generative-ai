# SOURCES — Job-Search Agent 3

## Starting point: my own JS1 and JS2, not the Reallocation Engine or Lectern

| Inherited | From | How | Hash record |
|---|---|---|---|
| `inherited/rules.py`: normalization, whole-word matching, HTML to text (the JS1 §4 rule) | `../js2-loop-tools-diff/agent/rules.py` (itself unchanged from JS1) | copied unchanged | `inherited/MANIFEST.sha256` |
| `inherited/board.py`, `inherited/providers.py`: Greenhouse/Ashby parsing and validation | `../js2-loop-tools-diff/agent/` | copied unchanged | `inherited/MANIFEST.sha256` |
| `resume/priya-nair.resume.example.json`: the fictional persona | JS1, carried through JS2 | copied unchanged | `inherited/MANIFEST.sha256` |
| `raw/*.json.gz`: every board response the collector captured | JS1 LIVE run 2026-10-30; JS2 LIVE run 2026-11-10 | JS2 files copied unchanged; the JS1 body gzip-wrapped | `raw/CAPTURES.json` (body hashes recorded at capture time, re-verified on every build) |
| Role phrases (5 of 9) and level words (12 of 14) | JS1 CONTRACT.md §4 A/B | reused in `filters/v1.0.json` | — |
| The "employer word" problem | JS1 CONTRACT.md R2 | made into an explicit rule (T7) and wrong version W2 | — |

**New in JS3:**
- `FILTER.md` and `filters/*.json`;
- `js3/` (corpus, filter, run, sample, labels, explain, shortlist, MCP server and client, transcript publisher);
- `tests/`, `evaluations/`, `transcripts/`, `review/`, `splits/`.

The JS1/JS2 judge (`claude -p` per posting) and the JS2 loop are **not** part of JS3. Nothing new was collected, because the corpus was big enough (see `corpus/PROVENANCE.json`).

## External

- **`@modelcontextprotocol/server-filesystem` 2.3.0** (npm; repository `github.com/modelcontextprotocol/servers`).
  - Evaluated only, never vendored.
  - Installed outside the repo with `--ignore-scripts`.
  - File hashes are in `evaluations/fs_server_2.3.0_dist.sha256`.
- **Claude Code CLI 2.1.310**, logged in with Aditya's account. It was the MCP client in `transcripts/claude_code_2026-11-25_run1.*`, using model `claude-opus-5-5` at effort `medium`.
- **pytest 8.3.3.** Everything else is the Python 3.12 standard library.
- **Course documents read:** the JS3 brief (Canvas PDF, 2026-11-25), and `prerequisites/ai-policy.md`, `frictional.md`, `github-submission.md` and `relative-quartile.md` (at `origin/main` `7e5c3d0`, fetched 2026-11-25).

## What Claude (Claude Code, Opus 5.5) contributed

_Kept up to date during the session. Aditya's own contributions are listed separately, and only once he has made them._

| Part | Claude Code did |
|---|---|
| FILTER.md v1.0 | Drafted the rules, reasons, evidence rules, sources section, split plan and wrong versions W1–W5 at Aditya's request, and committed them before any JS3 code. Wrote amendments A1/A2 (sampling) and clarifications C1/C2 (evidence rules), each before any label existed. |
| Code and tests | Wrote everything under `js3/`, `tests/` and `evaluations/`. The filter tests were committed before the scorer (`5de50f2` before `b33fca0`). |
| Corpus, run, split, sheet | Built them and ran them. Chose seeds and sizes per FILTER.md §5. |
| Tool server | Wrote the server and the test client, ran the Claude Code exchange, and published the sanitized transcript. |
| Evaluations | Read the server-filesystem source, ran 4 sessions, and drafted both evaluations and the *proposed* trust decisions. |
| Observations | Found the boilerplate false friend ("agent(s)" and "unity catalog" in employer boilerplate) by measuring the corpus. Claude (in the MCP run, 2026-11-25) separately flagged "junior" and "30 years" in posting 8091041002. |

## Not included (kept local)

- Aditya's real résumé, contacts, tracker and private chats.
- The private Claude chat output of the MCP run (`../../../../local/mcp_run1/`, sha256 of `claude_output.json`: `055fc37b…efabda`).
- The npm install of the evaluated server, caches, and `.venv/`.
