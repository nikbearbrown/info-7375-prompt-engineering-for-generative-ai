"""Phase 2d: FILTER.md section 1 text rules and the dataset builder (sections 3 and 5).

Written by Claude Code (claude-opus-5-5), 2026-11-25. Strings in the unit tests are hand-built
(SEEDED); the dataset tests read the committed live run runs/20261125T200226Z through tools.
"""
import json

import pytest

import js3kit
from jobwatch import dataset
from jobwatch.policy import Policy
from jobwatch.text import join_fields, normalize_field, normalize_single, split_sentences
from jobwatch.tools import PolicyDenied, Tools

RUN = "runs/20261125T200226Z"


# --- sentences (FILTER.md section 1, M4) -----------------------------------------------------
def test_period_inside_a_number_or_name_does_not_end_a_sentence():
    assert normalize_field("You have 3.5 years with Node.js and PyTorch. Next one") == \
        ["You have 3.5 years with Node.js and PyTorch.", "Next one"]


def test_period_followed_by_a_space_ends_a_sentence_even_in_an_abbreviation():
    # Known and accepted: "U.S. citizens" and "e.g. Python" split (Gate 1, M4 choice).
    assert normalize_field("Open to U.S. citizens") == ["Open to U.S.", "citizens"]


def test_question_and_exclamation_marks_end_sentences():
    assert normalize_field("Why us? Join now! Thanks") == ["Why us?", "Join now!", "Thanks"]


def test_block_element_ends_split_before_tags_are_stripped():
    assert normalize_field("<p>Intro</p><ul><li>Python</li><li>SQL</li></ul>Line<br/>Next<div>x</div>") == \
        ["Intro", "Python", "SQL", "Line", "Next x"]
    # Only the END of a block element ends a sentence (FILTER.md section 1), so the text before an
    # opening <div> runs on into it: "Next<div>x</div>" is one sentence.


def test_split_happens_on_raw_html_pieces():
    assert split_sentences("<li>a</li>b") == ["<li>a</li>", "b"]


# --- order and normalization (V3) -----------------------------------------------------------
def test_greenhouse_escaped_html_splits_after_the_first_unescape():
    raw = "&lt;p&gt;We build ML.&lt;/p&gt;&lt;p&gt;Benefits&amp;nbsp;here&lt;/p&gt;"
    assert normalize_field(raw) == ["We build ML.", "Benefits here"]


def test_second_unescape_and_whitespace_collapse_happen_within_each_sentence():
    assert normalize_field("<p>R&amp;amp;D   team\n\tworks</p>") == ["R&D team works"]


def test_no_6000_character_truncation():
    long = "word " * 3000
    (s,) = normalize_field(long)
    assert len(s) == len(long.strip()) > 6000


# --- joining (V4, K3) and title/location (K5) ------------------------------------------------
def test_fields_join_with_newline_sentences_with_space_and_offsets_are_exact():
    text, sents, spans = join_fields((("description", "<p>One.</p><p>Two</p>"), ("lists[0].text", "HEADING"),
                                      ("lists[0].content", ""), ("additional", "<li>Three</li>")))
    assert text == "One. Two\nHEADING\nThree"
    assert [text[s["start"]:s["end"]] for s in sents] == ["One.", "Two", "HEADING", "Three"]
    assert [s["field"] for s in sents] == ["description", "description", "lists[0].text", "additional"]
    assert [sp["field"] for sp in spans] == ["description", "lists[0].text", "additional"]


def test_a_lever_heading_is_its_own_sentence():
    text, sents, _ = join_fields((("lists[0].text", "THE SKILL SET"), ("lists[0].content", "<li>5+ years</li>")))
    assert [text[s["start"]:s["end"]] for s in sents] == ["THE SKILL SET", "5+ years"]


def test_title_and_location_are_one_field_each_and_missing_is_none():
    assert normalize_single("  Machine Learning   Engineer ") == "Machine Learning Engineer"
    assert normalize_single("Remote - U.S. ") == "Remote - U.S."
    assert normalize_single(None) is None
    assert normalize_single("   ") == ""


# --- boilerplate (section 3, U6) -----------------------------------------------------------
def _line(text_fields):
    text, sents, spans = join_fields(text_fields)
    return {"text": text, "sentences": [{"field": s["field"], "start": s["start"], "end": s["end"]} for s in sents]}


def test_boilerplate_is_a_sentence_in_at_least_half_of_one_boards_postings():
    lines = [_line((("d", "<p>About us.</p><p>Role A</p>"),)), _line((("d", "<p>About us.</p><p>Role B</p>"),)),
             _line((("d", "<p>Role C</p>"),)), _line((("d", "<p>Role D</p><p>Role D</p>"),))]
    dataset._flag_boilerplate(lines)
    flags = [[(ln["text"][s["start"]:s["end"]], s["boilerplate"]) for s in ln["sentences"]] for ln in lines]
    assert flags[0] == [("About us.", True), ("Role A", False)]
    # "Role D" twice in one posting counts once: 1 of 4 postings, not boilerplate.
    assert flags[3] == [("Role D", False), ("Role D", False)]


# --- the dataset of the committed run, read through tools --------------------------------
@pytest.fixture(scope="module")
def built():
    events = []
    tools = Tools(Policy(str(js3kit.ROOT), read_dirs=("runs",), write_dirs=()), on_event=events.append)
    lines, meta = dataset.build(tools, RUN)
    return lines, meta, events


def test_dataset_reads_the_run_only_through_tools_read_file(built):
    _, _, events = built
    assert events and all(e["tool"] == "read_file" and e["outcome"] == "read" for e in events)
    assert {e["args"]["path"].split("/")[0] for e in events} == {"runs"}


def test_dataset_counts_match_the_run_summary_and_the_failed_board_is_listed(built):
    lines, meta, _ = built
    summary = json.loads((js3kit.ROOT / RUN / "summary.json").read_text())
    ok = {b["key"]: b["count"] for b in summary["boards"] if b["status"] == "OK"}
    per_board = {}
    for ln in lines:
        per_board[ln["board"]] = per_board.get(ln["board"], 0) + 1
    assert per_board == ok and meta["postings"] == sum(ok.values())
    assert meta["failed_boards"] == ["greenhouse:stripe-js2-nonexistent"]
    assert len({ln["key"] for ln in lines}) == len(lines)


def test_every_sentence_offset_points_at_non_empty_text_inside_its_field(built):
    lines, _, _ = built
    for ln in lines:
        spans = {sp["field"]: sp for sp in ln["fields"]}
        for s in ln["sentences"]:
            piece = ln["text"][s["start"]:s["end"]]
            assert piece and piece == piece.strip() and "\n" not in piece
            assert spans[s["field"]]["start"] <= s["start"] and s["end"] <= spans[s["field"]]["end"]


def test_dataset_write_is_refused_outside_its_folder(tmp_path):
    tools = Tools(Policy(str(tmp_path), read_dirs=("runs",), write_dirs=("data",)))
    with pytest.raises(PolicyDenied):
        dataset.write(tools, [], {"run_id": "x"}, out_dir="labels")
