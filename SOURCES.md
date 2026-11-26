# Sources

## Data
- **Greenhouse Job Board API** — `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true`, public and read-only, used for
  samsara, databricks, toast, klaviyo, datadog and the deliberate 404 board `samsara-does-not-exist`. Fetched 2026-11-25; the sha256s
  are in `snapshot/2026-11-25/manifest.json`.
- **Lever Postings API** — `https://api.lever.co/v0/postings/<board>?mode=json`, public and read-only, used for palantir, spotify, zoox
  and kraken. Same date and manifest.
- **The fictional persona Evan Gordon** — `persona/evan-gordon.resume.json`, from my JS1. No real résumé was used.

## Code and specifications
- **My JS1 and JS2 work** — the JS2 agent at commit `7404ffb` (submitted in the course repo as `6d870788`), and the JS1 contract, rule
  code (`jsagent/rule.py`: the years pattern, the whole-word matcher, the US location list) and labeling rule.
- **Model Context Protocol specification**, revision 2025-06-18 (modelcontextprotocol.io): the message shapes for `initialize`,
  `tools/list`, `tools/call` and tool annotations, the stdio framing, and the JSON-RPC error codes. My server is written from this,
  without the SDK.
- **The official `fetch` server** — `github.com/modelcontextprotocol/servers`, `src/fetch`, commit `c799c85` (2026-11-18), version
  2026.11.18. Read for the evaluation (excerpts in `evidence/mcp/fetch_reference/EXCERPTS.txt`) and run as the PyPI package
  `mcp-server-fetch==2026.11.18`, with `mcp` 2.3.0 and its dependencies (full list in
  `evidence/mcp/fetch_run/environment_and_npm_effect.txt`).
- **Public test pages** — `https://example.com/` (a plain HTML page) and `http://169.254.169.254/` (the cloud metadata address, which
  was refused), used only in the fetch runs.
- **Python standard library documentation**, for audit hooks (`sys.addaudithook`), `gzip`, `zoneinfo` and `unittest`.

## Course
- INFO 7375, Chapters 7–9, and the JS3 brief "The Filter, the Tool, and the Score".

## AI assistance
- Claude Code (Claude Opus 5.5) wrote the code, the tests and the first drafts of the documents, at my direction. It also recorded
  the transcripts, read and ran the `fetch` server, and checked the claim labels. Which parts are mine and which are Claude's is set out in
  `SIGNOFF.md` and `FRICTIONAL.md`.
