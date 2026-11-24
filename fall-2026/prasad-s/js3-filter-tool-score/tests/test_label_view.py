"""Tests for tools/label_view.py. Constructed postings and constructed vault files only.

Every corpus file, vault/ file and labels file here is built inside a
temporary folder. No test reads the real corpus or the real vault/, and no
test writes outside its temporary folder.
"""

import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import label_view, seal_draw  # noqa: E402

GH = "greenhouse:constructedgh"
AB = "ashby:constructedab"
JS3_PRODUCT = [(GH, str(810000 + i)) for i in range(22)]
JS3_OTHER = [(AB, f"c-ab-{i:02d}") for i in range(8)]
FINAL = [(GH, str(710000 + i)) for i in range(15)] + [(AB, f"c-fin-{i:02d}") for i in range(5)]
# SEAL.md §8: the first JS3 set, retired; laid out like it, 22 product + 8 other.
EXPOSED = [(GH, str(760000 + i)) for i in range(22)] + [(AB, f"c-exp-{i:02d}") for i in range(8)]


def rank(board, posting_id):
    """SEAL.md §5, computed here independently of seal_draw."""
    return hashlib.sha256(f"a6ac8bbb:{board}:{posting_id}".encode("utf-8")).hexdigest()


def by_rank(keys):
    return sorted(keys, key=lambda key: rank(*key))


def write(root, rel, data):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else __import__("json").dumps(data), encoding="utf-8")


def seal_tsv(groups):
    """A draw output laid out as seal_draw writes it: product rows first, each group by rank."""
    lines = ["board_key\tid\tgroup\trank"]
    for group, keys in groups:
        lines += [f"{b}\t{i}\t{group}\t{rank(b, i)}" for b, i in by_rank(keys)]
    return "\n".join(lines) + "\n"


def gh_job(posting_id, **fields):
    base = {
        "id": int(posting_id),
        "title": f"Constructed Analyst {posting_id}",
        "location": {"name": "Constructed City"},
        "content": "&lt;p&gt;Constructed body text.&lt;/p&gt;",
        "absolute_url": f"https://example.com/jobs/{posting_id}",
        "updated_at": "2026-01-05T10:00:00-05:00",
        "departments": [{"name": "Dept-Zeta"}],
    }
    base.update(fields)
    return base


def ab_job(posting_id, **fields):
    base = {
        "id": posting_id,
        "title": f"Constructed Designer {posting_id}",
        "location": "Constructed Town",
        "secondaryLocations": [],
        "descriptionPlain": "Constructed plain body.",
        "jobUrl": f"https://example.com/ab/{posting_id}",
        "publishedAt": "2026-01-05T10:00:00Z",
        "department": "Dept-Zeta",
        "compensation": {"compensationTierSummary": "$999K"},
    }
    base.update(fields)
    return base


class Fixture:
    """A constructed JS3 folder: vault/ with the three sets, and a constructed corpus."""

    def __init__(self, tmp, js3_tsv=None, final_tsv=None, files=None, gh_overrides=None, ab_overrides=None,
                 exposed_tsv=None):
        self.root = Path(tmp)
        write(self.root, "vault/js3_heldout_ids_v2.tsv",
              js3_tsv if js3_tsv is not None else seal_tsv([("product", JS3_PRODUCT), ("other", JS3_OTHER)]))
        write(self.root, "vault/js3_heldout_ids.tsv",
              exposed_tsv if exposed_tsv is not None else seal_tsv([("product", EXPOSED[:22]), ("other", EXPOSED[22:])]))
        write(self.root, "vault/final_heldout_ids.tsv",
              final_tsv if final_tsv is not None else seal_tsv([("product", FINAL[:15]), ("other", FINAL[15:])]))
        if files is None:
            gh_overrides = gh_overrides or {}
            ab_overrides = ab_overrides or {}
            gh_ids = [i for _, i in JS3_PRODUCT + FINAL[:15]]
            ab_ids = [i for _, i in JS3_OTHER + FINAL[15:]]
            files = [
                (GH, "corpus/gh.json", "2026-01-01T00:00:00Z",
                 {"jobs": [gh_job(i, **gh_overrides.get(i, {})) for i in gh_ids]}),
                (AB, "corpus/ab.json", "2026-01-01T00:00:00Z",
                 {"jobs": [ab_job(i, **ab_overrides.get(i, {})) for i in ab_ids]}),
            ]
        self.corpus = []
        for board, rel, utc, body in files:
            write(self.root, rel, body)
            self.corpus.append((board, rel, utc))

    def run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = label_view.main(list(argv), root=self.root, corpus=self.corpus, out=out, err=err)
        return code, out.getvalue(), err.getvalue()


def position(key):
    return by_rank(JS3_PRODUCT + JS3_OTHER).index(key) + 1


def leaked(text):
    """Every posting id or board key from the three constructed sets that text contains (SEAL.md v1.5 §8)."""
    return [s for s in [GH, AB] + [i for _, i in JS3_PRODUCT + JS3_OTHER + FINAL + EXPOSED] if s in text]


def snapshot(root):
    return {(str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in Path(root).rglob("*")}


# ---------------------------------------------------------------- cleanup (FILTER.md F1)

class TestCleanup(unittest.TestCase):
    def test_title_both_ats(self):
        for board in (GH, AB):
            with self.subTest(board=board):
                self.assertEqual(label_view.clean_title(board, {"title": "  Senior\t Data \n Lead "}), "Senior Data Lead")
                for job in ({}, {"title": None}, {"title": "  \n "}, {"title": 42}):
                    self.assertIsNone(label_view.clean_title(board, job))

    def test_greenhouse_location(self):
        self.assertEqual(label_view.clean_location(GH, {"location": {"name": "  New   York,\tNY "}}), "New York, NY")
        for job in ({}, {"location": None}, {"location": "New York"}, {"location": {}},
                    {"location": {"name": "   "}}, {"location": {"name": 7}}):
            self.assertIsNone(label_view.clean_location(GH, job))

    def test_ashby_location_joins_secondaries(self):
        job = {"location": " New York ",
               "secondaryLocations": [{"location": "  Remote  "}, {"location": ""}, {"location": None},
                                      "not an object", {"location": "San   Francisco"}, {}]}
        self.assertEqual(label_view.clean_location(AB, job), "New York; Remote; San Francisco")
        self.assertEqual(label_view.clean_location(AB, {"location": None, "secondaryLocations": [{"location": " Dublin "}]}),
                         "Dublin")
        self.assertEqual(label_view.clean_location(AB, {"location": "Austin"}), "Austin")
        for job in ({}, {"location": "  ", "secondaryLocations": [{"location": " "}]}, {"location": 3}):
            self.assertIsNone(label_view.clean_location(AB, job))

    def test_greenhouse_text_steps_2_to_4(self):
        content = "&lt;p&gt;Lead the &lt;b&gt;roadmap&lt;/b&gt;&lt;/p&gt;\n\n&lt;ul&gt;&lt;li&gt;SQL &amp;amp; Python&lt;/li&gt;&lt;/ul&gt;"
        # unescaped once, so &amp;amp; becomes &amp; and stays; every tag becomes a space
        self.assertEqual(label_view.clean_text(GH, {"content": content}), "Lead the roadmap SQL &amp; Python")
        self.assertEqual(label_view.clean_text(GH, {"content": "road&lt;b&gt;map&lt;/b&gt;"}), "road map")
        for job in ({}, {"content": None}, {"content": "&lt;p&gt; &lt;/p&gt;"}, {"content": ["x"]}):
            self.assertIsNone(label_view.clean_text(GH, job))

    def test_ashby_text_whitespace_only(self):
        job = {"descriptionPlain": "  Line one\n\n  Line   two\t<b>bold</b> &amp; "}
        self.assertEqual(label_view.clean_text(AB, job), "Line one Line two <b>bold</b> &amp;")
        self.assertIsNone(label_view.clean_text(AB, {"content": "Greenhouse field, not Ashby's"}))
        for job in ({}, {"descriptionPlain": None}, {"descriptionPlain": " \n\t "}):
            self.assertIsNone(label_view.clean_text(AB, job))

    def test_unknown_ats_refused(self):
        with self.assertRaises(label_view.ViewError):
            label_view.clean_text("lever:constructed", {"content": "x"})


# ---------------------------------------------------------------- show

class TestShow(unittest.TestCase):
    def test_exactly_board_id_and_three_fields(self):
        key = JS3_PRODUCT[3]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, gh_overrides={key[1]: {
                "title": "  Constructed   Analyst, Payments ",
                "location": {"name": " Constructed   City "},
                "content": "&lt;p&gt;You  will analyse&lt;/p&gt;&lt;p&gt;payments data.&lt;/p&gt;"}})
            code, out, err = fx.run("show", str(position(key)))
            self.assertEqual(code, 0, err)
            self.assertEqual(out.splitlines(), [
                f"board_key: {GH}",
                f"id: {key[1]}",
                "title: Constructed Analyst, Payments",
                "location: Constructed City",
                "text:",
                "You will analyse payments data.",
            ])

    def test_missing_fields_print_missing(self):
        key = JS3_OTHER[2]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, ab_overrides={key[1]: {"title": None, "location": "  ", "descriptionPlain": None}})
            code, out, err = fx.run("show", str(position(key)))
            self.assertEqual(code, 0, err)
            self.assertEqual(out.splitlines(), [f"board_key: {AB}", f"id: {key[1]}", "title: (missing)",
                                                "location: (missing)", "text: (missing)"])

    def test_ashby_secondaries_joined_in_show(self):
        key = JS3_OTHER[5]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, ab_overrides={key[1]: {
                "location": "Constructed Town", "secondaryLocations": [{"location": " Remote "}, {"location": "Elsewhere"}]}})
            _, out, _ = fx.run("show", str(position(key)))
            self.assertIn("location: Constructed Town; Remote; Elsewhere\n", out)

    def test_nothing_forbidden_is_printed(self):
        for key in (JS3_PRODUCT[0], JS3_OTHER[0]):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                code, out, err = Fixture(tmp).run("show", str(position(key)))
                self.assertEqual(code, 0, err)
                lowered = out.lower()
                for word in ("relevant", "cannot_tell", "worth", "unclear", "verdict", "score", "c1", "c2", "c3",
                             "skill", "match", "group", "product", "other", "rank", "http", "example.com",
                             "2026-01-05", "dept-zeta", "$999", "url", "date", "compensation", "department"):
                    self.assertNotIn(word, lowered)
                self.assertNotIn(rank(*key), out)
                self.assertEqual([line.split(":", 1)[0] for line in out.splitlines()[:5]],
                                 ["board_key", "id", "title", "location", "text"])

    def test_text_wrapped_at_100_changing_no_words(self):
        key = JS3_PRODUCT[1]
        long_word = "x" * 120
        words = [f"word{n}" for n in range(80)] + [long_word] + ["tail", "end"]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, gh_overrides={key[1]: {"content": "&lt;p&gt;" + "  ".join(words) + "&lt;/p&gt;"}})
            _, out, _ = fx.run("show", str(position(key)))
            text_lines = out.splitlines()[5:]
            self.assertGreater(len(text_lines), 3)
            self.assertEqual(" ".join(text_lines), " ".join(words))
            self.assertTrue(all(len(line) <= 100 or line == long_word for line in text_lines))
            self.assertIn(long_word, text_lines)

    def test_latest_copy_wins(self):
        key = JS3_PRODUCT[7]
        gh_ids = [i for _, i in JS3_PRODUCT + FINAL[:15]]
        ab_ids = [i for _, i in JS3_OTHER + FINAL[15:]]
        files = [  # the later file is listed first: time decides, not order
            (GH, "corpus/late.json", "2026-01-02T00:00:00Z",
             {"jobs": [gh_job(key[1], title="Late Title", content="late text")]}),
            (GH, "corpus/early.json", "2026-01-01T00:00:00Z",
             {"jobs": [gh_job(i, title="Early Title", content="early text") for i in gh_ids]}),
            (AB, "corpus/ab.json", "2026-01-01T00:00:00Z", {"jobs": [ab_job(i) for i in ab_ids]}),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, files=files)
            _, out, _ = fx.run("show", str(position(key)))
            self.assertIn("title: Late Title\n", out)
            self.assertIn("late text", out)
            _, other_out, _ = fx.run("show", str(position(JS3_PRODUCT[8])))
            self.assertIn("title: Early Title\n", other_out)
            # the same copy seal_draw's latest-copy rule keeps
            _, latest = seal_draw.load_corpus(fx.root, fx.corpus)
            self.assertEqual(latest[key], "Late Title")


# ---------------------------------------------------------------- list and template

class TestListAndTemplate(unittest.TestCase):
    def test_list_order_is_rank_across_both_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = Fixture(tmp).run("list")
            self.assertEqual(code, 0, err)
            expected = by_rank(JS3_PRODUCT + JS3_OTHER)
            self.assertEqual(out.splitlines(), [f"{p}\t{b}\t{i}" for p, (b, i) in enumerate(expected, start=1)])
            # the vault file lists product first; list mixes the groups
            groups = [key in JS3_PRODUCT for key in expected]
            self.assertNotEqual(groups, sorted(groups, reverse=True))
            self.assertNotIn("product", out)
            self.assertNotIn(rank(*expected[0]), out)

    def test_list_does_not_read_the_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "corpus/gh.json").unlink()
            self.assertEqual(fx.run("list")[0], 0)

    def test_template_prints_30_empty_rows_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            before = snapshot(tmp)
            code, out, err = fx.run("template")
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshot(tmp), before)
            lines = out.splitlines()
            self.assertEqual(lines[0], "position\tboard_key\tid\tverdict\tparts\tevidence")
            self.assertEqual(len(lines), 31)
            expected = by_rank(JS3_PRODUCT + JS3_OTHER)
            for p, line in enumerate(lines[1:], start=1):
                self.assertEqual(line, f"{p}\t{expected[p - 1][0]}\t{expected[p - 1][1]}\t\t\t")


# ---------------------------------------------------------------- refusals

class TestRefusals(unittest.TestCase):
    def assert_refused(self, result, needle):
        code, out, err = result
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(needle, err)

    def test_position_outside_1_to_30(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            for arg in ("0", "31", "100", "abc", "1.5", ""):
                with self.subTest(arg=arg):
                    self.assert_refused(fx.run("show", arg), "not a position 1-30")

    def test_final_ids_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            for _, posting_id in (FINAL[0], FINAL[-1]):
                with self.subTest(posting_id=posting_id):
                    self.assert_refused(fx.run("show", posting_id), "final's set")

    def test_unknown_id_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp).run("show", "999999"), "not an id in JS3's set")

    def test_js3_id_refused_in_place_of_a_position(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp).run("show", JS3_OTHER[0][1]), "not an id")

    def test_overlapping_sets_refuse_every_command(self):
        final = seal_tsv([("product", FINAL[:14] + [JS3_PRODUCT[0]]), ("other", FINAL[15:])])
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, final_tsv=final)
            write(tmp, "labels.tsv", "position\n")
            for argv in (("list",), ("show", "1"), ("template",), ("check", str(Path(tmp) / "labels.tsv"))):
                with self.subTest(argv=argv):
                    self.assert_refused(fx.run(*argv), "both")

    def test_edited_rank_refused(self):
        tsv = seal_tsv([("product", JS3_PRODUCT), ("other", JS3_OTHER)]).replace(rank(*JS3_OTHER[0]), "0" * 64)
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp, js3_tsv=tsv).run("list"), "rank")

    def test_wrong_set_size_refused(self):
        tsv = seal_tsv([("product", JS3_PRODUCT[:21]), ("other", JS3_OTHER)])
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp, js3_tsv=tsv).run("list"), "holds 29")

    def test_missing_vault_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "vault/final_heldout_ids.tsv").unlink()
            self.assert_refused(fx.run("list"), "final_heldout_ids.tsv")

    def test_missing_corpus_file_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "corpus/ab.json").unlink()
            self.assert_refused(fx.run("show", "1"), "corpus/ab.json")

    def test_posting_not_in_corpus(self):
        key = JS3_PRODUCT[0]
        gh_ids = [i for _, i in JS3_PRODUCT + FINAL[:15] if i != key[1]]
        files = [(GH, "corpus/gh.json", "2026-01-01T00:00:00Z", {"jobs": [gh_job(i) for i in gh_ids]})]
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp, files=files).run("show", str(position(key))), "not in the corpus")

    def test_show_refusals_name_the_kind_and_never_repeat_the_argument(self):
        """SEAL.md v1.5 §8: refusals get pasted into chats, so they carry no id and never echo the argument."""
        final_kind = "the argument is an id in the final's set"
        exposed_kind = "the argument is an id in the exposed set"
        js3_kind = "the argument is an id in JS3's set"
        neither = "the argument is not a position 1-30, and not an id in JS3's set, the final's set or the exposed set"
        cases = [
            (FINAL[0][1], final_kind), (FINAL[14][1], final_kind), (FINAL[-1][1], final_kind),
            (EXPOSED[0][1], exposed_kind), (EXPOSED[21][1], exposed_kind), (EXPOSED[-1][1], exposed_kind),
            (JS3_PRODUCT[0][1], js3_kind), (JS3_PRODUCT[-1][1], js3_kind), (JS3_OTHER[-1][1], js3_kind),
            ("999999", neither), ("c-unknown-77", neither), ("31", neither), ("100", neither),
            ("abc", neither), ("1.5", neither), ("-7", neither), (GH, neither), (f"{GH}:{JS3_PRODUCT[0][1]}", neither),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            for arg, kind in cases:
                with self.subTest(arg=arg):
                    code, out, err = fx.run("show", arg)
                    self.assertEqual((code, out), (1, ""), err)
                    self.assertIn(kind, err)
                    self.assertNotIn(arg, err)
                    self.assertEqual(leaked(err), [])

    def test_command_line_errors_never_repeat_an_argument(self):
        """argparse would echo these ("invalid choice: ...", "unrecognized arguments: ...")."""
        some_id = JS3_PRODUCT[0][1]
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            for argv in ((), (some_id,), ("show",), ("show", "1", some_id), ("show", f"-x{some_id}"),
                         ("list", some_id), ("template", f"--{some_id}"), ("check",),
                         ("check", "labels.tsv", some_id)):
                with self.subTest(argv=argv):
                    code, out, err = fx.run(*argv)
                    self.assertEqual((code, out), (2, ""))
                    self.assertEqual(err, "error: not a valid command line; usage: "
                                          "label_view.py list | show N | template | check PATH\n")


# ---------------------------------------------------------------- check

class TestCheck(unittest.TestCase):
    SECRET = "SECRET-QUOTE"

    def valid_rows(self):
        expected = by_rank(JS3_PRODUCT + JS3_OTHER)
        choices = [("worth", "-"), ("not_worth", "role,level"), ("unclear", "location"), ("not_worth", "level")]
        rows = []
        for p, (board, posting_id) in enumerate(expected, start=1):
            verdict, parts = choices[p % len(choices)]
            rows.append([str(p), board, posting_id, verdict, parts, f"title: {self.SECRET} {p}"])
        return rows

    def labels_text(self, rows, header="position\tboard_key\tid\tverdict\tparts\tevidence"):
        return "\n".join([header] + ["\t".join(row) for row in rows]) + "\n"

    def run_check(self, text, raw=None):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            path = Path(tmp) / "elsewhere" / "labels.tsv"
            path.parent.mkdir()
            if raw is not None:
                path.write_bytes(raw)
            else:
                path.write_text(text, encoding="utf-8")
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            code, out, err = fx.run("check", str(path))
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)  # never changed
            self.assertNotIn(self.SECRET, out + err)
            return code, out, err

    def test_valid_file_is_ok(self):
        code, out, err = self.run_check(self.labels_text(self.valid_rows()))
        self.assertEqual((code, out), (0, "ok\n"), err)

    def test_valid_variants_are_ok(self):
        rows = self.valid_rows()
        rows.reverse()  # any row order
        rows[0][4] = "role, level" if rows[0][3] != "worth" else "-"
        text = self.labels_text(rows).replace("\n", "\r\n") + "\r\n"  # CRLF and a trailing blank line
        code, out, err = self.run_check(None, raw=b"\xef\xbb\xbf" + text.encode("utf-8"))  # BOM
        self.assertEqual((code, out), (0, "ok\n"), err)

    def test_each_kind_of_bad_file(self):
        final_board, final_id = FINAL[0]

        def edit(position, column, value):
            def apply(rows):
                rows[position - 1][column] = value
                return rows
            return apply

        cases = {
            "header": (lambda rows: rows, "line 1: the header is not", "position\tboard\tid\tverdict\tparts\tevidence"),
            "missing row": (lambda rows: rows[:6] + rows[7:], "position 7: no row", None),
            "duplicate": (lambda rows: rows + [list(rows[2])], "position 3 is already on line 4", None),
            "position out of range": (edit(5, 0, "31"), "position is not a whole number 1-30", None),
            "position not a number": (edit(5, 0, "five"), "position is not a whole number 1-30", None),
            "id mismatch": (edit(9, 2, "123"), "do not match JS3's set", None),
            "final id": (lambda rows: edit(9, 2, final_id)(edit(9, 1, final_board)(rows)), "final's set", None),
            "bad verdict": (edit(4, 3, "Worth"), "verdict is not one of worth, not_worth, unclear", None),
            "worth with parts": (lambda rows: edit(4, 4, "role")(edit(4, 3, "worth")(rows)), "parts must be - for worth", None),
            "not_worth with -": (lambda rows: edit(4, 4, "-")(edit(4, 3, "not_worth")(rows)), "parts must list", None),
            "unclear with no parts": (lambda rows: edit(4, 4, "")(edit(4, 3, "unclear")(rows)), "parts must list", None),
            "unknown part": (lambda rows: edit(4, 4, "role,skills")(edit(4, 3, "not_worth")(rows)), "parts must list", None),
            "part twice": (lambda rows: edit(4, 4, "role,role")(edit(4, 3, "not_worth")(rows)), "lists a part twice", None),
            "empty evidence": (edit(6, 5, "   "), "evidence is empty", None),
            "tab in evidence": (edit(6, 5, f"{self.SECRET}\tmore"), "7 columns", None),
            "too few columns": (lambda rows: rows[:2] + [rows[2][:5]] + rows[3:], "5 columns", None),
        }
        for name, (mutate, needle, header) in cases.items():
            with self.subTest(case=name):
                rows = mutate(self.valid_rows())
                text = self.labels_text(rows, header) if header else self.labels_text(rows)
                code, out, err = self.run_check(text)
                self.assertEqual(code, 1, out)
                self.assertIn(needle, out)
                self.assertNotIn("ok\n", out)

    def test_every_problem_is_reported(self):
        rows = self.valid_rows()
        rows[0][3] = "maybe"
        rows[1][5] = ""
        del rows[29]
        code, out, _ = self.run_check(self.labels_text(rows))
        self.assertEqual(code, 1)
        self.assertEqual(len(out.splitlines()), 3)

    def test_empty_file(self):
        code, out, _ = self.run_check("")
        self.assertEqual(code, 1)
        self.assertEqual(len(out.splitlines()), 31)  # the header and all 30 positions

    def test_unreadable_path_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = Fixture(tmp).run("check", str(Path(tmp) / "no_such_labels.tsv"))
            self.assertEqual((code, out), (1, ""))
            self.assertIn("cannot read", err)

    def test_exposed_set_rows_are_named(self):
        rows = self.valid_rows()
        rows[8][1], rows[8][2] = EXPOSED[0]
        code, out, _ = self.run_check(self.labels_text(rows))
        self.assertEqual(code, 1)
        self.assertEqual(out, "line 10 (position 9): names an id in the exposed set (the first JS3 set, SEAL.md §8)\n")

    def test_no_check_message_names_an_id(self):
        """SEAL.md v1.5 §8: check's output gets pasted, so on any bad file it carries no id and no board key."""
        expected = by_rank(JS3_PRODUCT + JS3_OTHER)

        def cell(position, column, value):
            def apply(rows):
                rows[position - 1][column] = value
                return rows
            return apply

        def put(position, key):
            def apply(rows):
                rows[position - 1][1], rows[position - 1][2] = key
                return rows
            return apply

        def put_all(keys):
            def apply(rows):
                for p, key in enumerate(keys, start=1):
                    rows[p - 1][1], rows[p - 1][2] = key
                return rows
            return apply

        def everything_at_once(rows):
            rows = rows[:25]  # positions 26-30 missing
            for mutate in (cell(1, 0, "31"), cell(2, 0, expected[1][1]), put(3, expected[9]), put(4, FINAL[0]),
                           put(5, EXPOSED[0]), put(6, (AB, "c-unknown-01")), cell(7, 3, "maybe"),
                           lambda r: cell(8, 4, "skills")(cell(8, 3, "unclear")(r)), cell(9, 5, " "),
                           cell(10, 5, f"{expected[10][1]}\tsee {expected[10][0]}")):
                rows = mutate(rows)
            return rows + [list(rows[11]), rows[12][:4]]

        cases = {
            "header is a data row": (lambda rows: rows, "\t".join([str(1), *expected[0], "worth", "-", "x"])),
            "every row missing": (lambda rows: [], None),
            "every other row missing": (lambda rows: rows[::2], None),
            "duplicate position": (lambda rows: rows + [list(rows[4])], None),
            "position out of range": (cell(3, 0, "31"), None),
            "position cell holds an id": (cell(3, 0, expected[2][1]), None),
            "another JS3 posting at this position": (put(3, expected[10]), None),
            "a posting from the final's set": (put(3, FINAL[2]), None),
            "a posting from the exposed set": (put(3, EXPOSED[2]), None),
            "an unknown posting": (put(3, (GH, "999999")), None),
            "board key and id swapped": (put(3, (expected[2][1], expected[2][0])), None),
            "bad verdict": (cell(3, 3, "maybe"), None),
            "bad parts": (lambda rows: cell(3, 4, "role,role")(cell(3, 3, "not_worth")(rows)), None),
            "empty evidence": (cell(3, 5, ""), None),
            "tab in evidence, an id inside it": (cell(3, 5, f"{expected[3][1]}\tmore"), None),
            "too few columns": (lambda rows: rows[:2] + [rows[2][:3]] + rows[3:], None),
            "every row from the exposed set": (put_all(by_rank(EXPOSED)), None),
            "every row it can from the final's set": (put_all(by_rank(FINAL)), None),
            "everything at once": (everything_at_once, "position\tboard\tid"),
        }
        for name, (mutate, header) in cases.items():
            with self.subTest(case=name):
                rows = mutate(self.valid_rows())
                text = self.labels_text(rows, header) if header else self.labels_text(rows)
                code, out, err = self.run_check(text)
                self.assertEqual(code, 1, out)
                self.assertNotEqual(out, "")
                self.assertEqual(leaked(out + err), [])
        code, out, err = self.run_check("")
        self.assertEqual((code, leaked(out + err)), (1, []))

    def test_unreadable_path_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"labels_{JS3_PRODUCT[0][1]}.tsv"
            code, out, err = Fixture(tmp).run("check", str(path))
            self.assertEqual((code, out), (1, ""))
            self.assertEqual(err, "error: cannot read the labels file (FileNotFoundError)\n")

    def test_a_labels_file_for_the_exposed_set_fails_on_every_row(self):
        # e.g. the first set's labels checked by mistake: all 30 rows name the exposed set
        rows = self.valid_rows()
        for p, key in enumerate(by_rank(EXPOSED), start=1):
            rows[p - 1][1], rows[p - 1][2] = key
        code, out, _ = self.run_check(self.labels_text(rows))
        self.assertEqual(code, 1)
        self.assertEqual(len(out.splitlines()), 30)
        self.assertTrue(all("names an id in the exposed set" in line for line in out.splitlines()))


# ---------------------------------------------------------------- the three sets (SEAL.md §8)

class TestThreeSets(unittest.TestCase):
    def assert_refused(self, result, needle):
        code, out, err = result
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(needle, err)

    def test_every_command_uses_the_v2_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            expected = by_rank(JS3_PRODUCT + JS3_OTHER)
            _, listed, _ = fx.run("list")
            _, template, _ = fx.run("template")
            self.assertEqual([tuple(line.split("\t")[1:3]) for line in listed.splitlines()], expected)
            self.assertEqual([tuple(line.split("\t")[1:3]) for line in template.splitlines()[1:]], expected)
            for _, posting_id in EXPOSED:
                self.assertNotIn(posting_id, listed + template)
            code, out, err = fx.run("show", "1")
            self.assertEqual(code, 0, err)
            self.assertIn(f"id: {expected[0][1]}\n", out)

    def test_missing_v2_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "vault/js3_heldout_ids_v2.tsv").unlink()
            for argv in (("list",), ("show", "1"), ("template",)):
                with self.subTest(argv=argv):
                    self.assert_refused(fx.run(*argv), "vault/js3_heldout_ids_v2.tsv")

    def test_missing_exposed_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "vault/js3_heldout_ids.tsv").unlink()
            for argv in (("list",), ("show", "1"), ("template",)):
                with self.subTest(argv=argv):
                    self.assert_refused(fx.run(*argv), "vault/js3_heldout_ids.tsv")

    def test_exposed_file_ranks_are_recomputed(self):
        tsv = seal_tsv([("product", EXPOSED[:22]), ("other", EXPOSED[22:])]).replace(rank(*EXPOSED[3]), "f" * 64)
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_refused(Fixture(tmp, exposed_tsv=tsv).run("list"), "vault/js3_heldout_ids.tsv line")

    def test_any_two_sets_sharing_a_posting_refuse_every_command(self):
        cases = {
            "both JS3's set and the final's set": {
                "final_tsv": seal_tsv([("product", FINAL[:14] + [JS3_PRODUCT[5]]), ("other", FINAL[15:])])},
            "both JS3's set and the exposed set": {
                "exposed_tsv": seal_tsv([("product", EXPOSED[:22]), ("other", EXPOSED[22:29] + [JS3_OTHER[2]])])},
            "both the final's set and the exposed set": {
                "exposed_tsv": seal_tsv([("product", EXPOSED[:21] + [FINAL[0]]), ("other", EXPOSED[22:])])},
        }
        for needle, files in cases.items():
            with tempfile.TemporaryDirectory() as tmp:
                fx = Fixture(tmp, **files)
                write(tmp, "labels.tsv", "position\n")
                for argv in (("list",), ("show", "1"), ("template",), ("check", str(Path(tmp) / "labels.tsv"))):
                    with self.subTest(pair=needle, argv=argv):
                        self.assert_refused(fx.run(*argv), needle)

    def test_set_and_corpus_refusals_name_no_id(self):
        """Every refusal before show prints a posting carries no id and no board key (SEAL.md v1.5 §8)."""
        v2 = seal_tsv([("product", JS3_PRODUCT), ("other", JS3_OTHER)])
        key = JS3_PRODUCT[0]
        gh_ids = [i for _, i in JS3_PRODUCT + FINAL[:15] if i != key[1]]
        cases = {
            "v2 and final overlap": {"final_tsv": seal_tsv([("product", FINAL[:14] + [key]), ("other", FINAL[15:])])},
            "v2 and exposed overlap": {"exposed_tsv": seal_tsv([("product", EXPOSED[:21] + [key]),
                                                                 ("other", EXPOSED[22:])])},
            "final and exposed overlap": {"exposed_tsv": seal_tsv([("product", EXPOSED[:21] + [FINAL[3]]),
                                                                    ("other", EXPOSED[22:])])},
            "a posting listed twice": {"js3_tsv": v2 + v2.splitlines()[1] + "\n"},
            "an edited rank": {"js3_tsv": v2.replace(rank(*key), "0" * 64)},
            "an extra column": {"js3_tsv": v2.replace(f"\t{key[1]}\tproduct\t", f"\t{key[1]}\tproduct\textra\t")},
            "a wrong size": {"js3_tsv": seal_tsv([("product", JS3_PRODUCT[:21]), ("other", JS3_OTHER)])},
            "the posting is not in the corpus": {"files": [(GH, "corpus/gh.json", "2026-01-01T00:00:00Z",
                                                            {"jobs": [gh_job(i) for i in gh_ids]})]},
        }
        for name, kwargs in cases.items():
            with tempfile.TemporaryDirectory() as tmp:
                fx = Fixture(tmp, **kwargs)
                for argv in (("list",), ("show", str(position(key)))):
                    with self.subTest(case=name, argv=argv):
                        code, out, err = fx.run(*argv)
                        if name == "the posting is not in the corpus" and argv == ("list",):
                            continue  # list does not read the corpus
                        self.assertEqual((code, out), (1, ""), err)
                        self.assertEqual(leaked(err), [])

    def test_exposed_ids_refused_by_show(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            for _, posting_id in (EXPOSED[0], EXPOSED[21], EXPOSED[-1]):
                with self.subTest(posting_id=posting_id):
                    self.assert_refused(fx.run("show", posting_id), "exposed set")

    def test_reads_what_replace_js3_writes(self):
        """End to end on a constructed corpus: draw, replace-js3, then list and show."""
        product = [str(500000 + i) for i in range(80)]
        other = [f"c-int-{i:02d}" for i in range(25)]
        files = [
            (GH, "corpus/gh.json", "2026-01-01T00:00:00Z",
             {"jobs": [gh_job(i, title=f"Product Constructed {i}") for i in product]}),
            (AB, "corpus/ab.json", "2026-01-01T00:00:00Z",
             {"jobs": [ab_job(i, title=f"Designer Constructed {i}") for i in other]}),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            corpus = []
            for board, rel, utc, body in files:
                write(tmp, rel, body)
                corpus.append((board, rel, utc))

            def seal(*argv):
                out, err = io.StringIO(), io.StringIO()
                code = seal_draw.main(list(argv), root=Path(tmp), corpus=corpus, sources=(), named=(),
                                      sums_dirs=(), out=out, err=err)
                self.assertEqual(code, 0, err.getvalue())

            seal("draw", "--final", "15", "5", "--js3", "22", "8")
            seal("replace-js3", "--final", "15", "5", "--exposed", "22", "8", "--js3", "22", "8")
            p_order = by_rank([(GH, i) for i in product])
            o_order = by_rank([(AB, i) for i in other])
            out, err = io.StringIO(), io.StringIO()
            code = label_view.main(["list"], root=Path(tmp), corpus=corpus, out=out, err=err)
            self.assertEqual(code, 0, err.getvalue())
            listed = [tuple(line.split("\t")[1:3]) for line in out.getvalue().splitlines()]
            self.assertEqual(listed, by_rank(p_order[37:59] + o_order[13:21]))  # SEAL.md §8: 38-59 and 14-21
            out, err = io.StringIO(), io.StringIO()
            code = label_view.main(["show", "30"], root=Path(tmp), corpus=corpus, out=out, err=err)
            self.assertEqual(code, 0, err.getvalue())
            self.assertIn(f"id: {listed[29][1]}\n", out.getvalue())


class TestConstants(unittest.TestCase):
    def test_spec_constants(self):
        self.assertEqual(label_view.SET_SIZE, 30)
        self.assertEqual(label_view.VERDICTS, ("worth", "not_worth", "unclear"))
        self.assertEqual(label_view.PARTS, ("role", "level", "location"))
        self.assertEqual(label_view.LABEL_HEADER, ("position", "board_key", "id", "verdict", "parts", "evidence"))
        self.assertIs(label_view.seal_draw, seal_draw)
        defaults = {name: p.default for name, p in __import__("inspect").signature(label_view.main).parameters.items()}
        self.assertIs(defaults["corpus"], seal_draw.CORPUS)
        self.assertEqual(defaults["root"], seal_draw.JS3_ROOT)


if __name__ == "__main__":
    unittest.main()
