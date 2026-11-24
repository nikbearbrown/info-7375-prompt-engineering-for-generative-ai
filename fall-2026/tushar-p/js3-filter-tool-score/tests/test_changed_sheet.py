"""tools/changed_sheet.py: the blind changed-postings sheet (changed rows + equal controls)."""

import csv
import importlib.util
import json
import shutil

import pytest

from agent import PROJECT_DIR
from agent.sheets import COLUMNS

FORBIDDEN = ("verdict", "score", "gate", "group", "mode", "changed", "control", "stratum")


def _load():
    spec = importlib.util.spec_from_file_location("changed_sheet", PROJECT_DIR / "tools" / "changed_sheet.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cs = _load()


def fake_results(verdicts_by_mode):
    return {m: {k: {"verdict": v} for k, v in vs.items()} for m, vs in verdicts_by_mode.items()}


def test_choose_takes_every_changed_posting_and_equal_unchanged_controls():
    keys = [("b", str(i)) for i in range(20)]
    base = {k: "reject" for k in keys}
    modes = {"v0.1": base, **{m: dict(base) for m in cs.MODES}}
    modes["v0.1+C1"][keys[3]] = "keep"
    modes["v0.2"][keys[3]] = "keep"
    modes["v0.1+C4"][keys[7]] = "cannot_tell"
    modes["v0.1+C1"][keys[0]] = "keep"                      # excluded: on another sheet
    chosen = cs.choose(fake_results(modes), excluded={keys[0], keys[1]})
    groups = chosen["groups"]
    assert sorted(k for k, g in groups.items() if g == "changed") == [keys[3], keys[7]]
    controls = [k for k, g in groups.items() if g == "control"]
    assert len(controls) == 2 and not set(controls) & {keys[0], keys[1], keys[3], keys[7]}
    assert all(chosen["moved_by"][k] == [] for k in controls)
    assert chosen["moved_by"][keys[3]] == ["v0.1+C1", "v0.2"] and chosen["moved_by"][keys[7]] == ["v0.1+C4"]
    assert sorted(chosen["rows"]) == sorted(groups) and len(chosen["rows"]) == 4
    assert cs.choose(fake_results(modes), excluded={keys[0], keys[1]}) == chosen   # seeded: same draw


def test_choose_refuses_when_controls_run_out():
    keys = [("b", "1"), ("b", "2"), ("b", "3")]
    modes = {"v0.1": {k: "reject" for k in keys}, **{m: {k: "keep" for k in keys[:2]} | {keys[2]: "reject"}
                                                     for m in cs.MODES}}
    with pytest.raises(ValueError):
        cs.choose(fake_results(modes), excluded=set())


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root = tmp_path_factory.mktemp("root")
    (root / "audit").mkdir()
    (root / "labels").mkdir()
    shutil.copy(PROJECT_DIR / "audit" / "audit-sheet.csv", root / "audit" / "audit-sheet.csv")
    shutil.copy(PROJECT_DIR / "labels" / "heldout-sheet.csv", root / "labels" / "heldout-sheet.csv")
    info = cs.build(root=root, run_dir=cs.RUN, key_path=root / "out" / "changed-key.json")
    return root, info


def test_built_sheet_is_blind_and_complete(built):
    root, info = built
    with open(root / "labels" / "changed-sheet.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert tuple(reader.fieldnames) == COLUMNS
    assert not any(word in col for col in reader.fieldnames for word in FORBIDDEN if col != "my_verdict")
    assert len(rows) == info["rows"] == 2 * info["changed"] and info["changed"] > 0
    assert [r["row"] for r in rows] == [str(i) for i in range(1, len(rows) + 1)]
    assert all(r["my_verdict"] == "" and r["note"] == "" for r in rows)
    for r in rows:
        assert r["text_file"].startswith("changed-texts/")
        text = (root / "labels" / r["text_file"]).read_text(encoding="utf-8")
        assert "--- posting text ---" in text and not any(f"{w}:" in text.split("---")[0] for w in FORBIDDEN)


def test_built_sheet_excludes_the_audit_and_heldout_rows(built):
    root, _ = built
    on_sheet = cs.sheet_keys(root / "labels" / "changed-sheet.csv")
    assert not on_sheet & (cs.sheet_keys(root / "audit" / "audit-sheet.csv")
                           | cs.sheet_keys(root / "labels" / "heldout-sheet.csv"))


def test_key_records_groups_and_matches_the_sheet(built):
    root, info = built
    key = json.loads((root / "out" / "changed-key.json").read_text())
    assert key["seed"] == 7375 and key["rules"] == "frozen at commit f3edf99"
    groups = [r["group"] for r in key["rows"]]
    assert groups.count("changed") == groups.count("control") == info["changed"]
    for r in key["rows"]:
        moved = [m for m in cs.MODES if r["verdicts"][m] != r["verdicts"]["v0.1"]]
        assert moved == r["moved_by"] and bool(moved) == (r["group"] == "changed")
    with open(root / "labels" / "changed-sheet.csv", newline="", encoding="utf-8") as fh:
        assert [(r["board"], r["id"]) for r in csv.DictReader(fh)] == [(r["board"], r["id"]) for r in key["rows"]]


def test_rebuild_refuses_to_overwrite_and_force_is_deterministic(built):
    root, _ = built
    sheet = root / "labels" / "changed-sheet.csv"
    before = sheet.read_bytes()
    with pytest.raises(FileExistsError):
        cs.build(root=root, run_dir=cs.RUN, key_path=root / "out" / "changed-key.json")
    cs.build(root=root, run_dir=cs.RUN, key_path=root / "out" / "changed-key.json", force=True)
    assert sheet.read_bytes() == before


def test_committed_sheet_matches_a_fresh_build(built):
    root, _ = built
    assert (root / "labels" / "changed-sheet.csv").read_bytes() == \
        (PROJECT_DIR / "labels" / "changed-sheet.csv").read_bytes()
