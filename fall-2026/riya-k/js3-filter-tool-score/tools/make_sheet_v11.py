"""Re-audit of filter v1.1's rejects: a second seeded, BLIND sample and sheet (same layout as tools/make_sheets.py).

    python3 tools/make_sheet_v11.py     # writes audit/v1.1/sample.json and audit/v1.1/label-sheet.html

Seed 7376 (a new seed, fixed here). None of the 78 postings already labeled can be drawn.
Strata (disjoint):
  R2  30 uniform random postings from all v1.1 rejects        -> the only part that supports a rate
  NR  10 random postings v1.1 NEWLY rejects (v1 said kept or cannot_tell) -> where v1.1 is most likely to lose a good job
"""

import html
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from js3 import corpus  # noqa: E402
from js3.text import plain_text  # noqa: E402
from make_sheets import TEMPLATE, lines, requirements, year_lines  # noqa: E402

SEED = 7376


def load(version):
    return {(r["board"], r["id"]): r for r in map(json.loads, open(ROOT / "out" / version / "decisions.jsonl"))}


def main():
    rng = random.Random(SEED)
    v1, v11 = load("v1"), load("v1.1")
    done = {(i["board"], i["id"]) for i in json.loads((ROOT / "audit" / "sample.json").read_text())["items"]}
    rej = sorted(k for k, r in v11.items() if r["decision"] == "rejected" and k not in done)
    newly = sorted(k for k in rej if v1[k]["decision"] in ("kept", "cannot_tell"))
    nr = rng.sample(newly, 10)
    r2 = rng.sample([k for k in rej if k not in set(nr)], 30)
    drawn = [("R2", k) for k in r2] + [("NR", k) for k in nr]
    rng.shuffle(drawn)
    posts = corpus.by_key(corpus.load())
    items, cards = [], []
    for n, (s, k) in enumerate(drawn, 1):
        r = v11[k]
        items.append({"item": n, "stratum": s, "board": k[0], "id": k[1], "title": r["title"],
                      "v1_decision": v1[k]["decision"], "v11_decision": r["decision"], "v11_gates_failed": r["gates_failed"]})
        p = posts[k]
        text = plain_text(p.get("content", ""))
        ls = lines(p.get("content", ""))
        yl, req = year_lines(ls), requirements(ls)
        years_html = "".join(f"<li>{html.escape(x)}</li>" for x in yl) or "<li><i>No years mentioned anywhere in the posting.</i></li>"
        req_html = "".join(f"<li>{html.escape(x)}</li>" for x in req) or "<li><i>No qualifications section found; see full text.</i></li>"
        emp = p.get("employment")
        cards.append(f"""
<section class="card" id="i{n}" data-item="{n}">
  <h2>#{n} · {html.escape(p['title'])}</h2>
  <p class="meta"><b>{html.escape(k[0].split(':')[1])}</b> · {html.escape(p['location']['name'] or '(no location)')}
     · employment field: {html.escape(emp) if emp else '(board does not say)'} · {len(text)} chars ·
     <a href="{html.escape(p.get('absolute_url', ''))}" target="_blank" rel="noopener">posting</a></p>
  <div class="box yrs"><b>Years of experience</b> (lines copied from the posting)<ul>{years_html}</ul></div>
  <div class="box req"><b>Requirements</b> (copied from the posting)<ul>{req_html}</ul></div>
  <details><summary>full text</summary><p class="full">{html.escape(text)}</p></details>
  <div class="ans">
    <label><input type="radio" name="v{n}" value="show"> Show to Arya</label>
    <label><input type="radio" name="v{n}" value="not"> Not for Arya</label>
    <label><input type="radio" name="v{n}" value="cannot_tell"> Can't tell</label>
    <input type="text" class="note" placeholder="why (a few words)" name="n{n}">
  </div>
</section>""")
    out = ROOT / "audit" / "v1.1"
    out.mkdir(parents=True, exist_ok=True)
    (out / "sample.json").write_text(json.dumps({"seed": SEED, "drawn_from": "out/v1.1/decisions.jsonl (rejects), excluding the 78 already labeled",
                                                 "pools": {"v1.1_rejects_not_yet_labeled": len(rej), "newly_rejected_by_v1.1": len(newly)},
                                                 "items": items}, indent=1, ensure_ascii=False) + "\n")
    page = (TEMPLATE.replace("{{N}}", str(len(items))).replace("{{CARDS}}", "".join(cards))
            .replace("JS3 hand labels (blind)", "JS3 v1.1 re-audit (blind)")
            .replace("js3-labels-v1", "js3-labels-v11-reaudit").replace("js3-hand-labels.json", "js3-v11-reaudit-labels.json")
            .replace("sheet:'audit/label-sheet.html'", "sheet:'audit/v1.1/label-sheet.html'")
            .replace("Answer from the posting only.", "Judge as <b>Arya</b>, not as yourself, and don't think about the filter's score. Answer from the posting only."))
    (out / "label-sheet.html").write_text(page)
    print(f"{len(items)} items; pools: {len(rej)} v1.1 rejects not yet labeled, {len(newly)} newly rejected")


if __name__ == "__main__":
    main()
