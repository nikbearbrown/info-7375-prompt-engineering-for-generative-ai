"""Draw the 80-posting hand-label sample exactly as FILTER.md section 5 says, with a fixed seed.

    python -B scripts/draw_sample.py
Writes:
  out/audit/sample_v1.0.json   which posting is in which set (do NOT open while labeling)
  out/audit/sheet_blind.json   the blind sheet: shuffled, no set, no score, no verdict, no Claude output

Order of draws (each later draw excludes everything drawn before it):
  1. audit_kept_random      10, simple random sample of v1.0 kept
  2. audit_reject_random    30, simple random sample of v1.0 rejects
  3. audit_close            10, from scores 5-7 not disqualified: 4 from each side of the threshold, then 2 more
  4. heldout_reject         15, random rejects
  5. heldout_kept_or_close  15, random from kept or the close-call band
"""
import json
import random
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import corpus, filter as flt, policy  # noqa: E402

SEED = 20261124
BLOCK = re.compile(r"<\s*(br|/p|/div|/li|/h[1-6]|/ul|/ol|p|div|h[1-6]|ul|ol)\b[^>]*>", re.I)


def readable(html: str) -> str:
    s = unescape(html or "")
    s = re.sub(r"<\s*li\b[^>]*>", "\n• ", s, flags=re.I)
    s = BLOCK.sub("\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s).replace(" ", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def raw_jobs():
    """Readable text per posting id, from the newest raw response that has it."""
    out = {}
    for rec_path in sorted((policy.OUT / "runs").glob("*.json")):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        raws = {e["board"]: e["raw"] for e in rec["trace"] if e["event"] == "request" and e.get("raw")}
        for key, o in rec["boards"].items():
            if o["outcome"] != "ok":
                continue
            ats, _ = key.split(":")
            data = json.loads((ROOT / raws[key]).read_text(encoding="utf-8"))
            for j in (data["jobs"] if ats != "lever" else data):
                if ats == "greenhouse":
                    text = readable(j.get("content"))
                elif ats == "lever":
                    parts = [readable(j.get("description"))]
                    for x in j.get("lists") or []:
                        parts.append(f"\n{x.get('text', '')}\n{readable(x.get('content'))}")
                    parts.append(readable(j.get("additional")))
                    text = "\n".join(parts).strip()
                else:
                    text = readable(j.get("descriptionHtml")) or (j.get("descriptionPlain") or "")
                out[f"{key}:{j['id']}"] = text
    return out


def draw(results: dict, cfg=flt.V1_0, seed=SEED) -> dict:
    rng = random.Random(seed)
    ids = sorted(results)
    kept = [i for i in ids if results[i]["verdict"] == "keep"]
    rejects = [i for i in ids if results[i]["verdict"] == "reject"]
    close = [i for i in ids if flt.is_close_call(results[i], cfg)]
    taken = set()

    def pick(pool, n):
        pool = [i for i in pool if i not in taken]
        got = rng.sample(pool, min(n, len(pool)))
        taken.update(got)
        return sorted(got)

    sets = {}
    sets["audit_kept_random"] = pick(kept, 10)
    sets["audit_reject_random"] = pick(rejects, 30)
    below = [i for i in close if results[i]["score"] < cfg["threshold"]]
    above = [i for i in close if results[i]["score"] >= cfg["threshold"]]
    c = pick(below, 4) + pick(above, 4)
    c += pick(close, 2)
    sets["audit_close"] = sorted(c)
    sets["heldout_reject"] = pick(rejects, 15)
    sets["heldout_kept_or_close"] = pick(sorted(set(kept) | set(close)), 15)
    order = sorted(taken)
    rng.shuffle(order)
    return {"seed": seed, "filter_version": cfg["version"],
            "pool_sizes": {"kept": len(kept), "rejects": len(rejects), "close": len(close),
                           "close_below": len(below), "close_above": len(above)},
            "sets": sets, "sheet_order": order}


def main() -> int:
    c = corpus.load()
    results = json.loads((policy.OUT / "filter" / "v1.0" / "results.json").read_text(encoding="utf-8"))["results"]
    sample = draw(results)
    texts = raw_jobs()
    sheet = []
    for n, pid in enumerate(sample["sheet_order"], 1):
        p = c["postings"][pid]
        sheet.append({"n": n, "id": pid, "board": p["board"], "title": p["title"], "location": p["location"],
                      "employment_type": p["employment_type"], "url": p["url"],
                      "still_listed_2026_11_24": p["last_seen_run"] == "20261125T023341Z",
                      "text": texts[pid]})
    policy.write_bytes(policy.OUT / "audit" / "sample_v1.0.json",
                       (json.dumps(sample, indent=1) + "\n").encode("utf-8"))
    policy.write_bytes(policy.OUT / "audit" / "sheet_blind.json",
                       (json.dumps(sheet, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(json.dumps(sample["pool_sizes"]), {k: len(v) for k, v in sample["sets"].items()}, "total", len(sheet))
    return 0


if __name__ == "__main__":
    sys.exit(main())
