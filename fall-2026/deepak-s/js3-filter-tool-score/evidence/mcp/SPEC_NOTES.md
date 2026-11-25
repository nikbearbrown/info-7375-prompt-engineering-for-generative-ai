# SPEC_NOTES.md: Model Context Protocol facts, fetched 2026-11-25

Fetched by Claude Code (claude-opus-5-5) in Deepak's session with curl, `--max-redirs 0` (redirects recorded, not followed), between 2026-11-25T18:25:46Z and 18:26:24Z (13:25 to 13:26 ET). Raw headers and bodies were committed in 4bb374a before this file was written. Nothing was built.

- Folder: `evidence/mcp/spec-fetch/20261125T182546Z/` (abbreviated `F/` below). Request log with status, content-type, bytes and redirect target per URL: `F/curl_log.tsv`. Hashes: `F/SHA256SUMS`.
- Each page was fetched as HTML and, where available, as Markdown (the same URL with `.md`). Citations below are to the Markdown bodies, by line number. Each Markdown body begins with a 3-line "Documentation Index" note added by the site; it is not part of the specification text.

## URLs and what came back

| File | URL | Status | Note |
|---|---|---|---|
| 01 | https://modelcontextprotocol.io/specification/latest/changelog | 307 | redirect to `/specification/2026-07-28/changelog` |
| 02 | https://modelcontextprotocol.io/specification/latest/changelog.md | 307 | redirect to `/specification/2026-07-28/changelog.md` |
| 03 | https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle | 308 | redirect to `/specification/2026-07-28/basic/versioning` |
| 04, 05 | https://modelcontextprotocol.io/specification/2026-07-28/changelog (and `.md`) | 200 | |
| 06, 07 | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle (and `.md`) | 200 | |
| 08, 09 | https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning (and `.md`) | 200 | |
| 10, 11 | https://modelcontextprotocol.io/specification/2026-07-28 (and `.md`) | 200 | the 2026-07-28 overview |
| 12 | https://modelcontextprotocol.io/specification/2026-07-28/server/discover.md | 200 | |
| 13 | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio.md | 200 | |
| 14 | https://modelcontextprotocol.io/specification/2026-07-28/basic/index.md | 200 | `_meta` keys and error codes |

## Current revision

`/specification/latest/changelog` redirected (307) to `/specification/2026-07-28/changelog` on 2026-11-25 (`F/01-latest-changelog-redirect.headers.txt`, `F/curl_log.tsv`). The 2026-07-28 changelog says it lists changes "since the previous revision, 2025-11-25" (`F/05-2026-07-28-changelog-md.body:7-8`). So the revision the site served as `latest` on the fetch date was 2026-07-28, and the one before it is 2025-11-25.

## initialize and notifications/initialized

**2025-11-25: both exist and are required.**
- "The initialization phase **MUST** be the first interaction between client and server." The client "**MUST** initiate this phase by sending an `initialize` request" with protocol version, capabilities and client info (`F/07-2025-11-25-lifecycle-md.body:40-51`, example at 53-96).
- The server "**MUST** respond with its own capabilities and information" (`:98`, example result with `protocolVersion`, `capabilities`, `serverInfo`, `instructions` at 100-145).
- "After successful initialization, the client **MUST** send an `initialized` notification": `{"jsonrpc": "2.0", "method": "notifications/initialized"}` (`:147-155`).
- Version negotiation: the client sends a version it supports; "If the server supports the requested protocol version, it **MUST** respond with the same version. Otherwise, the server **MUST** respond with another protocol version it supports"; a client that does not support the server's version "**SHOULD** disconnect" (`:165-175`).

**2026-07-28: both are removed.**
- Changelog major change 2: "Make MCP stateless: remove the `initialize`/`notifications/initialized` handshake." (`F/05-2026-07-28-changelog-md.body:14`)
- The old lifecycle URL redirects (308) to `basic/versioning` (`F/03-2026-07-28-lifecycle-redirect.headers.txt`). That page: "There is no negotiation handshake. Every request carries its protocol version, and the server accepts or rejects each request independently" (`F/09-2026-07-28-versioning-md.body:12-13`). It calls versions with an `initialize` handshake (2025-11-25 and earlier) "Legacy" and 2026-07-28 and later "Modern" (`:34-37`).

## How 2026-07-28 replaces the handshake

1. **Per-request `_meta`.** "Every request now carries its protocol version and client capabilities in `_meta` (`io.modelcontextprotocol/protocolVersion`, `io.modelcontextprotocol/clientCapabilities`). Clients SHOULD identify themselves on each request (`io.modelcontextprotocol/clientInfo`), and servers SHOULD identify themselves in each result's `_meta` (`io.modelcontextprotocol/serverInfo`)." (`F/05-2026-07-28-changelog-md.body:14`). The basic page marks `protocolVersion` and `clientCapabilities` Required, `clientInfo` and `logLevel` not required (`F/14-2026-07-28-basic-index-md.body:374-379`), and: "A request missing any required field is malformed; the server **MUST** reject it with JSON-RPC error code `-32602` (Invalid params)." (`:381-383`)
2. **`server/discover`.** "servers MUST implement this RPC to advertise their supported protocol versions, capabilities, and identity. Clients MAY call it before any other request for up-front version selection, or use it as a backward-compatibility probe on STDIO" (`F/05-2026-07-28-changelog-md.body:16`). The request "carries no body parameters beyond the standard `_meta`" (`F/12-2026-07-28-server-discover-md.body:13`). The example result holds `resultType: "complete"`, `supportedVersions`, `capabilities`, `_meta["io.modelcontextprotocol/serverInfo"]`, `instructions`, `ttlMs`, `cacheScope` (`:38-60`).
3. **`resultType` on every result.** "All results now carry a required `resultType` field: `"complete"` for ordinary results ..." (`F/05-2026-07-28-changelog-md.body:26`).
4. **`ttlMs` and `cacheScope`** are required on results of `server/discover` and `tools/list`, among others (`F/05-2026-07-28-changelog-md.body:36`).
5. **stdio backward compatibility.** A client that supports both eras "**SHOULD** probe with `server/discover` before sending any other request". A `DiscoverResult` or a recognized modern error means a modern server; "any other error, or does not respond within a reasonable timeout: the server is legacy. Fall back to the `initialize` handshake." The fallback "**MUST NOT** be keyed to one specific error code" (`F/13-2026-07-28-stdio-md.body:126-146`).
6. **Dual-era servers.** "A server that wishes to support both legacy clients ... and modern clients ... **MAY** implement both behaviors." A dual-era server serves a request carrying modern `_meta` statelessly and treats an `initialize` request as selecting legacy semantics, "scoped to the stdio process" on stdio (`F/09-2026-07-28-versioning-md.body:131-133`, `:179-188`).
7. **Legacy client against a modern-only server fails**: "stdio: the server rejects `initialize` with a JSON-RPC error; the exact code is implementation-defined ... Legacy clients have no fall-forward mechanism." (`F/09-2026-07-28-versioning-md.body:175`). A modern-only server "**SHOULD** name the protocol versions it supports in any error it returns to an `initialize` request" (`:157-160`).

## The error for an unsupported version

- **2025-11-25:** the lifecycle page's example initialization error is code `-32602`, message `"Unsupported protocol version"`, `data: {"supported": [...], "requested": "..."}` (`F/07-2025-11-25-lifecycle-md.body:270-285`). In that revision the normal path for a version the server does not support is to answer `initialize` with a different version it does support (`:170-172`), not an error.
- **2026-07-28:** `UnsupportedProtocolVersionError`, code `-32022`, message `"Unsupported protocol version"`, `data: {"supported": [...], "requested": "..."}`; the server "**MUST** respond" with it when it does not implement the requested version (`F/09-2026-07-28-versioning-md.body:48-67`). The code was renumbered from `-32004` in earlier drafts of this revision (`F/05-2026-07-28-changelog-md.body:61-67`); the error code table lists `-32022` `UnsupportedProtocolVersion` (`F/14-2026-07-28-basic-index-md.body:129-135`).

## Other 2026-07-28 facts relevant to a stdio server

- Messages are newline-delimited, "**MUST NOT** contain embedded newlines"; the server "**MUST NOT** write anything to its `stdout` that is not a valid MCP message" and "**MAY** write UTF-8 strings to `stderr`" (`F/13-2026-07-28-stdio-md.body:10-21`).
- "Servers **SHOULD** exit promptly when their standard input is closed" (`:105-107`).
- `ping` is removed in 2026-07-28 (`F/05-2026-07-28-changelog-md.body:20`).
- Tools from `tools/list` **SHOULD** come in a deterministic order (`F/05-2026-07-28-changelog-md.body:34`).
- The overview's Tool Safety principle: "descriptions of tool behavior such as annotations should be considered untrusted, unless obtained from a trusted server" (`F/11-2026-07-28-overview-md.body:112-116`).

## Claude Code CLI on this machine

Captured 2026-11-25T18:26:34Z (`evidence/mcp/claude-cli/captured_at_utc.txt`); all three commands exited 0 (`evidence/mcp/claude-cli/exit_codes.txt`).

- `claude --version`: `2.1.332 (Claude Code)` (`evidence/mcp/claude-cli/claude--version.txt`).
- `claude mcp --help`: subcommands `add`, `add-from-claude-desktop`, `add-json`, `get`, `help`, `list`, `login`, `logout`, `remove`, `reset-project-choices`, `serve` (`evidence/mcp/claude-cli/claude-mcp--help.txt`).
- `claude mcp add --help`: usage `claude mcp add [options] <name> <commandOrUrl> [args...]`; `-t, --transport` (stdio, sse, http; "Defaults to stdio"); `-s, --scope` (local, user, or project; default `"local"`); `-e, --env`; `-H, --header`; example `claude mcp add my-server -- my-command --some-flag arg1` (`evidence/mcp/claude-cli/claude-mcp-add--help.txt`).

Not captured: which protocol revision Claude Code 2.1.332 sends as a client (an `initialize` request, a `server/discover` probe, or per-request `_meta`). None of the help output states it, and no server has been run.
