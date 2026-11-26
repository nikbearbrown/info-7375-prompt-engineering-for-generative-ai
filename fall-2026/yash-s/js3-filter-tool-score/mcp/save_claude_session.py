"""Save Claude's side of a real headless session (stream-json) for the repo, with only
local machine details removed, and say exactly what was removed.

    python3 mcp/save_claude_session.py RAW.jsonl OUT.jsonl

Every message is kept, in order, with its text unchanged, except:
  1. The start-up message (type "system", subtype "init") keeps only the fields in
     KEEP_INIT. The others describe this machine: folders, the session socket,
     installed plugins, skills and agents.
  2. In every string, the home folder path is replaced by "~".
  3. The top-level field "credential_expires_at" is dropped from the final message.
The first line of OUT is a record of these changes. The raw file stays on my machine.
"""
import json
import sys
from pathlib import Path

KEEP_INIT = ["type", "subtype", "session_id", "tools", "mcp_servers", "model", "permissionMode",
             "apiKeySource", "claude_code_version", "output_style"]
DROP_TOP = ["credential_expires_at"]


def scrub(value, home):
    if isinstance(value, str):
        return value.replace(home, "~")
    if isinstance(value, list):
        return [scrub(v, home) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v, home) for k, v in value.items()}
    return value


def main(raw_path, out_path):
    home = str(Path.home())
    lines, removed = [], []
    for line in Path(raw_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        m = json.loads(line)
        if m.get("type") == "system" and m.get("subtype") == "init":
            removed += [k for k in m if k not in KEEP_INIT]
            m = {k: m[k] for k in KEEP_INIT if k in m}
        for k in DROP_TOP:
            if k in m:
                removed.append(k)
                m.pop(k)
        lines.append(json.dumps(scrub(m, home), ensure_ascii=False))
    note = {"type": "saved-copy-note",
            "note": "Real Claude Code headless session, saved by mcp/save_claude_session.py. Messages are unchanged "
                    "except: the init message keeps only " + ", ".join(KEEP_INIT) + "; the home folder path is "
                    "replaced by '~'; and these fields were dropped: " + ", ".join(sorted(set(removed))) + "."}
    with open(out_path, "x", encoding="utf-8") as f:
        f.write(json.dumps(note) + "\n" + "\n".join(lines) + "\n")
    print(f"wrote {out_path} ({len(lines)} messages; dropped {len(set(removed))} machine-detail fields)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
