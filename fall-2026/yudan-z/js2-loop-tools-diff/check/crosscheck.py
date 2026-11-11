"""Independent check (not the agent's report): for each board in a finished run, count the same company's
postings on all three applicant-tracking systems with its own small fetch code, and flag a board whose
count is far below what the company lists elsewhere. It imports nothing from agent/.

  python check/crosscheck.py runs/wrong-ats/run-<stamp>.json
Only GET requests to the same three allow-listed hosts. Exit 1 if anything is flagged.
"""
import json
import sys
import urllib.error
import urllib.request

ENDPOINTS = {
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{b}/jobs", lambda d: len(d["jobs"])),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{b}", lambda d: len(d["jobs"])),
    "lever": ("https://api.lever.co/v0/postings/{b}?mode=json", lambda d: len(d)),
}


def count(system, board):
    url, n = ENDPOINTS[system]
    req = urllib.request.Request(url.format(b=board), headers={"User-Agent": "js2 independent crosscheck"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return n(json.loads(r.read().decode("utf-8")))
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"


def main(path):
    for s in (sys.stdout,):
        s.reconfigure(encoding="utf-8")
    run = json.load(open(path, encoding="utf-8"))
    print(f"run {run['run']} reported exit '{run['exit']}'; checking each ok board against the other systems")
    flagged = 0
    for b in run["boards"]:
        if b["status"] != "ok":
            continue
        counts = {s: count(s, b["board"]) for s in ENDPOINTS}
        best = max((v for v in counts.values() if isinstance(v, int)), default=0)
        ratio_bad = isinstance(counts[b["system"]], int) and best >= 10 and counts[b["system"]] < 0.1 * best
        mark = "FLAG" if ratio_bad else "ok  "
        flagged += ratio_bad
        print(f"  {mark} {b['board']}: agent read {b['system']} = {b['postings']} postings; "
              + ", ".join(f"{s} = {v}" for s, v in counts.items()))
    print(f"{flagged} board(s) flagged" + (": the run finished, but its answer for these boards is wrong" if flagged else ""))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
