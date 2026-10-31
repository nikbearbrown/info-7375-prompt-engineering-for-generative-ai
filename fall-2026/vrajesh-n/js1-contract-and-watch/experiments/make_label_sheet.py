"""Pick 20 real postings from the 2026-10-31 live snapshot and write a blank label sheet.

Stratified on purpose (a first plain random draw on 2026-10-31 had no plausible-relevant posting,
so "always not_relevant" would have scored 20/20): all 9 non-senior software titles, 7 senior
software titles, 4 others (seed 7375). Each pool is split alternately between dev and heldout.
The rule's verdict is deliberately NOT shown, so hand labels are not anchored on it.
"""
import csv
import random
import re

from common import LABELS, postings
from earlybird import rule


def lines(text, pattern):
    return " | ".join(m.group(0).strip() for m in re.finditer(r"[^\n.]*" + pattern + r"[^\n.]*", text, re.I))[:300]


def main():
    if LABELS.exists():
        raise SystemExit(f"{LABELS} exists; refusing to overwrite hand labels")
    ps = sorted(postings().values(), key=lambda p: p["id"])
    rng = random.Random(7375)
    swe = [p for p in ps if rule.ROLE.search(p["title"])]
    junior = [p for p in swe if not rule.SENIOR.search(p["title"])]
    senior = [p for p in swe if rule.SENIOR.search(p["title"])]
    other = [p for p in ps if not rule.ROLE.search(p["title"])]
    pick = []
    for pool, k in ((junior, 9), (senior, 7), (other, 4)):
        chosen = rng.sample(pool, k)
        first = rng.choice(["dev", "heldout"])
        second = "heldout" if first == "dev" else "dev"
        pick += [(first if i % 2 == 0 else second, p) for i, p in enumerate(chosen)]
    # the odd pools (9, 7) can leave the sets at 11/9; move one of the "other" rows to even them out
    devs = [i for i, (s, _) in enumerate(pick) if s == "dev"]
    while len(devs) != 10:
        i = next(i for i in range(len(pick) - 1, -1, -1)
                 if pick[i][0] == ("dev" if len(devs) > 10 else "heldout"))
        pick[i] = ("heldout" if pick[i][0] == "dev" else "dev", pick[i][1])
        devs = [i for i, (s, _) in enumerate(pick) if s == "dev"]
    rng.shuffle(pick)
    pick.sort(key=lambda sp: sp[0])  # dev rows first, order within a set stays shuffled
    with LABELS.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["set", "posting_id", "title", "country", "years_asked", "sponsor_text", "job_url", "hand_label", "hand_note"])
        for s, p in pick:
            w.writerow([s, p["id"], p["title"], rule.country(p),
                        lines(p.get("descriptionPlain", ""), r"\d+\s*\+?\s*(?:(?:-|–|—|to)\s*\d+\s*)?\+?\s*years?\b"),
                        lines(p.get("descriptionPlain", ""), r"sponsor"), p.get("jobUrl"), "", ""])
    print(f"wrote {LABELS}: fill hand_label with relevant / not_relevant")


if __name__ == "__main__":
    main()
