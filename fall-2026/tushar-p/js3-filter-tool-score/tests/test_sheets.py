"""Blind label sheets: sizes, disjointness, determinism (seed 7375), and no filter output
on the sheets or in the posting text files. All postings are synthetic."""

import csv
import json

import pytest

from agent import sheets

VERDICT_FIELDS = ("verdict", "score", "gate", "near_threshold", "stratum", "first_failing")


def result(board, pid, verdict, near=False):
    return {"board": board, "id": pid, "verdict": verdict, "near_threshold": near,
            "score": {"total": 2 if near else 0}, "gates": {}}


def synthetic_results(n_reject=200, n_keep=30, n_ct=30, n_near=20):
    rs = [result("greenhouse/stripe", i, "reject") for i in range(n_reject)]
    rs += [result("ashby/notion", f"k{i}", "keep") for i in range(n_keep)]
    rs += [result("ashby/linear", f"c{i}", "cannot_tell") for i in range(n_ct)]
    rs += [result("greenhouse/stripe", 10_000 + i, "keep" if i % 2 else "reject", near=True) for i in range(n_near)]
    return rs


def test_sizes_and_disjoint():
    chosen = sheets.select(synthetic_results())
    strata = list(chosen["strata"].values())
    assert strata.count("near_threshold") == 15
    assert strata.count("reject") == 30 and strata.count("keep") == 10 and strata.count("cannot_tell") == 10
    assert len(chosen["audit"]) == 65 == len(set(chosen["audit"]))
    assert len(chosen["heldout"]) == 30 == len(set(chosen["heldout"]))
    assert not set(chosen["audit"]) & set(chosen["heldout"])
    assert chosen["shortfalls"] == {}


def test_near_threshold_rows_are_not_double_counted_as_keeps_or_rejects():
    rs = synthetic_results(n_near=4)
    chosen = sheets.select(rs)
    near_keys = {sheets.key_of(r) for r in rs if r["near_threshold"]}
    assert {k for k, s in chosen["strata"].items() if s == "near_threshold"} == near_keys  # all of them, <= 15
    assert all(chosen["strata"][k] == "near_threshold" for k in near_keys)


def test_shortfall_takes_whole_pool_and_reports_it():
    chosen = sheets.select(synthetic_results(n_keep=3, n_ct=0, n_near=0))
    strata = list(chosen["strata"].values())
    assert strata.count("keep") == 3 and strata.count("cannot_tell") == 0
    assert chosen["shortfalls"] == {"keep": {"target": 10, "available": 3},
                                    "cannot_tell": {"target": 10, "available": 0}}


def test_deterministic_with_seed_and_input_order():
    rs = synthetic_results()
    a = sheets.select(rs, 7375)
    b = sheets.select(list(reversed(rs)), 7375)
    assert a == b
    assert sheets.select(rs, 1)["audit"] != a["audit"]


def test_audit_rows_are_shuffled_not_grouped_by_stratum():
    chosen = sheets.select(synthetic_results())
    order = [chosen["strata"][k] for k in chosen["audit"]]
    runs = sum(1 for i in range(1, len(order)) if order[i] != order[i - 1])
    assert runs > 10  # grouped blocks would give exactly 3 changes


def make_run_with(tmp_path, results):
    """A run folder whose Greenhouse/Ashby raw files hold one posting per result."""
    run_id = "run-test-1"
    run = tmp_path / "run"
    boards = []
    for board in sorted({r["board"] for r in results}):
        provider, token = board.split("/")
        jobs = []
        for r in (r for r in results if r["board"] == board):
            if provider == "greenhouse":
                jobs.append({"id": r["id"], "title": f"Title {r['id']}", "location": {"name": "SF"},
                             "content": "&lt;p&gt;Synthetic posting text.&lt;/p&gt;", "absolute_url": f"https://x/{r['id']}"})
            else:
                jobs.append({"id": r["id"], "title": f"Title {r['id']}", "location": "Remote",
                             "secondaryLocations": [], "descriptionPlain": "Synthetic posting text.",
                             "jobUrl": f"https://y/{r['id']}"})
        raw = run / "raw" / provider / token
        raw.mkdir(parents=True)
        (raw / "attempt-1.raw").write_text(json.dumps({"jobs": jobs}))
        boards.append({"board": board, "provider": provider, "token": token, "status": "succeeded",
                       "raw_paths": [f"runs/{run_id}/raw/{provider}/{token}/attempt-1.raw"]})
    (run / "summary.json").write_text(json.dumps({"run_id": run_id, "boards": boards}))
    results_path = tmp_path / "results.jsonl"
    results_path.write_text("".join(json.dumps(r) + "\n" for r in results))
    return run, results_path


def test_written_sheets_are_blind(tmp_path):
    rs = synthetic_results()
    run, results_path = make_run_with(tmp_path, rs)
    root, key = tmp_path / "proj", tmp_path / "out" / "key.json"
    info = sheets.build_sheets(run, results_path, root=root, key_path=key)
    assert info["audit_rows"] == 65 and info["heldout_rows"] == 30
    for sheet in (root / "audit" / "audit-sheet.csv", root / "labels" / "heldout-sheet.csv"):
        rows = list(csv.DictReader(sheet.open()))
        assert tuple(rows[0].keys()) == sheets.COLUMNS
        filter_side = [c for c in sheets.COLUMNS if c not in ("my_verdict", "note")]  # human-entry columns
        assert not any(word in col for col in filter_side for word in VERDICT_FIELDS)
        assert all(r["my_verdict"] == "" and r["note"] == "" for r in rows)
        assert not any(r[c] in ("keep", "reject", "cannot_tell") for r in rows for c in sheets.COLUMNS)
        for r in rows:
            text = (sheet.parent / r["text_file"]).read_text()
            assert "Synthetic posting text." in text
            assert not any(word in text.lower() for word in ("verdict", "near_threshold", "stratum", "score"))
    # The stratum key exists, but outside the sheet folders.
    assert key.exists() and not list(root.rglob("*key*"))
    audit_ids = {r["id"] for r in csv.DictReader((root / "audit" / "audit-sheet.csv").open())}
    held_ids = {r["id"] for r in csv.DictReader((root / "labels" / "heldout-sheet.csv").open())}
    assert not audit_ids & held_ids


def test_refuses_to_overwrite_existing_sheets(tmp_path):
    run, results_path = make_run_with(tmp_path, synthetic_results())
    root = tmp_path / "proj"
    sheets.build_sheets(run, results_path, root=root)
    sheet = root / "audit" / "audit-sheet.csv"
    sheet.write_text("my hand labels")
    with pytest.raises(FileExistsError):
        sheets.build_sheets(run, results_path, root=root)
    assert sheet.read_text() == "my hand labels"
