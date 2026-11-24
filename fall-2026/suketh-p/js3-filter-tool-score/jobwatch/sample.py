"""The hand-label sample, drawn once from FILTER.md v0.1's audit records with a fixed seed.

Order of the draws (Claude Code's procedure; the held-out design is the student's choice):
  1. held-out: 15 at random from kept or review, then 15 at random from rejected
     (FILTER.md, "Addition before the reject audit"). Never used to change a rule.
  2. reject audit, from what is left: 30 at random from rejected (the brief: "at least 30").
  3. close calls, from what is left: 5 one point under the cutoff (pass role and level, score 1,
     location not outside) and 5 at the cutoff (kept or review with score 2).
  4. kept sample, from what is left: 10 at random from kept or review.
Every pool is sorted by (board, key) before sampling, so the same seed gives the same sample."""

import random

SEED = 20261124
SHUFFLE_SEED = 1125
SIZES = {"held-out kept or review": 15, "held-out rejected": 15, "audit random reject": 30,
         "audit one point under the cutoff": 5, "audit at the cutoff": 5, "audit kept sample": 10}


def _key(record):
    return (record["board"], record["key"])


def draw(records, seed=SEED, shuffle_seed=SHUFFLE_SEED):
    rng = random.Random(seed)
    taken, members = set(), []

    def pick(stratum, pool):
        pool = sorted((r for r in pool if _key(r) not in taken), key=_key)
        chosen = rng.sample(pool, SIZES[stratum])
        for record in chosen:
            taken.add(_key(record))
            members.append({"board": record["board"], "key": record["key"], "stratum": stratum,
                            "pool_size": len(pool)})

    kept = [r for r in records if r["fate"] in ("kept", "review")]
    rejected = [r for r in records if r["fate"] == "rejected"]
    pick("held-out kept or review", kept)
    pick("held-out rejected", rejected)
    pick("audit random reject", rejected)
    pick("audit one point under the cutoff",
         [r for r in rejected if "role" not in r["reasons"] and "level" not in r["reasons"]
          and r["score"] == 1 and "location" not in r["reasons"]])
    pick("audit at the cutoff", [r for r in kept if r["score"] == 2])
    pick("audit kept sample", kept)

    order = list(range(len(members)))
    random.Random(shuffle_seed).shuffle(order)
    for number, index in enumerate(order, start=1):
        members[index]["label_id"] = f"P{number:02d}"
    return sorted(members, key=lambda m: m["label_id"])
