"""Turn a raw `claude -p --output-format stream-json --verbose` log into a committable transcript of ONLY the
model/tool exchange: prompt, tool calls, tool results, replies. Drops hook output, plugin paths, session ids, the user's
memory and thinking blocks. Usage: python scripts/sanitize_transcript.py <raw.jsonl> <out.md> "<prompt>" "<date>" """
import json
import sys

raw, out, prompt, date = sys.argv[1:5]
lines = ["# Claude Code <-> earlybird-score session\n", f"Date: {date}. Raw log kept private (transcripts/private/, git-ignored).\n",
         "Kept: prompt, tool calls, tool results, replies. Dropped: hook output, plugin paths, session ids, thinking blocks.\n",
         f"\n## Prompt I gave Claude\n\n> {prompt}\n"]
model = version = ""
for l in open(raw, encoding="utf-8"):
    e = json.loads(l)
    if e.get("type") == "system" and e.get("subtype") == "init":
        model, version = e.get("model", ""), e.get("claude_code_version", "")
        lines.append(f"\nModel: `{model}`. Claude Code {version}. MCP server `earlybird-score` status: "
                     f"{[m['status'] for m in e.get('mcp_servers', [])]}.\n")
    elif e.get("type") in ("assistant", "user"):
        for b in e["message"].get("content", []):
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and e["type"] == "assistant":
                lines.append(f"\n### Claude says\n\n{b['text']}\n")
            elif b.get("type") == "tool_use":
                lines.append(f"\n### Claude calls a tool\n\n`{b['name']}` with\n\n```json\n{json.dumps(b['input'], indent=1)}\n```\n")
            elif b.get("type") == "tool_result":
                c = b.get("content")
                text = "".join(x.get("text", "") for x in c) if isinstance(c, list) else str(c)
                lines.append(f"\n### Tool result\n\n```json\n{text}\n```\n")
    elif e.get("type") == "result":
        lines.append(f"\n### Final result (is_error={e.get('is_error')}, turns={e.get('num_turns')}, "
                     f"{e.get('duration_ms')} ms)\n\n{e.get('result')}\n")
open(out, "w", encoding="utf-8").write("".join(lines))
