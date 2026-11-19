"""Tests for tools/filter_run.py --filter v1|v2 (FILTER.md v2). Constructed data, temporary folders only.

The v1 tests in tests/test_filter_run.py run the default and still pass
unchanged; here, --filter v1 is checked against the same expectations and
against the default byte for byte, and v2 is checked on postings built to
exercise F6 (v2), F9 and F10. No test reads the real corpus or vault.
"""

import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import test_filter_run as v1_tests
from support import JS1 as PROJECT

from agent import filter as filter_v1
from tools import filter_run, seal_draw

GH = "greenhouse:constructedgh"
AB = "ashby:constructedab"
NOW = datetime(2026, 11, 20, 9, 0, 0, tzinfo=timezone.utc)
V2_FOLDER = "filter_v2_2026-11-20T090000Z"
SEALED = [(GH, "7100001"), (GH, "7200001")]  # final's set, JS3's held-out set: v2 would keep both

# id: (title, location or None, text). Under v2:
GH_JOBS = {
    "6001": ("Product Manager, Payments", "New York", "Python and SQL."),             # relevant, score 2
    "6002": ("Associate Product Manager", "Remote", "You will run user research."),   # relevant, score 1; two title terms
    "6003": ("Senior Product Manager", "NYC", "Python, SQL, A/B testing."),           # F9: Senior
    "6004": ("Product Manager", "New York", "Python. 5+ years of experience."),       # F10: 5+ years
    "6005": ("Product Manager, Growth", "New York or Remote", "A body with no skill."),  # relevant, score 0; two locations
    "6006": ("Product Manager", None, "Python and SQL."),                             # cannot_tell: no location
    "6007": ("Software Engineer", "New York", "Python SQL"),                          # C1 fails
    "6008": ("Product Analyst", "NYC", "SQL, A/B testing and roadmapping. 3+ years."),  # relevant, score 3; 3 is not above 3
}
AB_JOBS = {
    "c-ab-1": ("Product Manager", "Remote", "Python, SQL, A/B testing, roadmapping, user research."),  # relevant, 5
    "c-ab-2": ("Staff Product Manager", "New York", "Python"),                                        # F9: Staff
}
SUMMARY_V2 = f"""JS3 filter v2 run (FILTER.md v2; SEAL.md v1.5). Counts only: no ids, no titles.
corpus: 2 files, 12 postings (one copy per board key and id)
sealed postings withheld, not judged and not written: 2
judged: 10
verdicts:
  {AB}: relevant 1, not_relevant 1, cannot_tell 0; total 2
  {GH}: relevant 4, not_relevant 3, cannot_tell 1; total 8
  all boards: relevant 5, not_relevant 4, cannot_tell 1; total 10
closest calls: 5 ({AB} 1, {GH} 4)
rule.py cross-check: not run for v2, which is not compared with rule.py: rule.py is v1's rule, and v2 changes F6 (a skills threshold of 0) and adds C4 (F9, F10), so v2's verdicts are meant to differ from it (FILTER.md v2)
postings with a missing field: 1 (judged under F7)
written to: output/{V2_FOLDER}/
"""
YEARS = "The posting asks for no more than 3 years of experience."
NO_SENIORITY = "The title has no seniority word."
JUSTIFICATIONS = [  # (position, board_key, id, claim, field), in F8 order and claim order
    (1, AB, "c-ab-1", "The title names a target role: Product Manager.", "title"),
    (1, AB, "c-ab-1", "The location is workable: Remote.", "location"),
    (1, AB, "c-ab-1", NO_SENIORITY, "title"),
    (1, AB, "c-ab-1", YEARS, "text"),
    (1, AB, "c-ab-1", "The role calls for Python.", "text"),
    (1, AB, "c-ab-1", "The role calls for SQL.", "text"),
    (1, AB, "c-ab-1", "The role calls for A/B testing.", "text"),
    (1, AB, "c-ab-1", "The role calls for roadmapping.", "text"),
    (1, AB, "c-ab-1", "The role calls for user research.", "text"),
    (2, GH, "6008", "The title names a target role: Product Analyst.", "title"),
    (2, GH, "6008", "The location is workable: NYC.", "location"),
    (2, GH, "6008", NO_SENIORITY, "title"),
    (2, GH, "6008", YEARS, "text"),
    (2, GH, "6008", "The role calls for SQL.", "text"),
    (2, GH, "6008", "The role calls for A/B testing.", "text"),
    (2, GH, "6008", "The role calls for roadmapping.", "text"),
    (3, GH, "6001", "The title names a target role: Product Manager.", "title"),
    (3, GH, "6001", "The location is workable: New York.", "location"),
    (3, GH, "6001", NO_SENIORITY, "title"),
    (3, GH, "6001", YEARS, "text"),
    (3, GH, "6001", "The role calls for Python.", "text"),
    (3, GH, "6001", "The role calls for SQL.", "text"),
    (4, GH, "6002", "The title names a target role: Associate Product Manager.", "title"),
    (4, GH, "6002", "The title names a target role: Product Manager.", "title"),
    (4, GH, "6002", "The location is workable: Remote.", "location"),
    (4, GH, "6002", NO_SENIORITY, "title"),
    (4, GH, "6002", YEARS, "text"),
    (4, GH, "6002", "The role calls for user research.", "text"),
    (5, GH, "6005", "The title names a target role: Product Manager.", "title"),
    (5, GH, "6005", "The location is workable: New York.", "location"),
    (5, GH, "6005", "The location is workable: Remote.", "location"),
    (5, GH, "6005", NO_SENIORITY, "title"),
    (5, GH, "6005", YEARS, "text"),
]


def gh_job(posting_id, title, location, text):
    job = {"id": int(posting_id), "title": title, "content": f"&lt;p&gt;{text} BODY-MARKER&lt;/p&gt;",
           "updated_at": "2026-01-05T10:00:00-05:00"}
    if location is not None:
        job["location"] = {"name": location}
    return job


def seal_file(keys):
    return "\n".join(["board_key\tid\tgroup\trank"]
                     + [f"{b}\t{i}\tproduct\t{seal_draw.rank(b, i)}" for b, i in keys]) + "\n"


class Fixture:
    def __init__(self, tmp):
        self.root = Path(tmp)
        gh = [gh_job(i, *fields) for i, fields in GH_JOBS.items()]
        gh += [gh_job(i, "Product Manager", "New York", "SEALED-TEXT Python and SQL.") for _, i in SEALED]
        ab = [{"id": i, "title": t, "location": loc, "descriptionPlain": f"{text} BODY-MARKER"}
              for i, (t, loc, text) in AB_JOBS.items()]
        self.corpus = [(GH, "corpus/gh.json", "2026-01-01T00:00:00Z"), (AB, "corpus/ab.json", "2026-01-01T00:00:00Z")]
        self.write("corpus/gh.json", json.dumps({"jobs": gh}))
        self.write("corpus/ab.json", json.dumps({"jobs": ab}))
        manifest = ["path\tboard_key\tutc_time\tsha256\tjobs\tunique_ids\tsha256sums_check\tsidecar_check"]
        for board, rel, utc in self.corpus:
            digest = hashlib.sha256((self.root / rel).read_bytes()).hexdigest()
            manifest.append(f"{rel}\t{board}\t{utc}\t{digest}\t0\t0\tnot listed\tno sidecar")
        self.write("vault/corpus_manifest.tsv", "\n".join(manifest) + "\n")
        self.write("vault/final_heldout_ids.tsv", seal_file(SEALED[:1]))
        self.write("vault/js3_heldout_ids_v2.tsv", seal_file(SEALED[1:]))
        shutil.copy(PROJECT / "resume_persona.json", self.root / "resume_persona.json")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def read(self, name, folder=V2_FOLDER):
        return (self.root / "output" / folder / name).read_text(encoding="utf-8")

    def rows(self, name, folder=V2_FOLDER):
        lines = self.read(name, folder).splitlines()
        return [dict(zip(lines[0].split("\t"), line.split("\t"))) for line in lines[1:]]


def run(root, corpus, *argv, now=NOW):
    out, err = io.StringIO(), io.StringIO()
    code = filter_run.main(list(argv), root=root, corpus=corpus, now=now, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def files_of(folder):
    return {p.name: p.read_bytes() for p in Path(folder).iterdir()}


class TestV1Unchanged(unittest.TestCase):
    def test_filter_v1_gives_the_committed_v1_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = v1_tests.Fixture(tmp)
            code, out, err = run(fx.root, fx.corpus, "--filter", "v1", now=v1_tests.NOW)
            self.assertEqual(code, 0, err)
            self.assertEqual(out, v1_tests.SUMMARY)
            folder = fx.root / "output" / v1_tests.FOLDER
            self.assertEqual(sorted(files_of(folder)),
                             ["cannot_tell.tsv", "closest_calls.tsv", "shortlist.tsv", "summary.txt", "verdicts.tsv"])
            self.assertEqual((folder / "verdicts.tsv").read_text().splitlines()[0], v1_tests.HEADER)

    def test_the_default_is_v1_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            default, explicit = v1_tests.Fixture(a), v1_tests.Fixture(b)
            self.assertEqual(run(default.root, default.corpus, now=v1_tests.NOW)[0], 0)
            self.assertEqual(run(explicit.root, explicit.corpus, "--filter", "v1", now=v1_tests.NOW)[0], 0)
            self.assertEqual(files_of(default.root / "output" / v1_tests.FOLDER),
                             files_of(explicit.root / "output" / v1_tests.FOLDER))

    def test_v1_judges_with_no_options(self):
        calls = []
        real = filter_v1.judge

        def recording(*args):
            calls.append(args[2:])
            return real(*args)

        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            with mock.patch.object(filter_run.filter_v1, "judge", recording):
                self.assertEqual(run(fx.root, fx.corpus, "--filter", "v1")[0], 0)
        self.assertEqual(set(calls), {()})  # judge(posting, persona), exactly as before


class TestV2(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)
        self.code, self.out, self.err = run(self.fx.root, self.fx.corpus, "--filter", "v2")

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_the_v2_folder_with_justifications(self):
        self.assertEqual(self.code, 0, self.err)
        self.assertEqual(sorted(files_of(self.fx.root / "output" / V2_FOLDER)),
                         ["cannot_tell.tsv", "closest_calls.tsv", "justifications.tsv", "shortlist.tsv", "summary.txt",
                          "verdicts.tsv"])
        self.assertEqual(self.out, self.fx.read("summary.txt"))

    def test_summary(self):
        self.assertEqual(self.fx.read("summary.txt"), SUMMARY_V2)

    def test_columns_gain_c4_and_its_reason(self):
        expected = v1_tests.HEADER.replace("\tC3\t", "\tC3\tC4\tC4_reason\t")
        for name in ("verdicts.tsv", "cannot_tell.tsv", "closest_calls.tsv"):
            self.assertEqual(self.fx.read(name).splitlines()[0], expected, name)
        self.assertEqual(self.fx.read("shortlist.tsv").splitlines()[0], "position\t" + expected)
        rows = {r["id"]: r for r in self.fx.rows("verdicts.tsv")}
        self.assertEqual((rows["6003"]["verdict"], rows["6003"]["C4"], rows["6003"]["C4_reason"]),
                         ("not_relevant", "fail", 'title has "Senior"'))
        self.assertEqual((rows["6004"]["verdict"], rows["6004"]["C4"], rows["6004"]["C4_reason"]),
                         ("not_relevant", "fail", 'text states "5+ years", a minimum above 3 years'))
        self.assertEqual((rows["c-ab-2"]["C4"], rows["c-ab-2"]["C4_reason"]), ("fail", 'title has "Staff"'))
        self.assertEqual((rows["6005"]["verdict"], rows["6005"]["C3"], rows["6005"]["score"], rows["6005"]["C4"]),
                         ("relevant", "pass", "0", "pass"))
        self.assertEqual((rows["6006"]["verdict"], rows["6006"]["missing"]), ("cannot_tell", "location"))

    def test_v2_uses_v2_options(self):
        calls = []
        real = filter_v1.judge

        def recording(*args):
            calls.append(args[2:])
            return real(*args)

        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            with mock.patch.object(filter_run.filter_v1, "judge", recording):
                self.assertEqual(run(fx.root, fx.corpus, "--filter", "v2")[0], 0)
        self.assertEqual(len(calls), len(GH_JOBS) + len(AB_JOBS))
        self.assertTrue(all(len(c) == 1 and c[0] is filter_v1.V2_OPTIONS for c in calls))
        self.assertEqual(filter_v1.V2_OPTIONS, {"skills_needed": 0, "seniority_words": filter_v1.SENIORITY_WORDS,
                                                "max_years": 3})
        self.assertEqual(filter_run.FILTERS, {"v1": None, "v2": filter_v1.V2_OPTIONS})

    def test_shortlist_in_f8_order(self):
        self.assertEqual([(r["position"], r["id"], r["score"]) for r in self.fx.rows("shortlist.tsv")],
                         [("1", "c-ab-1", "5"), ("2", "6008", "3"), ("3", "6001", "2"), ("4", "6002", "1"),
                          ("5", "6005", "0")])

    def test_justifications(self):
        lines = self.fx.read("justifications.tsv").splitlines()
        self.assertEqual(lines[0], "position\tboard_key\tid\tclaim_no\tclaim\tfield")
        got = [line.split("\t") for line in lines[1:]]
        claim_no = {}  # claim_no restarts at 1 for each posting
        numbered = []
        for position, board, posting_id, claim, field in JUSTIFICATIONS:
            claim_no[posting_id] = claim_no.get(posting_id, 0) + 1
            numbered.append([str(position), board, posting_id, str(claim_no[posting_id]), claim, field])
        self.assertEqual(got, numbered)

    def test_justifications_only_for_the_shortlist(self):
        shortlisted = {r["id"] for r in self.fx.rows("shortlist.tsv")}
        self.assertEqual({r["id"] for r in self.fx.rows("justifications.tsv")}, shortlisted)

    def test_rule_py_is_never_consulted(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            real = filter_run.rule.judge
            with mock.patch.object(filter_run.rule, "judge", side_effect=real) as rule_judge:
                code, _, err = run(fx.root, fx.corpus, "--filter", "v2")
            self.assertEqual(code, 0, err)
            # agent/filter.py itself calls rule.judge for C1-C3; filter_run's cross-check adds no second call
            self.assertEqual(rule_judge.call_count, len(GH_JOBS) + len(AB_JOBS))

    def test_no_body_text_or_sealed_posting_in_any_file(self):
        for name, data in files_of(self.fx.root / "output" / V2_FOLDER).items():
            text = data.decode("utf-8")
            with self.subTest(file=name):
                for marker in ["BODY-MARKER", "SEALED", "You will run", "A body with no skill"] + [i for _, i in SEALED]:
                    self.assertNotIn(marker, text)


class TestSealedNeverJudged(unittest.TestCase):
    def test_v2_never_judges_a_sealed_posting(self):
        seen = []
        real = filter_v1.judge

        def recording(posting, *rest):
            seen.append(posting["posting_id"])
            return real(posting, *rest)

        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            with mock.patch.object(filter_run.filter_v1, "judge", recording):
                code, out, err = run(fx.root, fx.corpus, "--filter", "v2")
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(seen), sorted(list(GH_JOBS) + list(AB_JOBS)))
        self.assertIn("withheld, not judged and not written: 2", out)


class TestCommandLine(unittest.TestCase):
    def test_only_v1_or_v2(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(io.StringIO()):
            fx = Fixture(tmp)
            with self.assertRaises(SystemExit) as raised:
                run(fx.root, fx.corpus, "--filter", "v3")
        self.assertEqual(raised.exception.code, 2)
        self.assertFalse((Path(tmp) / "output").exists())

    def test_v1_and_v2_side_by_side(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            self.assertEqual(run(fx.root, fx.corpus, "--filter", "v1")[0], 0)
            self.assertEqual(run(fx.root, fx.corpus, "--filter", "v2")[0], 0)
            v1 = [r["id"] for r in fx.rows("shortlist.tsv", "filter_v1_2026-11-20T090000Z")]
            v2 = [r["id"] for r in fx.rows("shortlist.tsv")]
            self.assertEqual(v1, ["c-ab-1", "6003", "6008", "6001"])  # v1 keeps the Senior title, needs 2 skills
            self.assertEqual(v2, ["c-ab-1", "6008", "6001", "6002", "6005"])
            self.assertFalse((fx.root / "output" / "filter_v1_2026-11-20T090000Z" / "justifications.tsv").exists())


if __name__ == "__main__":
    unittest.main()
