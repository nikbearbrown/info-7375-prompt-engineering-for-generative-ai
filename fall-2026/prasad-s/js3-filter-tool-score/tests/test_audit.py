"""Tests for tools/audit.py. Constructed corpus, constructed vault, temporary folders only.

The fixture runs the real tools/filter_run.py on a constructed corpus, with
its clock set so it writes exactly output/filter_v1_2026-11-17T210612Z/, the
run audit.py reads. No test reads the real corpus, the real vault/ or the
real run, and no test writes outside its temporary folder.
"""

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from support import JS1 as PROJECT

from tools import audit, filter_run, seal_draw

GH = "greenhouse:constructedgh"
AB = "ashby:constructedab"
RUN_TIME = datetime(2026, 11, 17, 21, 6, 12, tzinfo=timezone.utc)
COMPARE_TIME = datetime(2026, 11, 19, 9, 30, 0, tzinfo=timezone.utc)
COMPARE = "compare_2026-11-19T093000Z"
SEED = "js3-audit-2026-11-18"

# Constructed postings; every one is not_relevant under FILTER v1.
PLAIN = [(GH, str(6000 + i)) for i in range(40)]      # C1 fail, C2 fail, score 0
B_ONLY = [(AB, f"c-b-{i:02d}") for i in range(5)]      # C1 fail, C2 pass, score 2: closest calls
B_AND_C = [(GH, str(6100 + i)) for i in range(3)]      # C1 pass, C2 pass, score 1: closest calls
C_ONLY = [(GH, str(6200 + i)) for i in range(4)]       # C1 pass, C2 pass, score 0
FINAL = [(GH, "7100001")]
V2 = [(GH, "7200001")]
EXPOSED = [(AB, "c-b-01"), (GH, "6100"), (GH, "6005")]
JUDGED = PLAIN + B_ONLY + B_AND_C + C_ONLY


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# The audit list, computed here independently of audit.py (AUDIT.md §2-§4).
GROUP_A = set(sorted(JUDGED, key=lambda key: sha(f"{SEED}:{key[0]}:{key[1]}"))[:30])
GROUP_B = set(B_ONLY + B_AND_C)
GROUP_C = set(B_AND_C + C_ONLY)
LIST = sorted(GROUP_A | GROUP_B | GROUP_C, key=lambda key: sha(f"{SEED}:order:{key[0]}:{key[1]}"))
N = len(LIST)
ALL_IDS = [i for _, i in JUDGED + FINAL + V2]


def gh_job(posting_id, title, location, text):
    return {"id": int(posting_id), "title": title, "location": {"name": location},
            "content": f"&lt;p&gt;{text}&lt;/p&gt;", "updated_at": "2026-01-05T10:00:00-05:00",
            "absolute_url": f"https://example.invalid/{posting_id}", "departments": [{"name": "Dept-Zeta"}]}


def gh_jobs():
    jobs = [gh_job(i, f"Constructed Engineer {i}", "Constructed City", f"Java and Go, item {i}.") for _, i in PLAIN]
    jobs += [gh_job(i, f"Product Manager, Constructed {n}", "Remote", f"Python first, then Python again, item {n}.")
             for n, (_, i) in enumerate(B_AND_C)]
    jobs += [gh_job(i, f"Product Analyst, Constructed {n}", "NYC", f"A plain constructed body, item {n}.")
             for n, (_, i) in enumerate(C_ONLY)]
    jobs += [gh_job(i, "SEALED-TITLE Product Manager", "New York", "SEALED-TEXT Python SQL") for _, i in FINAL + V2]
    return jobs


def ab_jobs():
    return [{"id": i, "title": f"Constructed Designer {n}", "location": "New York", "secondaryLocations": [],
             "descriptionPlain": f"Python and SQL, item {n}.", "compensation": {"summary": "$999K"}}
            for n, (_, i) in enumerate(B_ONLY)]


def seal_file(keys):
    return "\n".join(["board_key\tid\tgroup\trank"]
                     + [f"{b}\t{i}\tproduct\t{seal_draw.rank(b, i)}" for b, i in keys]) + "\n"


class Fixture:
    def __init__(self, tmp):
        self.root = Path(tmp)
        self.corpus = [(GH, "corpus/gh.json", "2026-01-01T00:00:00Z"), (AB, "corpus/ab.json", "2026-01-01T00:00:00Z")]
        self.write("corpus/gh.json", json.dumps({"jobs": gh_jobs()}))
        self.write("corpus/ab.json", json.dumps({"jobs": ab_jobs()}))
        manifest = ["path\tboard_key\tutc_time\tsha256\tjobs\tunique_ids\tsha256sums_check\tsidecar_check"]
        for board, rel, utc in self.corpus:
            digest = hashlib.sha256((self.root / rel).read_bytes()).hexdigest()
            manifest.append(f"{rel}\t{board}\t{utc}\t{digest}\t0\t0\tnot listed\tno sidecar")
        self.write("vault/corpus_manifest.tsv", "\n".join(manifest) + "\n")
        self.write("vault/final_heldout_ids.tsv", seal_file(FINAL))
        self.write("vault/js3_heldout_ids_v2.tsv", seal_file(V2))
        self.write("vault/js3_heldout_ids.tsv", seal_file(EXPOSED))
        shutil.copy(PROJECT / "resume_persona.json", self.root / "resume_persona.json")
        out, err = io.StringIO(), io.StringIO()
        code = filter_run.main([], root=self.root, corpus=self.corpus, now=RUN_TIME, out=out, err=err)
        assert code == 0, err.getvalue()
        assert (self.root / audit.RUN).is_dir()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run(self, *argv, now=COMPARE_TIME):
        out, err = io.StringIO(), io.StringIO()
        code = audit.main(list(argv), root=self.root, corpus=self.corpus, now=now, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def drawn(self):
        code, _, err = self.run("draw")
        assert code == 0, err
        return self

    def list_rows(self):
        lines = (self.root / "audit/audit_list.tsv").read_text(encoding="utf-8").splitlines()
        return [dict(zip(lines[0].split("\t"), line.split("\t"))) for line in lines[1:]]

    def snapshot(self):
        return {(str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in self.root.rglob("*")}


def leaked(text):
    return [i for i in ALL_IDS if i in text]


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def assert_refused(self, result, needle, code=1):
        got_code, out, err = result
        self.assertEqual((got_code, out), (code, ""), err)
        self.assertIn(needle, err)
        self.assertEqual(leaked(err), [])
        return err


# ---------------------------------------------------------------- draw

class TestDraw(Case):
    def test_the_list_file(self):
        self.fx.drawn()
        rows = self.fx.list_rows()
        self.assertEqual(list(rows[0]), ["position", "board_key", "id", "in_A", "in_B", "in_C", "in_exposed"])
        yes = lambda flag: "yes" if flag else "no"  # noqa: E731
        self.assertEqual(rows, [{"position": str(p), "board_key": b, "id": i, "in_A": yes((b, i) in GROUP_A),
                                 "in_B": yes((b, i) in GROUP_B), "in_C": yes((b, i) in GROUP_C),
                                 "in_exposed": yes((b, i) in EXPOSED)} for p, (b, i) in enumerate(LIST, start=1)])

    def test_group_a_is_the_30_lowest_ranks_among_the_rejects(self):
        self.fx.drawn()
        in_a = {(r["board_key"], r["id"]) for r in self.fx.list_rows() if r["in_A"] == "yes"}
        self.assertEqual(len(in_a), 30)
        ranks = sorted(sha(f"{SEED}:{b}:{i}") for b, i in JUDGED)
        self.assertEqual(sorted(sha(f"{SEED}:{b}:{i}") for b, i in in_a), ranks[:30])
        self.assertEqual(audit.a_rank(*JUDGED[0]), sha(f"{SEED}:{JUDGED[0][0]}:{JUDGED[0][1]}"))

    def test_group_a_draws_from_not_relevant_postings_only(self):
        # Every posting in FILTER v1's run is a reject; here the three lowest-ranked plain ones are made
        # relevant or cannot_tell, as in some other run, and group (A) must pass over them.
        rank = lambda key: sha(f"{SEED}:{key[0]}:{key[1]}")  # noqa: E731
        lowest = sorted(PLAIN, key=rank)[:3]
        path = self.fx.root / audit.RUN / "verdicts.tsv"
        lines = path.read_text(encoding="utf-8").splitlines()
        for key, verdict in zip(lowest, ("relevant", "relevant", "cannot_tell")):
            at = next(n for n, line in enumerate(lines) if line.startswith(f"{key[0]}\t{key[1]}\t"))
            lines[at] = lines[at].replace("\tnot_relevant\t", f"\t{verdict}\t", 1)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.fx.drawn()
        in_a = {(r["board_key"], r["id"]) for r in self.fx.list_rows() if r["in_A"] == "yes"}
        self.assertEqual(in_a, set(sorted(set(JUDGED) - set(lowest), key=rank)[:30]))

    def test_group_b_is_every_closest_call_and_c_every_double_pass(self):
        self.fx.drawn()
        rows = self.fx.list_rows()
        self.assertEqual({(r["board_key"], r["id"]) for r in rows if r["in_B"] == "yes"}, GROUP_B)
        self.assertEqual({(r["board_key"], r["id"]) for r in rows if r["in_C"] == "yes"}, GROUP_C)
        closest = (self.fx.root / audit.RUN / "closest_calls.tsv").read_text().splitlines()[1:]
        self.assertEqual({tuple(line.split("\t")[:2]) for line in closest}, GROUP_B)

    def test_each_posting_once_and_overlaps_counted_in_each_group(self):
        self.fx.drawn()
        rows = self.fx.list_rows()
        keys = [(r["board_key"], r["id"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        for key in B_AND_C:
            row = rows[keys.index(key)]
            self.assertEqual((row["in_B"], row["in_C"]), ("yes", "yes"))

    def test_order_follows_the_order_hash(self):
        self.fx.drawn()
        keys = [(r["board_key"], r["id"]) for r in self.fx.list_rows()]
        self.assertEqual(keys, LIST)
        self.assertEqual(audit.order_rank(*LIST[0]), sha(f"{SEED}:order:{LIST[0][0]}:{LIST[0][1]}"))
        # not the group-(A) rank, and not grouped: the order hash is a different hash
        self.assertNotEqual(keys, sorted(keys, key=lambda key: sha(f"{SEED}:{key[0]}:{key[1]}")))
        flags = [key in GROUP_A for key in keys]
        self.assertNotEqual(flags, sorted(flags, reverse=True))

    def test_counts_only(self):
        code, out, err = self.fx.run("draw")
        self.assertEqual(code, 0, err)
        a, b, c = GROUP_A, GROUP_B, GROUP_C
        exposed = len(set(EXPOSED) & set(LIST))
        self.assertEqual(out, f"JS3 reject audit list (AUDIT.md v1), from {audit.RUN}/. Counts only: no ids.\n"
                              f"group A (random rejects): 30 of {len(JUDGED)} not_relevant postings\n"
                              f"group B (closest calls): {len(b)}\n"
                              f"group C (both gates pass): {len(c)}\n"
                              f"overlaps: A and B {len(a & b)}, A and C {len(a & c)}, B and C {len(b & c)}, "
                              f"all three {len(a & b & c)}\n"
                              f"audit list: {N} postings, each once\n"
                              f"exposed postings on the list (SEAL.md §8): {exposed}\n"
                              f"written to: audit/audit_list.tsv\n")
        self.assertEqual(leaked(out), [])
        self.assertEqual((len(b & c), exposed >= 2), (3, True))

    def test_the_seed_is_a_constant_with_no_option(self):
        self.assertEqual(audit.SEED, SEED)
        self.assert_refused(self.fx.run("draw", "--seed", "other"), "not a valid command line", code=2)
        self.assertFalse((self.fx.root / "audit").exists())


class TestDrawRefusals(Case):
    def assert_nothing_written(self, needle):
        self.assert_refused(self.fx.run("draw"), needle)
        self.assertFalse((self.fx.root / "audit").exists())

    def edit_verdicts(self, change):
        path = self.fx.root / audit.RUN / "verdicts.tsv"
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(change(lines)) + "\n", encoding="utf-8")

    def test_refuses_to_overwrite(self):
        self.fx.drawn()
        before = (self.fx.root / "audit/audit_list.tsv").read_bytes()
        self.assert_refused(self.fx.run("draw"), "refusing to overwrite: audit/audit_list.tsv")
        self.assertEqual((self.fx.root / "audit/audit_list.tsv").read_bytes(), before)

    def test_refuses_a_sealed_posting_in_the_run(self):
        plain = f"{PLAIN[0][0]}\t{PLAIN[0][1]}\t"
        for board, posting_id in FINAL + V2:
            with self.subTest(posting_id=posting_id), tempfile.TemporaryDirectory() as tmp:
                self.fx = Fixture(tmp)
                # a copy of a plain reject's row under the sealed posting's key (closest_call stays "no")
                self.edit_verdicts(lambda lines: lines + [next(line for line in lines if line.startswith(plain))
                                                          .replace(plain, f"{board}\t{posting_id}\t", 1)])
                self.assert_nothing_written("the final's set or JS3's held-out set")

    def test_refuses_when_closest_calls_and_verdicts_disagree(self):
        path = self.fx.root / audit.RUN / "closest_calls.tsv"
        path.write_text("\n".join(path.read_text().splitlines()[:-1]) + "\n")
        self.assert_nothing_written("closest_calls.tsv does not match")

    def test_refuses_fewer_than_30_rejects(self):
        keep = {f"{GH}\t{i}\t" for _, i in PLAIN[:10]} | {f"{b}\t{i}\t" for b, i in B_ONLY + B_AND_C + C_ONLY}
        self.edit_verdicts(lambda lines: lines[:1] + [l for l in lines[1:] if any(l.startswith(k) for k in keep)])
        self.assert_nothing_written("the run has 22 not_relevant postings; group (A) needs 30")

    def test_refuses_without_the_run(self):
        shutil.rmtree(self.fx.root / audit.RUN)
        self.assert_nothing_written(f"cannot read {audit.RUN}/verdicts.tsv")

    def test_refuses_an_edited_sealed_file(self):
        path = self.fx.root / "vault/js3_heldout_ids_v2.tsv"
        path.write_text(path.read_text().replace(seal_draw.rank(*V2[0]), "0" * 64))
        self.assert_nothing_written("vault/js3_heldout_ids_v2.tsv line 2: rank")


class TestListIntegrity(Case):
    def commands(self):
        labels = str(self.fx.root / "labels.tsv")
        self.fx.write("labels.tsv", "x\n")
        return (("show", "1"), ("template",), ("check", labels), ("compare", labels))

    def test_every_command_refuses_before_draw(self):
        for argv in self.commands():
            with self.subTest(argv=argv):
                self.assert_refused(self.fx.run(*argv), "run draw first")

    def test_every_command_refuses_an_edited_list(self):
        self.fx.drawn()
        path = self.fx.root / "audit/audit_list.tsv"
        lines = path.read_text().splitlines()
        lines[1], lines[2] = lines[2], lines[1]  # two rows swapped
        path.write_text("\n".join(lines) + "\n")
        self.fx.write("audit/compare_2026-11-18T000000Z/summary.txt", "constructed\n")  # an earlier compare, so context gets past its own refusal
        for argv in self.commands() + (("context", "1"),):
            with self.subTest(argv=argv):
                self.assert_refused(self.fx.run(*argv), "does not match the list re-derived")


# ---------------------------------------------------------------- show and template

class TestShow(Case):
    def test_exactly_the_posting_s_own_text(self):
        self.fx.drawn()
        key = B_AND_C[0]
        code, out, err = self.fx.run("show", str(LIST.index(key) + 1))
        self.assertEqual(code, 0, err)
        self.assertEqual(out, f"board_key: {GH}\nid: 6100\ntitle: Product Manager, Constructed 0\nlocation: Remote\n"
                              f"text:\nPython first, then Python again, item 0.\n")

    def test_blind_on_every_position(self):
        self.fx.drawn()
        forbidden = ("group", "in_a", "in_b", "in_c", "exposed", "verdict", "relevant", "pass", "fail", "missing",
                     "score", "closest", "match", "c1", "c2", "c3", "rank", "yes", "http", "dept-zeta", "$999",
                     "2026-01-05", "audit")
        for p, key in enumerate(LIST, start=1):
            code, out, err = self.fx.run("show", str(p))
            with self.subTest(position=p):
                self.assertEqual(code, 0, err)
                self.assertEqual([line.split(":", 1)[0] for line in out.splitlines()[:5]],
                                 ["board_key", "id", "title", "location", "text"])
                lowered = out.lower()
                for word in forbidden:
                    self.assertNotIn(word, lowered)
                self.assertNotIn(sha(f"{SEED}:{key[0]}:{key[1]}"), out)

    def test_a_position_only(self):
        self.fx.drawn()
        cases = [(LIST[0][1], "an id on the audit list"), (FINAL[0][1], "an id in the final's set"),
                 (V2[0][1], "an id in JS3's held-out set"), ("999999", f"not a position 1-{N}"),
                 ("0", f"not a position 1-{N}"), (str(N + 1), f"not a position 1-{N}"), ("abc", "not a position")]
        for arg, kind in cases:
            with self.subTest(arg=arg):
                err = self.assert_refused(self.fx.run("show", arg), kind)
                if len(arg) > 2:
                    self.assertNotIn(arg, err)


class TestTemplate(Case):
    def test_template(self):
        self.fx.drawn()
        before = self.fx.snapshot()
        code, out, err = self.fx.run("template")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.fx.snapshot(), before)
        lines = out.splitlines()
        self.assertEqual(lines[0], "position\tboard_key\tid\tverdict\tparts\tevidence")
        self.assertEqual(lines[1:], [f"{p}\t{b}\t{i}\t\t\t" for p, (b, i) in enumerate(LIST, start=1)])
        self.assertNotIn("yes", out)


# ---------------------------------------------------------------- hand verdicts

def hand_labels():
    """{key: (verdict, parts)}: a constructed labeling with worth, unclear and every false-friend shape."""
    labels = {key: ("not_worth", "role, location") for key in LIST}
    labels.update({
        B_AND_C[0]: ("not_worth", "role"),             # C1 passed, hand failed role: candidate
        B_AND_C[1]: ("not_worth", "level, location"),  # C1 passed (level) and C2 passed (location): candidate
        B_AND_C[2]: ("unclear", "location"),           # unclear names an undecidable part: never a candidate
        C_ONLY[0]: ("worth", "-"),
        C_ONLY[1]: ("not_worth", "role"),              # candidate
        C_ONLY[2]: ("not_worth", "location"),          # candidate
        C_ONLY[3]: ("not_worth", "level"),             # candidate
        B_ONLY[0]: ("worth", "-"),
        B_ONLY[1]: ("not_worth", "role"),              # C1 failed by rule too: not a candidate
        B_ONLY[2]: ("not_worth", "location"),          # C2 passed: candidate
        B_ONLY[3]: ("unclear", "role"),
        B_ONLY[4]: ("not_worth", "role,level"),        # C1 failed, location not failed: not a candidate
    })
    plain_in_a = [key for key in LIST if key in GROUP_A and key in PLAIN]
    for key in plain_in_a[:2]:
        labels[key] = ("worth", "-")
    labels[plain_in_a[2]] = ("unclear", "location")
    return labels


CANDIDATES = {
    B_AND_C[0]: "C1 passed; hand failed role",
    B_AND_C[1]: "C1 passed; hand failed level; C2 passed; hand failed location",
    C_ONLY[1]: "C1 passed; hand failed role",
    C_ONLY[2]: "C2 passed; hand failed location",
    C_ONLY[3]: "C1 passed; hand failed level",
    B_ONLY[2]: "C2 passed; hand failed location",
}


def valid_rows():
    labels = hand_labels()
    return [[str(p), b, i, *labels[(b, i)], f"title: SECRET-QUOTE {p}"] for p, (b, i) in enumerate(LIST, start=1)]


def labels_text(rows=None):
    rows = valid_rows() if rows is None else rows
    return "\n".join(["position\tboard_key\tid\tverdict\tparts\tevidence"] + ["\t".join(row) for row in rows]) + "\n"


class TestCheck(Case):
    def check(self, text):
        self.fx.write("elsewhere/hand.tsv", text)
        path = self.fx.root / "elsewhere/hand.tsv"
        before = path.read_bytes()
        result = self.fx.run("check", str(path))
        self.assertEqual(path.read_bytes(), before)
        self.assertNotIn("SECRET-QUOTE", result[1] + result[2])
        self.assertEqual(leaked(result[1] + result[2]), [])
        return result

    def test_valid_file_is_ok(self):
        self.fx.drawn()
        self.assertEqual(self.check(labels_text())[:2], (0, "ok\n"))

    def test_each_kind_of_bad_file_names_no_id(self):
        self.fx.drawn()

        def cell(position, column, value):
            def apply(rows):
                rows[position - 1][column] = value
                return rows
            return apply

        cases = {
            "missing row": (lambda rows: rows[:4] + rows[5:], "position 5: no row"),
            "duplicate": (lambda rows: rows + [list(rows[1])], "position 2 is already on line 3"),
            "position past N": (cell(3, 0, str(N + 1)), f"position is not a whole number 1-{N}"),
            "another audit posting": (lambda rows: cell(3, 2, rows[7][2])(cell(3, 1, rows[7][1])(rows)),
                                      "do not match the audit list at this position"),
            "a final's id": (lambda rows: cell(3, 2, FINAL[0][1])(cell(3, 1, GH)(rows)), "names an id in the final's set"),
            "a v2 id": (lambda rows: cell(3, 2, V2[0][1])(cell(3, 1, GH)(rows)), "names an id in JS3's held-out set"),
            "bad verdict": (cell(3, 3, "maybe"), "verdict is not one of worth, not_worth, unclear"),
            "worth with parts": (lambda rows: cell(3, 4, "role")(cell(3, 3, "worth")(rows)), "parts must be - for worth"),
            "unknown part": (lambda rows: cell(3, 4, "skills")(cell(3, 3, "not_worth")(rows)), "parts must list"),
            "empty evidence": (cell(3, 5, " "), "evidence is empty"),
            "tab in evidence": (cell(3, 5, f"{LIST[2][1]}\tSECRET-QUOTE"), "7 columns"),
        }
        for name, (mutate, needle) in cases.items():
            with self.subTest(case=name):
                code, out, _ = self.check(labels_text(rows=mutate(valid_rows())))
                self.assertEqual(code, 1, out)
                self.assertIn(needle, out)

    def test_empty_file(self):
        self.fx.drawn()
        code, out, _ = self.check("")
        self.assertEqual((code, len(out.splitlines())), (1, N + 1))  # the header and every position

    def test_unreadable_path_is_not_repeated(self):
        self.fx.drawn()
        err = self.assert_refused(self.fx.run("check", str(self.fx.root / f"hand_{LIST[0][1]}.tsv")), "cannot read")
        self.assertNotIn("hand_", err)


# ---------------------------------------------------------------- compare

class TestCompare(Case):
    def compared(self):
        self.fx.drawn()
        self.fx.write("audit/hand.tsv", labels_text())
        return self.fx.run("compare", str(self.fx.root / "audit/hand.tsv"))

    def read(self, name):
        return (self.fx.root / "audit" / COMPARE / name).read_text(encoding="utf-8")

    def tsv(self, name):
        lines = self.read(name).splitlines()
        return [dict(zip(lines[0].split("\t"), line.split("\t"))) for line in lines[1:]]

    def test_writes_three_files_and_prints_the_summary_only(self):
        code, out, err = self.compared()
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(p.name for p in (self.fx.root / "audit" / COMPARE).iterdir()),
                         ["false_friend_candidates.tsv", "rows.tsv", "summary.txt"])
        self.assertEqual(out, self.read("summary.txt"))
        self.assertEqual(leaked(out), [])

    def test_rows(self):
        self.compared()
        rows = self.tsv("rows.tsv")
        labels = hand_labels()
        verdicts = {(r["board_key"], r["id"]): r for r in
                    (dict(zip(filter_run.COLUMNS, line.split("\t")))
                     for line in (self.fx.root / audit.RUN / "verdicts.tsv").read_text().splitlines()[1:])}
        self.assertEqual(self.read("rows.tsv").splitlines()[0].split("\t")[:6],
                         ["position", "board_key", "id", "title", "location", "in_A"])
        self.assertEqual([(r["board_key"], r["id"]) for r in rows], LIST)
        for p, row in enumerate(rows, start=1):
            key = (row["board_key"], row["id"])
            rule = verdicts[key]
            with self.subTest(position=p):
                self.assertEqual(row["position"], str(p))
                self.assertEqual((row["title"], row["location"]), (rule["title"], rule["location"]))
                self.assertEqual([row[c] for c in ("in_A", "in_B", "in_C", "in_exposed")],
                                 ["yes" if key in s else "no" for s in (GROUP_A, GROUP_B, GROUP_C, set(EXPOSED))])
                self.assertEqual([row[c] for c in ("rule_verdict", "C1", "C2", "C3", "score", "title_match",
                                                   "location_match", "skills_found")],
                                 [rule[c] for c in ("verdict", "C1", "C2", "C3", "score", "title_match",
                                                    "location_match", "skills_found")])
                self.assertEqual((row["hand_verdict"], row["hand_parts"], row["hand_evidence"]),
                                 (*labels[key], f"title: SECRET-QUOTE {p}"))
                self.assertEqual(row["wrong"], "yes" if labels[key][0] == "worth" else "no")

    def test_false_friend_candidates_are_not_worth_rows_only(self):
        self.compared()
        rows = self.tsv("false_friend_candidates.tsv")
        self.assertEqual({(r["board_key"], r["id"]): r["candidate_because"] for r in rows}, CANDIDATES)
        self.assertTrue(all(r["hand_verdict"] == "not_worth" for r in rows))
        self.assertEqual([(r["board_key"], r["id"]) for r in rows], [k for k in LIST if k in CANDIDATES])
        self.assertEqual(self.read("false_friend_candidates.tsv").splitlines()[0].split("\t")[3:5],
                         ["title", "location"])
        by_key = {(r["board_key"], r["id"]): r for r in rows}
        self.assertEqual((by_key[B_AND_C[1]]["title"], by_key[B_AND_C[1]]["location"]),
                         ("Product Manager, Constructed 1", "Remote"))
        self.assertEqual((by_key[B_ONLY[2]]["title"], by_key[B_ONLY[2]]["location"]),
                         ("Constructed Designer 2", "New York"))

    def test_no_body_text_in_any_compare_file(self):
        self.compared()
        bodies = ["Java and Go", "Python first, then Python again", "A plain constructed body", "Python and SQL, item"]
        for name in ("rows.tsv", "false_friend_candidates.tsv", "summary.txt"):
            text = self.read(name)
            for body in bodies:
                self.assertNotIn(body, text, name)

    def test_summary(self):
        code, out, err = self.compared()
        self.assertEqual(code, 0, err)
        labels = hand_labels()

        def counts(keys):
            v = [labels[k][0] for k in keys]
            return len(v), v.count("worth"), v.count("unclear"), v.count("not_worth")

        n_a, wrong_a, unclear_a, confirmed_a = counts(GROUP_A)
        lower, upper = audit.clopper_pearson(wrong_a, n_a)
        lines = [f"JS3 reject audit (AUDIT.md v1) of {audit.RUN}/. Counts only: no ids.",
                 f"audited postings: {N}, each labeled once and counted in every group it is in",
                 f"group A (random rejects): n {n_a}, wrong (worth) {wrong_a}, unclear {unclear_a}, "
                 f"confirmed (not_worth) {confirmed_a}",
                 f"  rate of wrong rejects: {wrong_a}/{n_a} = {100 * wrong_a / n_a:.1f}%; exact Clopper-Pearson "
                 f"95% interval {100 * lower:.1f}% to {100 * upper:.1f}%"]
        for g, name, keys in (("B", "closest calls", GROUP_B), ("C", "both gates pass", GROUP_C)):
            n, wrong, unclear, confirmed = counts(keys)
            lines += [f"group {g} ({name}): n {n}, wrong (worth) {wrong}, unclear {unclear}, "
                      f"confirmed (not_worth) {confirmed}", "  chosen, not random: counts only, no rate (AUDIT.md §5)"]
        n, wrong, unclear, confirmed = counts(LIST)
        lines += [f"all audited: n {n}, wrong (worth) {wrong}, unclear {unclear}, confirmed (not_worth) {confirmed}",
                  f"exposed postings audited (SEAL.md §8): {len(set(EXPOSED) & set(LIST))}",
                  f"false-friend candidates: {len(CANDIDATES)}",
                  f"written to: audit/{COMPARE}/"]
        self.assertEqual(out, "\n".join(lines) + "\n")
        # the hand-computed numbers behind it
        self.assertEqual(counts(GROUP_B), (8, 1, 2, 5))
        self.assertEqual(counts(GROUP_C), (7, 1, 1, 5))
        self.assertGreaterEqual(wrong_a, 2)
        self.assertEqual(n_a, wrong_a + unclear_a + confirmed_a)

    def test_refuses_unless_check_passes(self):
        self.fx.drawn()
        rows = valid_rows()
        rows[0][3] = "maybe"
        self.fx.write("audit/hand.tsv", labels_text(rows=rows))
        self.assert_refused(self.fx.run("compare", str(self.fx.root / "audit/hand.tsv")),
                            "does not pass check (1 problems")
        self.assertFalse((self.fx.root / "audit" / COMPARE).exists())

    def test_refuses_to_overwrite(self):
        self.compared()
        before = {p.name: p.read_bytes() for p in (self.fx.root / "audit" / COMPARE).iterdir()}
        self.assert_refused(self.fx.run("compare", str(self.fx.root / "audit/hand.tsv")),
                            f"refusing to overwrite: audit/{COMPARE}/")
        self.assertEqual({p.name: p.read_bytes() for p in (self.fx.root / "audit" / COMPARE).iterdir()}, before)


# ---------------------------------------------------------------- context

class TestContext(Case):
    def test_refuses_before_compare(self):
        self.fx.drawn()
        self.assert_refused(self.fx.run("context", "1"), "context runs only after compare")
        (self.fx.root / "audit" / COMPARE).mkdir()  # an empty folder is not a finished compare
        self.assert_refused(self.fx.run("context", "1"), "context runs only after compare")

    def test_matched_terms_in_their_own_field(self):
        self.fx.drawn()
        self.fx.write("audit/hand.tsv", labels_text())
        self.assertEqual(self.fx.run("compare", str(self.fx.root / "audit/hand.tsv"))[0], 0)
        code, out, err = self.fx.run("context", str(LIST.index(B_AND_C[0]) + 1))
        self.assertEqual(code, 0, err)
        self.assertEqual(out, f"board_key: {GH}\nid: 6100\n"
                              'title term (C1) "Product Manager", in the title: 1 place\n'
                              "  [Product Manager], Constructed 0\n"
                              'location term (C2) "Remote", in the location: 1 place\n'
                              "  [Remote]\n"
                              'skill (C3) "Python", in the text: 2 places\n'
                              "  [Python] first, then Python again, item 0.\n"
                              "  Python first, then [Python] again, item 0.\n")
        code, out, err = self.fx.run("context", str(LIST.index(B_ONLY[0]) + 1))
        self.assertIn("title term (C1): none matched\n", out)
        self.assertIn('skill (C3) "SQL", in the text: 1 place\n  Python and [SQL], item 0.\n', out)

    def test_context_is_about_80_characters(self):
        text = "a" * 100 + " Python " + "b" * 100
        (snippet,) = audit.snippets("python", text)
        self.assertEqual(snippet, "…" + "a" * 39 + " [Python] " + "b" * 39 + "…")
        self.assertEqual(audit.snippets("SQL", "no skill here"), [])

    def test_a_position_only(self):
        self.fx.drawn()
        self.fx.write(f"audit/{COMPARE}/summary.txt", "constructed\n")
        err = self.assert_refused(self.fx.run("context", LIST[0][1]), "an id on the audit list")
        self.assertNotIn(LIST[0][1], err)


# ---------------------------------------------------------------- Clopper-Pearson

class TestClopperPearson(unittest.TestCase):
    def test_k_zero_matches_the_closed_form(self):
        for n in (1, 2, 5, 30, 100):
            with self.subTest(n=n):
                lower, upper = audit.clopper_pearson(0, n)
                self.assertEqual(lower, 0.0)
                self.assertAlmostEqual(upper, 1 - 0.025 ** (1 / n), places=12)

    def test_k_equals_n(self):
        for n in (1, 2, 5, 30, 100):
            with self.subTest(n=n):
                lower, upper = audit.clopper_pearson(n, n)
                self.assertEqual(upper, 1.0)
                self.assertAlmostEqual(lower, 0.025 ** (1 / n), places=12)

    def test_symmetry(self):
        for n in (1, 7, 30):
            for k in range(n + 1):
                with self.subTest(n=n, k=k):
                    self.assertAlmostEqual(audit.clopper_pearson(k, n)[0], 1 - audit.clopper_pearson(n - k, n)[1],
                                           places=12)

    def test_audit_md_s_example_and_a_textbook_value(self):
        self.assertEqual(f"{100 * audit.clopper_pearson(0, 30)[1]:.1f}%", "11.6%")  # AUDIT.md §5
        lower, upper = audit.clopper_pearson(3, 10)
        self.assertAlmostEqual(lower, 0.06674, places=4)
        self.assertAlmostEqual(upper, 0.65245, places=4)

    def test_tails_hold_alpha_over_two(self):
        for k, n in ((1, 30), (4, 30), (29, 30)):
            lower, upper = audit.clopper_pearson(k, n)
            self.assertAlmostEqual(1 - audit.binomial_cdf(k - 1, n, lower), 0.025, places=12)
            self.assertAlmostEqual(audit.binomial_cdf(k, n, upper), 0.025, places=12)

    def test_bad_arguments(self):
        for k, n in ((-1, 5), (6, 5), (0, 0)):
            with self.assertRaises(ValueError):
                audit.clopper_pearson(k, n)


class TestCommandLine(Case):
    def test_usage_errors_never_repeat_an_argument(self):
        for argv in ((), ("6100",), ("show",), ("show", "1", "6100"), ("context", "1", "6100"), ("draw", "6100")):
            with self.subTest(argv=argv):
                code, out, err = self.fx.run(*argv)
                self.assertEqual((code, out), (2, ""))
                self.assertEqual(err, "error: not a valid command line; usage: "
                                      "audit.py draw | show N | template | check PATH | compare PATH | context N\n")


if __name__ == "__main__":
    unittest.main()
