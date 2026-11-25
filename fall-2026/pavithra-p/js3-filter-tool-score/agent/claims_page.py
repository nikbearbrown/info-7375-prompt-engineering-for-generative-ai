"""The page where I label every claim of the shortlist by hand (the final label), next to the checker's first label."""
import html
import json

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JS3 claim labels</title><style>
body{background:#fafaf7;color:#1d1d1b;font:15px/1.5 system-ui,-apple-system,sans-serif;margin:0 auto;max-width:960px;padding:16px}
.post{border:1px solid #ddd;border-radius:8px;padding:12px 14px;margin:14px 0;background:#fff}
.t{font-weight:600;font-size:16px}.m{color:#6b6b66;font-size:13px}.d{white-space:pre-wrap;font-size:13px;max-height:320px;overflow:auto}
.claim{border-top:1px solid #eee;padding:8px 0}.q{background:#f3f1ea;border-radius:6px;padding:3px 8px;font-size:13px;margin:4px 0}
.mach{font-size:12px;color:#6b6b66}button{margin-right:6px;padding:5px 10px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer}
button.on{background:#1d1d1b;color:#fff}input{width:100%;box-sizing:border-box;margin-top:4px;padding:4px;border:1px solid #ddd;border-radius:6px}
#bar{position:sticky;top:0;background:#fafaf7;padding:8px 0;border-bottom:1px solid #ddd}
</style></head><body>
<div id="bar">JS3 claim labels · <span id="n"></span> · <button id="dl">Download claim-labels.csv</button></div>
<p>For each claim: is it supported, contradicted or insufficient against the posting's own text? Supported only if the quote
is in the posting and says what the claim says. A matching word alone is not enough. The checker's first label is shown in grey;
yours is the one that counts.</p><div id="rows"></div>
<script>
const P=__POSTS__;const KEY="js3-claim-labels-v1";let L={};try{L=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(L))}catch(e){}count()}
const total=P.reduce((a,p)=>a+p.claims.length,0);
function count(){document.getElementById("n").textContent=Object.values(L).filter(x=>x.label).length+" of "+total+" claims labelled"}
const box=document.getElementById("rows");
P.forEach((p,i)=>{const d=document.createElement("div");d.className="post";
d.innerHTML=`<div class="t">${i+1}. ${p.title}</div><div class="m">${p.key} · <a href="${p.url}" target="_blank" rel="noopener">posting</a></div>
<details><summary>Posting text</summary><div class="d"></div></details>`;d.querySelector(".d").textContent=p.text;
p.claims.forEach((c,j)=>{const id=p.key+"#"+(j+1);const e=document.createElement("div");e.className="claim";
e.innerHTML=`<div><b>${c.about}</b>: <span class="c"></span></div><div class="q"></div><div class="mach"></div>
<div><button data-v="supported">supported</button><button data-v="contradicted">contradicted</button><button data-v="insufficient">insufficient</button></div><input placeholder="note (optional)">`;
e.querySelector(".c").textContent=c.claim;e.querySelector(".q").textContent=c.quote?"\\u201c"+c.quote+"\\u201d":"(no quote)";
e.querySelector(".mach").textContent="checker: "+c.machine_label+" ("+c.machine_reason+")";
const inp=e.querySelector("input");inp.value=(L[id]||{}).note||"";
function paint(){e.querySelectorAll("button").forEach(b=>b.classList.toggle("on",(L[id]||{}).label===b.dataset.v))}
e.querySelectorAll("button").forEach(b=>b.onclick=()=>{L[id]=Object.assign(L[id]||{},{label:b.dataset.v,at:new Date().toISOString()});save();paint()});
inp.oninput=()=>{L[id]=Object.assign(L[id]||{},{note:inp.value});save()};paint();d.appendChild(e)});box.appendChild(d)});count();
document.getElementById("dl").onclick=()=>{const q=s=>'"'+String(s||"").replace(/"/g,'""')+'"';const lines=["claim_id,about,claim,quote,machine_label,my_label,note,labelled_at"];
P.forEach(p=>p.claims.forEach((c,j)=>{const id=p.key+"#"+(j+1);const l=L[id]||{};lines.push([q(id),q(c.about),q(c.claim),q(c.quote),q(c.machine_label),q(l.label),q(l.note),q(l.at)].join(","))}));
const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([lines.join("\\n")+"\\n"],{type:"text/csv"}));a.download="claim-labels.csv";a.click()};
</script></body></html>
"""


def build(entries, text_by_key):
    posts = [{"key": e["key"], "title": html.escape(e["title"]), "url": html.escape(e["url"]),
              "text": text_by_key[e["key"]], "claims": e["claims"]} for e in entries if e["valid"]]
    return PAGE.replace("__POSTS__", json.dumps(posts, ensure_ascii=False).replace("</", "<\\/"))
