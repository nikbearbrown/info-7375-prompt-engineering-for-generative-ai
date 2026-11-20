# TOOLSERVER.md — Job-Search Agent 3: the agent as a tool, and two servers evaluated

**Author:** Prasad Shinde
**Written:** 2026-11-20
**Version:** v1 — 2026-11-20
**Rests on:** tools/mcp_server.py and tools/mcp_client.py (JS3-CP10a); CONTRACT.md v0.11 and v0.12; the transcripts in transcripts/ (JS3-CP10c, CP10d).

## 1. What I offered Claude
(Brief: "Offer one capability ... to Claude through a small tool server that speaks the Model Context Protocol ... Write it from scratch ... Preserve the real transcript in both directions.")

One tool, score_posting(board_key, posting_id). It judges one posting from the frozen corpus with FILTER v2, and returns the verdict, C1–C4 with their reasons, the score and, for a kept posting, the agent's claims. The server is tools/mcp_server.py: JSON-RPC 2.0 over stdio, Python standard library only, no MCP SDK. It implements initialize, notifications/initialized, ping, tools/list and tools/call, at protocol versions 2025-11-25, 2025-06-18 and 2024-11-05.

**The real transcript, both directions,** is transcripts/mcp_server_2026-11-20T190550Z.jsonl: every line Claude Code (the desktop app) sent and every line the server sent, unaltered. Claude Code's own account of the session is transcripts/claude_code_session_2026-11-20T1905Z.md. In order:
1. Claude Code sent server/discover, the probe of the 2026-07-28 protocol, which drops the initialize handshake. The server does not implement it, and answered -32601, method not found.
2. Claude Code fell back to initialize, asking for 2025-11-25, and the server agreed to 2025-11-25.
3. Then notifications/initialized, tools/list, and two tools/call. greenhouse:stripe 7737124 came back relevant, with its four claims, identical to output/filter_v2_2026-11-19T201210Z/. An unknown id came back as an isError result that repeats nothing the client sent.

The scripted client, tools/mcp_client.py (standard library only), made two more transcripts. One is a good call (client_js3_good_call.jsonl). The other is a posting from the final's sealed set, read from vault/ by the shell so that no sealed id was typed into any chat (client_js3_sealed_refusal.jsonl). It was refused, with no id in the message.

## 2. My server, evaluated as if someone else wrote it
(Brief: "evaluate it the way you would a server someone else wrote: what it declares versus what it does, what a compatible client is not entitled to, and your trust decision about it.")

**What it declares:** one tool. Its description says it judges one posting from the frozen corpus, never returns the posting's text, and refuses sealed postings. Its inputSchema allows exactly board_key (one of four values) and posting_id, and nothing else.

**What it does, and how I know:**
- It reads only the corpus files, the manifest, the two sealed id files and the persona; it writes only its transcript; it makes no network request. tests/test_mcp.py checks all three, and I read the code.
- It refuses sealed postings before anything is looked up. The final's-set transcript shows the refusal, and the tests show the corpus is never loaded for it.
- It never returns body text: the only posting words a result can carry are the seniority word or years phrase that failed C4. The tests check this, and the two real results show it.
- It answers newer clients by failing their probe, not by speaking their protocol: it does not implement 2026-07-28. Claude Code fell back; another client might not.

**What a compatible client is not entitled to:**
- any posting's text, or any posting in the sealed sets, whatever it asks;
- a protocol newer than 2025-11-25, since server/discover is not answered;
- a verdict from any other filter version, since the tool always judges with FILTER v2;
- treating the description as a guarantee. The description is my claim about the code; the tests and transcripts are the evidence.

**My trust decision:** I trust it for this use, scoring development postings for Alex on my own machine, because I can check every claim above in the code, the tests and the transcripts, and its reach is small: it reads five kinds of file, writes in one place, and uses no network. I would not trust it to keep the sealed sets sealed against a determined user of the same machine: the refusal lives in the server, but the vault files are plain files right next to it.

## 3. A server someone else wrote: @modelcontextprotocol/server-filesystem
(Brief: "Evaluate one other tool server from a source you can name the same way.")

**The source:** the MCP project's reference filesystem server, published on npm as @modelcontextprotocol/server-filesystem, from the modelcontextprotocol/servers repository. I probed it with my scripted client, giving it one throwaway folder, /tmp/fs_probe, holding one file.

**What happened:**
- npm's latest version, 2.4.0, declares node >=24. On this Mac's Node 20, it crashed before answering initialize (transcripts/client_filesystem_list.jsonl). A compatible client cannot rely on a server starting just because its package installs.
- The date-numbered 2026.8.31 ran, although npm marks it deprecated ("Date-based versions are no longer published"). It identified itself as secure-filesystem-server 0.2.0, at protocol 2025-11-25 (transcripts/client_filesystem_2026.8.31_*.jsonl). The package has two version lines, and the one npm calls latest is not the one that ran here.
- It declared 14 tools: read_file (deprecated), read_text_file, read_media_file, read_multiple_files, write_file, edit_file, create_directory, list_directory, list_directory_with_sizes, directory_tree, move_file, search_files, get_file_info and list_allowed_directories. Four of them change files: write_file, edit_file and move_file are annotated destructive, and create_directory is not.
- Given no roots by my client, it fell back to its command-line folder, resolved /tmp to /private/tmp by itself, and allowed both.
- read_text_file inside the folder returned the file. Outside it, /etc/hosts was refused: "Access denied - path outside allowed directories: /etc/hosts not in /tmp/fs_probe, /private/tmp/fs_probe".

**What it declares versus what it does:** the folder limit held on the one read I tried outside it. The annotations (readOnlyHint, destructiveHint, openWorldHint) are hints about the tools, not limits on them. Its refusal repeats the requested path and the allowed folders back to the client, which mine deliberately never does. I did not test writes, moves, symlinks or search patterns, so I make no claim about them.

**What a compatible client is not entitled to:** that the annotations are enforced; that the allowed-folder check holds for paths I did not try; that the server stays inside the folder at all. The check is the server's own code, and the process runs with my user's full permissions: through npx, it is code downloaded from npm and run on my machine.

**My trust decision:** I would use it only with a throwaway folder or one I could afford to lose, only at a pinned version I had probed, and only with its read tools unless I watched every write. I would not point it at my repository or my home folder. Trust here rests on the package's source and its maintainers, which I have not audited, not on its descriptions.

## 4. What this does not show
- One real Claude Code session and four scripted probes. The protocol fallback I saw is one client's behavior on one day.
- I did not test the filesystem server's write tools, its symlink handling or large inputs.
- My server's tests were written by Claude Code to my prompts; no one else has reviewed the server.

## Changelog
- **v1 — 2026-11-20.** Written after the transcripts were committed. Claude (Claude.ai) typed it at my request from the committed transcripts; the trust decisions are mine.