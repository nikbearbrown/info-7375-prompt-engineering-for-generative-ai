"""Tests for tools/measure.py. Constructed corpus, vault, run, audit list and hand labels, in temporary folders.

The fixture runs the real pipeline on constructed data: tools/filter_run.py
(clock set to the run audit.py reads), tools/audit.py draw, then a
constructed pass-3 hand-verdict file. The expected verdicts below were worked
out by hand for each constructed posting under each variant; measure's table
is checked against them. No test reads the real corpus, vault, run or audit.
"""

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from support import JS1 as PROJECT

from tools import audit, filter_run, measure, seal_draw

GH = "greenhouse:constructedgh"
RUN_TIME = datetime(2026, 11, 17, 21, 6, 12, tzinfo=timezone.utc)
MEASURE_TIME = datetime(2026, 11, 19, 12, 0, 0, tzinfo=timezone.utc)
FOLDER = "measure_2026-11-19T120000Z"
VARIANTS = ["v1", "T1", "T0", "S", "Y", "T0+S", "T0+Y", "T0+S+Y", "T1+S+Y"]

PLAIN = [str(8000 + i) for i in range(30)]  # Engineer, Constructed City, no skill: rejected by every variant
NAMED = {  # id: (title, location or None, text)
    "8100": ("Product Manager, Constructed Zero", "New York", "A constructed body with no skill."),
    "8101": ("Product Manager, Constructed One", "NYC", "You will use Python."),
    "8102": ("Senior Product Manager", "Remote", "Python and SQL daily."),
    "8103": ("Product Manager, Constructed Years", "New York", "Python and SQL. You have 5+ years of experience."),
    "8104": ("Product Manager, Constructed History", "Remote", "Python. Over the past 10 years we have grown."),
    "8105": ("Product Manager, Constructed Nowhere", None, "Java only."),
    "8106": ("Staff Product Manager", "NYC", "A constructed body with no skill."),
}
# Worked out by hand, one letter per variant in VARIANTS order: R relevant (kept), N not_relevant, T cannot_tell.
#   8100 score 0;  8101 score 1;  8102 Senior, score 2;  8103 "5+ years", score 2;
#   8104 "10 years" in company history (the pattern's false positive), score 1;
#   8105 no location, score 0 (cannot_tell once C3 passes);  8106 Staff, score 0.
EXPECTED = {
    "8100": "NNRNNRRRN",
    "8101": "NRRNNRRRR",
    "8102": "RRRNRNRNN",
    "8103": "RRRRNRNNN",
    "8104": "NRRNNRNNN",
    "8105": "NNTNNTTTN",
    "8106": "NNRNNNRNN",
}
EXPECTED.update({posting_id: "N" * len(VARIANTS) for posting_id in PLAIN})
SEALED_FINAL, SEALED_V2 = "7100001", "7200001"
HAND = {"8100": ("worth", "-"), "8101": ("worth", "-"), "8104": ("worth", "-"),
        "8102": ("not_worth", "level"), "8103": ("not_worth", "level"), "8106": ("not_worth", "level"),
        "8105": ("unclear", "location")}


def gh_job(posting_id, title, location, text):
    job = {"id": int(posting_id), "title": title, "content": f"&lt;p&gt;{text}&lt;/p&gt;",
           "updated_at": "2026-01-05T10:00:00-05:00"}
    if location is not None:
        job["location"] = {"name": location}
    return job


def seal_file(posting_ids):
    return "\n".join(["board_key\tid\tgroup\trank"]
                     + [f"{GH}\t{i}\tproduct\t{seal_draw.rank(GH, i)}" for i in posting_ids]) + "\n"


class Fixture:
    def __init__(self, tmp):
        self.root = Path(tmp)
        jobs = [gh_job(i, f"Constructed Engineer {i}", "Constructed City", f"Java and Go, item {i}.") for i in PLAIN]
        jobs += [gh_job(i, *fields) for i, fields in NAMED.items()]
        jobs += [gh_job(i, "SEALED-TITLE Product Manager", "New York", "SEALED-TEXT Python and SQL.")
                 for i in (SEALED_FINAL, SEALED_V2)]
        self.corpus = [(GH, "corpus/gh.json", "2026-01-01T00:00:00Z")]
        self.write("corpus/gh.json", json.dumps({"jobs": jobs}))
        digest = hashlib.sha256((self.root / "corpus/gh.json").read_bytes()).hexdigest()
        self.write("vault/corpus_manifest.tsv", "path\tboard_key\tutc_time\tsha256\tjobs\tunique_ids\tsha256sums_check\t"
                                                "sidecar_check\ncorpus/gh.json\t" + GH + "\t2026-01-01T00:00:00Z\t"
                                                + digest + "\t0\t0\tnot listed\tno sidecar\n")
        self.write("vault/final_heldout_ids.tsv", seal_file([SEALED_FINAL]))
        self.write("vault/js3_heldout_ids_v2.tsv", seal_file([SEALED_V2]))
        self.write("vault/js3_heldout_ids.tsv", seal_file(PLAIN[:2]))
        shutil.copy(PROJECT / "resume_persona.json", self.root / "resume_persona.json")
        for tool, argv, now in ((filter_run, [], RUN_TIME), (audit, ["draw"], None)):
            out, err = io.StringIO(), io.StringIO()
            code = tool.main(argv, root=self.root, corpus=self.corpus, now=now, out=out, err=err)
            assert code == 0, err.getvalue()
        self.listed = [line.split("\t")[2] for line in (self.root / "audit/audit_list.tsv").read_text().splitlines()[1:]]
        self.write(measure.HAND_FILE, self.hand_text())

    def hand(self):
        """{id: (verdict, parts)} for every audited posting; the first plain reject on the list is unclear."""
        labels = {i: HAND.get(i, ("not_worth", "role, location")) for i in self.listed}
        first_plain = next(i for i in self.listed if i in PLAIN)
        labels[first_plain] = ("unclear", "location")
        return labels

    def hand_text(self, labels=None):
        labels = labels or self.hand()
        rows = [f"{p}\t{GH}\t{i}\t{labels[i][0]}\t{labels[i][1]}\tconstructed evidence {p}"
                for p, i in enumerate(self.listed, start=1)]
        return "\n".join(["position\tboard_key\tid\tverdict\tparts\tevidence"] + rows) + "\n"

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run(self, *argv, now=MEASURE_TIME):
        out, err = io.StringIO(), io.StringIO()
        code = measure.main(list(argv), root=self.root, corpus=self.corpus, now=now, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def read(self, name):
        return (self.root / "output" / FOLDER / name).read_text(encoding="utf-8")

    def rows(self, name):
        lines = self.read(name).splitlines()
        if lines and lines[0].startswith("hand labels: "):  # table.tsv's first line names the hand file
            lines = lines[1:]
        return [dict(zip(lines[0].split("\t"), line.split("\t"))) for line in lines[1:]]


def expected_row(variant, fx, labels=None):
    column = VARIANTS.index(variant)
    outcome = {"R": "kept", "N": "rejected", "T": "cannot_tell"}
    cells = {f"{o}_{h}": 0 for o in ("kept", "rejected", "cannot_tell") for h in ("worth", "not_worth", "unclear")}
    for posting_id, (hand, _) in (labels or fx.hand()).items():
        cells[f"{outcome[EXPECTED[posting_id][column]]}_{hand}"] += 1
    letters = [EXPECTED[i][column] for i in EXPECTED]
    return {"audited": str(len(fx.listed)), **{k: str(v) for k, v in cells.items()}, "judged": str(len(EXPECTED)),
            "kept": str(letters.count("R")), "cannot_tell": str(letters.count("T"))}


class TestMeasure(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)
        self.code, self.out, self.err = self.fx.run()

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_the_table_and_a_kept_file_per_variant_and_prints_the_table_only(self):
        self.assertEqual(self.code, 0, self.err)
        self.assertEqual(sorted(p.name for p in (self.fx.root / "output" / FOLDER).iterdir()),
                         sorted(["table.tsv"] + [f"kept_{v}.tsv" for v in VARIANTS]))
        self.assertEqual(self.out, self.fx.read("table.tsv"))
        self.assertEqual(self.err, "")

    def test_table_counts(self):
        rows = self.fx.rows("table.tsv")
        self.assertEqual(list(rows[0]), list(measure.TABLE_HEADER))
        self.assertEqual([r["variant"] for r in rows], VARIANTS)
        for row in rows:
            with self.subTest(variant=row["variant"]):
                self.assertEqual({k: v for k, v in row.items() if k not in ("variant", "options")},
                                 expected_row(row["variant"], self.fx))

    def test_the_hand_computed_headline_numbers(self):
        rows = {r["variant"]: r for r in self.fx.rows("table.tsv")}
        self.assertEqual([rows[v]["kept"] for v in VARIANTS], ["2", "4", "6", "1", "1", "4", "4", "2", "1"])
        self.assertEqual([rows[v]["cannot_tell"] for v in VARIANTS], ["0", "0", "1", "0", "0", "1", "1", "1", "0"])
        # v1 keeps the two level failures and none of the three worth postings; T0+S+Y keeps two of the three.
        self.assertEqual((rows["v1"]["kept_worth"], rows["v1"]["kept_not_worth"], rows["v1"]["rejected_worth"]),
                         ("0", "2", "3"))
        self.assertEqual((rows["T0+S+Y"]["kept_worth"], rows["T0+S+Y"]["kept_not_worth"],
                          rows["T0+S+Y"]["rejected_worth"]), ("2", "0", "1"))
        self.assertEqual(rows["T0"]["options"], "skills_needed=0")
        self.assertEqual(rows["T1+S+Y"]["options"], "skills_needed=1; seniority_words=FILTER.md §5 (Senior, Staff, "
                                                    "Lead, Group, Principal, Director, Head of); max_years=3")

    def test_kept_files(self):
        expected_order = {  # F8: score high to low, then id as a string
            "v1": ["8102", "8103"], "T1": ["8102", "8103", "8101", "8104"],
            "T0": ["8102", "8103", "8101", "8104", "8100", "8106"], "S": ["8103"], "Y": ["8102"],
            "T0+S": ["8103", "8101", "8104", "8100"], "T0+Y": ["8102", "8101", "8100", "8106"],
            "T0+S+Y": ["8101", "8100"], "T1+S+Y": ["8101"],
        }
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                lines = self.fx.read(f"kept_{variant}.tsv").splitlines()
                self.assertEqual(lines[0], "board_key\tid\ttitle\tlocation\treasons")
                self.assertEqual([line.split("\t")[1] for line in lines[1:]], expected_order[variant])
        by_id = {r["id"]: r for r in self.fx.rows("kept_T0+Y.tsv")}
        self.assertEqual(by_id["8100"], {"board_key": GH, "id": "8100", "title": "Product Manager, Constructed Zero",
                                         "location": "New York", "reasons": "C1: Product Manager; C2: New York; "
                                                                            "C3: score 0; C4: pass"})
        self.assertEqual({r["id"]: r["reasons"] for r in self.fx.rows("kept_v1.tsv")}["8103"],
                         "C1: Product Manager; C2: New York; C3: score 2 (Python, SQL)")

    def test_v1_reproduces_filter_run(self):
        shortlist = (self.fx.root / audit.RUN / "shortlist.tsv").read_text().splitlines()[1:]
        kept = self.fx.read("kept_v1.tsv").splitlines()[1:]
        self.assertEqual([line.split("\t")[2] for line in shortlist], [line.split("\t")[1] for line in kept])

    def test_no_body_text_and_no_sealed_posting_in_any_file(self):
        for path in (self.fx.root / "output" / FOLDER).iterdir():
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                for marker in ("SEALED", SEALED_FINAL, SEALED_V2, "Java and Go", "constructed body", "past 10 years"):
                    self.assertNotIn(marker, text)

    def test_refuses_to_overwrite(self):
        before = {p.name: p.read_bytes() for p in (self.fx.root / "output" / FOLDER).iterdir()}
        code, out, err = self.fx.run()
        self.assertEqual((code, out), (1, ""))
        self.assertIn(f"refusing to overwrite: output/{FOLDER}/", err)
        self.assertEqual({p.name: p.read_bytes() for p in (self.fx.root / "output" / FOLDER).iterdir()}, before)


class TestStops(unittest.TestCase):
    def assert_stops(self, fx, needle):
        code, out, err = fx.run()
        self.assertEqual((code, out), (1, ""), err)
        self.assertIn(needle, err)
        self.assertFalse((fx.root / "output" / FOLDER).exists())
        for posting_id in [SEALED_FINAL, SEALED_V2] + PLAIN + list(NAMED):
            self.assertNotIn(posting_id, err)

    def test_sealed_postings_are_never_judged(self):
        seen = []
        real = measure.filter_v1.judge

        def recording(posting, persona, options=None):
            seen.append(posting["posting_id"])
            return real(posting, persona, options)

        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            with mock.patch.object(measure.filter_v1, "judge", recording):
                code, _, err = fx.run()
        self.assertEqual(code, 0, err)
        self.assertEqual(len(seen), len(VARIANTS) * len(EXPECTED))
        self.assertNotIn(SEALED_FINAL, seen)
        self.assertNotIn(SEALED_V2, seen)

    def test_hand_file_that_fails_the_audit_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            labels = fx.hand()
            labels[fx.listed[0]] = ("maybe", "-")
            fx.write(measure.HAND_FILE, fx.hand_text(labels))
            self.assert_stops(fx, "audit/hand_verdicts_r3.tsv does not pass the audit check (1 problems")

    def test_missing_hand_file_or_audit_list(self):
        for rel, needle in ((measure.HAND_FILE, "cannot read the hand-verdict file"),
                            ("audit/audit_list.tsv", "cannot read audit/audit_list.tsv")):
            with self.subTest(rel=rel), tempfile.TemporaryDirectory() as tmp:
                fx = Fixture(tmp)
                (fx.root / rel).unlink()
                self.assert_stops(fx, needle)

    def test_corpus_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            path = fx.root / "corpus/gh.json"
            path.write_bytes(path.read_bytes() + b" ")
            self.assert_stops(fx, "corpus/gh.json: SHA-256 does not match vault/corpus_manifest.tsv")


class TestHandOption(unittest.TestCase):
    OTHER = "audit/hand_other.tsv"

    def all_worth(self, fx):
        return {posting_id: ("worth", "-") for posting_id in fx.listed}

    def assert_table(self, fx, out, first_line, labels):
        self.assertEqual(out, fx.read("table.tsv"))
        self.assertEqual(out.splitlines()[:2], [first_line, "\t".join(measure.TABLE_HEADER)])
        for row in fx.rows("table.tsv"):
            with self.subTest(variant=row["variant"]):
                self.assertEqual({k: v for k, v in row.items() if k not in ("variant", "options")},
                                 expected_row(row["variant"], fx, labels))

    def test_the_default_is_r3(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.write(self.OTHER, fx.hand_text(self.all_worth(fx)))  # present, but not asked for
            code, out, err = fx.run()
            self.assertEqual(code, 0, err)
            self.assert_table(fx, out, "hand labels: audit/hand_verdicts_r3.tsv", fx.hand())

    def test_hand_reads_another_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.write(self.OTHER, fx.hand_text(self.all_worth(fx)))
            (fx.root / measure.HAND_FILE).unlink()  # so r3 cannot be what is read
            code, out, err = fx.run("--hand", self.OTHER)
            self.assertEqual(code, 0, err)
            self.assert_table(fx, out, f"hand labels: {self.OTHER}", self.all_worth(fx))
            rows = {r["variant"]: r for r in fx.rows("table.tsv")}
            self.assertEqual((rows["v1"]["kept_worth"], rows["v1"]["kept_not_worth"]), ("2", "0"))

    def test_hand_takes_an_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as elsewhere:
            fx = Fixture(tmp)
            path = Path(elsewhere) / "hand.tsv"
            path.write_text(fx.hand_text(self.all_worth(fx)), encoding="utf-8")
            code, out, err = fx.run("--hand", str(path))
            self.assertEqual(code, 0, err)
            self.assert_table(fx, out, f"hand labels: {path}", self.all_worth(fx))

    def test_a_hand_file_that_fails_check_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            labels = self.all_worth(fx)
            labels[fx.listed[-1]] = ("worth", "role")  # parts must be - for worth
            fx.write(self.OTHER, fx.hand_text(labels))
            code, out, err = fx.run("--hand", self.OTHER)
            self.assertEqual((code, out), (1, ""))
            self.assertIn(f"{self.OTHER} does not pass the audit check (1 problems", err)
            self.assertFalse((fx.root / "output" / FOLDER).exists())
            code, out, err = fx.run("--hand", "audit/no_such_file.tsv")
            self.assertEqual((code, out), (1, ""))
            self.assertIn("cannot read the hand-verdict file", err)


class TestVariants(unittest.TestCase):
    def test_the_nine_variants(self):
        self.assertEqual([name for name, _ in measure.VARIANTS], VARIANTS)
        options = dict(measure.VARIANTS)
        self.assertEqual(options["v1"], {})
        self.assertEqual(options["T0+S+Y"], {"skills_needed": 0, "seniority_words": ("Senior", "Staff", "Lead", "Group",
                                                                                   "Principal", "Director", "Head of"),
                                             "max_years": 3})
        self.assertEqual(options["T1+S+Y"]["skills_needed"], 1)
        self.assertEqual(measure.HAND_FILE, "audit/hand_verdicts_r3.tsv")


if __name__ == "__main__":
    unittest.main()
