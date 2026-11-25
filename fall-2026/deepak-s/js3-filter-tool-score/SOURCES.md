# SOURCES.md: every endpoint, spec page and tool-server source used

Job-Search Agent 3. Compiled by Claude Code (claude-opus-5-5) on 2026-11-25 from the request logs and commits named in each row. All access dates are 2026-11-25 (UTC times in the cited logs). The "Read by Deepak" cells were set by Deepak's instruction of 2026-11-25.

## Job board endpoints (public, GET only)

| Source | URL | Accessed | Evidence | Read by Deepak |
|---|---|---|---|---|
| Greenhouse Job Board API, stripe (with descriptions) | https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true | 18:23:22Z (manual), 20:02Z (run) | evidence/manual-capture/20261125T182322Z/curl_log.tsv; runs/20261125T200226Z/summary.json | Not read by Deepak |
| Greenhouse Job Board API, stripe-js2-nonexistent (deliberate 404) | https://boards-api.greenhouse.io/v1/boards/stripe-js2-nonexistent/jobs?content=true | 20:02Z (run) | runs/20261125T200226Z/summary.json | Not read by Deepak |
| Lever Postings API (EU), lever | https://api.eu.lever.co/v0/postings/lever?mode=json | 18:23:25Z, 20:02Z | as above | Not read by Deepak |
| Lever Postings API (US), palantir | https://api.lever.co/v0/postings/palantir?mode=json | 18:23:28Z, 20:02Z | as above | Not read by Deepak |
| Ashby public job posting API, linear | https://api.ashbyhq.com/posting-api/job-board/linear | 18:23:32Z, 20:02Z | as above | Not read by Deepak |
| Ashby public job posting API, notion | https://api.ashbyhq.com/posting-api/job-board/notion | 18:23:34Z, 20:02Z | as above | Not read by Deepak |

The providers' terms of use were not read in this session (as in JS2).

## Model Context Protocol specification pages (fetched with curl, redirects recorded, not followed)

| Page | URL | Accessed (UTC) | Saved as | Read by Deepak |
|---|---|---|---|---|
| 01-latest-changelog-redirect | https://modelcontextprotocol.io/specification/latest/changelog | 2026-11-25T18:25:46Z | evidence/mcp/spec-fetch/20261125T182546Z/01-latest-changelog-redirect.body | Not read by Deepak |
| 02-latest-changelog-md-redirect | https://modelcontextprotocol.io/specification/latest/changelog.md | 2026-11-25T18:25:48Z | evidence/mcp/spec-fetch/20261125T182546Z/02-latest-changelog-md-redirect.body | Not read by Deepak |
| 03-2026-07-28-lifecycle-redirect | https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle | 2026-11-25T18:25:50Z | evidence/mcp/spec-fetch/20261125T182546Z/03-2026-07-28-lifecycle-redirect.body | Not read by Deepak |
| 04-2026-07-28-changelog | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-25T18:25:52Z | evidence/mcp/spec-fetch/20261125T182546Z/04-2026-07-28-changelog.body | Not read by Deepak |
| 05-2026-07-28-changelog-md | https://modelcontextprotocol.io/specification/2026-07-28/changelog.md | 2026-11-25T18:25:53Z | evidence/mcp/spec-fetch/20261125T182546Z/05-2026-07-28-changelog-md.body | Not read by Deepak |
| 06-2025-11-25-lifecycle | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle | 2026-11-25T18:25:55Z | evidence/mcp/spec-fetch/20261125T182546Z/06-2025-11-25-lifecycle.body | Not read by Deepak |
| 07-2025-11-25-lifecycle-md | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle.md | 2026-11-25T18:25:57Z | evidence/mcp/spec-fetch/20261125T182546Z/07-2025-11-25-lifecycle-md.body | Not read by Deepak |
| 08-2026-07-28-versioning | https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning | 2026-11-25T18:25:58Z | evidence/mcp/spec-fetch/20261125T182546Z/08-2026-07-28-versioning.body | Not read by Deepak |
| 09-2026-07-28-versioning-md | https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning.md | 2026-11-25T18:26:00Z | evidence/mcp/spec-fetch/20261125T182546Z/09-2026-07-28-versioning-md.body | Not read by Deepak |
| 10-2026-07-28-overview | https://modelcontextprotocol.io/specification/2026-07-28 | 2026-11-25T18:26:02Z | evidence/mcp/spec-fetch/20261125T182546Z/10-2026-07-28-overview.body | Not read by Deepak |
| 11-2026-07-28-overview-md | https://modelcontextprotocol.io/specification/2026-07-28.md | 2026-11-25T18:26:03Z | evidence/mcp/spec-fetch/20261125T182546Z/11-2026-07-28-overview-md.body | Not read by Deepak |
| 12-2026-07-28-server-discover-md | https://modelcontextprotocol.io/specification/2026-07-28/server/discover.md | 2026-11-25T18:26:21Z | evidence/mcp/spec-fetch/20261125T182546Z/12-2026-07-28-server-discover-md.body | Not read by Deepak |
| 13-2026-07-28-stdio-md | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio.md | 2026-11-25T18:26:23Z | evidence/mcp/spec-fetch/20261125T182546Z/13-2026-07-28-stdio-md.body | Not read by Deepak |
| 14-2026-07-28-basic-index-md | https://modelcontextprotocol.io/specification/2026-07-28/basic/index.md | 2026-11-25T18:26:24Z | evidence/mcp/spec-fetch/20261125T182546Z/14-2026-07-28-basic-index-md.body | Not read by Deepak |
| 15-2026-07-28-tools-md | https://modelcontextprotocol.io/specification/2026-07-28/server/tools.md | 2026-11-25T21:20:10Z | evidence/mcp/spec-fetch/20261125T212010Z/15-2026-07-28-tools-md.body | Not read by Deepak |
| 16-2026-07-28-caching-md | https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching.md | 2026-11-25T21:20:12Z | evidence/mcp/spec-fetch/20261125T212010Z/16-2026-07-28-caching-md.body | Not read by Deepak |

## Tool-server sources

| Source | URL | Accessed | Evidence | Read by Deepak |
|---|---|---|---|---|
| npm registry metadata, @modelcontextprotocol/server-filesystem (versions, dates, 2.3.0 tarball and integrity) | https://registry.npmjs.org/@modelcontextprotocol/server-filesystem | 21:23Z | evidence/mcp/other-server/install.md | Not read by Deepak |
| npm package @modelcontextprotocol/server-filesystem 2.3.0 and its dependencies (installed in a /tmp sandbox) | https://registry.npmjs.org/@modelcontextprotocol/server-filesystem/-/server-filesystem-2.3.0.tgz | 21:23Z | evidence/mcp/other-server/npm_install.log, npm_ls.json, installed-dist-sha256.txt | Not read by Deepak |
| npm registry metadata, @modelcontextprotocol/server (dependency publish dates) | https://registry.npmjs.org/@modelcontextprotocol/server | 21:24Z | evidence/mcp/other-server/install.md | Not read by Deepak |
| GitHub tags of modelcontextprotocol/servers (git ls-remote) | https://github.com/modelcontextprotocol/servers | 21:23Z | evidence/mcp/other-server/install.md | Not read by Deepak |
| GitHub API: commits touching src/filesystem/package.json | https://api.github.com/repos/modelcontextprotocol/servers/commits?path=src/filesystem/package.json&per_page=8 | 21:24Z | evidence/mcp/other-server/install.md | Not read by Deepak |
| src/filesystem/package.json at 5c6686a8 and 2f882b11 | https://raw.githubusercontent.com/modelcontextprotocol/servers/5c6686a8c35864aa0675f63ee956aae87ea69ea3/src/filesystem/package.json | 21:24Z | evidence/mcp/other-server/install.md | Not read by Deepak |
| Source archive of modelcontextprotocol/servers at 5c6686a8 (read for MCP_EVAL.md section 2) | https://codeload.github.com/modelcontextprotocol/servers/tar.gz/5c6686a8c35864aa0675f63ee956aae87ea69ea3 | 21:24Z | sha256 in evidence/mcp/other-server/install.md | Not read by Deepak |
| Source archive at tag v2.3.0 (36380287; checked and not used: its filesystem package is 2.2.0) | https://codeload.github.com/modelcontextprotocol/servers/tar.gz/36380287ed3b15d115b55f546617d723072b1296 | 21:23Z | evidence/mcp/other-server/install.md | Not read by Deepak |

## Earlier work this agent starts from (same personal repository)

| Source | Commit | Read by Deepak |
|---|---|---|
| JS2 "The Loop, the Tools, and the Diff", fall2026/deepak-kumaran-ts/js2-loop-tools-diff/ | b2ac533 | Not read by Deepak |
| JS1 "Contract and Watch" (rule, normalization, judge backend), fall2026/deepak-kumaran-ts/js1-contract-and-watch/ | b91c877 | Not read by Deepak |

## Local tools whose output is cited

| Tool | Version | Evidence | Read by Deepak |
|---|---|---|---|
| Claude Code CLI (`claude --version`, `claude mcp --help`, `claude mcp add --help`) | 2.1.332 | evidence/mcp/claude-cli/ | Not read by Deepak |
| Node.js and npm (Phase 5e only) | node v24.21.0, npm 11.19.0 | evidence/mcp/other-server/20261125T212437Z-run.json | Not read by Deepak |
