"""The hand-label sheet (brief Step 2.1 and 2.4): which postings Siddi judges, chosen by fixed seeds, shown blind.

Audit part (seed 7375): 30 random rejects, every close call (score = threshold - 1 or threshold), every kept
posting. Held-out part (seed 7376): 20 postings not in the audit part, 12 from titles with a data/ML/AI word and
8 from everything else. The sheet never shows a verdict, a score, or which part an item came from."""
from __future__ import annotations

import hashlib
import html
import json
import random
import re
from html.parser import HTMLParser

from .textprep import normalize_quotes, whole_word

AUDIT_SEED, HELD_SEED = 7375, 7376
N_RANDOM_REJECTS = 30
HELD_A, HELD_B = 12, 8
HELD_A_WORDS = ("data", "machine learning", "ml", "ai", "analytics", "analyst", "scientist")
COMPANY = {"stripe": "Stripe", "notion": "Notion", "Canva": "Canva"}


def key(r) -> str:
    return f"{r['board']}:{r['id']}"


def select(results: list[dict], threshold: int) -> list[dict]:
    """Returns [{key, roles}] in selection order (not the order Siddi sees)."""
    by_key = {key(r): r for r in results}
    roles: dict[str, list[str]] = {}

    def add(k, role):
        roles.setdefault(k, []).append(role)

    rejects = sorted(key(r) for r in results if r["verdict"] == "reject")
    for k in random.Random(AUDIT_SEED).sample(rejects, N_RANDOM_REJECTS):
        add(k, "random_reject")
    for r in sorted(results, key=key):
        if r["score"] is not None and r["score"] in (threshold - 1, threshold):
            add(key(r), "close_call")
        if r["verdict"] == "keep":
            add(key(r), "kept")
        if r["verdict"] == "cannot_tell":
            add(key(r), "cannot_tell")
    rest = sorted(k for k in by_key if k not in roles)
    pool_a = [k for k in rest if any(whole_word(w).search(by_key[k]["title"].lower()) for w in HELD_A_WORDS)]
    pool_b = [k for k in rest if k not in set(pool_a)]
    rng = random.Random(HELD_SEED)
    for k in rng.sample(pool_a, HELD_A):
        add(k, "held_out_A")
    for k in rng.sample(pool_b, HELD_B):
        add(k, "held_out_B")
    return [{"key": k, "roles": v} for k, v in roles.items()]


class _Readable(HTMLParser):
    BLOCK = {"li", "p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("• ")

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def readable_text(posting: dict) -> str:
    """What a person reads: the whole posting, tags removed, case kept, nothing cut."""
    if not posting.get("text"):
        return f"(no text collected: {posting.get('text_missing')})"
    if posting["text_format"] == "plain":
        t = posting["text"]
    else:
        p = _Readable()
        p.feed(html.unescape(posting["text"]))
        p.close()
        t = "".join(p.parts)
    t = normalize_quotes(t).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in t.split("\n")]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def build(results: list[dict], postings: list[dict], threshold: int, extra: list[dict] | None = None):
    """Returns (manifest, items shown on the sheet). `extra` = already-labelled postings, never shown."""
    chosen = select(results, threshold)
    order = list(range(len(chosen)))
    random.Random(AUDIT_SEED + HELD_SEED).shuffle(order)
    by_key = {key(p): p for p in postings}
    items, manifest_items = [], []
    for n, idx in enumerate(order, start=1):
        c = chosen[idx]
        p = by_key[c["key"]]
        items.append({"n": n, "company": COMPANY.get(p["board"], p["board"]), "title": p["title"],
                      "location": p["location"].get("name") or "(none given)", "text": readable_text(p)})
        manifest_items.append({"n": n, "key": c["key"], "roles": c["roles"]})
    shown = json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")
    manifest = {"audit_seed": AUDIT_SEED, "held_out_seed": HELD_SEED, "threshold": threshold,
                "counts": {role: sum(1 for m in manifest_items if role in m["roles"])
                           for role in ("random_reject", "close_call", "kept", "cannot_tell",
                                        "held_out_A", "held_out_B")},
                "items_shown_sha256": hashlib.sha256(shown).hexdigest(), "items": manifest_items}
    return manifest, items


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>JS3 Hand Labels</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a64;--line:#dddbd3;--card:#fff;--rel:#1f6f43;--not:#8a2f24;--accent:#2b4c7e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#171716;--fg:#ecebe6;--muted:#a3a29b;--line:#34332f;--card:#1f1f1d;--rel:#5fbf88;--not:#e48a7c;--accent:#8fb0e3}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;margin:0}
main{max-width:860px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:8px 0}
.rule{border:1px solid var(--line);background:var(--card);padding:12px 14px;border-radius:8px}
.rule p{margin:4px 0}
.bar{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:2;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.card{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:12px 14px;margin:14px 0}
.card.done{border-left:4px solid var(--accent)}
.meta{color:var(--muted);font-size:13px}
.title{font-weight:600;font-size:16px;margin:2px 0}
details pre{white-space:pre-wrap;font:13px/1.45 ui-monospace,Consolas,monospace;max-height:420px;overflow:auto;border-top:1px solid var(--line);padding-top:8px}
.btns{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
button{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:transparent;color:var(--fg);cursor:pointer}
button.on.rel{background:var(--rel);color:#fff;border-color:var(--rel)}
button.on.not{background:var(--not);color:#fff;border-color:var(--not)}
input.reason{flex:1;min-width:200px;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--fg)}
textarea{width:100%;height:160px;font:12px ui-monospace,Consolas,monospace;background:var(--card);color:var(--fg);border:1px solid var(--line)}
</style></head><body><main>
<h1>JS3 hand labels: is this posting worth Jordan Lee's time?</h1>
<div class="rule">
<p><b>Your labeling rule (JS1 LABELING.md, 2026-10-31):</b> 1. Data Engineer / AIML roles. 2. 2+ years is too much (FILTER.md v1 settled the cap at 4). 3. Anywhere in the USA. 4. Master's roles and some internships count. 5. When unclear, lean to skill.</p>
<p><b>Jordan Lee (fictional):</b> B.S. Computer Engineering (2024), 2 years' experience; skills python, sql, scala, spark, airflow, kafka, dbt, bigquery, gcp, docker, kubernetes, tableau.</p>
<p class="meta">__N__ postings, shuffled. Nothing on this page says what the filter decided. Judge each one yourself; the reason box is optional. When done, copy the box at the bottom into chat (or tell Claude to read it from this page).</p>
</div>
<div class="bar"><span id="progress"></span><button onclick="window.scrollTo(0,document.body.scrollHeight)">Go to results</button></div>
<div id="cards"></div>
<h2>Results</h2>
<textarea id="out" readonly></textarea>
</main>
<script>
const ITEMS = __ITEMS__;
const KEY = "js3-hand-labels-v1";
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { state = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} render(); }
function esc(s){ return s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c])); }
const cards = document.getElementById("cards");
ITEMS.forEach(it => {
  const d = document.createElement("div"); d.className = "card"; d.id = "c" + it.n;
  d.innerHTML = `<div class="meta">#${it.n} · ${esc(it.company)}</div><div class="title">${esc(it.title)}</div>
  <div class="meta">${esc(it.location)}</div>
  <details><summary>Posting text</summary><pre>${esc(it.text)}</pre></details>
  <div class="btns"><button class="rel" data-v="relevant">Relevant</button><button class="not" data-v="not_relevant">Not relevant</button>
  <input class="reason" placeholder="reason (optional)"></div>`;
  d.querySelectorAll("button").forEach(b => b.onclick = () => { state[it.n] = Object.assign(state[it.n] || {}, {label: b.dataset.v}); save(); });
  const inp = d.querySelector("input");
  inp.value = (state[it.n] || {}).reason || "";
  inp.oninput = () => { state[it.n] = Object.assign(state[it.n] || {}, {reason: inp.value}); save(); };
  cards.appendChild(d);
});
function render(){
  let done = 0;
  ITEMS.forEach(it => {
    const s = state[it.n] || {}; const d = document.getElementById("c" + it.n);
    d.classList.toggle("done", !!s.label); if (s.label) done++;
    d.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === s.label));
  });
  document.getElementById("progress").textContent = `${done} of ${ITEMS.length} labelled`;
  const out = ITEMS.map(it => ({n: it.n, label: (state[it.n] || {}).label || null, reason: (state[it.n] || {}).reason || ""}));
  document.getElementById("out").value = JSON.stringify(out);
}
render();
</script></body></html>
"""


def page(items: list[dict]) -> str:
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    return PAGE.replace("__ITEMS__", data).replace("__N__", str(len(items)))
