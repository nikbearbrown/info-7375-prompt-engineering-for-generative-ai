"""Near-duplicate clusters, the sealed held-out split, the dev audit draw and the blind sheet.

  .venv/bin/python -m js3.sample            (deterministic; seeds 7375 / 7376 / 7377)

Plan: FILTER.md §5 as amended by A1/A2 (change log), written before this draw.
Outputs:
  splits/clusters.json      key -> near-duplicate cluster id
  splits/groups.json        sampling groups with seeds (NOT for the labeler: shows scores and groups)
  review/LABEL_SHEET.csv    the blind sheet: sheet_id, key, title, board, location, departments, file, label, reason
  review/postings/Sxx.md    full posting text for each sheet row (no score, no verdict, no highlights)
"""
import csv
import itertools
import json
import random
from collections import defaultdict
from pathlib import Path

from inherited.rules import normalize

from .corpus import load_corpus
from .filter import load_filter
from .run import score_all
from .text import readable

ROOT = Path(__file__).resolve().parent.parent
JACCARD = 0.8
SHINGLE = 5
SEED_H, SEED_DEV, SEED_SHEET = 7375, 7376, 7377
H_SIZES = {"H-keep": 3, "H-near-reject(3-5)": 10, "H-other-reject": 10}
DEV_RANDOM_REJECTS, DEV_CLOSE_EACH_SIDE = 30, 6


def shingles(p):
    w = normalize(readable(p["text"])).split()
    return frozenset(" ".join(w[i:i + SHINGLE]) for i in range(max(1, len(w) - SHINGLE + 1)))


def clusters(corpus):
    """Single-link clusters of same-board postings with shingle Jaccard >= 0.8 (exact duplicates included)."""
    sh = {k: shingles(p) for k, p in corpus.items()}
    parent = {k: k for k in corpus}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_board = defaultdict(list)
    for k, p in corpus.items():
        by_board[p["board"]].append(k)
    for keys in by_board.values():
        for a, b in itertools.combinations(sorted(keys), 2):
            A, B = sh[a], sh[b]
            if not A or not B or min(len(A), len(B)) < JACCARD * max(len(A), len(B)):
                continue  # Jaccard <= min/max, so this pair cannot reach the threshold
            if len(A & B) / len(A | B) >= JACCARD:
                parent[find(a)] = find(b)
    members = defaultdict(list)
    for k in sorted(corpus):
        members[find(k)].append(k)
    return {k: min(ms) for ms in members.values() for k in ms}  # cluster id = its smallest key


def draw():
    corpus = load_corpus()
    results, _ = score_all(load_filter("v1.0"), corpus)
    cl = clusters(corpus)
    members = defaultdict(list)
    for k in sorted(corpus):
        members[cl[k]].append(k)

    def cluster_set(pred):
        return sorted({cl[k] for k, r in results.items() if pred(r)})

    def rep(rng, c, pred=lambda r: True):
        return rng.choice([k for k in members[c] if pred(results[k])])

    keep = lambda r: r["verdict"] == "keep"
    rej = lambda r: r["verdict"] == "reject"
    near = lambda r: r["verdict"] == "reject" and 3 <= r["score"] <= 5

    # 1. Held-out H (seed 7375): clusters, one labeled posting per cluster.
    rng = random.Random(SEED_H)
    H, used = {}, set()
    for name, pred in (("H-keep", keep), ("H-near-reject(3-5)", near), ("H-other-reject", rej)):
        pool = [c for c in cluster_set(pred) if c not in used and (name != "H-other-reject" or
                not any(near(results[k]) or keep(results[k]) for k in members[c]))]
        picked = rng.sample(pool, min(H_SIZES[name], len(pool)))
        used.update(picked)
        H[name] = [rep(rng, c, pred) for c in picked]
    h_clusters = used

    # 2. Dev audit (seed 7376), everything outside H's clusters.
    rng = random.Random(SEED_DEV)
    outside = lambda k: cl[k] not in h_clusters
    # 30 rejects, uniform over postings; a draw whose cluster was already drawn is skipped (one per cluster).
    pool = [k for k, r in results.items() if rej(r) and outside(k)]
    order = rng.sample(pool, len(pool))
    random_rejects, seen_c = [], set()
    for k in order:
        if cl[k] in seen_c:
            continue
        seen_c.add(cl[k])
        random_rejects.append(k)
        if len(random_rejects) == DEV_RANDOM_REJECTS:
            break
    kept_out = [k for k, r in results.items() if keep(r) and outside(k)]
    lowest_kept = min(results[k]["score"] for k in kept_out)
    is_below = lambda r: rej(r) and r["score"] == 5
    is_above = lambda r: keep(r) and r["score"] == lowest_kept
    below = sorted({cl[k] for k, r in results.items() if is_below(r) and outside(k)})
    above = sorted({cl[k] for k, r in results.items() if is_above(r) and outside(k)})
    kept_cl = sorted({cl[k] for k in kept_out})
    # A1: one labeled posting per cluster, the same posting if a cluster is in several groups.
    chosen = {}

    def pick(c, pred):
        if c not in chosen:
            chosen[c] = rep(rng, c, pred)
        return chosen[c]

    for k in random_rejects:
        chosen[cl[k]] = k
    close_below = [pick(c, is_below) for c in rng.sample(below, min(DEV_CLOSE_EACH_SIDE, len(below)))]
    close_above = [pick(c, is_above) for c in rng.sample(above, min(DEV_CLOSE_EACH_SIDE, len(above)))]
    kept_sample = [pick(c, keep) for c in kept_cl]  # A2: fewer than 8 keep clusters outside H: all taken
    dev = {"D-random-reject": random_rejects, "D-close-below(score 5)": close_below,
           f"D-close-above(score {lowest_kept})": close_above, "D-kept(all outside H)": kept_sample}

    # Disjointness: no cluster in both dev and H.
    dev_keys = sorted({k for ks in dev.values() for k in ks})
    h_keys = sorted({k for ks in H.values() for k in ks})
    assert not ({cl[k] for k in dev_keys} & {cl[k] for k in h_keys}), "dev/H cluster overlap"

    groups = {
        "plan": "FILTER.md §5 + amendments A1, A2", "filter": "v1.0",
        "seeds": {"heldout": SEED_H, "dev": SEED_DEV, "sheet_order": SEED_SHEET},
        "near_duplicate_rule": f"same board, word {SHINGLE}-shingle Jaccard >= {JACCARD}, single-link",
        "clusters_total": len(members),
        "pools": {"rejects_outside_H": len(pool), "score5_reject_clusters_outside_H": len(below),
                  "keeps_outside_H": len(kept_out), "keep_clusters_outside_H": len(kept_cl),
                  "keeps_total": sum(keep(r) for r in results.values()),
                  "keep_clusters_total": len(cluster_set(keep))},
        "shortfalls": {
            "D-close-above": f"{len(above)} clusters at score {lowest_kept} outside H (planned 6)" if len(above) < 6 else None,
            "D-kept": f"{len(kept_cl)} keep clusters ({len(kept_out)} postings) outside H (planned 8); one posting from each taken"
            if len(kept_cl) < 8 else None},
        "heldout": {g: [{"key": k, "score": results[k]["score"], "verdict": results[k]["verdict"]} for k in ks] for g, ks in H.items()},
        "dev": {g: [{"key": k, "score": results[k]["score"], "verdict": results[k]["verdict"]} for k in ks] for g, ks in dev.items()},
    }

    # 3. Blind sheet (seed 7377): dev + H together, shuffled, one row per posting.
    all_keys = sorted(set(dev_keys) | set(h_keys))
    random.Random(SEED_SHEET).shuffle(all_keys)
    sheet_ids = {k: f"S{i + 1:02d}" for i, k in enumerate(all_keys)}
    groups["sheet_ids"] = sheet_ids
    groups["split_of_sheet_id"] = {sheet_ids[k]: ("heldout" if k in h_keys else "dev") for k in all_keys}

    (ROOT / "splits").mkdir(exist_ok=True)
    (ROOT / "splits" / "clusters.json").write_text(json.dumps(cl, indent=0, sort_keys=True) + "\n")
    (ROOT / "splits" / "groups.json").write_text(json.dumps(groups, indent=1) + "\n")

    pdir = ROOT / "review" / "postings"
    pdir.mkdir(parents=True, exist_ok=True)
    for old in pdir.glob("S*.md"):
        old.unlink()
    with (ROOT / "review" / "LABEL_SHEET.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sheet_id", "key", "title", "board", "location", "departments", "full_text", "label", "reason"])
        for k in all_keys:
            p, sid = corpus[k], sheet_ids[k]
            w.writerow([sid, k, p["title"], p["board"], p["location"] or "", "; ".join(p["departments"]),
                        f"review/postings/{sid}.md", "", ""])
            (pdir / f"{sid}.md").write_text(
                f"# {sid} — {p['title']}\n\n- key: `{k}`\n- board: {p['provider']}:{p['board']}\n"
                f"- location: {p['location'] or '(missing)'}\n- departments: {', '.join(p['departments']) or '(missing)'}\n"
                f"- url: {p['url']}\n- captured: {p['last_seen']}\n\n---\n\n{readable(p['text'])}\n",
                encoding="utf-8")
    return groups


if __name__ == "__main__":
    g = draw()
    print(json.dumps({k: g[k] for k in ("seeds", "clusters_total", "pools", "shortfalls")}, indent=1))
    print({grp: len(v) for grp, v in {**g["heldout"], **g["dev"]}.items()}, "sheet rows:", len(g["sheet_ids"]))


# ---- Plan amendment A3: fresh held-out set H2 (FILTER.md change log) -----------------------------------
SEED_H2, SEED_H2_SHEET = 7378, 7379
H2_SIZES = {"H2-near-reject(3-5)": 10, "H2-role-phrase-reject(<=2)": 7, "H2-other-reject": 7}


def draw_h2(write=True):
    """write=False recomputes the draw without touching any file (used by the tests while the sheet is being labeled)."""
    corpus = load_corpus()
    results, _ = score_all(load_filter("v1.0"), corpus)
    cl = json.loads((ROOT / "splits" / "clusters.json").read_text())
    groups = json.loads((ROOT / "splits" / "groups.json").read_text())
    used = {cl[k] for k in groups["sheet_ids"]}

    def stratum(r):
        if r["verdict"] != "reject":
            return r["verdict"]                          # keep / cannot_tell: not eligible for H2
        if 3 <= r["score"] <= 5:
            return "H2-near-reject(3-5)"
        if r["parts"]["R"]["points"] > 0:
            return "H2-role-phrase-reject(<=2)"
        return "H2-other-reject"

    rank = {"keep": 0, "cannot_tell": 1, "H2-near-reject(3-5)": 2, "H2-role-phrase-reject(<=2)": 3, "H2-other-reject": 4}
    members = defaultdict(list)
    for k in sorted(corpus):
        if cl[k] not in used:
            members[cl[k]].append(k)
    cl_stratum = {c: min((stratum(results[k]) for k in ks), key=rank.get) for c, ks in members.items()}
    rng = random.Random(SEED_H2)
    h2 = {}
    for name, n in H2_SIZES.items():
        pool = sorted(c for c, s in cl_stratum.items() if s == name)
        picked = rng.sample(pool, min(n, len(pool)))
        h2[name] = [rng.choice([k for k in members[c] if stratum(results[k]) == name]) for c in picked]
    keys = sorted(k for ks in h2.values() for k in ks)
    assert not ({cl[k] for k in keys} & used) and len({cl[k] for k in keys}) == len(keys)
    random.Random(SEED_H2_SHEET).shuffle(keys)
    sheet_ids = {k: f"H{i + 1:02d}" for i, k in enumerate(keys)}
    out = {"plan": "FILTER.md amendment A3", "seeds": {"heldout2": SEED_H2, "sheet_order": SEED_H2_SHEET},
           "eligible_clusters": dict(sorted(((s, sum(v == s for v in cl_stratum.values())) for s in set(cl_stratum.values())))),
           "shortfall": "no v1.0 keep cluster is outside the 63-row sheet, so H2 has no v1.0 keep",
           "heldout2": {g: [{"key": k, "score": results[k]["score"], "verdict": results[k]["verdict"]} for k in ks]
                        for g, ks in h2.items()},
           "sheet_ids": sheet_ids}
    if not write:
        return out
    (ROOT / "splits" / "heldout2.json").write_text(json.dumps(out, indent=1) + "\n")
    pdir = ROOT / "review" / "postings_h2"
    pdir.mkdir(parents=True, exist_ok=True)
    for old in pdir.glob("H*.md"):
        old.unlink()
    with (ROOT / "review" / "LABEL_SHEET_H2.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sheet_id", "key", "title", "board", "location", "departments", "full_text", "label", "reason"])
        for k in keys:
            p, sid = corpus[k], sheet_ids[k]
            w.writerow([sid, k, p["title"], p["board"], p["location"] or "", "; ".join(p["departments"]),
                        f"review/postings_h2/{sid}.md", "", ""])
            (pdir / f"{sid}.md").write_text(
                f"# {sid} — {p['title']}\n\n- key: `{k}`\n- board: {p['provider']}:{p['board']}\n"
                f"- location: {p['location'] or '(missing)'}\n- departments: {', '.join(p['departments']) or '(missing)'}\n"
                f"- url: {p['url']}\n- captured: {p['last_seen']}\n\n---\n\n{readable(p['text'])}\n", encoding="utf-8")
    return out
