"""JS3 Step 2: collect one fresh snapshot of the ten JS2 boards, with descriptions (FILTER.md section 3).

One GET per board through JS2's LiveFetcher: allow-listed hosts only, HTTPS GET only, 1 s apart per host, every redirect hop checked.
Raw bytes are saved unchanged with their sha256. A failed board is "not observed" and an empty one is "0 postings, needs review",
never "no relevant jobs". The script refuses to overwrite an existing snapshot folder.

    python3 scripts/collect_snapshot.py            # writes snapshot/<today ET>/
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import net, policy, providers  # noqa: E402

ET = ZoneInfo("America/New_York")


def now():
    return datetime.now(ET).isoformat(timespec="seconds")


def main():
    boards = json.loads((ROOT / "config" / "boards.json").read_text())["boards"]
    budgets = json.loads((ROOT / "config" / "budgets.json").read_text())
    allow = policy.load_allowlist()
    out = ROOT / "snapshot" / datetime.now(ET).strftime("%Y-%m-%d")
    if out.exists():
        sys.exit(f"refused: {out.relative_to(ROOT)} already exists; a snapshot is never overwritten")
    (out / "raw").mkdir(parents=True)

    hops = []
    fetcher = net.LiveFetcher(allow, budgets["max_redirect_hops"], on_hop=hops.append, before_wait=lambda s: None)
    started, rows = now(), []
    for b in boards:
        provider, board = b["provider"], b["board"]
        url = providers.snapshot_url(provider, board)
        fetched_at = now()
        r = fetcher.get(url, budgets["request_timeout_s"])
        row = {"provider": provider, "board": board, "url": url, "fetched_at": fetched_at, "status": r.status,
               "error": r.error, "redirect_hops": r.hops, "file": None, "sha256": None, "bytes": None,
               "postings": None, "no_description": None, "outcome": None}
        if r.body is not None:
            path = out / "raw" / f"{provider}__{board}.json"
            path.write_bytes(r.body)
            row.update(file=str(path.relative_to(out)), sha256=hashlib.sha256(r.body).hexdigest(), bytes=len(r.body))
        if r.status == 200:
            try:
                postings = providers.parse_list(provider, r.body, board)
                row["postings"] = len(postings)
                row["no_description"] = sum(1 for p in postings if not p["content"])
                row["outcome"] = "observed" if postings else "0 postings, needs review"
            except providers.ShapeError as e:
                row.update(outcome="not observed (bad shape)", error=str(e))
        else:
            row["outcome"] = "not observed"
        rows.append(row)
        print(f"{provider:10} {board:24} {str(r.status):5} {str(row['postings']):>5} postings  "
              f"{str(row['no_description']):>4} without description  {row['outcome']}")

    manifest = {"what": "JS3 snapshot: one list request per board, with descriptions (FILTER.md section 3)",
                "started": started, "finished": now(), "requests": len(rows), "user_agent": net.USER_AGENT,
                "boards": rows}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}/manifest.json  ({len(rows)} requests)")


if __name__ == "__main__":
    main()
