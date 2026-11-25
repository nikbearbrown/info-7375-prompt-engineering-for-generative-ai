"""Blind hand-judging sheet (the human, not Claude, gives every verdict). Shows each posting in the shuffled order of
audit/sheet_order.json WITHOUT the filter's verdict or group. Saves after every answer to labels/hand_verdicts.jsonl;
you can quit and resume.   Run in your own Terminal:  python3 -m js3.judge"""
import json, re, sys, textwrap
from datetime import datetime
from pathlib import Path
from js3.filter import load_corpus

OUT = Path("labels/hand_verdicts.jsonl")
QUAL = re.compile(r"(qualifications|requirements|what you.{0,20}(bring|need|have)|who you are|you have|about you|you might be|skills)", re.I)

def excerpt(text, n=1500):
    m = QUAL.search(text or ""); start = max(0, m.start() - 100) if m else 0
    s = (text or "")[start:start + n]
    return ("..." if start else "") + s + ("..." if len(text or "") > start + n else "")

def main():
    order = json.loads(Path("audit/sheet_order.json").read_text())
    corpus = {p["id"]: p for p in load_corpus()}
    done = {}
    if OUT.exists():
        for l in OUT.read_text().splitlines(): r = json.loads(l); done[r["id"]] = r
    print(open("audit/AUDIT_RULE.md").read().split("\n", 1)[1][:900]); print("=" * 80)
    i = 0
    while i < len(order):
        pid = order[i]
        if pid in done: i += 1; continue
        p = corpus[pid]; board = pid.split(":")[1]
        print(f"\n[{i+1}/{len(order)}]  ({len(done)} judged)\nTITLE:    {p['title']}\nCOMPANY:  {board}     LOCATION: {p.get('location')}\n")
        print(textwrap.fill(excerpt(p["text"]).replace("\n", " · "), 110) if p["text"] else "(no posting text)")
        while True:
            a = input("\nWorth Nadia's time?  y / n / ?   (m = full text, q = quit): ").strip().lower()
            if a == "m": print(p["text"]); continue
            if a == "q": print(f"saved {len(done)} verdicts to {OUT}"); return
            if a in ("y", "n", "?"): break
        why = input("  reason (optional, Enter to skip): ").strip()
        rec = {"item": i + 1, "id": pid, "verdict": a, "reason": why, "at": datetime.now().isoformat(timespec="seconds")}
        with OUT.open("a") as f: f.write(json.dumps(rec) + "\n")
        done[pid] = rec; i += 1
    print(f"\nAll {len(order)} judged. Saved to {OUT}.")

if __name__ == "__main__": main()
