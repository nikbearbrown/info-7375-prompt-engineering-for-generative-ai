"""Tests for tools/filter_run.py. Constructed corpus, constructed vault, temporary folders only.

No test reads the real corpus or the real vault/, and no test writes outside
its temporary folder. The persona is the fictional resume_persona.json,
copied in.
"""

import hashlib
import io
import json
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from support import JS1 as PROJECT

from tools import filter_run, seal_draw

GH = "greenhouse:constructedgh"
AB = "ashby:constructedab"
NOW = datetime(2026, 11, 17, 20, 0, 0, tzinfo=timezone.utc)
FOLDER = "filter_v1_2026-11-17T200000Z"
SEALED_FINAL = [(GH, "7100001"), (AB, "c-sealed-01")]
SEALED_V2 = [(GH, "7200001"), (AB, "c-sealed-02")]
EXPOSED = [(GH, "5003"), (AB, "c-ab-03")]  # the first JS3 set (SEAL.md §8): judged like any posting


def gh(posting_id, title, location, text):
    job = {"id": int(posting_id), "title": title, "updated_at": "2026-01-05T10:00:00-05:00",
           "absolute_url": f"https://example.invalid/{posting_id}"}
    if location is not None:
        job["location"] = {"name": location}
    if text is not None:
        job["content"] = f"&lt;p&gt;{text} BODY-MARKER-{posting_id}&lt;/p&gt;"  # escaped, as Greenhouse sends it
    return job


def ab(posting_id, title, location, text):
    return {"id": posting_id, "title": title, "location": location, "secondaryLocations": [],
            "descriptionPlain": f"{text} BODY-MARKER-{posting_id}", "publishedAt": "2026-01-05T10:00:00Z"}


# Constructed postings. Expected: (verdict, score, closest call).
GH_LATE = [
    gh("5001", "Product Manager, Payments", "New York", "Python and SQL"),               # relevant 2, closest
    gh("5002", "Product Analyst", "Remote - US", "Python, SQL, A/B testing"),           # relevant 3
    gh("5003", "Software Engineer", "New York", "Python SQL user research"),            # not_relevant 3, closest
    gh("5004", "Product Manager", None, "Python and SQL"),                               # cannot_tell: location
    gh("5005", "Product Manager", "London", None),                                       # not_relevant, no text
    gh("4001", "Late Title Product Manager", "NYC", "Python SQL roadmapping user research"),  # relevant 4
    gh("7100001", "SEALED-TITLE Product Manager", "New York", "SEALED-TEXT Python SQL"),
    gh("7200001", "SEALED-TITLE Product Analyst", "Remote", "SEALED-TEXT Python SQL"),
]
GH_EARLY = [
    gh("4001", "Early Title Software Engineer", "London", "Java"),                      # replaced by the late copy
    gh("4002", "Associate Product Manager", "Remote", "Python SQL"),                    # relevant 2, closest
]
AB_JOBS = [
    ab("c-ab-01", "Product Manager", "Remote", "Python, SQL, A/B testing, roadmapping, user research"),  # relevant 5
    ab("c-ab-02", "Product Designer", "New York", "Python SQL"),                        # not_relevant 2, closest
    ab("c-ab-03", "Product Manager", "New York", "Python"),                             # not_relevant 1, closest
    ab("c-ab-04", "Product Manager", "  ", "Python SQL"),                               # cannot_tell: location
    ab("c-ab-05", "Product Analyst", "NYC", "SQL and user research"),                   # relevant 2, closest
    ab("c-sealed-01", "SEALED-TITLE Product Manager", "Remote", "SEALED-TEXT Python SQL"),
    ab("c-sealed-02", "SEALED-TITLE Product Manager", "NYC", "SEALED-TEXT Python SQL"),
]
FILES = [  # (board, path, utc, jobs); the later Greenhouse file is listed first: time decides
    (GH, "corpus/gh_late.json", "2026-01-02T00:00:00Z", GH_LATE),
    (GH, "corpus/gh_early.json", "2026-01-01T00:00:00Z", GH_EARLY),
    (AB, "corpus/ab.json", "2026-01-01T12:00:00Z", AB_JOBS),
]

SUMMARY = f"""JS3 filter v1 run (FILTER.md v1; SEAL.md v1.5). Counts only: no ids, no titles.
corpus: 3 files, 16 postings (one copy per board key and id)
sealed postings withheld, not judged and not written: 4
judged: 12
verdicts:
  {AB}: relevant 2, not_relevant 2, cannot_tell 1; total 5
  {GH}: relevant 4, not_relevant 2, cannot_tell 1; total 7
  all boards: relevant 6, not_relevant 4, cannot_tell 2; total 12
closest calls: 6 ({AB} 3, {GH} 3)
rule.py cross-check: 9 postings with no missing field; disagreements: 0
postings with a missing field: 3 (judged under F7; not compared with rule.py)
written to: output/{FOLDER}/
"""
HEADER = "board_key\tid\ttitle\tlocation\tverdict\tC1\tC2\tC3\tscore\ttitle_match\tlocation_match\tskills_found\tmissing\tclosest_call"


def seal_file(keys):
    lines = ["board_key\tid\tgroup\trank"] + [f"{b}\t{i}\tproduct\t{seal_draw.rank(b, i)}" for b, i in keys]
    return "\n".join(lines) + "\n"


class Fixture:
    def __init__(self, tmp):
        self.root = Path(tmp)
        self.corpus = []
        for board, rel, utc, jobs in FILES:
            self.write(rel, json.dumps({"jobs": jobs}))
            self.corpus.append((board, rel, utc))
        self.write_manifest()
        self.write("vault/final_heldout_ids.tsv", seal_file(SEALED_FINAL))
        self.write("vault/js3_heldout_ids_v2.tsv", seal_file(SEALED_V2))
        self.write("vault/js3_heldout_ids.tsv", seal_file(EXPOSED))
        shutil.copy(PROJECT / "resume_persona.json", self.root / "resume_persona.json")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_manifest(self, rels=None):
        rows = ["path\tboard_key\tutc_time\tsha256\tjobs\tunique_ids\tsha256sums_check\tsidecar_check"]
        for board, rel, utc in self.corpus:
            if rels is None or rel in rels:
                digest = hashlib.sha256((self.root / rel).read_bytes()).hexdigest()
                rows.append(f"{rel}\t{board}\t{utc}\t{digest}\t0\t0\tnot listed\tno sidecar")
        self.write("vault/corpus_manifest.tsv", "\n".join(rows) + "\n")

    def run(self, now=NOW):
        out, err = io.StringIO(), io.StringIO()
        code = filter_run.main([], root=self.root, corpus=self.corpus, now=now, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    @property
    def folder(self):
        return self.root / "output" / FOLDER

    def read(self, name):
        return (self.folder / name).read_text(encoding="utf-8")

    def rows(self, name):
        lines = self.read(name).splitlines()
        header = lines[0].split("\t")
        return [dict(zip(header, line.split("\t"))) for line in lines[1:]]


class TestRun(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)
        self.code, self.out, self.err = self.fx.run()

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_the_five_files_and_prints_the_summary_only(self):
        self.assertEqual(self.code, 0, self.err)
        self.assertEqual(sorted(p.name for p in self.fx.folder.iterdir()),
                         ["cannot_tell.tsv", "closest_calls.tsv", "shortlist.tsv", "summary.txt", "verdicts.tsv"])
        self.assertEqual(self.out, self.fx.read("summary.txt"))
        self.assertEqual(self.err, "")

    def test_summary(self):
        self.assertEqual(self.fx.read("summary.txt"), SUMMARY)

    def test_summary_counts_add_up(self):
        text = self.fx.read("summary.txt")
        number = lambda pattern: int(re.search(pattern, text).group(1))  # noqa: E731
        postings, sealed, judged = number(r"(\d+) postings"), number(r"not written: (\d+)"), number(r"judged: (\d+)")
        self.assertEqual(postings, sealed + judged)
        per_board = re.findall(r"^  (.+?): relevant (\d+), not_relevant (\d+), cannot_tell (\d+); total (\d+)$",
                               text, re.MULTILINE)
        *boards, (label, *total) = per_board
        self.assertEqual(label, "all boards")
        self.assertEqual([name for name, *_ in boards], [AB, GH])
        for name, *counts in boards:
            self.assertEqual(sum(map(int, counts[:3])), int(counts[3]), name)
        for column in range(4):
            self.assertEqual(sum(int(b[column + 1]) for b in boards), int(total[column]))
        self.assertEqual(int(total[3]), judged)
        compared, missing = number(r"cross-check: (\d+) postings"), number(r"missing field: (\d+)")
        self.assertEqual(compared + missing, judged)
        self.assertEqual(number(r"disagreements: (\d+)"), 0)
        closest = number(r"closest calls: (\d+)")
        self.assertEqual(closest, sum(int(n) for n in re.findall(r"constructed\w+ (\d+)[,)]", text)))
        self.assertEqual(closest, len(self.fx.rows("closest_calls.tsv")))
        self.assertEqual(int(total[0]), len(self.fx.rows("shortlist.tsv")))
        self.assertEqual(int(total[2]), len(self.fx.rows("cannot_tell.tsv")))
        self.assertEqual(judged, len(self.fx.rows("verdicts.tsv")))

    def test_sealed_postings_appear_in_no_output_file(self):
        for name in ("verdicts.tsv", "shortlist.tsv", "cannot_tell.tsv", "closest_calls.tsv", "summary.txt"):
            text = self.fx.read(name)
            for _, posting_id in SEALED_FINAL + SEALED_V2:
                self.assertNotIn(posting_id, text, name)
            self.assertNotIn("SEALED", text, name)
        self.assertNotIn("SEALED", self.out)
        self.assertIn("withheld, not judged and not written: 4", self.out)

    def test_exposed_set_is_judged(self):
        judged = {(r["board_key"], r["id"]) for r in self.fx.rows("verdicts.tsv")}
        self.assertTrue(set(EXPOSED) <= judged)

    def test_no_body_text_in_any_output_file(self):
        for name in ("verdicts.tsv", "shortlist.tsv", "cannot_tell.tsv", "closest_calls.tsv", "summary.txt"):
            self.assertNotIn("BODY-MARKER", self.fx.read(name), name)

    def test_verdicts_tsv(self):
        lines = self.fx.read("verdicts.tsv").splitlines()
        self.assertEqual(lines[0], HEADER)
        ids = [line.split("\t")[1] for line in lines[1:]]
        self.assertEqual(ids, ["c-ab-01", "c-ab-02", "c-ab-03", "c-ab-04", "c-ab-05",
                               "4001", "4002", "5001", "5002", "5003", "5004", "5005"])
        by_id = {line.split("\t")[1]: line for line in lines[1:]}
        self.assertEqual(by_id["5004"], f"{GH}\t5004\tProduct Manager\t\tcannot_tell\tpass\tmissing\tpass\t2\t"
                                        "Product Manager\t\tPython; SQL\tlocation\tno")
        self.assertEqual(by_id["5005"], f"{GH}\t5005\tProduct Manager\tLondon\tnot_relevant\tpass\tfail\tmissing\t\t"
                                        "Product Manager\t\t\ttext\tno")
        self.assertEqual(by_id["4002"], f"{GH}\t4002\tAssociate Product Manager\tRemote\trelevant\tpass\tpass\tpass\t2\t"
                                        "Associate Product Manager; Product Manager\tRemote\tPython; SQL\t\tyes")
        self.assertEqual(by_id["c-ab-01"], f"{AB}\tc-ab-01\tProduct Manager\tRemote\trelevant\tpass\tpass\tpass\t5\t"
                                           "Product Manager\tRemote\tPython; SQL; A/B testing; roadmapping; "
                                           "user research\t\tno")
        self.assertEqual(by_id["5003"].split("\t")[4:9], ["not_relevant", "fail", "pass", "pass", "3"])

    def test_latest_copy_wins(self):
        row = {r["id"]: r for r in self.fx.rows("verdicts.tsv")}["4001"]
        self.assertEqual((row["title"], row["verdict"], row["score"]), ("Late Title Product Manager", "relevant", "4"))

    def test_shortlist_in_f8_order_with_positions(self):
        rows = self.fx.rows("shortlist.tsv")
        self.assertEqual(self.fx.read("shortlist.tsv").splitlines()[0], "position\t" + HEADER)
        self.assertEqual([(r["position"], r["id"], r["score"]) for r in rows],
                         [("1", "c-ab-01", "5"), ("2", "4001", "4"), ("3", "5002", "3"),
                          ("4", "c-ab-05", "2"), ("5", "4002", "2"), ("6", "5001", "2")])
        self.assertTrue(all(r["verdict"] == "relevant" for r in rows))

    def test_cannot_tell_names_the_missing_fields(self):
        self.assertEqual([(r["board_key"], r["id"], r["missing"]) for r in self.fx.rows("cannot_tell.tsv")],
                         [(AB, "c-ab-04", "location"), (GH, "5004", "location")])

    def test_closest_calls(self):
        self.assertEqual([r["id"] for r in self.fx.rows("closest_calls.tsv")],
                         ["5003", "c-ab-02", "c-ab-05", "4002", "5001", "c-ab-03"])
        self.assertTrue(all(r["closest_call"] == "yes" and r["missing"] == "" for r in self.fx.rows("closest_calls.tsv")))

    def test_refuses_to_overwrite(self):
        before = {p.name: p.read_bytes() for p in self.fx.folder.iterdir()}
        code, out, err = self.fx.run()
        self.assertEqual((code, out), (1, ""))
        self.assertIn(f"refusing to overwrite: output/{FOLDER}/", err)
        self.assertEqual({p.name: p.read_bytes() for p in self.fx.folder.iterdir()}, before)


class TestStops(unittest.TestCase):
    """Every stop writes nothing: no output/ folder appears."""

    def assert_stops(self, fx, needle):
        code, out, err = fx.run()
        self.assertEqual((code, out), (1, ""), err)
        self.assertIn(needle, err)
        self.assertFalse((fx.root / "output").exists())
        for _, posting_id in SEALED_FINAL + SEALED_V2:
            self.assertNotIn(posting_id, err)
        return err

    def test_hash_mismatch_stops_before_judging(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            path = fx.root / "corpus/ab.json"
            path.write_bytes(path.read_bytes() + b" ")
            with mock.patch.object(filter_run.filter_v1, "judge") as judge:
                self.assert_stops(fx, "corpus/ab.json: SHA-256 does not match vault/corpus_manifest.tsv")
                judge.assert_not_called()

    def test_file_not_in_manifest_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.write_manifest(rels={"corpus/gh_late.json", "corpus/ab.json"})
            self.assert_stops(fx, "corpus/gh_early.json: not listed in vault/corpus_manifest.tsv")

    def test_manifest_file_not_in_corpus_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            manifest = fx.root / "vault/corpus_manifest.tsv"
            manifest.write_text(manifest.read_text() + "corpus/other.json\tx\ty\t" + "0" * 64 + "\t0\t0\ta\tb\n")
            self.assert_stops(fx, "corpus/other.json: listed in vault/corpus_manifest.tsv but not in the corpus")

    def test_missing_corpus_file_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            (fx.root / "corpus/gh_early.json").unlink()
            self.assert_stops(fx, "corpus file missing or unreadable: corpus/gh_early.json")

    def test_unexpected_shape_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.write("corpus/ab.json", json.dumps({"status": 404}))
            fx.write_manifest()
            self.assert_stops(fx, "corpus file is not the board's job list: corpus/ab.json")

    def test_sealed_posting_not_in_corpus_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.write("vault/js3_heldout_ids_v2.tsv", seal_file(SEALED_V2 + [(GH, "7999999")]))
            self.assert_stops(fx, "a sealed posting is not in the corpus")

    def test_edited_sealed_file_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            path = fx.root / "vault/final_heldout_ids.tsv"
            path.write_text(path.read_text().replace(seal_draw.rank(*SEALED_FINAL[0]), "0" * 64))
            self.assert_stops(fx, "vault/final_heldout_ids.tsv line 2: rank")

    def test_refused_persona_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            persona = json.loads((fx.root / "resume_persona.json").read_text())
            fx.write("resume_persona.json", json.dumps(dict(persona, email="someone@university.invalid")))
            self.assert_stops(fx, "résumé refused")

    def test_rule_py_disagreement_stops_and_writes_nothing(self):
        real = filter_run.filter_v1.judge

        def flipped(posting, persona):
            record = real(posting, persona)
            if not record["missing"] and record["verdict"] == "relevant":
                record["verdict"] = "not_relevant"
            return record

        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            with mock.patch.object(filter_run.filter_v1, "judge", flipped):
                self.assert_stops(fx, "rule.py cross-check failed: 6 postings with no missing field disagree")


class TestConstants(unittest.TestCase):
    def test_defaults(self):
        defaults = {name: p.default for name, p in __import__("inspect").signature(filter_run.main).parameters.items()}
        self.assertIs(defaults["corpus"], seal_draw.CORPUS)
        self.assertEqual(defaults["root"], PROJECT)
        self.assertEqual(filter_run.SEALED_FILES, ("final_heldout_ids.tsv", "js3_heldout_ids_v2.tsv"))


if __name__ == "__main__":
    unittest.main()
