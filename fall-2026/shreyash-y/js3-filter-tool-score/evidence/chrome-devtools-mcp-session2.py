"""Session 2 with chrome-devtools-mcp: is it useful for checking a job posting? One public posting page,
read-only tools only (no click, fill, type or upload)."""
import json, os, re, sys, pathlib
sys.path.insert(0, os.getcwd())
from js3.mcp_client import Client, PROTOCOL
CDM = os.path.expanduser("~/.npm/_npx/ba38acecdf97096f/node_modules/chrome-devtools-mcp")
url = {json.loads(l)["key"]: json.loads(l) for l in open("data/corpus.jsonl")}["klaviyo:7792539003"]["url"]
env = dict(os.environ, CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS="1", CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS="1")
c = Client(["node", f"{CDM}/build/src/bin/chrome-devtools-mcp.js", "--isolated", "--headless",
            "--usageStatistics=false", "--performanceCrux=false"],
           "transcripts/other-server/chrome-devtools-mcp-1.10.1-posting-check-2026-11-25.jsonl", env=env)
def text(r):
    return "\n".join(x.get("text", "") for x in (r.get("result") or {}).get("content", []) if x.get("type") == "text")
try:
    c.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "js3-eval-client", "version": "1.0.0"}})
    c.notify("notifications/initialized")
    c.request("tools/list", {})
    pages = c.request("tools/call", {"name": "list_pages", "arguments": {}}, timeout=120)
    t = text(pages); print("LIST_PAGES:", t[:300])
    m = re.search(r"(\d+):", t); pid = int(m.group(1)) if m else 1
    nav = c.request("tools/call", {"name": "navigate_page", "arguments": {"pageId": pid, "type": "url", "url": url, "timeout": 30000}}, timeout=120)
    print("NAVIGATE:", text(nav)[:300])
    snap = c.request("tools/call", {"name": "take_snapshot", "arguments": {"pageId": pid}}, timeout=120)
    st = text(snap); print("SNAPSHOT chars:", len(st)); print(st[:1200])
    net = c.request("tools/call", {"name": "list_network_requests", "arguments": {"pageId": pid, "pageSize": 200}}, timeout=120)
    nt = text(net); hosts = sorted(set(re.findall(r"https?://([^/\s\"']+)", nt)))
    print("NETWORK hosts:", len(hosts), hosts)
finally:
    c.close()
