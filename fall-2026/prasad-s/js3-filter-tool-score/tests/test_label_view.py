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
    """A constructed JS3 folder: vault/ with both sets, and a constructed corpus."""

    def __init__(self, tmp, js3_tsv=None, final_tsv=None, files=None, gh_overrides=None, ab_overrides=None):
        self.root = Path(tmp)
        write(self.root, "vault/js3_heldout_ids.tsv",
              js3_tsv if js3_tsv is not None else seal_tsv([("product", JS3_PRODUCT), ("other", JS3_OTHER)]))
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
            "missing row": (lambda rows: rows[:6] + rows[7:], "position 7 (", None),
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
