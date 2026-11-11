"""Unit tests for labels/make_split.py (CONTRACT.md Interfaces › split.json). Written by Claude Code on 2026-10-30. All ids and labels are constructed."""
import importlib.util
import json

import pytest

from conftest import ROOT

HEADER = "posting_id,board,title,hand_label,labeled_on,note\n"
IDS = [str(1000 + i) for i in range(20)]


def make_split():
    spec = importlib.util.spec_from_file_location("make_split", ROOT / "labels" / "make_split.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_labels(workdir, rows):
    (workdir / "labels").mkdir(exist_ok=True)
    text = HEADER + "".join(f"{pid},acme,Title {pid},{label},2026-10-30,work\n" for pid, label in rows)
    (workdir / "labels" / "labels.csv").write_text(text, encoding="utf-8")
    return text


def labelled(ids=IDS):
    return [(pid, "relevant" if i % 3 == 0 else "not_relevant") for i, pid in enumerate(ids)]


def test_twenty_labelled_ids_split_ten_and_ten_and_labels_csv_is_untouched(workdir):
    text = write_labels(workdir, labelled())
    assert make_split().main(["--seed", "7375"]) == 0
    split = json.loads((workdir / "labels" / "split.json").read_text())
    assert split["seed"] == 7375 and set(split) == {"seed", "development", "held_out"}
    assert len(split["development"]) == len(split["held_out"]) == 10
    assert sorted(split["development"] + split["held_out"]) == IDS
    assert (workdir / "labels" / "labels.csv").read_text() == text


def test_the_split_depends_only_on_the_seed(workdir):
    write_labels(workdir, labelled())
    module = make_split()
    shuffled = list(reversed(IDS))
    assert module.make_split(7375, IDS) == module.make_split(7375, shuffled)
    assert module.make_split(7375, IDS) != module.make_split(7376, IDS)


def test_an_existing_split_is_never_replaced_by_a_different_one(workdir):
    write_labels(workdir, labelled())
    module = make_split()
    assert module.main(["--seed", "7375"]) == 0
    first = (workdir / "labels" / "split.json").read_bytes()
    assert module.main(["--seed", "7375"]) == 0
    assert module.main(["--seed", "1"]) == 2
    assert (workdir / "labels" / "split.json").read_bytes() == first


@pytest.mark.parametrize("rows", [
    labelled(IDS[:19]),                                # 19 ids
    labelled(IDS) + [("1000", "relevant")],            # 21 rows
    labelled(IDS[:19]) + [("1000", "relevant")],       # 20 rows, a repeated id
    labelled(IDS[:19]) + [("1019", "")],               # an unlabelled row
    labelled(IDS[:19]) + [("1019", "maybe")],          # a label outside the two
])
def test_anything_but_twenty_unique_labelled_ids_is_refused(workdir, rows, capsys):
    write_labels(workdir, rows)
    assert make_split().main(["--seed", "7375"]) == 2
    assert not (workdir / "labels" / "split.json").exists()
    assert "make_split: refused:" in capsys.readouterr().err
