"""A local page for my hand check of every shortlist claim (FILTER.md E4). Blind to the checker's label.

    python -B scripts/claim_server.py --version v1.0     # then open http://127.0.0.1:8766
Shows, one claim at a time: the posting (title + full text, the quote highlighted where it occurs),
the claim, its kind, and its quote. It does NOT show Claude's checker label or the agent's answer.
I label supported / contradicted / insufficient with a note. Saved atomically to
labels/claim_checks_<version>.csv after every claim.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import label_server as ls  # noqa: E402  (reuses its atomic CSV writer)
from draw_sample import raw_jobs  # noqa: E402

FIELDS = ["k", "id", "claim_no", "kind", "claim", "quote", "my_label", "my_note", "labeled_at_utc"]
VALID = {"supported", "contradicted", "insufficient"}

PAGE = ls.PAGE.split("<header>")[0].replace("JS3 blind labels", "JS3 claim check") + r"""<header>
 <div class="row"><b>Claim check (blind to the checker)</b><span class="mut" id="prog"></span><span class="mut" id="status"></span></div>
 <details><summary class="mut">Evidence rules (FILTER.md E1-E3)</summary><p>
 <b>supported</b>: the quote is in the posting and, read in its own sentence, states what the claim says.
 <b>contradicted</b>: some part of the posting states the opposite (say which, in the note).
 <b>insufficient</b>: no quote; or the quote only mentions the keyword without stating the claim (a nice-to-have cited as a requirement, the company's product cited as the job's duties, boilerplate cited as the work).
 Judge only against the posting text, not your view of the job.</p></details>
 <div class="row"><button data-l="supported">supported</button><button data-l="contradicted">contradicted</button><button data-l="insufficient">insufficient</button>
 <input type="text" id="note" placeholder="one-line note (required)"><button id="prev">&larr; prev</button><button id="next">save &amp; next &rarr;</button></div>
 <div class="grid" id="grid"></div>
 <p id="claimbox" style="margin:8px 0 0"></p>
</header>
<main><h1 id="title"></h1><pre id="text"></pre></main>
<style>mark{background:#f3d36b;color:#000}button.sel{outline:3px solid var(--acc)}
.grid span.supported{background:var(--ok);color:#fff}.grid span.contradicted{background:var(--no);color:#fff}.grid span.insufficient{background:#8a7a3a;color:#fff}</style>
<script>
let sheet=[],labels={},cur=0,pick=null;const $=id=>document.getElementById(id);
const esc=t=>String(t??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
async function load(){sheet=await (await fetch('/api/sheet')).json();labels=await (await fetch('/api/labels')).json();
 const f=sheet.findIndex(s=>!labels[s.k]);cur=f<0?0:f;show();}
function grid(){$('grid').innerHTML=sheet.map((s,i)=>`<span class="${labels[s.k]?labels[s.k].my_label:''} ${i===cur?'cur':''}" data-i="${i}">${s.k}</span>`).join('');
 $('grid').querySelectorAll('span').forEach(e=>e.onclick=()=>{cur=+e.dataset.i;show();});$('prog').textContent=`${Object.keys(labels).length} / ${sheet.length} checked`;}
function show(){const s=sheet[cur],l=labels[s.k];pick=l?l.my_label:null;$('note').value=l?l.my_note:'';
 $('title').textContent=`${s.title}  (${s.board})`;
 $('claimbox').innerHTML=`<b>#${s.k} · ${esc(s.kind)}</b> &nbsp; <b>Claim:</b> ${esc(s.claim)}<br><b>Quote:</b> ${s.quote?'"'+esc(s.quote)+'"':'<i>(no quote)</i>'}`;
 let html=esc(s.text);
 if(s.quote){const words=s.quote.trim().split(/\s+/).map(w=>esc(w).replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
  try{const re=new RegExp(words.join('\\s+'),'i');const m=html.match(re);html=m?html.replace(re,x=>`<mark id="hit">${x}</mark>`):'<b>[quote not found in this text]</b>\n\n'+html;}catch(e){}}
 $('text').innerHTML=html;document.querySelectorAll('button[data-l]').forEach(b=>b.classList.toggle('sel',b.dataset.l===pick));grid();
 const h=document.getElementById('hit');if(h)h.scrollIntoView({block:'center'});else window.scrollTo(0,0);$('status').textContent='';}
document.querySelectorAll('button[data-l]').forEach(b=>b.onclick=()=>{pick=b.dataset.l;show_sel();$('note').focus();});
function show_sel(){document.querySelectorAll('button[data-l]').forEach(b=>b.classList.toggle('sel',b.dataset.l===pick));}
async function save(){const s=sheet[cur],note=$('note').value.trim();if(!pick){$('status').textContent='pick a label';return false;}
 if(!note){$('status').textContent='a note is required';return false;}
 const r=await fetch('/api/label',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({k:s.k,id:s.id,my_label:pick,my_note:note})});
 if(!r.ok){$('status').textContent='save failed: '+await r.text();return false;}labels=await r.json();return true;}
$('next').onclick=async()=>{if(await save()){cur=Math.min(cur+1,sheet.length-1);show();$('status').textContent='saved';}};
$('prev').onclick=()=>{cur=Math.max(cur-1,0);show();};
$('note').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('next').click();}});load();
</script></body></html>"""


def build_sheet(version: str) -> list:
    run = json.loads((ROOT / "out" / "shortlist" / version / "run.json").read_text(encoding="utf-8"))
    texts = raw_jobs()
    sheet, k = [], 0
    for pid in run["shortlist"]:
        r = run["records"][pid]
        for j, c in enumerate(r.get("claims", []), 1):
            k += 1
            sheet.append({"k": k, "id": pid, "claim_no": j, "kind": c["kind"], "claim": c["claim"], "quote": c["quote"],
                          "title": r["title"], "board": r["board"], "text": texts[pid]})
    return sheet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1.0")
    ap.add_argument("--port", type=int, default=8766)
    args = ap.parse_args()
    sheet = build_sheet(args.version)
    out = ROOT / "labels" / f"claim_checks_{args.version}.csv"
    by_k = {s["k"]: s for s in sheet}

    def read():
        if not out.exists():
            return {}
        import csv
        with out.open(encoding="utf-8", newline="") as f:
            return {int(r["k"]): r for r in csv.DictReader(f)}

    class H(ls.Handler):
        def do_GET(self):
            if self.path == "/":
                return self._send(200, PAGE, "text/html")
            if self.path == "/api/sheet":
                return self._send(200, json.dumps(sheet, ensure_ascii=False))
            if self.path == "/api/labels":
                return self._send(200, json.dumps(read(), ensure_ascii=False))
            self._send(404, "not found", "text/plain")

        def do_POST(self):
            try:
                d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                k, pid, lab, note = int(d["k"]), d["id"], d["my_label"], " ".join(str(d["my_note"]).split())
            except (ValueError, KeyError, TypeError):
                return self._send(400, "bad request", "text/plain")
            s = by_k.get(k)
            if s is None or s["id"] != pid or lab not in VALID or not note:
                return self._send(400, "label must be supported|contradicted|insufficient with a note", "text/plain")
            rows = read()
            rows[k] = {**{f: s.get(f, "") for f in FIELDS}, "my_label": lab, "my_note": note,
                       "labeled_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            ls.LABELS, ls.FIELDS = out, FIELDS
            ls.write_labels(rows)
            self._send(200, json.dumps(read(), ensure_ascii=False))

    srv = ThreadingHTTPServer(("127.0.0.1", args.port), H)
    print(f"checking {len(sheet)} claims -> {out.relative_to(ROOT)}; open http://127.0.0.1:{args.port}")
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
