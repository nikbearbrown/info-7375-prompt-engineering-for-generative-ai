"""Collect every posting from the expected sources (FILTER.md section 3).

    python3 -m js3.collect [--sources config/sources.json] [--budgets config/budgets.json] [--label NAME]

Network and write rules come from JS2, unchanged (js3/js2/: policy, transport, ats are byte-identical
copies). Every request passes policy.check_request (GET to 3 allow-listed hosts only); every file write
passes Policy.check_write (inside data/ only; append-only). The collector never applies, emails,
messages or logs in: there is no code path that sends anything but a GET.

Output (all under data/):
  raw/<run>/<ats>-<slug>.json.gz      the exact bytes each source returned (gzip), sha256 in sources.json
  runs/<run>/sources.json             one status per source: ok | empty | error (+ reason)
  corpus/<run>.jsonl.gz               one normalized posting per line (JS2 ats shape + source, html)
Exit code: 0 every source ok · 3 at least one source empty or errored (the shortlist is then incomplete).
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import sys
import time

from .js2 import ats, policy, transport

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _write(pol, rel, data):
    path = os.path.join(BASE, rel)
    d = pol.check_write(path)
    if not policy.granted(d):
        raise policy.PolicyDenied(d)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return d


def _html_by_id(src_ats, body):
    """Ashby's descriptionPlain loses headings; keep descriptionHtml for the evidence labeler."""
    if src_ats != "ashby":
        return {}
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return {str(j.get("id")): j.get("descriptionHtml") or "" for j in data.get("jobs") or []}


def collect(sources_path, budgets_path, label=None, get=transport.get, now=None):
    with open(os.path.join(BASE, sources_path), encoding="utf-8") as f:
        sources = json.load(f)["sources"]
    with open(os.path.join(BASE, budgets_path), encoding="utf-8") as f:
        budgets = json.load(f)
    pol = policy.Policy(BASE, os.path.join(BASE, "data"), state_dir=os.path.join(BASE, "data", "state"),
                        config_dir=os.path.join(BASE, "config"))
    stamp = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H-%M-%SZ")
    run = stamp + (f"-{label}" if label else "")
    if os.path.exists(os.path.join(BASE, "data", "runs", run)):
        raise SystemExit(f"run {run} already exists; refusing to overwrite (append-only)")
    t0, n_req = time.monotonic(), 0
    statuses, corpus = [], []
    for src in sources:
        key = ats.board_key(src["ats"], src["slug"])
        st = {"source": key, "company": src["company"], "status": None, "reason": "", "postings": 0,
              "attempts": 0}
        try:
            url = ats.board_url(src["ats"], src["slug"])
        except ats.BadSlug as e:
            st.update(status="error", reason=str(e))
            statuses.append(st)
            continue
        resp = None
        for attempt in range(1 + budgets["max_retries_per_source"]):
            if n_req >= budgets["max_requests"] or time.monotonic() - t0 > budgets["max_seconds"]:
                st.update(status="error", reason="budget exhausted before this source was fetched")
                break
            n_req += 1
            st["attempts"] += 1
            try:
                resp = get(url, budgets["request_timeout_seconds"], budgets["max_response_bytes"])
            except policy.PolicyDenied as e:
                st.update(status="error", reason=f"policy: {e}")
                resp = None
                break
            if resp.error_kind in ("timeout", "network") or (resp.status or 0) >= 500:
                continue  # transient: one retry
            break
        if st["status"] is None:
            if resp is None or resp.error_kind or resp.status != 200:
                why = (resp.error_kind or f"HTTP {resp.status}") if resp else "no response"
                st.update(status="error", reason=why)
            else:
                rel = f"data/raw/{run}/{key.replace(':', '-')}.json.gz"
                _write(pol, rel, gzip.compress(resp.body, mtime=0))
                st.update(raw=rel, sha256=hashlib.sha256(resp.body).hexdigest(), bytes=len(resp.body))
                try:
                    postings = ats.parse(src["ats"], resp.body)
                except ats.BadResponse as e:
                    st.update(status="error", reason=f"bad response: {e}")
                    postings = []
                html_map = _html_by_id(src["ats"], resp.body)
                for p in postings:
                    p["source"] = key
                    p["company"] = src["company"]
                    p["html"] = html_map.get(p["id"], p["content"])
                corpus.extend(postings)
                if st["status"] is None:
                    st.update(status="ok" if postings else "empty", postings=len(postings),
                              reason="" if postings else "HTTP 200 with 0 postings: cannot tell (AB4)")
        statuses.append(st)
    summary = {"run": run, "started_utc": stamp, "requests": n_req,
               "seconds": round(time.monotonic() - t0, 2), "sources": statuses,
               "total_postings": len(corpus),
               "complete": all(s["status"] == "ok" for s in statuses)}
    _write(pol, f"data/runs/{run}/sources.json", json.dumps(summary, indent=2).encode())
    lines = "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in corpus)
    _write(pol, f"data/corpus/{run}.jsonl.gz", gzip.compress(lines.encode("utf-8"), mtime=0))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sources", default="config/sources.json")
    ap.add_argument("--budgets", default="config/budgets.json")
    ap.add_argument("--label")
    a = ap.parse_args(argv)
    s = collect(a.sources, a.budgets, a.label)
    for st in s["sources"]:
        print(f"{st['source']:<26} {st['status']:<6} {st['postings']:>4}  {st['reason']}")
    print(f"run {s['run']}: {s['total_postings']} postings, {s['requests']} requests, {s['seconds']} s, "
          f"{'complete' if s['complete'] else 'INCOMPLETE'}")
    return 0 if s["complete"] else 3


if __name__ == "__main__":
    sys.exit(main())
