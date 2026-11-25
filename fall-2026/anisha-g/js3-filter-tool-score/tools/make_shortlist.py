"""Source-grounded shortlist: every posting the filter kept, every claim in its justification labelled against the
posting text. Writes out/shortlist_v<ver>.json and out/shortlist_v<ver>.md.  Run:  python3 tools/make_shortlist.py [filter file]"""
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
from js3 import filter as F, evidence as E
cfg = F.load_filter(sys.argv[1] if len(sys.argv) > 1 else "filters/filter_v1.0.json")
corpus = {p["id"]: p for p in F.load_corpus()}
ds = [F.evaluate(p, cfg) for p in corpus.values()]
out, md = [], [f"## Filter v{cfg['version']}: {sum(d['status']=='kept' for d in ds)} kept, ranked by score\n"]
for d in F.rank(ds):
    j = E.justify(corpus[d["id"]], cfg); j["url"] = corpus[d["id"]]["url"]; out.append(j)
    md.append(f"### {'✅ SHORTLISTED' if j['shortlist'] else '⛔ NOT shortlisted'}: {d['title']} · `{d['id']}` · score {d['score']}")
    md.append(f"[posting]({j['url']}) · {('**Why not:** ' + j['why_not']) if j['why_not'] else 'Every claim needed for the shortlist is SUPPORTED by the text.'}\n")
    md.append("| Claim | Label | Quote from the posting (or why I cannot tell) |\n|---|---|---|")
    for c in j["claims"]:
        md.append(f"| {c['claim']} | **{c['label']}** | {c['say'].replace('|', '/')} |")
    md.append("")
v = cfg["version"]
Path(f"out/shortlist_v{v}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
Path(f"out/shortlist_v{v}.md").write_text("\n".join(md) + "\n")
print(f"{len(out)} kept, {sum(j['shortlist'] for j in out)} shortlisted -> out/shortlist_v{v}.md")
