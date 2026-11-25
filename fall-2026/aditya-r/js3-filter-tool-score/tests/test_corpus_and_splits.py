"""Checks on the observed corpus and the committed split (these read real captures, not fixtures)."""
import csv
import json
from pathlib import Path

from inherited.rules import html_to_text, normalize
from js3.corpus import load_corpus
from js3.filter import load_filter, score_posting
from js3.text import readable

ROOT = Path(__file__).resolve().parent.parent
GROUPS = json.loads((ROOT / "splits" / "groups.json").read_text())
CLUSTERS = json.loads((ROOT / "splits" / "clusters.json").read_text())
CORPUS = load_corpus()
V1 = load_filter("v1.0")


def test_provenance_counts():
    prov = json.loads((ROOT / "corpus" / "PROVENANCE.json").read_text())
    assert prov["unique_postings"] == len(CORPUS) == 1294
    assert prov["unique_postings_by_board"] == {"databricks": 995, "figma": 144, "notion": 155}
    assert [u["status"] for u in prov["unavailable_boards"]] == [404]


def test_readable_matches_inherited_normalization():
    for p in CORPUS.values():
        assert normalize(readable(p["text"])) == normalize(html_to_text(p["text"]))


def test_heldout_and_dev_disjoint_by_cluster():
    split = GROUPS["split_of_sheet_id"]
    ids = GROUPS["sheet_ids"]
    dev_c = {CLUSTERS[k] for k, s in ids.items() if split[s] == "dev"}
    h_c = {CLUSTERS[k] for k, s in ids.items() if split[s] == "heldout"}
    assert dev_c and h_c and not (dev_c & h_c)
    assert len({CLUSTERS[k] for k in ids}) == len(ids)  # one posting per cluster on the sheet


def test_thirty_distinct_random_rejects_that_v1_rejects():
    rr = GROUPS["dev"]["D-random-reject"]
    assert len({r["key"] for r in rr}) == 30
    for r in rr:
        assert score_posting(CORPUS[r["key"]], V1)["verdict"] == "reject"


def test_sheet_is_blind():
    with (ROOT / "review" / "LABEL_SHEET.csv").open(encoding="utf-8-sig") as f:
        header = next(csv.reader(f))
    assert not {"score", "verdict", "group", "split", "prediction"} & {h.lower() for h in header}
    for md in (ROOT / "review" / "postings").glob("S*.md"):
        head = md.read_text(encoding="utf-8").split("---", 1)[0].lower()
        assert "score" not in head and "verdict" not in head and "group" not in head


def test_draw_is_reproducible():
    from js3.sample import draw
    before = json.dumps(GROUPS, sort_keys=True)
    after = json.dumps(draw(), sort_keys=True)
    assert before == after


def test_h2_disjoint_from_sheet_blind_and_reproducible():
    from js3.sample import draw_h2
    h2 = json.loads((ROOT / "splits" / "heldout2.json").read_text())
    sheet_clusters = {CLUSTERS[k] for k in GROUPS["sheet_ids"]}
    h2_keys = list(h2["sheet_ids"])
    assert len(h2_keys) == 24 and len({CLUSTERS[k] for k in h2_keys}) == 24
    assert not {CLUSTERS[k] for k in h2_keys} & sheet_clusters
    with (ROOT / "review" / "LABEL_SHEET_H2.csv").open(encoding="utf-8-sig") as f:
        header = next(csv.reader(f))
    assert not {"score", "verdict", "group", "split"} & {h.lower() for h in header}
    labels = (ROOT / "review" / "LABEL_SHEET_H2.csv").read_bytes()
    assert json.dumps(draw_h2(), sort_keys=True) == json.dumps(h2, sort_keys=True)
    (ROOT / "review" / "LABEL_SHEET_H2.csv").write_bytes(labels)  # draw_h2 rewrites the blank sheet; keep any labels
