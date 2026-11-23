"""Blind labeler (tools/label.py): write-once labels, resume, --correct, labeled_at column,
atomic writes, and no reads under out/. Every sheet and posting here is tiny and synthetic,
built with the real sheet writer so the format matches production."""

import builtins
import csv
import io
import os

import pytest

from agent import sheets
from tools import label

NOW = "2026-11-23T10:15:00-05:00"
LATER = "2026-11-25T09:00:00-05:00"


def posting(board, pid, title, text, locations=("Boston, MA",)):
    return {"board": board, "id": pid, "title": title, "locations": list(locations),
            "date": "2026-11-01", "url": f"https://example.test/{pid}", "text": text}


SYNTHETIC = [
    posting("greenhouse/acme", 1, "Synthetic Data Intern",
            "We build things. This is a summer intern role for students. "
            "Candidates must be located in Boston. We do not sponsor visas.\nSalary is fine."),
    posting("ashby/beta", "b2", "Synthetic Platform Engineer",
            "Five years of experience required. Fully remote within the US."),
    posting("greenhouse/acme", 3, "Synthetic Analyst", "No keywords at all here"),
]


def make_sheet(root, postings=SYNTHETIC):
    sheet = root / "labels" / "heldout-sheet.csv"
    by_key = {(p["board"], str(p["id"])): p for p in postings}
    sheets.write_sheet(sheet, list(by_key), by_key)
    return sheet


def rows_of(sheet):
    with open(sheet, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        return header, [dict(zip(header, v)) for v in reader]


def feed(*answers):
    """An ask() that returns the given answers in order, then raises EOFError like a closed stdin."""
    it = iter(answers)
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None

    ask.prompts = prompts
    return ask


class Screen:
    def __init__(self):
        self.lines = []

    def __call__(self, *parts):
        self.lines.append(" ".join(str(p) for p in parts))

    @property
    def text(self):
        return "\n".join(self.lines)


def run(argv, *answers, now=NOW):
    screen = Screen()
    code = label.main([str(a) for a in argv], ask=feed(*answers), say=screen, now=lambda: now)
    return code, screen


# ---------------------------------------------------------------- core behaviour

def test_writes_a_verdict_note_and_timestamp(tmp_path):
    sheet = make_sheet(tmp_path)
    code, screen = run([sheet], "k", "looks like a fit", "q")
    assert code == 0
    _, rows = rows_of(sheet)
    assert rows[0]["my_verdict"] == "keep"
    assert rows[0]["note"] == "looks like a fit"
    assert rows[0]["labeled_at"] == NOW
    assert [r["my_verdict"] for r in rows[1:]] == ["", ""]
    assert [r["labeled_at"] for r in rows[1:]] == ["", ""]
    assert "row 1   (1/3)" in screen.text
    assert "labeled 1/3 (1 this session), skipped 0, left 2" in screen.text


def test_each_verdict_key_and_empty_note(tmp_path):
    sheet = make_sheet(tmp_path)
    run([sheet], "k", "", "r", "", "c", "")
    _, rows = rows_of(sheet)
    assert [r["my_verdict"] for r in rows] == ["keep", "reject", "cannot_tell"]
    assert [r["note"] for r in rows] == ["", "", ""]


def test_resumes_at_first_unlabeled_row(tmp_path):
    sheet = make_sheet(tmp_path)
    run([sheet], "r", "first pass", "q")
    code, screen = run([sheet], "c", "", "q", now=LATER)
    assert code == 0
    assert "row 1   (1/3)" not in screen.text
    assert "row 2   (2/3)" in screen.text
    _, rows = rows_of(sheet)
    assert (rows[0]["my_verdict"], rows[0]["note"], rows[0]["labeled_at"]) == ("reject", "first pass", NOW)
    assert (rows[1]["my_verdict"], rows[1]["labeled_at"]) == ("cannot_tell", LATER)
    assert rows[2]["my_verdict"] == ""


def test_skip_is_not_saved_and_is_offered_again(tmp_path):
    sheet = make_sheet(tmp_path)
    code, screen = run([sheet], "s", "k", "", "q")
    _, rows = rows_of(sheet)
    assert [r["my_verdict"] for r in rows] == ["", "keep", ""]
    assert "labeled 1/3 (1 this session), skipped 1, left 1" in screen.text
    code, screen = run([sheet], "q")
    assert "row 1   (1/3)" in screen.text


def test_invalid_key_reprompts_without_writing(tmp_path):
    sheet = make_sheet(tmp_path)
    before = sheet.read_bytes()
    code, screen = run([sheet], "keep", "x", "", "q")
    assert code == 0
    assert sheet.read_bytes() == before
    assert screen.text.count("please type k, r, c, f, s or q") == 3


def test_eof_at_note_prompt_does_not_save_the_row(tmp_path):
    sheet = make_sheet(tmp_path)
    before = sheet.read_bytes()
    code, screen = run([sheet], "k")  # stdin closes at the note prompt
    assert code == 0
    assert sheet.read_bytes() == before
    assert "not saved" in screen.text


# ---------------------------------------------------------------- write-once

def test_refuses_to_overwrite_an_existing_verdict(tmp_path):
    sheet = make_sheet(tmp_path)
    run([sheet], "r", "mine", "q")
    after_first = sheet.read_bytes()
    with pytest.raises(label.LabelError, match="written once"):
        label.write_label(sheet, "1", "keep", "changed my mind", LATER)
    assert sheet.read_bytes() == after_first


def test_refuses_when_the_row_was_labeled_on_disk_after_the_session_loaded(tmp_path, monkeypatch):
    sheet = make_sheet(tmp_path)
    original_write = label.write_label

    def labeled_elsewhere_first(path, row_no, verdict, note, labeled_at):
        original_write(path, row_no, "reject", "other window", NOW)
        return original_write(path, row_no, verdict, note, labeled_at)

    monkeypatch.setattr(label, "write_label", labeled_elsewhere_first)
    code, screen = run([sheet], "k", "", "q")
    assert code == 2
    assert "written once" in screen.text
    _, rows = rows_of(sheet)
    assert (rows[0]["my_verdict"], rows[0]["note"]) == ("reject", "other window")


def test_correct_keeps_the_old_value_and_date_in_the_note(tmp_path):
    sheet = make_sheet(tmp_path)
    run([sheet], "k", "seemed fine", "q")
    code, screen = run([sheet, "--correct", "1"], "r", "missed the visa line", now=LATER)
    assert code == 0
    _, rows = rows_of(sheet)
    assert rows[0]["my_verdict"] == "reject"
    assert rows[0]["labeled_at"] == LATER
    assert rows[0]["note"] == (f"[corrected 2026-11-25: was keep (labeled {NOW}), old note: seemed fine]"
                               " missed the visa line")
    assert [r["my_verdict"] for r in rows[1:]] == ["", ""]


def test_correct_refuses_blank_rows_same_verdict_and_cancel(tmp_path):
    sheet = make_sheet(tmp_path)
    code, screen = run([sheet, "--correct", "2"], "k", "")
    assert code == 2 and "no verdict yet" in screen.text
    run([sheet], "k", "", "q")
    labeled = sheet.read_bytes()
    code, screen = run([sheet, "--correct", "1"], "k", "")
    assert code == 2 and "nothing to correct" in screen.text
    code, screen = run([sheet, "--correct", "1"], "q")
    assert code == 0 and "cancelled" in screen.text
    code, screen = run([sheet, "--correct", "99"], "r", "")
    assert code == 2 and "not found" in screen.text
    assert sheet.read_bytes() == labeled


# ---------------------------------------------------------------- sheet format

def test_adds_labeled_at_without_changing_other_columns(tmp_path):
    sheet = make_sheet(tmp_path)
    header_before, rows_before = rows_of(sheet)
    assert header_before == list(sheets.COLUMNS)
    run([sheet], "s", "c", "a note, with a comma", "q")
    header_after, rows_after = rows_of(sheet)
    assert header_after == list(sheets.COLUMNS) + ["labeled_at"]
    assert len(rows_after) == len(rows_before)
    for i, (before, after) in enumerate(zip(rows_before, rows_after)):
        changed = {"my_verdict", "note"} if i == 1 else set()
        for col in sheets.COLUMNS:
            if col not in changed:
                assert after[col] == before[col], (i, col)
    assert rows_after[1]["note"] == "a note, with a comma"
    assert [r["labeled_at"] for r in rows_after] == ["", NOW, ""]


def test_untouched_sheet_bytes_survive_a_rewrite(tmp_path):
    """Rewriting with the same csv dialect leaves unlabeled rows byte-identical."""
    sheet = make_sheet(tmp_path)
    original_lines = sheet.read_bytes().split(b"\r\n")
    run([sheet], "s", "s", "k", "", "q")
    new_lines = sheet.read_bytes().split(b"\r\n")
    assert new_lines[0] == original_lines[0] + b",labeled_at"
    assert new_lines[1] == original_lines[1] + b","
    assert new_lines[2] == original_lines[2] + b","


def test_failed_replace_leaves_the_sheet_unchanged_and_no_temp_file(tmp_path, monkeypatch):
    sheet = make_sheet(tmp_path)
    before = sheet.read_bytes()

    def crash(src, dst):
        raise OSError("simulated crash during replace")

    monkeypatch.setattr(label.os, "replace", crash)
    code, screen = run([sheet], "k", "", "q")
    assert code == 2
    assert sheet.read_bytes() == before
    assert sorted(p.name for p in sheet.parent.iterdir()) == ["heldout-sheet.csv", "texts"]


# ---------------------------------------------------------------- display and blindness

def test_shows_metadata_preview_and_keyword_sentences(tmp_path):
    long_text = "Opening line. " + "Filler sentence. " * 60 + "Must be authorized to work in the US."
    sheet = make_sheet(tmp_path, SYNTHETIC[:1] + [posting("ashby/beta", "b9", "Long One", long_text)])
    code, screen = run([sheet], "s", "s")
    out = screen.text
    assert "board:     greenhouse/acme" in out
    assert "title:     Synthetic Data Intern" in out
    assert "locations: Boston, MA" in out
    assert "date:      2026-11-01" in out
    assert "  • This is a summer intern role for students." in out
    assert "  • Candidates must be located in Boston." in out
    assert "  • We do not sponsor visas." in out
    assert "  • We build things." not in out and "  • Salary is fine." not in out
    assert "sentences with year, sponsor, visa, authoriz, remote, located, intern: 3" in out
    # second row: preview is capped at 800 characters, keyword sentence past the cap still listed
    assert "  • Must be authorized to work in the US." in out
    preview_line = next(line for line in screen.lines if line.startswith("Opening line."))
    assert len(preview_line) == label.PREVIEW_CHARS + 1 and preview_line.endswith("…")


def test_full_text_pages_on_f(tmp_path):
    many_lines = "\n".join(f"line {i}." for i in range(1, 101))
    sheet = make_sheet(tmp_path, [posting("ashby/beta", "p1", "Paged", many_lines)])
    ask = feed("f", "", "q", "q")
    screen = Screen()
    label.main([str(sheet)], ask=ask, say=screen, now=lambda: NOW)
    assert "line 100." not in screen.lines  # stopped after the second page
    assert "line 1." in screen.lines and "line 2." in screen.lines
    assert any("Enter for more, q to stop" in p for p in ask.prompts)
    assert sum("Enter for more" in p for p in ask.prompts) == 2


def test_never_shows_columns_beyond_the_reader_fields(tmp_path):
    """Even if a sheet carried filter output, the labeler would not display it."""
    sheet = make_sheet(tmp_path)
    header, rows = rows_of(sheet)
    header = header + ["score", "verdict", "stratum"]
    for r in rows:
        r.update(score="SECRET-SCORE-7", verdict="SECRET-VERDICT", stratum="SECRET-STRATUM")
    label.write_sheet_atomic(sheet, header, rows)
    code, screen = run([sheet], "s", "s", "s")
    assert "SECRET" not in screen.text


def test_never_opens_anything_under_out(tmp_path, monkeypatch):
    sheet = make_sheet(tmp_path)
    out_dir = tmp_path / "out" / "filter-v0.1"
    out_dir.mkdir(parents=True)
    (out_dir / "sheet-key.json").write_text('{"stratum": "SECRET"}')
    (out_dir / "results.jsonl").write_text('{"verdict": "SECRET"}\n')
    opened = []
    real_open, real_io_open, real_os_open = builtins.open, io.open, os.open

    def spy(real):
        def wrapper(file, *args, **kwargs):
            if not isinstance(file, int):
                opened.append(os.path.realpath(os.fspath(file)))
            return real(file, *args, **kwargs)
        return wrapper

    monkeypatch.setattr(builtins, "open", spy(real_open))
    monkeypatch.setattr(io, "open", spy(real_io_open))
    monkeypatch.setattr(os, "open", spy(real_os_open))
    code, screen = run([sheet], "f", "k", "note", "s", "r", "", "q")
    run([sheet, "--correct", "1"], "c", "")
    monkeypatch.undo()
    out_root = os.path.realpath(tmp_path / "out")
    assert opened, "the spy saw no opens, so it would not catch an out/ read"
    assert os.path.realpath(sheet) in opened
    assert not [p for p in opened if p == out_root or p.startswith(out_root + os.sep)]
    assert "SECRET" not in screen.text


def test_refuses_text_files_and_sheets_under_out_or_outside_the_sheet_folder(tmp_path):
    sheet = make_sheet(tmp_path)
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "leak.txt").write_text("SECRET")
    header, rows = rows_of(sheet)
    rows[0]["text_file"] = "../out/leak.txt"
    label.write_sheet_atomic(sheet, header, rows)
    code, screen = run([sheet], "k", "")
    assert code == 2 and "(blind labeling)" in screen.text and "SECRET" not in screen.text
    rows[0]["text_file"] = "../escape.txt"
    label.write_sheet_atomic(sheet, header, rows)
    code, screen = run([sheet], "k", "")
    assert code == 2 and "outside" in screen.text
    out_sheet = tmp_path / "out" / "copy.csv"
    out_sheet.write_bytes(make_sheet(tmp_path / "fresh").read_bytes())
    code, screen = run([out_sheet], "q")
    assert code == 2 and "(blind labeling)" in screen.text
    assert "row 1" not in screen.text
