"""A local, blind labeling page for the 80-posting sheet. Not part of the agent.

    python -B scripts/label_server.py            # then open http://127.0.0.1:8765
Shows one posting at a time from out/audit/sheet_blind.json: board, title, location,
employment-type field and full text. No filter score, verdict, set, or Claude output.
Every save rewrites labels/hand_labels.csv atomically (temp file, then rename), so a crash
can never leave it half-written. Listens on 127.0.0.1 only.
"""
import csv
import io
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "out" / "audit" / "sheet_blind.json"
LABELS = ROOT / "labels" / "hand_labels.csv"
FIELDS = ["n", "id", "title", "hand_label", "note", "labeled_at_utc"]
VALID = {"relevant", "not_relevant"}

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>JS3 blind labels</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#e2e1dc;--acc:#2f5d8a;--ok:#2e7d4f;--no:#a33b2b}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#e9e8e3;--mut:#9d9c96;--card:#1f1f1d;--line:#34332f;--acc:#7fb0e0;--ok:#6fc28f;--no:#e5806f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,sans-serif}
header{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);padding:10px 16px;z-index:2}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.mut{color:var(--mut)}
main{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:6px 0}pre{white-space:pre-wrap;font:inherit;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px}
button{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
button.sel.relevant{background:var(--ok);color:#fff;border-color:var(--ok)}button.sel.not_relevant{background:var(--no);color:#fff;border-color:var(--no)}
input[type=text]{flex:1;min-width:240px;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
.grid{display:flex;flex-wrap:wrap;gap:3px;margin-top:6px}.grid span{width:22px;height:18px;font-size:10px;text-align:center;border-radius:3px;background:var(--line);cursor:pointer}
.grid span.relevant{background:var(--ok);color:#fff}.grid span.not_relevant{background:var(--no);color:#fff}.grid span.cur{outline:2px solid var(--acc)}
details{margin:6px 0}.meta{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px}
</style></head><body>
<header>
 <div class="row"><b>Blind label sheet</b><span class="mut" id="prog"></span><span class="mut" id="status"></span></div>
 <details><summary class="mut">Labeling rule (inherited from JS1, LABELING_RULE.md)</summary>
 <p><b>relevant</b> = I would tell Jack Spencer this posting is worth a day of his time to apply. All four must hold:
 (1) the main day-to-day work is data engineering (pipelines, data platforms/infrastructure, data integration, analytics engineering);
 (2) the level fits a 5-year individual contributor (not people management, not Staff/Principal/Director, not roughly 8+ years required, not intern/new-grad/PhD);
 (3) full-time; (4) he meets most stated must-haves, and none is a whole area he has never worked in.
 Ignore location, visa, salary, and the company. Close calls: data science / ML roles are not_relevant unless the main work is pipelines or infrastructure; backend roles are relevant only if centered on data systems. Unclear: pick the label you'd stand behind and start the note with "close call:".
 Jack: Python, SQL, Spark, Airflow, Kafka, dbt, Snowflake, AWS; batch and streaming pipelines; ETL; 5 years; M.S. completed.</p></details>
 <div class="row"><button id="b_rel" data-l="relevant">relevant</button><button id="b_not" data-l="not_relevant">not_relevant</button>
 <input type="text" id="note" placeholder="one-line note: what in the posting decided it (required)">
 <button id="prev">&larr; prev</button><button id="next">save &amp; next &rarr;</button></div>
 <div class="grid" id="grid"></div>
</header>
<main><h1 id="title"></h1><div class="meta" id="meta"></div><pre id="text"></pre></main>
<script>
let sheet=[],labels={},cur=0,pick=null;
const $=id=>document.getElementById(id);
async function load(){sheet=await (await fetch('/api/sheet')).json();labels=await (await fetch('/api/labels')).json();
 const first=sheet.findIndex(s=>!labels[s.n]);cur=first<0?0:first;show();}
function grid(){$('grid').innerHTML=sheet.map((s,i)=>`<span class="${labels[s.n]?labels[s.n].hand_label:''} ${i===cur?'cur':''}" data-i="${i}">${s.n}</span>`).join('');
 $('grid').querySelectorAll('span').forEach(e=>e.onclick=()=>{cur=+e.dataset.i;show();});
 $('prog').textContent=`${Object.keys(labels).length} / ${sheet.length} labeled`;}
function esc(t){return String(t??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function show(){const s=sheet[cur],l=labels[s.n];pick=l?l.hand_label:null;$('note').value=l?l.note:'';
 $('title').textContent=`#${s.n}  ${s.title}`;
 $('meta').innerHTML=`<span class="mut">board</span><span>${esc(s.board)}</span><span class="mut">location</span><span>${esc(s.location)}</span>`+
 `<span class="mut">employment-type field</span><span>${esc(s.employment_type??'(none on this board)')}</span>`+
 `<span class="mut">still listed 2026-11-24</span><span>${s.still_listed_2026_11_24?'yes':'no (seen 2026-11-10 only)'}</span>`+
 `<span class="mut">url</span><span><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.url)}</a></span>`;
 $('text').textContent=s.text;btns();grid();window.scrollTo(0,0);$('status').textContent='';}
function btns(){['b_rel','b_not'].forEach(id=>{const b=$(id);b.className=(pick===b.dataset.l?'sel ':'')+b.dataset.l;});}
$('b_rel').onclick=()=>{pick='relevant';btns();$('note').focus();};$('b_not').onclick=()=>{pick='not_relevant';btns();$('note').focus();};
async function save(){const s=sheet[cur],note=$('note').value.trim();
 if(!pick){$('status').textContent='pick a label first';return false;} if(!note){$('status').textContent='a one-line note is required';return false;}
 const r=await fetch('/api/label',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({n:s.n,id:s.id,hand_label:pick,note})});
 if(!r.ok){$('status').textContent='save failed: '+await r.text();return false;} labels=await r.json();return true;}
$('next').onclick=async()=>{if(await save()){cur=Math.min(cur+1,sheet.length-1);show();$('status').textContent='saved';}};
$('prev').onclick=()=>{cur=Math.max(cur-1,0);show();};
$('note').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('next').click();}});
load();
</script></body></html>"""


def read_labels() -> dict:
    if not LABELS.exists():
        return {}
    with LABELS.open(encoding="utf-8", newline="") as f:
        return {int(r["n"]): r for r in csv.DictReader(f)}


def write_labels(rows: dict) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for n in sorted(rows):
        w.writerow({k: rows[n][k] for k in FIELDS})
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=LABELS.parent, prefix=".hand_labels.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    os.replace(tmp, LABELS)


class Handler(BaseHTTPRequestHandler):
    sheet = []

    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            return self._send(200, PAGE, "text/html")
        if self.path == "/api/sheet":
            return self._send(200, json.dumps(self.sheet, ensure_ascii=False))
        if self.path == "/api/labels":
            return self._send(200, json.dumps(read_labels(), ensure_ascii=False))
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/label":
            return self._send(404, "not found", "text/plain")
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            n, pid, lab, note = int(d["n"]), d["id"], d["hand_label"], " ".join(str(d["note"]).split())
        except (ValueError, KeyError, TypeError):
            return self._send(400, "bad request", "text/plain")
        entry = next((s for s in self.sheet if s["n"] == n), None)
        if entry is None or entry["id"] != pid or lab not in VALID or not note:
            return self._send(400, "label must be relevant|not_relevant with a note, for a posting on the sheet", "text/plain")
        rows = read_labels()
        rows[n] = {"n": n, "id": pid, "title": entry["title"], "hand_label": lab, "note": note,
                   "labeled_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        write_labels(rows)
        self._send(200, json.dumps(read_labels(), ensure_ascii=False))

    def log_message(self, fmt, *args):
        pass


def main() -> int:
    Handler.sheet = json.loads(SHEET.read_text(encoding="utf-8"))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"labeling {len(Handler.sheet)} postings -> {LABELS.relative_to(ROOT)}; open http://127.0.0.1:{port}  (Ctrl+C to stop)")
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
