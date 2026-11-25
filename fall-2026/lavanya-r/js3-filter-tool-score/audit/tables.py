"""Print AUDIT.md's per-posting tables from the committed files (recomputable).

python3 -B audit/tables.py
"""
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent.parent
D = {json.loads(l)["key"]: json.loads(l) for l in open(HERE / "out/filter/v1.0/decisions.jsonl")}
H = {json.loads(l)["key"]: json.loads(l) for l in open(HERE / "audit/hand_verdicts.jsonl")}
draw = json.loads((HERE / "audit/draw.json").read_text())
NAMES = {"A": "30 random rejects", "B": "10 closest calls (score 4 and 5)", "C": "10 random kept"}
for g in "ABC":
    print(f"\n### Group {g}: {NAMES[g]}\n")
    print("| Sheet # | Title (board) | Filter v1.0 | Why | Score | My verdict | Filter wrong? |")
    print("|---|---|---|---|---|---|---|")
    for k in sorted(draw["groups"][g], key=lambda k: H[k]["n"]):
        d, h = D[k], H[k]["verdict"]
        wrong = (d["verdict"] == "keep" and h == "n") or (d["verdict"] != "keep" and h == "y")
        why = ", ".join(d["rejected_by"]) or "—"
        print(f"| {H[k]['n']} | {d['title'].strip()} ({k.split('/')[1]}) | {d['verdict']} | {why} "
              f"| {d['score']} | {h} | {'**yes**' if wrong else ('?' if h == '?' else 'no')} |")
