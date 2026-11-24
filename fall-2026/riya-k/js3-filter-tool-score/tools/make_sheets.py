"""Draw the audit + held-out samples from filter v1's decisions (seeded), and write one BLIND labeling sheet.

    python3 tools/make_sheets.py            # writes audit/sample.json and audit/label-sheet.html

Seed 7375, fixed. The sheet never shows the filter's decision, score or stratum; items are shuffled together, so the
labeler cannot tell a reject from a keep or an audit item from a held-out one. sample.json keeps the mapping.

Strata (disjoint):
  audit   R  32 random rejected            (brief: at least 30 random rejects)
          N  10 closest calls: 6 gate-passing rejects at score 5, 4 from {kept at score 6, A3 abstentions}
          K  10 random kept
          T   6 random cannot_tell
  heldout H  20: 6 kept, 4 near (gate-passing score 4-5 or A3), 10 random from everything else
"""

import html
import json
import re
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import corpus  # noqa: E402
from js3.text import plain_text  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
SEED = 7375
CUES = ["you might be a good fit", "minimum qualifications", "qualifications", "requirements", "what you'll bring",
        "what you bring", "you may be a good fit", "about you", "you have", "we're looking for", "you will"]


REQ_CUES = ["you may be a good fit", "you might be a good fit", "minimum qualifications", "basic qualifications",
            "required qualifications", "preferred qualifications", "qualifications", "requirements", "what you'll bring",
            "what you bring", "what we're looking for", "what we look for", "who you are", "about you",
            "you might thrive", "you'll thrive", "we'd love to hear from you if", "you have:"]
REQ_END = ["benefits", "the annual compensation", "annual salary", "compensation", "pay range", "salary range",
           "logistics", "about databricks", "about anthropic", "about us", "our commitment", "equal opportunity",
           "we encourage you to apply", "pay transparency", "local pay range"]


def lines(content):
    """HTML -> list of visible lines, keeping list items and paragraphs apart (only for showing the labeler)."""
    t = html.unescape(html.unescape(content or ""))
    t = re.sub(r"(?i)<\s*(br|/li|/p|/h\d|/div|li)[^>]*>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return [re.sub(r"\s+", " ", x).strip() for x in t.split("\n") if re.sub(r"\s+", " ", x).strip()]


def requirements(ls, max_lines=22):
    """The qualifications part of the posting, verbatim: from the first qualification cue to the pay/benefits part."""
    low = [x.lower() for x in ls]
    start = next((i for i, x in enumerate(low) if any(c in x for c in REQ_CUES) and len(x) < 200), None)
    if start is None:
        return []
    out = []
    for i in range(start, len(ls)):
        if i > start and any(low[i].startswith(e) or (e in low[i] and len(low[i]) < 80) for e in REQ_END):
            break
        out.append(ls[i])
    return out[:max_lines] + (["… (more in full text)"] if len(out) > max_lines else [])


def year_lines(ls):
    """Every line that mentions a number of years, verbatim."""
    return [x for x in ls if re.search(r"\d\s*\+?\s*(?:-|–|to)?\s*\d*\s*\+?\s*(years?|yrs)\b", x, re.I)]


def snippet(text, n=900):
    low = text.lower()
    starts = [low.find(c) for c in CUES if low.find(c) > 0]
    a = min(starts) if starts else 0
    return ("…" if a else "") + text[a:a + n] + ("…" if a + n < len(text) else "")


def draw(recs, rng):
    key = lambda r: (r["board"], r["id"])  # noqa: E731
    used = set()

    def take(pool, k):
        pool = [r for r in pool if key(r) not in used]
        pool.sort(key=key)
        got = rng.sample(pool, min(k, len(pool)))
        used.update(key(r) for r in got)
        return got

    gate_pass_rej = lambda lo, hi: [r for r in recs if r["decision"] == "rejected" and not r["gates_failed"]  # noqa
                                    and lo <= r["score"] <= hi]
    a3 = [r for r in recs if (r["abstain"] or "").startswith("A3")]
    kept6 = [r for r in recs if r["decision"] == "kept" and r["score"] == 6]
    out = []
    out += [("audit", "N", r) for r in take(gate_pass_rej(5, 5), 6) + take(kept6 + a3, 4)]
    out += [("audit", "R", r) for r in take([r for r in recs if r["decision"] == "rejected"], 32)]
    out += [("audit", "K", r) for r in take([r for r in recs if r["decision"] == "kept"], 10)]
    out += [("audit", "T", r) for r in take([r for r in recs if r["decision"] == "cannot_tell"], 6)]
    out += [("heldout", "H", r) for r in take([r for r in recs if r["decision"] == "kept"], 6)]
    out += [("heldout", "H", r) for r in take(gate_pass_rej(4, 5) + a3, 4)]
    out += [("heldout", "H", r) for r in take(recs, 10)]
    return out


def main():
    rng = random.Random(SEED)
    recs = [json.loads(l) for l in open(HERE / "out" / "v1" / "decisions.jsonl")]
    posts = corpus.by_key(corpus.load())
    drawn = draw(recs, rng)
    order = list(range(len(drawn)))
    rng.shuffle(order)
    items = []
    for n, i in enumerate(order, 1):
        split, stratum, r = drawn[i]
        items.append({"item": n, "split": split, "stratum": stratum, "board": r["board"], "id": r["id"],
                      "title": r["title"], "v1_decision": r["decision"], "v1_score": r["score"]})
    (HERE / "audit").mkdir(exist_ok=True)
    (HERE / "audit" / "sample.json").write_text(json.dumps(
        {"seed": SEED, "drawn_from": "out/v1/decisions.jsonl", "note": "mapping hidden from the labeling sheet",
         "items": items}, indent=1, ensure_ascii=False) + "\n")
    cards = []
    for it in items:
        p = posts[(it["board"], it["id"])]
        text = plain_text(p.get("content", ""))
        emp = p.get("employment")
        ls = lines(p.get("content", ""))
        yl, req = year_lines(ls), requirements(ls)
        years_html = ("".join(f"<li>{html.escape(x)}</li>" for x in yl) if yl
                      else "<li><i>No years mentioned anywhere in the posting.</i></li>")
        req_html = ("".join(f"<li>{html.escape(x)}</li>" for x in req) if req
                    else "<li><i>No qualifications section found; see full text.</i></li>")
        cards.append(f"""
<section class="card" id="i{it['item']}" data-item="{it['item']}">
  <h2>#{it['item']} · {html.escape(it['title'])}</h2>
  <p class="meta"><b>{html.escape(it['board'].split(':')[1])}</b> · {html.escape(p['location']['name'] or '(no location)')}
     · employment field: {html.escape(emp) if emp else '(board does not say)'} · {len(text)} chars ·
     <a href="{html.escape(p.get('absolute_url', ''))}" target="_blank" rel="noopener">posting</a></p>
  <div class="box yrs"><b>Years of experience</b> (lines copied from the posting)<ul>{years_html}</ul></div>
  <div class="box req"><b>Requirements</b> (copied from the posting)<ul>{req_html}</ul></div>
  <details><summary>full text</summary><p class="full">{html.escape(text)}</p></details>
  <div class="ans">
    <label><input type="radio" name="v{it['item']}" value="show"> Show to Arya</label>
    <label><input type="radio" name="v{it['item']}" value="not"> Not for Arya</label>
    <label><input type="radio" name="v{it['item']}" value="cannot_tell"> Can't tell</label>
    <input type="text" class="note" placeholder="why (a few words)" name="n{it['item']}">
  </div>
</section>""")
    page = TEMPLATE.replace("{{N}}", str(len(items))).replace("{{CARDS}}", "".join(cards))
    (HERE / "audit" / "label-sheet.html").write_text(page)
    print(f"{len(items)} items -> audit/sample.json, audit/label-sheet.html")


TEMPLATE = """<!doctype html><meta charset="utf-8"><title>JS3 hand labels (blind)</title>
<style>
body{font:15px/1.5 -apple-system,system-ui,sans-serif;max-width:920px;margin:0 auto;padding:16px;background:#fafaf8;color:#222}
header{position:sticky;top:0;background:#fafaf8;padding:8px 0;border-bottom:1px solid #ccc;z-index:2}
.card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:12px 16px;margin:14px 0}
.card.done{border-left:6px solid #3a7}
h2{font-size:17px;margin:0 0 4px}.meta{color:#555;font-size:13px;margin:0 0 8px}
.box{padding:8px 12px;border-radius:6px;margin:8px 0;font-size:14px}.box ul{margin:4px 0;padding-left:20px}.yrs{background:#fff6dc;border:1px solid #e8d38a}.req{background:#f2f5fa;border:1px solid #cdd8ea}
.full{white-space:pre-wrap;font-size:13px;color:#333}
.ans{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-top:8px}
.note{flex:1;min-width:200px;padding:4px 6px}
button{padding:6px 12px;font-size:14px}
</style>
<header><b>Blind hand labels: {{N}} postings</b> · <span id="count">0</span>/{{N}} done ·
<button id="dl">Download my labels (JSON)</button>
<details><summary>How to judge</summary><p>For each posting: would you show it to <b>Arya Sahni</b>? Arya is a fictional
early-career AI engineer (about 1 year: AI Engineer co-op; Python, SQL, LangGraph, MLflow, Power BI, AWS, Delta Lake),
in Boston, wants a <b>US, full-time, non-senior</b> job in AI/ML/data. Answer from the posting only. "Can't tell" if the
posting doesn't give you enough to decide. The sheet does not show what the filter decided, on purpose.
Answers save in this browser as you go; click Download when done.</p></details></header>
{{CARDS}}
<script>
const KEY='js3-labels-v1';let s={};try{s=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(s))}catch(e){};paint()}
function paint(){let n=0;document.querySelectorAll('.card').forEach(c=>{const i=c.dataset.item;const d=s[i]&&s[i].verdict;c.classList.toggle('done',!!d);if(d)n++});document.getElementById('count').textContent=n}
document.querySelectorAll('.card').forEach(c=>{const i=c.dataset.item;s[i]=s[i]||{};
 c.querySelectorAll('input[type=radio]').forEach(r=>{if(s[i].verdict===r.value)r.checked=true;r.onchange=()=>{s[i].verdict=r.value;s[i].at=new Date().toISOString();save()}});
 const t=c.querySelector('.note');t.value=s[i].note||'';t.oninput=()=>{s[i].note=t.value;save()}});
paint();
document.getElementById('dl').onclick=()=>{const b=new Blob([JSON.stringify({labeler:'Riya Kapadnis',sheet:'audit/label-sheet.html',downloaded:new Date().toISOString(),labels:s},null,1)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='js3-hand-labels.json';a.click()};
</script>"""

if __name__ == "__main__":
    main()
