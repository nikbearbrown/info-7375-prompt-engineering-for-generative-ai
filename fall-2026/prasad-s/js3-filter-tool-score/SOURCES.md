# SOURCES.md — Job-Search Agent 3

## My own earlier work
- **JS2**, js2-loop-tools-diff/ at 64e00c7: agent/, tests/, tools/, CONTRACT.md, GATE.md, config.json, resume_persona.json and .gitignore, copied in unchanged (JS3-CP4a). Two JS2 files became test fixtures, copied byte for byte (tests/fixtures/js2/, JS3-CP4b).
- **JS1 and JS2's evidence:** the 20 raw board responses that form the frozen corpus (FILTER.md §3), read in place and checked against vault/corpus_manifest.tsv.

## Course materials
- The JS3 brief (Chapters 7–9).
- Lectern, the instructor's reference agent (fall-2026/nik-bear-brown/lectern/): reference only, as in JS2. No Lectern file or code is in this folder.

## Data
- Public job-board APIs: Greenhouse (boards-api.greenhouse.io: Stripe, Duolingo, Robinhood) and Ashby (api.ashbyhq.com: Notion). The postings belong to those companies; they are used here as a fixed test corpus.

## Specifications and documentation
- The Model Context Protocol specification, modelcontextprotocol.io: revision 2025-11-25 (the one my server implements) and the 2026-07-28 changelog (the initialize handshake removed, server/discover added), read on 2026-11-19 and 2026-11-20.
- Claude Code's MCP documentation, code.claude.com/docs: server scopes and the project .mcp.json file, used to register the server.
- The exact (Clopper–Pearson) binomial interval: C. J. Clopper and E. S. Pearson, Biometrika, 1934; implemented with the standard library in tools/audit.py.

## Third-party software, probed but not part of JS3
- @modelcontextprotocol/server-filesystem on npm (repository: modelcontextprotocol/servers), versions 2.4.0 and 2026.8.31, run through npx with a throwaway folder (TOOLSERVER.md §3).

## AI assistance
- **Claude Code** (Anthropic, the desktop app) wrote all of JS3's code and tests to my prompts, asked me when a prompt left something open, ran tests, and planted bugs to show the tests can fail. It never committed; I reviewed and committed every change.
- **Claude.ai** (Anthropic), in my course Project chat, reviewed my decisions and drafts, proposed designs and leans that I accepted or changed, wrote the shell checks I ran, and typed most documents at my request from the committed files. Each document's changelog says which parts.
- Neither labeled any posting or claim: every hand verdict and claim label is mine.