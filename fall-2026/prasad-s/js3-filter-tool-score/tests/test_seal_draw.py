"""Tests for tools/seal_draw.py. Constructed postings only.

Every corpus file, seen-list source and vault/ folder here is built inside a
temporary folder. No test reads the real corpus or writes to the real vault/.
"""

import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import seal_draw  # noqa: E402

GH = "greenhouse:constructedgh"
AB = "ashby:constructedab"


def write(root, rel, data):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def gh_jobs(*pairs):
    """Constructed Greenhouse body: ids are JSON numbers."""
    return {"jobs": [{"id": job_id, **({} if title is None else {"title": title})} for job_id, title in pairs]}


def ab_jobs(*pairs):
    """Constructed Ashby body: ids are strings."""
    return {"jobs": [{"id": job_id, **({} if title is None else {"title": title})} for job_id, title in pairs]}


class Fixture:
    """A constructed JS3 folder with its corpus and seen-list sources in a temp dir."""

    def __init__(self, root, files, seen=None, named=()):
        self.root = Path(root)
        self.corpus = []
        for board, rel, utc, body in files:
            write(self.root, rel, body)
            self.corpus.append((board, rel, utc))
        self.sources = []
        if seen is not None:
            # A JS2-shaped run report carries its own board key; JS1-shaped
            # sources always mean greenhouse:stripe (TestSeenExtractors).
            write(self.root, "constructed_seen/run_report.json",
                  {"boards": [{"board": GH, "new_ids": list(seen), "new_postings": []}]})
            self.sources.append(("constructed_seen/run_report.json", "run report", "js2_run_report"))
        self.named = named

    def run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = seal_draw.main(list(argv), root=self.root, corpus=self.corpus, sources=self.sources,
                              named=self.named, sums_dirs=(), out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def state(self):
        return seal_draw.build(self.root, self.corpus, self.sources, self.named)


def read_tsv(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:]]


def independent_rank(board, posting_id):
    return hashlib.sha256(f"a6ac8bbb:{board}:{posting_id}".encode("utf-8")).hexdigest()


class TestLatestCopy(unittest.TestCase):
    def test_latest_file_wins_by_time_not_list_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            # The later file is listed first: time decides, not order.
            fx = Fixture(tmp, [
                (GH, "c/late.json", "2026-01-02T00:00:00Z", gh_jobs((900001, "Engineer, Constructed"))),
                (GH, "c/early.json", "2026-01-01T00:00:00Z", gh_jobs((900001, "Product Manager, Constructed"),
                                                                       (900002, "Product Lead, Constructed"))),
            ])
            state = fx.state()
            self.assertEqual(state["latest"][(GH, "900001")], "Engineer, Constructed")
            self.assertIn((GH, "900001"), state["groups"]["other"])
            self.assertIn((GH, "900002"), state["groups"]["product"])
            self.assertEqual(len(state["latest"]), 2)  # one copy per (board, id)

    def test_same_id_on_two_boards_is_two_postings(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, [
                (GH, "c/gh.json", "2026-01-01T00:00:00Z", gh_jobs((77, "Product A"))),
                ("greenhouse:constructedgh2", "c/gh2.json", "2026-01-01T00:00:00Z", gh_jobs((77, "Product B"))),
            ])
            self.assertEqual(len(fx.state()["latest"]), 2)


class TestSeen(unittest.TestCase):
    def test_seen_ids_leave_the_pool(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, [(GH, "c/a.json", "2026-01-01T00:00:00Z",
                                gh_jobs((100, "Product X"), (101, "Product Y"), (102, "Other Z")))],
                         seen=["100", "102", "555"])
            state = fx.state()
            self.assertEqual(set(state["pool"]), {(GH, "101")})
            self.assertEqual(state["seen"], {(GH, "100"), (GH, "102"), (GH, "555")})

    def test_seen_ids_never_drawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = list(range(200, 220))
            fx = Fixture(tmp, [(GH, "c/a.json", "2026-01-01T00:00:00Z",
                                gh_jobs(*[(i, "Product") for i in ids]))], seen=["200", "201", "202", "203"])
            code, _, err = fx.run("draw", "--final", "3", "0", "--js3", "5", "0")
            self.assertEqual(code, 0, err)
            drawn = {row["id"] for f in ("final_heldout_ids.tsv", "js3_heldout_ids.tsv")
                     for row in read_tsv(Path(tmp) / "vault" / f)}
            self.assertFalse(drawn & {"200", "201", "202", "203"})

    def test_named_seen_id_must_still_be_in_its_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "c/NOTE.md", "example id 300\n")
            fx = Fixture(tmp, [(GH, "c/a.json", "2026-01-01T00:00:00Z", gh_jobs((300, "Product")))],
                         named=((GH, "300", "c/NOTE.md", "other"),))
            self.assertIn((GH, "300"), fx.state()["seen"])
            write(tmp, "c/NOTE.md", "the id is gone\n")
            with self.assertRaises(seal_draw.SealError):
                fx.state()


class TestGroups(unittest.TestCase):
    def test_grouping(self):
        cases = {
            "PRODUCT MANAGER": "product",
            "  Senior\t\nproduct   Analyst  ": "product",
            "Production Lead": "product",          # SEAL.md §3: the substring catches it, on purpose
            "Pro duct Manager": "other",
            "Engineer": "other",
            "   ": "other",                         # empty after cleanup is missing
            None: "other",                          # null title
            42: "other",                            # not text
        }
        for title, group in cases.items():
            with self.subTest(title=title):
                self.assertEqual(seal_draw.group_of(title), group)

    def test_missing_title_field_goes_to_other(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, [(AB, "c/ab.json", "2026-01-01T00:00:00Z", ab_jobs(("c-1", None), ("c-2", "  pRoDuCt  ")))])
            groups = fx.state()["groups"]
            self.assertEqual(groups["other"], [(AB, "c-1")])
            self.assertEqual(groups["product"], [(AB, "c-2")])

    def test_clean_title(self):
        self.assertEqual(seal_draw.clean_title("  a \t b\n c "), "a b c")
        self.assertIsNone(seal_draw.clean_title(" \n "))


class TestRankAndDraw(unittest.TestCase):
    def make(self, tmp, n_product=12, n_other=8):
        product = [(1000 + i, f"Product Constructed {i}") for i in range(n_product)]
        other = [(f"o-{i}", f"Designer Constructed {i}") for i in range(n_other)]
        return Fixture(tmp, [
            (GH, "c/gh.json", "2026-01-01T00:00:00Z", gh_jobs(*product)),
            (AB, "c/ab.json", "2026-01-01T00:00:00Z", ab_jobs(*other)),
        ])

    def test_seed_and_rank(self):
        self.assertEqual(seal_draw.SEED, "a6ac8bbb")
        self.assertEqual(seal_draw.rank(GH, "1000"), independent_rank(GH, "1000"))
        self.assertRegex(seal_draw.rank(GH, "1000"), r"^[0-9a-f]{64}$")

    def test_ranks_lowest_first_within_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            code, _, err = fx.run("draw", "--final", "2", "3", "--js3", "4", "5")
            self.assertEqual(code, 0, err)
            for name in ("final_heldout_ids.tsv", "js3_heldout_ids.tsv"):
                rows = read_tsv(Path(tmp) / "vault" / name)
                for group in ("product", "other"):
                    ranks = [r["rank"] for r in rows if r["group"] == group]
                    self.assertEqual(ranks, sorted(ranks))
                for r in rows:
                    self.assertEqual(r["rank"], independent_rank(r["board_key"], r["id"]))

    def test_final_takes_lowest_js3_next_no_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            code, out, err = fx.run("draw", "--final", "2", "3", "--js3", "4", "5")
            self.assertEqual(code, 0, err)
            final = read_tsv(Path(tmp) / "vault" / "final_heldout_ids.tsv")
            js3 = read_tsv(Path(tmp) / "vault" / "js3_heldout_ids.tsv")
            expected_product = sorted(((independent_rank(GH, str(1000 + i)), str(1000 + i)) for i in range(12)))
            expected_other = sorted(((independent_rank(AB, f"o-{i}"), f"o-{i}") for i in range(8)))
            self.assertEqual([r["id"] for r in final if r["group"] == "product"], [i for _, i in expected_product[:2]])
            self.assertEqual([r["id"] for r in js3 if r["group"] == "product"], [i for _, i in expected_product[2:6]])
            self.assertEqual([r["id"] for r in final if r["group"] == "other"], [i for _, i in expected_other[:3]])
            self.assertEqual([r["id"] for r in js3 if r["group"] == "other"], [i for _, i in expected_other[3:8]])
            keys = lambda rows: {(r["board_key"], r["id"]) for r in rows}
            self.assertFalse(keys(final) & keys(js3))
            self.assertEqual(out, "final's set: product 2, other 3\nJS3's held-out set: product 4, other 5\n")

    def test_final_does_not_move_when_js3_size_changes(self):
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            self.make(tmp1).run("draw", "--final", "2", "3", "--js3", "4", "5")
            self.make(tmp2).run("draw", "--final", "2", "3", "--js3", "1", "1")
            a = (Path(tmp1) / "vault" / "final_heldout_ids.tsv").read_text()
            b = (Path(tmp2) / "vault" / "final_heldout_ids.tsv").read_text()
            self.assertEqual(a, b)

    def test_tsv_has_no_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            fx.run("draw", "--final", "2", "3", "--js3", "4", "5")
            for name in ("final_heldout_ids.tsv", "js3_heldout_ids.tsv"):
                text = (Path(tmp) / "vault" / name).read_text()
                self.assertNotIn("Constructed", text)
                self.assertEqual(text.splitlines()[0], "board_key\tid\tgroup\trank")

    def test_draw_refuses_to_overwrite(self):
        for existing in ("final_heldout_ids.tsv", "js3_heldout_ids.tsv"):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as tmp:
                fx = self.make(tmp)
                write(tmp, f"vault/{existing}", "constructed earlier draw\n")
                code, out, err = fx.run("draw", "--final", "2", "3", "--js3", "4", "5")
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertIn("refusing to overwrite", err)
                self.assertEqual((Path(tmp) / "vault" / existing).read_text(), "constructed earlier draw\n")
                self.assertEqual(sorted(p.name for p in (Path(tmp) / "vault").iterdir()), [existing])

    def test_draw_refuses_when_group_too_small(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp, n_product=12, n_other=8)
            code, _, err = fx.run("draw", "--final", "1", "5", "--js3", "1", "4")
            self.assertEqual(code, 1)
            self.assertIn("other group has 8", err)
            self.assertFalse((Path(tmp) / "vault" / "final_heldout_ids.tsv").exists())

    def test_draw_keeps_half_the_product_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp, n_product=12, n_other=8)
            code, _, err = fx.run("draw", "--final", "3", "0", "--js3", "4", "0")  # 7 of 12
            self.assertEqual(code, 1)
            self.assertIn("less than half", err)
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp, n_product=12, n_other=8)
            code, _, err = fx.run("draw", "--final", "2", "0", "--js3", "4", "0")  # 6 of 12: exactly half
            self.assertEqual(code, 0, err)


class TestReplaceJs3(unittest.TestCase):
    """SEAL.md §8: the next ranks after the exposed set, same seed, same pool, same ranking.

    The constructed pool: 16 product postings (17 less one seen) and 10 other.
    The committed files come from draw --final 2 1 --js3 3 2, so the exposed
    set is product ranks 3-5 and other ranks 2-3.
    """

    FINAL, EXPOSED, JS3 = ("2", "1"), ("3", "2"), ("4", "3")

    def make(self, tmp):
        product = [(1000 + i, f"Product Constructed {i}") for i in range(17)]
        other = [(f"o-{i}", f"Designer Constructed {i}") for i in range(10)]
        return Fixture(tmp, [
            (GH, "c/gh.json", "2026-01-01T00:00:00Z", gh_jobs(*product)),
            (AB, "c/ab.json", "2026-01-01T00:00:00Z", ab_jobs(*other)),
        ], seen=["1016"])

    def order(self, group):
        """The pool's group in rank order, computed independently of seal_draw."""
        keys = ([(GH, str(1000 + i)) for i in range(16)] if group == "product"
                else [(AB, f"o-{i}") for i in range(10)])
        return sorted(keys, key=lambda key: independent_rank(*key))

    def set_file(self, product_keys, other_keys):
        lines = ["board_key\tid\tgroup\trank"]
        lines += [f"{b}\t{i}\tproduct\t{independent_rank(b, i)}" for b, i in product_keys]
        lines += [f"{b}\t{i}\tother\t{independent_rank(b, i)}" for b, i in other_keys]
        return "\n".join(lines) + "\n"

    def drawn(self, tmp):
        fx = self.make(tmp)
        code, _, err = fx.run("draw", "--final", *self.FINAL, "--js3", *self.EXPOSED)
        self.assertEqual(code, 0, err)
        return fx

    def replace(self, fx, final=FINAL, exposed=EXPOSED, js3=JS3):
        return fx.run("replace-js3", "--final", *final, "--exposed", *exposed, "--js3", *js3)

    def committed(self, tmp):
        vault = Path(tmp) / "vault"
        return {name: (vault / name).read_bytes() for name in ("final_heldout_ids.tsv", "js3_heldout_ids.tsv")
                if (vault / name).exists()}

    def assert_nothing_written(self, tmp, run, needle):
        """run() must fail with needle, print nothing, write no v2 file and leave the committed files as they were."""
        before = self.committed(tmp)
        code, out, err = run()
        self.assertEqual((code, out), (1, ""), err)
        self.assertIn(needle, err)
        self.assertFalse((Path(tmp) / "vault" / "js3_heldout_ids_v2.tsv").exists())
        self.assertEqual(self.committed(tmp), before)
        return err

    def test_takes_exactly_the_next_ranks_after_the_exposed_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.drawn(tmp)
            before = self.committed(tmp)
            code, out, err = self.replace(fx)
            self.assertEqual(code, 0, err)
            product, other = self.order("product"), self.order("other")
            # the committed files are what this test expects them to be ...
            self.assertEqual(before["final_heldout_ids.tsv"].decode(), self.set_file(product[:2], other[:1]))
            self.assertEqual(before["js3_heldout_ids.tsv"].decode(), self.set_file(product[2:5], other[1:3]))
            # ... the replacement is the next ranks in each group, in draw's format ...
            v2 = (Path(tmp) / "vault" / "js3_heldout_ids_v2.tsv").read_text(encoding="utf-8")
            self.assertEqual(v2, self.set_file(product[5:9], other[3:6]))
            # ... the committed files are untouched, and the seen posting is never drawn
            self.assertEqual(self.committed(tmp), before)
            self.assertNotIn("\t1016\t", v2)
            self.assertEqual(out,
                             "final's set: product 2, other 1; matches vault/final_heldout_ids.tsv\n"
                             "exposed set: product 3, other 2; matches vault/js3_heldout_ids.tsv\n"
                             "JS3's held-out set v2: product 4 (ranks 6-9), other 3 (ranks 4-6); "
                             "written to vault/js3_heldout_ids_v2.tsv\n"
                             "sealed product postings: 6 of 16; the development pool keeps 10\n")
            for _, posting_id in product + other:
                self.assertNotIn(posting_id, out + err)
            self.assertNotIn("Constructed", out + v2)

    def test_stops_if_a_committed_file_does_not_match(self):
        product = self.order("product")

        def swap(lines):
            lines[1], lines[2] = lines[2], lines[1]
            return lines

        def other_posting(lines):
            b, i = product[12]
            lines[1] = f"{b}\t{i}\tproduct\t{independent_rank(b, i)}"
            return lines

        mutations = {
            "two rows swapped": (swap, "line 2 differs"),
            "a row missing": (lambda lines: lines[:-2] + lines[-1:], "the re-derived set has"),
            "a row added": (lambda lines: lines[:-1] + [lines[-2], ""], "the re-derived set has"),
            "a different posting, its rank correct": (other_posting, "line 2 differs"),
            "a blank line at the end": (lambda lines: lines + [""], "the re-derived set has"),
            "a changed header": (lambda lines: ["board_key\tid\tgroup\tRANK"] + lines[1:], "line 1 differs"),
        }
        names = ("final_heldout_ids.tsv", "js3_heldout_ids.tsv")
        for name in names:
            other_name = names[1 - names.index(name)]
            for case, (mutate, detail) in mutations.items():
                with self.subTest(file=name, case=case), tempfile.TemporaryDirectory() as tmp:
                    fx = self.drawn(tmp)
                    path = Path(tmp) / "vault" / name
                    path.write_text("\n".join(mutate(path.read_text(encoding="utf-8").split("\n"))),
                                    encoding="utf-8")
                    err = self.assert_nothing_written(tmp, lambda: self.replace(fx), f"vault/{name} does not match")
                    self.assertIn(detail, err)
                    self.assertIn("nothing written", err)
                    self.assertNotIn(other_name, err)
            with self.subTest(file=name, case="missing"), tempfile.TemporaryDirectory() as tmp:
                fx = self.drawn(tmp)
                (Path(tmp) / "vault" / name).unlink()
                self.assert_nothing_written(tmp, lambda: self.replace(fx), f"cannot read vault/{name}")

    def test_stops_if_the_sizes_do_not_match_the_committed_files(self):
        cases = (
            ({"final": ("2", "2")}, "vault/final_heldout_ids.tsv does not match"),
            ({"final": ("1", "1")}, "vault/final_heldout_ids.tsv does not match"),
            ({"exposed": ("3", "3")}, "vault/js3_heldout_ids.tsv does not match"),
            ({"exposed": ("4", "2")}, "vault/js3_heldout_ids.tsv does not match"),
        )
        for sizes, needle in cases:
            with self.subTest(sizes=sizes), tempfile.TemporaryDirectory() as tmp:
                fx = self.drawn(tmp)
                self.assert_nothing_written(tmp, lambda: self.replace(fx, **sizes), needle)

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.drawn(tmp)
            write(tmp, "vault/js3_heldout_ids_v2.tsv", "constructed earlier replacement\n")
            before = self.committed(tmp)
            code, out, err = self.replace(fx)
            self.assertEqual((code, out), (1, ""))
            self.assertIn("refusing to overwrite: vault/js3_heldout_ids_v2.tsv", err)
            self.assertEqual((Path(tmp) / "vault/js3_heldout_ids_v2.tsv").read_text(),
                             "constructed earlier replacement\n")
            self.assertEqual(self.committed(tmp), before)

    def test_half_rule_counts_the_final_and_the_replacement_not_the_exposed_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            # 2 + 6 = 8 sealed of 16: exactly half, allowed, although 2 + 3 + 6 = 11 leave the pool's first ranks
            fx = self.drawn(tmp)
            code, out, err = self.replace(fx, js3=("6", "0"))
            self.assertEqual(code, 0, err)
            self.assertIn("sealed product postings: 8 of 16; the development pool keeps 8\n", out)
            self.assertIn("other 0 (no ranks)", out)
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.drawn(tmp)  # 2 + 7 = 9 sealed of 16: more than half
            self.assert_nothing_written(tmp, lambda: self.replace(fx, js3=("7", "0")), "less than half")

    def test_each_group_must_hold_all_three_ranges(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.drawn(tmp)  # other: 1 + 2 + 8 = 11 > 10
            self.assert_nothing_written(tmp, lambda: self.replace(fx, js3=("4", "8")),
                                        "the other group has 10 postings")
        product, other = self.order("product"), self.order("other")
        for js3, expect_ok in ((("6", "0"), False), (("5", "0"), True)):
            with self.subTest(js3=js3), tempfile.TemporaryDirectory() as tmp:
                # draw itself refuses an exposed set of 9 (2 + 9 > half of 16), so the committed files are
                # written here by hand, in draw's format, from the independent ranking
                fx = self.make(tmp)
                write(tmp, "vault/final_heldout_ids.tsv", self.set_file(product[:2], other[:1]))
                write(tmp, "vault/js3_heldout_ids.tsv", self.set_file(product[2:11], other[1:3]))
                run = lambda: self.replace(fx, exposed=("9", "2"), js3=js3)  # noqa: E731
                if expect_ok:  # 2 + 9 + 5 = 16: the whole group, allowed; 2 + 5 = 7 sealed
                    code, _, err = run()
                    self.assertEqual(code, 0, err)
                    self.assertEqual((Path(tmp) / "vault/js3_heldout_ids_v2.tsv").read_text(encoding="utf-8"),
                                     self.set_file(product[11:16], []))
                else:  # 2 + 9 + 6 = 17 > 16, though 2 + 6 = 8 sealed passes the half-rule
                    err = self.assert_nothing_written(tmp, run, "the product group has 16 postings")
                    self.assertIn("need 17", err)

    def test_negative_size_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.drawn(tmp)
            self.assert_nothing_written(tmp, lambda: self.replace(fx, js3=("-1", "3")), "0 or more")

    def test_file_names(self):
        self.assertEqual(seal_draw.FINAL_FILE, "final_heldout_ids.tsv")
        self.assertEqual(seal_draw.JS3_FILE, "js3_heldout_ids.tsv")
        self.assertEqual(seal_draw.JS3_V2_FILE, "js3_heldout_ids_v2.tsv")


class TestCounts(unittest.TestCase):
    TITLES =["Product Zebracorn Constructed", "Quasar Wrangler Constructed", "  product   OKAPI constructed "]

    def make(self, tmp):
        return Fixture(tmp, [
            (GH, "c/gh_2026-01-01.json", "2026-01-01T00:00:00Z", gh_jobs((987654, self.TITLES[0]), (987655, self.TITLES[1]))),
            (AB, "c/ab.json", "2026-01-02T03:04:05Z", ab_jobs(("c-zz-1002", self.TITLES[2]), ("c-zz-1003", None))),
        ], seen=["987655", "424242"])

    def test_counts_output_has_no_id_or_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = self.make(tmp).run("counts")
            self.assertEqual(code, 0, err)
            for secret in ["987654", "987655", "424242", "c-zz-1002", "c-zz-1003", "Zebracorn", "Quasar",
                           "OKAPI", "Wrangler"] + self.TITLES:
                self.assertNotIn(secret, out)
            self.assertEqual((Path(tmp) / "vault" / "counts.txt").read_text(), out)
            self.assertNotIn("Constructed", out.replace("constructed", ""))

    def test_counts_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = self.make(tmp).run("counts")
            self.assertIn(f"unique postings: {AB} 2, {GH} 2; total 4", out)
            self.assertIn("seen ids found: 2; in the corpus: 1; not in the corpus: 1", out)
            self.assertIn(f"pool: {AB} 2, {GH} 1; total 3", out)
            self.assertIn(f"product group: {AB} 1, {GH} 1; total 2", out)
            self.assertIn(f"other group: {AB} 1, {GH} 0; total 1", out)
            self.assertIn("needs a product group of at least 74: does not fit (2)", out)
            self.assertIn("needs an other group of at least 13: does not fit (1)", out)

    def test_counts_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make(tmp).run("counts")
            manifest = read_tsv(Path(tmp) / "vault" / "corpus_manifest.tsv")
            self.assertEqual([m["jobs"] for m in manifest], ["2", "2"])
            self.assertEqual(manifest[0]["sha256"],
                             hashlib.sha256((Path(tmp) / "c/gh_2026-01-01.json").read_bytes()).hexdigest())
            self.assertEqual(manifest[0]["sha256sums_check"], "not listed")
            seen = read_tsv(Path(tmp) / "vault" / "seen_ids.tsv")
            self.assertEqual({(s["id"], s["in_corpus"], s["kind"]) for s in seen},
                             {("987655", "yes", "run report"), ("424242", "no", "run report")})
            # counts may be rerun: its files are overwritten, not refused.
            code, _, err = self.make(tmp).run("counts")
            self.assertEqual(code, 0, err)

    def test_sha256sums_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            good = hashlib.sha256((Path(tmp) / "c/gh_2026-01-01.json").read_bytes()).hexdigest()
            write(tmp, "c/SHA256SUMS.txt", f"{good}  gh_2026-01-01.json\n{'0' * 64}  ab.json\n")
            out = io.StringIO()
            seal_draw.main(["counts"], root=fx.root, corpus=fx.corpus, sources=fx.sources, named=(),
                           sums_dirs=("c",), out=out, err=io.StringIO())
            checks = [m["sha256sums_check"] for m in read_tsv(Path(tmp) / "vault" / "corpus_manifest.tsv")]
            self.assertEqual(checks, ["match", "MISMATCH"])
            self.assertIn("listed in a SHA256SUMS.txt: 2; hash matches: 1", out.getvalue())

    def test_sidecar_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, [
                (GH, "c/match.json", "2026-01-01T00:00:00Z", gh_jobs((1, "Product"))),
                (GH, "c/mismatch.json", "2026-01-02T00:00:00Z", gh_jobs((2, "Product"))),
                (GH, "c/none.json", "2026-01-03T00:00:00Z", gh_jobs((3, "Product"))),
                (GH, "c/nohash.json", "2026-01-04T00:00:00Z", gh_jobs((4, "Product"))),
                (GH, "c/broken.json", "2026-01-05T00:00:00Z", gh_jobs((5, "Product"))),
            ])
            good = hashlib.sha256((Path(tmp) / "c/match.json").read_bytes()).hexdigest()
            write(tmp, "c/match.json.sidecar.json", {"file": "match.json", "sha256": good.upper()})
            write(tmp, "c/mismatch.json.sidecar.json", {"sha256": "f" * 64})
            write(tmp, "c/nohash.json.sidecar.json", {"file": "nohash.json"})
            write(tmp, "c/broken.json.sidecar.json", "not json")
            code, out, err = fx.run("counts")
            self.assertEqual(code, 0, err)
            rows = read_tsv(Path(tmp) / "vault" / "corpus_manifest.tsv")
            self.assertEqual(list(rows[0])[-2:], ["sha256sums_check", "sidecar_check"])
            self.assertEqual([r["sidecar_check"] for r in rows],
                             ["match", "MISMATCH", "no sidecar", "sidecar without sha256", "sidecar without sha256"])
            self.assertIn("corpus files with a sidecar sha256: 2; hash matches: 1", out)

    def test_missing_corpus_file_stops_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            (Path(tmp) / "c/ab.json").unlink()
            code, out, err = fx.run("counts")
            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            self.assertIn("c/ab.json", err)
            self.assertFalse((Path(tmp) / "vault").exists())

    def test_unparseable_corpus_file_stops_counts(self):
        for body in ("Not Found", {"status": 404}, {"jobs": [{"title": "no id"}]}):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as tmp:
                fx = self.make(tmp)
                write(tmp, "c/gh_2026-01-01.json", body)
                code, out, err = fx.run("counts")
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertIn("c/gh_2026-01-01.json", err)

    def test_missing_seen_source_stops_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = self.make(tmp)
            (Path(tmp) / "constructed_seen/run_report.json").unlink()
            code, out, err = fx.run("counts")
            self.assertEqual((code, out), (1, ""))
            self.assertIn("constructed_seen/run_report.json", err)


class TestSeenExtractors(unittest.TestCase):
    """Every extraction shape, on constructed files laid out like JS1's and JS2's."""

    def test_each_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "s/labels.json", {"note": "constructed", "labels": [{"id": "11"}, {"id": "12"}]})
            write(tmp, "s/selected.json", {"development": ["13"], "held_out": ["14"]})
            write(tmp, "s/meta.json", {"15": {"file": "15.txt"}, "16": {"file": "16.txt"}})
            write(tmp, "s/sampling.json", {"17_r1": {"posting_id": "17"}, "17_r2": {"posting_id": "17"}})
            write(tmp, "s/way2_input_18.txt", "constructed")
            write(tmp, "s/js1_report.json", {"summary": {"new_ids": ["19"]}, "new_postings": [{"posting_id": "20"}]})
            write(tmp, "s/js2_report.json", {"boards": [{"board": AB, "new_ids": ["c-21"],
                                                         "new_postings": [{"posting_id": "c-22"}]}]})
            sources = [("s/labels.json", "hand label", "labels"), ("s/selected.json", "other", "selected_ids"),
                       ("s/meta.json", "saved reply", "metadata_keys"),
                       ("s/sampling.json", "sampled", "sampling_posting_ids"),
                       ("s/way2_input_18.txt", "action surface", "id_in_file_name"),
                       ("s/js1_report.json", "run report", "js1_run_report"),
                       ("s/js2_report.json", "run report", "js2_run_report")]
            rows = seal_draw.load_seen(tmp, sources, ())
            got = {(b, i) for b, i, _, _ in rows}
            stripe = "greenhouse:stripe"
            self.assertEqual(got, {(stripe, str(n)) for n in range(11, 21)} | {(AB, "c-21"), (AB, "c-22")})
            # sampled twice, listed once per source
            self.assertEqual(sum(1 for r in rows if r[1] == "17"), 1)

    def test_unexpected_shape_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "s/labels.json", {"rows": []})
            with self.assertRaises(seal_draw.SealError) as ctx:
                seal_draw.load_seen(tmp, [("s/labels.json", "hand label", "labels")], ())
            self.assertIn("s/labels.json", str(ctx.exception))


class TestCorpusList(unittest.TestCase):
    """Checks the script's constants against their file names only. No corpus file is opened."""

    def test_twenty_files_four_boards(self):
        counts = {}
        for board, _, _ in seal_draw.CORPUS:
            counts[board] = counts.get(board, 0) + 1
        self.assertEqual(counts, {"greenhouse:stripe": 8, "greenhouse:duolingo": 4,
                                  "greenhouse:robinhood": 4, "ashby:notion": 4})

    def test_utc_time_matches_file_name(self):
        for _, rel, utc in seal_draw.CORPUS:
            with self.subTest(rel=rel):
                name = Path(rel).name
                stamp = re.search(r"(\d{4}-\d{2}-\d{2})(?:T(\d{2})(\d{2})(\d{2})Z)?", name)
                date, hh, mm, ss = stamp.groups()
                expected = f"{date}T{hh or '00'}:{mm or '00'}:{ss or '00'}Z"
                self.assertEqual(utc, expected)

    def test_no_file_after_run2(self):
        self.assertTrue(all(utc <= "2026-11-08T01:54:38Z" for _, _, utc in seal_draw.CORPUS))


if __name__ == "__main__":
    unittest.main()
