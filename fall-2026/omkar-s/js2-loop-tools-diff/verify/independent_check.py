"""Independent check of one finished run. It does NOT trust the agent's report.

    python3 -m verify.independent_check runs/<run-folder> [--no-probe]

It uses none of the loop's logic (no agent.loop, no agent.ats). It shares only the permission
policy, store and transport, so its own requests and writes stay inside the same rules.

  C1 raw evidence intact  : the sha256 of each raw file equals the sha256 the trace recorded.
  C2 counts recomputed    : the posting count is recounted from the raw bytes with its own
                            minimal parser and compared with report.json.
  C3 empty-board evidence : for every board the report shows with 0 postings,
                            (a) look up a reference count written down by someone else
                                (config/reference-counts.json), and
                            (b) LIVE cross-probe: ask the other two allow-listed ATSs for the same
                                company slug. If either says the company has postings, then
                                "0 postings / no new jobs" is CONTRADICTED.
Writes independent-check.md and .json into the run folder (new files only) and saves the probe
responses there. Exit code 0 = nothing contradicted; 1 = at least one contradiction; 2 = could not check.
"""
import argparse
import hashlib
import json
import os
import sys
from urllib.parse import quote

from agent import policy, store, transport

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{s}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{s}",
    "lever": "https://api.lever.co/v0/postings/{s}?mode=json",
}


def count_postings(body):
    """Own minimal recount: Greenhouse/Ashby {'jobs': [...]}, Lever [...]. None if not a list."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):
        return len(data["jobs"])
    return None


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def check(run_dir, base=HERE, probe=True, get=None):
    get = get or transport.get
    with open(os.path.join(run_dir, "report.json"), encoding="utf-8") as f:
        report = json.load(f)
    trace = load_jsonl(os.path.join(run_dir, "trace.jsonl"))
    with open(os.path.join(base, "config", "reference-counts.json"), encoding="utf-8") as f:
        refs = {r["key"]: r for r in json.load(f)["references"]}
    obs = [e for e in trace if e.get("event") == "observation"]
    findings = []

    # C1 + C2
    last_ok = {}
    for o in obs:
        with open(os.path.join(run_dir, o["raw"]), "rb") as f:
            body = f.read()
        sha_ok = hashlib.sha256(body).hexdigest() == o["sha256"]
        findings.append({"check": "C1", "board": o["board"], "raw": o["raw"],
                         "result": "OK" if sha_ok else "CONTRADICTED",
                         "detail": "sha256 matches trace" if sha_ok else "raw file changed since the run"})
        if o.get("http_status") == 200:
            last_ok[o["board"]] = count_postings(body)
    for b in report["boards"]:
        if b["status"] in ("not_attempted", "repeat_skipped"):
            continue
        recount = last_ok.get(b["key"])
        reported = b.get("postings")
        same = (recount == reported) or (reported is None and b["status"] != "ok")
        findings.append({"check": "C2", "board": b["key"], "result": "OK" if same else "CONTRADICTED",
                         "detail": f"report says {reported}, raw recount says {recount}"})

    # C3
    pol = policy.Policy(base, os.path.join(base, "runs"))
    st = store.Store(pol)
    probes_dir = os.path.join(run_dir, "independent-probes")
    for b in report["boards"]:
        if b.get("postings") != 0:
            continue
        ev = {"check": "C3", "board": b["key"], "reference": refs.get(b["key"]), "probes": []}
        reasons = []
        if ev["reference"] and ev["reference"]["postings"] > 0:
            r = ev["reference"]
            reasons.append(f"reference says {r['postings']} postings on {r['date']} ({r['source']})")
        if probe:
            if not os.path.isdir(probes_dir):
                st.makedirs(probes_dir)
            ats_name, slug = b["key"].split(":", 1)
            for other, tmpl in PROBE_URLS.items():
                url = tmpl.format(s=quote(slug, safe=""))
                try:
                    resp = get(url, 20, 10_000_000)
                except policy.PolicyDenied as e:
                    ev["probes"].append({"ats": other, "url": url, "refused": e.decision["reason"]})
                    continue
                n = count_postings(resp.body) if resp.status == 200 else None
                raw = os.path.join(probes_dir, f"{other}-{slug}.json")
                if not os.path.exists(raw):
                    st.write_new(raw, resp.body or b"")
                ev["probes"].append({"ats": other, "url": url, "http_status": resp.status, "postings": n,
                                     "raw": os.path.relpath(raw, run_dir),
                                     "sha256": hashlib.sha256(resp.body or b"").hexdigest()})
                if other != ats_name and n:
                    reasons.append(f"{other} has {n} postings for '{slug}' right now ({url})")
        ev["result"] = "CONTRADICTED" if reasons else "UNCONFIRMED"
        ev["detail"] = ("; ".join(reasons) if reasons else
                        "no reference and no other ATS has this company: the empty board is unexplained, not confirmed")
        findings.append(ev)
    return report, findings


def render(report, findings):
    bad = [f for f in findings if f["result"] == "CONTRADICTED"]
    L = [f"# Independent check of run {report['run_id']}", "",
         f"The agent reported **{report['exit']['status']}** (exit code {report['exit']['code']}).",
         f"This check found **{len(bad)} contradiction(s)**.", "",
         "| Check | Board | Result | Evidence |", "|---|---|---|---|"]
    for f in findings:
        L.append(f"| {f['check']} | `{f['board']}` | {f['result']} | {f['detail']} |")
    for f in findings:
        if f["check"] == "C3":
            L += ["", f"## C3 probes for `{f['board']}`", ""]
            for p in f["probes"]:
                L.append(f"- {p['ats']}: `{p['url']}` -> HTTP {p.get('http_status')}, postings {p.get('postings')}"
                         f" (raw `{p.get('raw')}`)" if "refused" not in p else f"- {p['ats']}: refused: {p['refused']}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--no-probe", action="store_true", help="skip the live cross-ATS probe (C3b)")
    a = ap.parse_args(argv)
    run_dir = a.run_dir if os.path.isabs(a.run_dir) else os.path.join(HERE, a.run_dir)
    try:
        report, findings = check(run_dir, probe=not a.no_probe)
        pol = policy.Policy(HERE, os.path.join(HERE, "runs"))
        st = store.Store(pol)
        st.write_new(os.path.join(run_dir, "independent-check.json"), json.dumps(findings, indent=1))
        st.write_new(os.path.join(run_dir, "independent-check.md"), render(report, findings))
    except (OSError, ValueError, KeyError, policy.PolicyDenied) as e:
        print(f"could not check: {e}", file=sys.stderr)
        return 2
    print(render(report, findings))
    return 1 if any(f["result"] == "CONTRADICTED" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
