"""Build the seeded "earlier" response used for the baseline run (labeled seeded everywhere).

    python3 seed.py --remove 5

Fetches the board once through the same allow-listed fetch, saves that response byte
for byte, then writes a copy without the N most recently first-published postings.
Running the watch on the copy first and live second makes those N postings "new".
Both files are written under runs/seed/, inside the agent's own run folder.
"""
import argparse
import datetime as dt
import json
import os

import watch


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--remove", type=int, default=5)
    args = parser.parse_args(argv)
    out_dir = watch._inside(os.path.join(watch.HERE, "runs", "seed"), watch.HERE)
    os.makedirs(out_dir, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    url = watch.BOARD_URL.format(board=watch.BOARD)
    raw = watch.fetch(url)
    source = os.path.join(out_dir, f"{stamp}_live_source.json")
    with open(source, "wb") as f:
        f.write(raw)
    data = json.loads(raw)
    newest = sorted(data["jobs"], key=lambda j: (j.get("first_published") or j.get("updated_at") or "", j["id"]),
                    reverse=True)[:args.remove]
    removed = {j["id"] for j in newest}
    seeded = dict(data, jobs=[j for j in data["jobs"] if j["id"] not in removed])
    seeded_path = os.path.join(out_dir, "earlier_response_SEEDED.json")
    with open(seeded_path, "w", encoding="utf-8") as f:
        json.dump(seeded, f, ensure_ascii=False)
    notes = {
        "seeded": True,
        "made_at": stamp,
        "from": os.path.relpath(source, watch.HERE),
        "fetched": url,
        "removed": [{"id": j["id"], "title": j["title"], "first_published": j.get("first_published")} for j in newest],
        "why": "No response was saved before 2026-10-31, so the earlier response is reconstructed by removing the "
               "most recently first-published postings from today's live response.",
    }
    with open(os.path.join(out_dir, "SEED.json"), "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(notes, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
