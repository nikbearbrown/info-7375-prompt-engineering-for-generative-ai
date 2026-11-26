"""JS3 audit scripts (reports/audit_run.py, audit_sample.py, audit_report.py) on fake raw folders.

Every test builds its raw folders and audit files under tmp_path, so the repo's audit/ folder is
never written and nothing is fetched. The scripts are loaded from their files because reports/
is a folder of scripts, not a package.
"""

import csv
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OLD, NEW = "2026-11-01T000000Z", "2026-11-08T000000Z"
CSV_HEADER = ["sample_id", "board", "posting_id", "my_label", "my_reason"]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"audit_test_{name}", ROOT / "reports" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gh(job_id, title, location="United States", extra=""):
    content = f"<p>Marker M{job_id}. You will build backend services in Java.{extra}</p>"
    return {"id": job_id, "title": title, "location": {"name": location}, "offices": [],
            "content": content, "absolute_url": f"https://example.test/gh/{job_id}"}


def _write(folder, board, jobs, greenhouse=True):
    folder.mkdir(parents=True, exist_ok=True)
    data = {"jobs": jobs}
    if greenhouse:
        data["meta"] = {"total": len(jobs)}
    (folder / f"{board}_content.json").write_text(json.dumps(data), encoding="utf-8")


def _small_raw(tmp_path):
    raw = tmp_path / "raw"
    _write(raw / OLD, "stripe", [_gh(1, "Old Title"), _gh(2, "Backend Engineer")])
    _write(raw / NEW, "stripe", [_gh(1, "Backend Engineer, Payments"), _gh(3, "Senior Software Engineer"),
                                 dict(_gh(4, "Backend Engineer"), content="")])
    _write(raw / NEW, "openai", [{"id": "abc-uuid", "title": "Account Executive", "location": "London",
                                  "secondaryLocations": [], "jobUrl": "https://example.test/ashby/abc-uuid",
                                  "address": {"postalAddress": {"addressCountry": "United Kingdom"}},
                                  "descriptionHtml": "<p>Sell things.</p>"}], greenhouse=False)
    (raw / NEW / "stripe_content.headers.txt").write_text("HTTP 200", encoding="utf-8")
    (raw / OLD / "stripe_list.json").write_text(json.dumps({"jobs": [{"id": 99, "title": "x"}]}), encoding="utf-8")
    return raw


def _big_raw(tmp_path):
    jobs = [_gh(2000 + i, f"Senior Software Engineer {i}") for i in range(40)]
    jobs += [_gh(3000 + i, f"Backend Engineer {i}") for i in range(12)]
    jobs += [_gh(4000 + i, f"Backend Engineer Five {i}", extra=" You need 5+ years of experience.") for i in range(5)]
    jobs += [_gh(5000 + i, f"Backend Engineer London {i}", "London, United Kingdom") for i in range(5)]
    raw = tmp_path / "raw"
    _write(raw / NEW, "stripe", jobs)
    return raw


def _run(tmp_path, raw):
    out = tmp_path / "audit"
    _load("audit_run").run(raw, out)
    return out, json.loads((out / "all_verdicts.json").read_text(encoding="utf-8"))


def _sample(tmp_path, out_name="s1"):
    audit_dir, data = _run(tmp_path, _big_raw(tmp_path))
    out = tmp_path / out_name
    assert _load("audit_sample").sample(audit_dir, out) == 0
    return audit_dir, data, out


def test_run_dedupes_with_newest_folder_winning(tmp_path):
    _, data = _run(tmp_path, _small_raw(tmp_path))
    keys = [(p["board"], str(p["posting_id"])) for p in data["postings"]]
    assert keys == sorted(set(keys))
    assert data["total"] == len(keys) == 5
    by = {k: p for k, p in zip(keys, data["postings"])}
    assert by[("stripe", "1")]["title"] == "Backend Engineer, Payments"
    assert NEW in by[("stripe", "1")]["raw_file"]
    assert OLD in by[("stripe", "2")]["raw_file"]
    assert ("stripe", "99") not in by
    assert by[("openai", "abc-uuid")]["url"] == "https://example.test/ashby/abc-uuid"
    assert by[("stripe", "3")]["failed_check"] == "1a"
    assert by[("stripe", "4")]["status"] == "error"
    assert data["generated_from"] == [OLD, NEW]


def test_summary_rows_add_up(tmp_path):
    out, data = _run(tmp_path, _small_raw(tmp_path))
    lines = [l for l in (out / "summary.md").read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    assert header == ["board", "total", "1a", "1b", "2", "3", "4", "5", "6", "error", "relevant"]
    rows = {}
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows[cells[0]] = [int(c) for c in cells[1:]]
    assert set(rows) == {"stripe", "openai", "total"}
    for row in rows.values():
        assert row[0] == sum(row[1:])
    assert rows["total"] == [a + b for a, b in zip(rows["stripe"], rows["openai"])]
    assert rows["total"][0] == data["total"]
    assert rows["stripe"][header.index("error") - 1] == 1


def test_sample_is_reproducible_with_the_seed(tmp_path):
    audit_dir, _, out1 = _sample(tmp_path)
    mod = _load("audit_sample")
    assert mod.SEED == 20261124
    out2 = tmp_path / "s2"
    assert mod.sample(audit_dir, out2) == 0
    for name in ("sample_key.json", "hand_verdicts.csv", "to_judge.md"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes(), name


def test_sample_strata_do_not_overlap(tmp_path):
    _, data, out = _sample(tmp_path)
    key = json.loads((out / "sample_key.json").read_text(encoding="utf-8"))
    assert list(key) == [f"S{i:02d}" for i in range(1, len(key) + 1)]
    picked = [(e["board"], str(e["posting_id"])) for e in key.values()]
    assert len(picked) == len(set(picked))
    strata = [e["stratum"] for e in key.values()]
    assert strata.count("random_reject") == 30
    assert 1 <= strata.count("close_call") <= 10
    by = {(p["board"], str(p["posting_id"])): p for p in data["postings"]}
    for e in key.values():
        p = by[(e["board"], str(e["posting_id"]))]
        if e["stratum"] == "kept":
            assert p["verdict"] == "relevant"
        elif e["stratum"] == "random_reject":
            assert (p["verdict"], p["status"]) == ("not_relevant", "ok")


def test_hand_verdicts_csv_is_blank(tmp_path):
    _, _, out = _sample(tmp_path)
    with (out / "hand_verdicts.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == CSV_HEADER
    assert all(len(r) == 5 and r[3] == r[4] == "" for r in rows[1:])


def test_to_judge_is_blind(tmp_path):
    _, _, out = _sample(tmp_path)
    text = (out / "to_judge.md").read_text(encoding="utf-8")
    for word in ("random_reject", "close_call", "stratum", "failed_check", "filter verdict", "cut at",
                 "match: senior", "min 5 years", "1 found"):
        assert word not in text.lower(), word
    assert not re.search(r"\bkept\b", text.lower())
    assert "<p>" not in text
    key = json.loads((out / "sample_key.json").read_text(encoding="utf-8"))
    for sid, e in key.items():
        assert sid in text and f"Marker M{e['posting_id']}." in text


def test_sample_refuses_to_overwrite_filled_labels(tmp_path, capsys):
    audit_dir, _, out = _sample(tmp_path)
    mod = _load("audit_sample")
    assert mod.sample(audit_dir, out) == 0  # blank labels may be overwritten
    path = out / "hand_verdicts.csv"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    rows[1][3] = "relevant"
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    before = {n: (out / n).read_bytes() for n in ("hand_verdicts.csv", "sample_key.json", "to_judge.md")}
    capsys.readouterr()
    assert mod.sample(audit_dir, out, seed=1) != 0
    assert {n: (out / n).read_bytes() for n in before} == before
    assert "hand_verdicts.csv" in capsys.readouterr().err


def test_clopper_pearson_known_values():
    cp = _load("audit_report").clopper_pearson
    assert cp(0, 30)[0] == 0
    assert cp(0, 30)[1] == pytest.approx(1 - 0.025 ** (1 / 30), abs=1e-6)
    assert cp(30, 30) == pytest.approx((0.025 ** (1 / 30), 1.0), abs=1e-6)
    lo, hi = cp(3, 30)
    assert lo == pytest.approx(0.0211, abs=0.0005)
    assert hi == pytest.approx(0.2653, abs=0.0005)


def _report_dir(tmp_path, labels):
    d = tmp_path / "labels"
    d.mkdir()
    key, rows = {}, [CSV_HEADER]
    for i, (stratum, verdict, fc, label) in enumerate(labels, start=1):
        sid = f"S{i:02d}"
        key[sid] = {"board": "stripe", "posting_id": i, "title": f"Title {sid}", "stratum": stratum,
                    "verdict": verdict, "failed_check": fc, "seed": 20261124}
        rows.append([sid, "stripe", str(i), label, f"why {sid}"])
    (d / "sample_key.json").write_text(json.dumps(key), encoding="utf-8")
    with (d / "hand_verdicts.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    return d


def _labels():
    labels = [("random_reject", "not_relevant", "1a", "relevant" if i < 3 else "not_relevant") for i in range(30)]
    return labels + [("kept", "relevant", None, "not_relevant")]


def test_report_writes_intervals_and_only_disagreements(tmp_path):
    d = _report_dir(tmp_path, _labels())
    out = tmp_path / "out"
    assert _load("audit_report").report(d, out) == 0
    text = (out / "AUDIT.md").read_text(encoding="utf-8")
    assert "This is an estimate from 30 random rejects, not a measured rate for all postings." in text
    assert "0.021" in text and "0.265" in text
    assert "Title S01" in text and "Title S31" in text and "Title S10" not in text
    assert "## False friend\n\n(to be written by Isaac)" in text
    assert "## Rule changes (v2)\n\n(to be written by Isaac)" in text


@pytest.mark.parametrize("bad", ["", "maybe", "Relevant"])
def test_report_rejects_bad_labels_without_writing(tmp_path, capsys, bad):
    labels = _labels()
    labels[4] = ("random_reject", "not_relevant", "1a", bad)
    d = _report_dir(tmp_path, labels)
    out = tmp_path / "out"
    assert _load("audit_report").report(d, out) != 0
    assert not (out / "AUDIT.md").exists()
    assert "S05" in capsys.readouterr().err
