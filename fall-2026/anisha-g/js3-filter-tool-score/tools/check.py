"""Independent check by recomputation (does not import js3). Re-derives from the saved files:
1) corpus hash matches CORPUS.sha256; 2) postings per board in the corpus = collection_summary.json;
3) R1 (title words) and R2 (seniority) recomputed with its own regexes agree with out/decisions_v1.0.jsonl;
4) the audit sets are disjoint, sized 30/10/6/30, and A is all rejects, C all keeps; 5) the hand verdicts match their frozen hash.
Run:  python3 tools/check.py"""
import gzip, hashlib, json, re, collections, sys
from pathlib import Path
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
want = dict(l.split()[::-1] for l in Path("CORPUS.sha256").read_text().splitlines())
check("corpus hash", hashlib.sha256(Path("data/corpus.jsonl.gz").read_bytes()).hexdigest() == want["data/corpus.jsonl.gz"])
corpus = [json.loads(l) for l in gzip.open("data/corpus.jsonl.gz", "rt")]
summ = json.loads(Path("data/collection_summary.json").read_text())
per = collections.Counter(":".join(p["id"].split(":")[:2]) for p in corpus)
check("postings per board = summary", all(per[k] == v["n"] for k, v in summ["boards"].items()), dict(per))
check("total", len(corpus) == summ["total"] == 1734, len(corpus))
cfg = json.loads(Path("filters/filter_v1.0.json").read_text())
def w(t, x): return re.search(r"(?<![A-Za-z0-9])" + re.escape(x) + r"(?![A-Za-z0-9])", t or "", re.I) is not None
dec = {json.loads(l)["id"]: json.loads(l) for l in open("out/decisions_v1.0.jsonl")}
bad = [p["id"] for p in corpus if dec[p["id"]]["status"] != "cannot_tell" and
       (dec[p["id"]]["r1"] != any(w(p["title"], x) for x in cfg["role_words"]) or
        dec[p["id"]]["r2_reject"] != any(w(p["title"], x) for x in cfg["seniority_words"]))]
check("R1/R2 recomputed independently", not bad, f"{len(bad)} disagree")
check("kept count v1.0", sum(d["status"] == "kept" for d in dec.values()) == 11)
s = json.loads(Path("audit/sets.json").read_text())
ids = s["A_random_rejects"] + s["B_close_calls"] + s["C_kept_sample"] + s["H_heldout"]
check("sets disjoint and sized", len(set(ids)) == 76 and [len(s[k]) for k in ["A_random_rejects", "B_close_calls", "C_kept_sample", "H_heldout"]] == [30, 10, 6, 30])
check("A all rejected, C all kept", all(dec[i]["status"] == "rejected" for i in s["A_random_rejects"]) and all(dec[i]["status"] == "kept" for i in s["C_kept_sample"]))
hv = Path("labels/hand_verdicts.jsonl").read_bytes()
check("hand verdicts unchanged since frozen", hashlib.sha256(hv).hexdigest() == Path("labels/hand_verdicts.sha256").read_text().split()[0])
check("76 verdicts, one per sheet item", len({json.loads(l)["id"] for l in hv.decode().splitlines()} & set(ids)) == 76)
sys.exit(0 if ok else 1)
