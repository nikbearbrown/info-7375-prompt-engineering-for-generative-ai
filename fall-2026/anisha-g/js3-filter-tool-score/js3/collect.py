"""Collector (FILTER.md section 3). One pass over boards.json, at most 5 boards (my JS2 budget). A failed board is
reported as failed, never as 0 postings. Writes data/corpus.jsonl.gz and data/collection_summary.json.
Run:  python3 -m js3.collect"""
import gzip, hashlib, json, sys, time
from pathlib import Path
from js3.policy import Policy
from js3.textio import html_to_text

MAX_BOARDS = 5
URLS = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
        "lever": "https://api.lever.co/v0/postings/{slug}?mode=json"}

def parse_board(ats, slug, body):
    data = json.loads(body)
    out = []
    if ats == "greenhouse":
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list): raise ValueError("no 'jobs' list")
        for j in data["jobs"]:
            loc = (j.get("location") or {}).get("name") if isinstance(j.get("location"), dict) else None
            out.append({"id": f"greenhouse:{slug}:{j['id']}", "title": (j.get("title") or "").strip(), "location": loc or None,
                        "url": j.get("absolute_url"), "text": html_to_text(j.get("content") or "")})
    elif ats == "lever":
        if not isinstance(data, list): raise ValueError("Lever response is not a list")
        for j in data:
            parts = [j.get("descriptionPlain") or ""]
            for l in j.get("lists") or []:
                parts += [l.get("text") or "", html_to_text(l.get("content") or "")]
            parts.append(j.get("additionalPlain") or "")
            loc = (j.get("categories") or {}).get("location")
            out.append({"id": f"lever:{slug}:{j['id']}", "title": (j.get("text") or "").strip(), "location": loc or None,
                        "url": j.get("hostedUrl"), "text": "\n".join(p.strip() for p in parts if p and p.strip())})
    else:
        raise ValueError(f"unknown ATS {ats}")
    return out

def collect(boards, fetch, timeout=30):
    postings, summary = [], {}
    for i, b in enumerate(boards):
        key = f"{b.get('ats')}:{b.get('slug')}"
        if i >= MAX_BOARDS:
            summary[key] = {"status": "not-reached", "n": None, "error": f"over the {MAX_BOARDS}-board budget"}; continue
        url = URLS.get(b.get("ats"), "").format(slug=b.get("slug"))
        rec = {"url": url, "status": "failed", "n": None, "error": "", "http": None, "bytes": None, "sha256": None}
        summary[key] = rec
        try:
            r = fetch(url, timeout)
            rec.update(http=r.status, bytes=len(r.body), sha256=hashlib.sha256(r.body).hexdigest())
            if r.status != 200: rec["error"] = f"HTTP {r.status}"; continue
            ps = parse_board(b["ats"], b["slug"], r.body)
            rec.update(status="ok", n=len(ps)); postings += ps
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
    return postings, summary

def main():
    from js3.fetch import make_fetch
    pol = Policy(".")
    boards = json.loads(Path("boards.json").read_text())["boards"]
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    postings, summary = collect(boards, make_fetch(pol))
    out = pol.check_write(Path("data/corpus.jsonl.gz"))
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for p in postings: f.write(json.dumps(p, ensure_ascii=False) + "\n")
    pol.check_write(Path("data/collection_summary.json")).write_text(json.dumps({"collected_at": t0, "boards": summary, "total": len(postings)}, indent=1))
    for k, r in summary.items(): print(f"{k:28s} {r['status']:8s} {r['n'] if r['n'] is not None else '-':>5}  {r['error']}")
    print(f"total postings: {len(postings)}   ({t0})")
    return 0 if all(r["status"] == "ok" for r in summary.values()) else 1

if __name__ == "__main__": sys.exit(main())
