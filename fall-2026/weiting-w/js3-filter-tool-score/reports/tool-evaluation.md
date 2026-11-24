# Two tool servers, evaluated the same way

Chapter 8. One server I wrote, one I did not, put through the same three
questions: **what does it declare, what does it actually do, and what is a
compatible client entitled to?** Then a trust decision for each.

Both evaluations are run from real transcripts, captured by driving each server
as a subprocess over stdin/stdout and writing every line of both directions to
a file. Nothing below is retyped from memory.

- `evidence/transcripts/session.txt` — mine, 9 requests.
- `evidence/transcripts/other-server-filesystem.txt` — theirs, 9 requests.

Both captured **2026-11-23**.

---

# Server 1 — `js3-score-posting`, which I wrote

`toolserver/server.py`, 241 lines of Python standard library. JSON-RPC 2.0 over
newline-delimited stdio: `initialize`, `tools/list`, `tools/call`, and the
`notifications/initialized` notification. No SDK, no dependency, no framework.

## What it declares

One tool, `score_posting`, taking one required string `text`, with
`additionalProperties: false`. The description claims: pure arithmetic over a
published word list; reads no file; makes no network request; calls no model;
empty text is an error rather than a 0.

## What it actually does

| claim | how it was checked | result |
|---|---|---|
| scores from a published word list | transcript id 3: six evidence entries, each naming the word and the sentence it matched | holds — a caller can recompute the total by hand |
| reads no file | `grep` for `open(`, `Path(`, `read_text` in `toolserver/` | holds — no file is opened anywhere in the package |
| no network | the module imports `json`, `sys`, `pathlib` and `jobfilter.score`; no socket, no urllib, no http client, transitively | holds |
| no model, no API key | no `os.environ`, no `anthropic`, no `openai` anywhere in the package | holds |
| empty text is an error | transcript id 5 | holds — `isError: true`, "An empty body is not a score of 0" |
| `additionalProperties: false` | transcript id 6 — a `path` argument smuggled alongside `text` | holds, and it is **enforced in code**, not merely declared in the schema |

That last row is the one I would check first in somebody else's server, because
a schema is a document and a document does not stop anything. The transcript
shows the extra argument being named and refused:

```
--> {"id": 6, "method": "tools/call", "params": {"name": "score_posting",
     "arguments": {"text": "hello", "path": "../../etc/passwd"}}}
<-- {"id": 6, "result": {"isError": true, "content": [{"type": "text",
     "text": "unexpected argument(s): ['path']"}]}}
```

## What a compatible client is not entitled to

- **Any file.** Not through an argument: `score_posting` takes text, not a
  path. There is no argument that names a location, so there is nothing to
  confine and nothing to get wrong. This is the one design decision in the
  server I would defend hardest — it is the difference between *validating* a
  path and *not having one*.
- **Any other tool.** `tools/call` with `name: "read_file"` returns
  JSON-RPC −32602 (transcript id 7). The server has no tool dispatch table to
  grow into one.
- **Any other method.** `resources/list` returns −32601 (transcript id 8). The
  server declares no resources and implements no resource methods, so a client
  that assumes the rest of MCP is present finds nothing.
- **The corpus.** The server never loads `evidence/raw/`. A client cannot ask
  it what postings exist, only to score text the client already has.

## Trust decision — I would run this, and the reason is its size

**Accept**, with the reasoning stated so it can be disagreed with: the surface
is one function from a string to a number plus its evidence. It has no
argument naming a resource, no state between calls, no dependency outside the
standard library, and nothing it could leak that the caller did not already
send it. The strongest argument for trusting it is not that I wrote it — it is
that it is small enough for the checks above to be exhaustive rather than
representative.

**What that trust does not extend to.** The *answers* are only as good as the
word list in FILTER.md, and A2 cut three signals from that list after measuring
that they were wrong 70%, 84% and 100% of the time. A caller trusting the
server's arithmetic is not thereby entitled to trust its judgement, which is
why every response carries the sentence behind every point: the server is built
to be checked, not believed.

---

# Server 2 — `@modelcontextprotocol/server-filesystem`, which I did not

**Source, named:** the npm package `@modelcontextprotocol/server-filesystem`,
version **2.4.0**, `repository.url = git+https://github.com/modelcontextprotocol/servers.git`,
license "SEE LICENSE IN LICENSE". Installed from the public npm registry on
2026-11-23 and run with `npx -y @modelcontextprotocol/server-filesystem@2.4.0 <dir>`.
I evaluated the code that npm installed, not a GitHub page.

I picked a filesystem server deliberately: it is the one kind of tool server
whose confinement question is the same question JS2's own permission policy was
built around, so I had a prior opinion to be wrong about.

## What it declares

`initialize` reports `serverInfo.name = "secure-filesystem-server"` — note that
this is **not** the package name — and `tools.listChanged: true`,
`resources.listChanged: true`. `tools/list` returns **16 tools**. Ten are
annotated `readOnlyHint: true`; `write_file`, `edit_file` and `move_file` are
annotated `destructiveHint: true`. **All 16 are annotated
`openWorldHint: false`.** Fifteen of the 16 descriptions end with some form of
"Only works within allowed directories" — the exception is
`list_allowed_directories`, which is the tool that reports what they are.

## What it actually does

I ran it against a sandbox containing one allowed directory, one file outside
it, and a symlink from inside pointing out.

| attempt | transcript | result |
|---|---|---|
| read a file inside the allowed directory | id 3 | content returned |
| read an absolute path outside it | id 4 | **refused** — "Access denied - path outside allowed directories" |
| read it via `sandbox/../outside/secret.txt` | id 5 | **refused**, and the message shows the path *after* resolution |
| read it via a symlink inside the sandbox pointing out | id 6 | **refused** — "Access denied - symlink target outside allowed directories" |
| write a new file inside the allowed directory | id 7 | **succeeded** |
| write a file outside it | id 8 | **refused** |
| `list_allowed_directories` | id 9 | returns exactly the one directory given on the command line |

**The confinement holds on all three escapes I tried**, including the symlink —
which is the one a `startswith` check misses and the one JS2's own policy
needed a resolved parent-chain test to catch. On the evidence of these four
refusals I think the "secure" in its self-reported name is earned on the axis
it is claiming.

### Two things the declarations do not say

**1. The package can open a network port; the annotations suggest otherwise.**
Every tool is marked `openWorldHint: false`, and `dist/index.js` carries:

```
export const TRANSPORTS = ["stdio", "streamable-http"];
```

with `dist/http.js` importing `node:http` and calling `httpServer.listen({host, port})`.
Run as I ran it, it never opened a socket — the default transport is stdio and
`node:http` is the only network import in the package. **This is not a
contradiction**, and I want to be exact rather than dramatic: `openWorldHint`
describes whether a *tool* reaches outside the system, not which transport the
*server* was started with, and the usage line advertises `--transport` plainly.
It is a place where a reader skimming annotations could conclude "this never
opens a socket" and be wrong about the package while right about the tools.

**2. A refusal discloses where a symlink points.** The reply to id 6 is:

> Access denied - symlink target outside allowed directories:
> `.../mcpeval/outside/secret.txt` not in `.../mcpeval/sandbox`

The client asked about `sandbox/escape-link.txt` and learned the path the
symlink resolves to — a path outside the allowed directory, which it was not
entitled to read. The content is protected and the *location* is not. For a
filesystem server this is a reasonable trade for a legible error message, and
it is worth knowing before pointing one at a directory whose layout is itself
sensitive.

## What a compatible client is entitled to, which is the real finding

The interesting question for this server is not what it refuses. It is what it
grants, and the honest answer is: **inside the allowed directory, a compatible
client can do almost anything.** `write_file` succeeded in the transcript, and
its own description says it "will overwrite existing files without warning".
`move_file` and `edit_file` are there too. The allowed-directory boundary is a
wall around a room in which the client has a free hand.

The package does ship the controls for this — `--read-only`, `--read-only-dir
<dir>` and `--confine-roots` are in its usage line — but **none of them is on
by default**, and nothing in the protocol handshake tells a client which of them
is in force. `list_allowed_directories` reports *where*, never *how much*.

## Trust decision — conditional accept, and the condition is the flag

**I would run it, with `--read-only`, pointed at a directory I chose
deliberately. I would not run it writable over a directory I had not inventoried
first.**

The reasoning: the confinement is the part I tested and it held against the
three escapes that matter. What I cannot test away is that the default
configuration is read/write, that overwriting is explicitly unwarned, and that
a client which has been told something persuasive can use `write_file` exactly
as the protocol intends. That is not a defect in the server — it is the
capability it exists to provide — but "the sandbox is sound" and "the sandbox is
safe to hand out" are different claims, and only the first one is what my
transcript establishes.

**What this evaluation did not check**, stated because four refusals in a
scratch directory is not an audit: I did not test a hardlink, a `TOCTOU` race
between the check and the open, a path containing a NUL byte, a Windows
8.3-style short name, or the `streamable-http` transport at all. I read the
import graph and ran nine requests. Someone who needed to depend on this should
read `dist/path-validation.js` properly, which I did not.

---

## The same three questions, side by side

| | mine | theirs |
|---|---|---|
| tools declared | 1 | 16 |
| can name a path | no — there is no path argument | yes, every tool |
| writes to disk | never | yes, by default, unwarned |
| network capability in the package | none | `node:http`, behind a non-default flag |
| confinement tested | not applicable — nothing to confine | 3 escapes, all refused |
| what a client gets that it should not | nothing I found | the location a symlink resolves to |
| trust decision | accept | accept **with `--read-only`** |

The contrast is the lesson, and it is not that mine is better — it does one
thing. It is that **the question "is this server safe" is not answerable about
a server, only about a server plus a configuration**. Mine has no
configuration, so the answer is a property of the code. Theirs has four flags
that change the answer completely, none of them visible to a client at
handshake time, and the default is the permissive one.
