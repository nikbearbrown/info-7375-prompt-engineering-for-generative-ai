"""The shortlist's claims kit (tools/claims_kit.py): Section 5's claims, word-for-word passages, a rule-based checker by
Section 2's labels (silence is never support), a sealed label file, and a blank labeling sheet.

The checker and kit tests use CONSTRUCTED postings; the last class checks the committed kit against a fresh build.
"""

import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from job_agent import filter as flt
from job_agent import filter_run
from job_agent.rule import _flat

from .loop_helpers import REPO, ashby_job, body, greenhouse_job
from .test_filter_run import save

spec = importlib.util.spec_from_file_location("claims_kit", REPO / "tools" / "claims_kit.py")
claims_kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims_kit)

RUN_ID = "2026-11-21T044414Z"
COMMITTED = REPO / "js3" / "claims" / RUN_ID
CLAIM_ROW = re.compile(r"^\| (\d\d\.\d[a-z]?) \|")
EXPORT = ("To comply with U.S. export control laws and regulations, candidates for this role may need to meet certain "
          "legal status requirements.")
RULES, JANE = flt.load_rules(version="1.0"), flt.load_profile()
S, C, I = claims_kit.SUPPORTED, claims_kit.CONTRADICTED, claims_kit.INSUFFICIENT


def cells(line: str) -> list:
    """A table row's cells, split at the pipes that are not escaped."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]


def blank_labels(text: str, row: re.Pattern, keep: int) -> str:
    """A sheet with each row's cells after the first `keep` emptied, so a filled sheet compares with a fresh one."""
    out = []
    for line in text.splitlines():
        if row.match(line):
            parts = re.split(r"(?<!\\)\|", line)
            line = "|".join(parts[:keep + 1] + [" "] * (len(parts) - keep - 2) + [""])
        out.append(line)
    return "\n".join(out)


class CheckerTest(unittest.TestCase):
    """Each claim's rule, on sentences written for the test."""

    def years(self, *sentences):
        return claims_kit.check_years(list(sentences), JANE, RULES)[0]

    def status(self, *sentences):
        return claims_kit.check_status(list(sentences), JANE, RULES)[0]

    def start(self, *sentences):
        return claims_kit.check_start(list(sentences), JANE, RULES)[0]

    def test_silence_is_never_support(self):
        self.assertEqual(self.status(), I)
        self.assertEqual(self.start(), I)
        self.assertEqual(self.years(), I)

    def test_years(self):
        self.assertEqual(self.years("3+ years of professional software development experience."), S)
        self.assertEqual(self.years("3-5 years of experience with Python."), S)  # a range asks its smallest number
        self.assertEqual(self.years("5+ years of software engineering experience"), C)
        self.assertEqual(self.years("5+ years of Go is a plus."), S)  # optional
        self.assertEqual(self.years("2+ years of Python.", "6+ years of C++."), C)
        self.assertEqual(self.years("Have 8+ years of experience, ideally within high-growth startups."), I)
        self.assertEqual(self.years("The company was founded 15 years ago."), I)  # not about the candidate

    def test_status(self):
        self.assertEqual(self.status("Visa sponsorship is available for this role."), S)
        self.assertEqual(self.status("We are unable to sponsor visas for this role."), C)
        self.assertEqual(self.status("Applicants must be U.S. citizens."), C)
        self.assertEqual(self.status("We don't sponsor work visas."), C)
        self.assertEqual(self.status("We do not offer visa sponsorship."), C)
        self.assertEqual(self.status(EXPORT), I)  # on the topic, settles nothing

    def test_start(self):
        self.assertEqual(self.start("The start date is June 2027."), S)
        self.assertEqual(self.start("The start date is May 2027."), S)
        self.assertEqual(self.start("You must start in January 2027."), C)
        self.assertEqual(self.start("Candidates must start immediately."), C)
        self.assertEqual(self.start("We keep the ecosystem safe from the start."), I)
        self.assertEqual(self.start("The start date is flexible."), S)
        self.assertEqual(self.start("Start in Spring 2027."), I)  # March to May overlaps May 2027
        self.assertEqual(self.start("Start in Fall 2026."), C)
        self.assertEqual(self.start("Start in Summer 2027."), S)
        self.assertEqual(self.start("Start in early 2028."), S)

    def test_topic_claims_need_the_role_in_the_sentence(self):
        def topic(group, sentence):
            return claims_kit.check_topic(group, sentence, RULES)[0]
        self.assertEqual(topic("APIs", "We build APIs for the world."), I)  # FILTER.md Section 5's counterexample
        self.assertEqual(topic("APIs", "You will build APIs."), S)
        self.assertEqual(topic("APIs", "- Design APIs and backend systems."), S)  # a list item
        self.assertEqual(topic("APIs", "Build and evolve the APIs through which developers work."), S)
        self.assertEqual(topic("APIs", "You will build the rest of the platform."), I)  # "REST" must be uppercase

    def test_the_field_claims(self):
        self.assertEqual(claims_kit.check_employment(ashby_job("x"), RULES)[0], S)
        self.assertEqual(claims_kit.check_employment(ashby_job("x", employmentType="Contract"), RULES)[0], C)
        self.assertEqual(claims_kit.check_employment(ashby_job("x", employmentType=None), RULES)[0], I)
        self.assertEqual(claims_kit.check_location(ashby_job("x"), JANE)[0], S)
        dc = ashby_job("x", location="Washington, DC", address={"postalAddress": {
            "addressCountry": "United States", "addressRegion": "District of Columbia",
            "addressLocality": "Washington"}})
        self.assertEqual(claims_kit.check_location(dc, JANE)[0], C)
        self.assertEqual(claims_kit.check_location(ashby_job("x", location="Remote", address=None), JANE)[0], I)
        self.assertEqual(claims_kit.check_level("Senior Software Engineer", RULES)[0], C)
        self.assertEqual(claims_kit.check_level("Software Engineer, Leadership Tools", RULES)[0], S)
        self.assertEqual(claims_kit.check_role("Software Engineer, Payments", RULES)[0], S)
        self.assertEqual(claims_kit.check_role("Frontend Software Engineer", RULES)[0], C)
        self.assertEqual(claims_kit.check_role("Account Director", RULES)[0], I)

    def test_passages_keep_us_eg_and_dec_with_what_follows(self):
        text = EXPORT + " The cluster (e.g. compute) is ours. Start Dec. 2026 here.\nNext line."
        self.assertEqual(claims_kit.passage_sentences(text),
                         [EXPORT, "The cluster (e.g. compute) is ours.", "Start Dec. 2026 here.", "Next line."])


class ClaimsKitTest(unittest.TestCase):
    """A filter run over CONSTRUCTED saved answers from three systems, then its claims kit."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-claims-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        runs, boards = self.root / "runs", self.root / "boards.json"
        boards.write_text(json.dumps({"boards": [{"system": "ashby", "name": "acme"},
                                                 {"system": "greenhouse", "name": "beta"},
                                                 {"system": "lever", "name": "gamma"}]}), encoding="utf-8")
        good = "You will build APIs and design SQL schemas for our backend."
        jobs = [ashby_job("a-1", title="Software Engineer, Payments", descriptionPlain=good + "\n3+ years of "
                          "experience with Python.\nVisa sponsorship is available for this role.\nThe start date is "
                          "June 2027."),
                ashby_job("a-2", title="Backend Engineer, Data", descriptionPlain="We build APIs for the world.\n"
                          "You will design SQL schemas for our backend."),
                ashby_job("a-3", title="Software Engineer, Infra",
                          descriptionPlain=EXPORT + "\n5+ years of Go is a plus.\n- Design APIs and backend systems."),
                ashby_job("s-1", title="Senior Software Engineer, Payments", descriptionPlain=good)]
        gh = greenhouse_job(7, title="Software Engineer, Search")
        gh["content"] = "&lt;p&gt;" + good + "&lt;/p&gt;"
        lever = {"id": "l-1", "text": "Software Engineer - Platform", "hostedUrl": "https://example.com/lever/l-1",
                 "country": "US", "workplaceType": "hybrid", "descriptionPlain": good, "lists": [],
                 "categories": {"commitment": "Full-time", "location": "New York, NY",
                                "allLocations": ["New York, NY"]}}
        save(runs, "2026-11-02T000000Z", "ashby-acme", body("ashby", jobs))
        save(runs, "2026-11-02T000000Z", "greenhouse-beta", body("greenhouse", [gh]))
        save(runs, "2026-11-02T000000Z", "lever-gamma", body("lever", [lever]))
        clock = lambda: datetime(2026, 11, 21, 7, 0, 0, tzinfo=timezone.utc)  # noqa: E731
        self.run = filter_run.run(runs_root=runs, boards_path=boards, out_root=self.root / "runs-out", now=clock,
                                      rules_version="1.0")
        self.raw = {**{j["id"]: j for j in jobs}, "7": gh, "l-1": lever}

    def build(self, seed=5):
        return claims_kit.build(self.run["out"], self.root / f"claims-{seed}-{len(list(self.root.iterdir()))}", seed)

    def sealed(self, out):
        return json.loads((out / "sealed" / "checker-labels.json").read_text(encoding="utf-8"))

    def labels(self, out):
        sealed = self.sealed(out)
        ids = {p["posting"]: p["id"] for p in sealed["postings"]}
        return {(ids[c["posting"]], c["type"], c["group"]): c["label"] for c in sealed["claims"]}

    def test_the_kit_holds_a_blank_sheet_and_a_sealed_file_whose_hash_is_in_the_readme(self):
        out = self.build()
        sealed = self.sealed(out)
        self.assertEqual(len(sealed["postings"]), 5)  # the shortlist; the senior posting is not on it
        sheet = (out / "LABELS.md").read_text(encoding="utf-8")
        rows = [line for line in sheet.splitlines() if CLAIM_ROW.match(line)]
        self.assertEqual([CLAIM_ROW.match(r).group(1) for r in rows], [c["claim"] for c in sealed["claims"]])
        self.assertTrue(all(cells(r)[3:] == ["", "", "", ""] for r in rows))  # every label and note cell is blank
        for claim in sealed["claims"]:
            self.assertNotIn(claim["why"], sheet)
        self.assertIsNone(re.search(r"(?i)\b(score|rank|checker says)\b", sheet))
        digest = hashlib.sha256((out / "sealed" / "checker-labels.json").read_bytes()).hexdigest()
        self.assertIn(f"`{digest}`", (out / "README.md").read_text(encoding="utf-8"))

    def test_each_posting_gets_claims_1_to_7_and_one_per_topic_group(self):
        out = self.build()
        sealed = self.sealed(out)
        records = {r["id"]: r for r in self.run["records"]}
        for posting in sealed["postings"]:
            claims = [c for c in sealed["claims"] if c["posting"] == posting["posting"]]
            self.assertEqual([c["type"] for c in claims if c["type"] < 8], [1, 2, 3, 4, 5, 6, 7])
            self.assertEqual(sorted(c["group"] for c in claims if c["type"] == 8),
                             sorted(records[posting["id"]]["topics"]))

    def test_the_checker_labels_follow_section_2(self):
        labels = self.labels(self.build())
        self.assertEqual([labels[("a-1", t, None)] for t in (5, 6, 7)], [S, S, S])
        self.assertEqual([labels[("a-2", t, None)] for t in (5, 6, 7)], [I, I, I])  # silence
        self.assertEqual(labels[("a-2", 8, "APIs")], I)  # "We build APIs for the world."
        self.assertEqual(labels[("a-2", 8, "Databases")], S)
        self.assertEqual(labels[("a-3", 5, None)], I)  # the export-control sentence
        self.assertEqual(labels[("a-3", 7, None)], S)  # optional years
        self.assertEqual([labels[(k, 1, None)] for k in ("a-1", "7", "l-1")], [S, S, S])

    def test_the_passages_are_word_for_word_from_the_saved_posting(self):
        out = self.build()
        sealed = self.sealed(out)
        ids = {p["posting"]: p["id"] for p in sealed["postings"]}
        texts = {}
        for key, (posting, _) in claims_kit.audit_kit.saved_postings(
                json.loads((self.run["out"] / "verdicts.json").read_text())).items():
            texts[key[1]] = _flat(posting["descriptionPlain"])
        rows = {CLAIM_ROW.match(line).group(1): cells(line) for line in
                (out / "LABELS.md").read_text(encoding="utf-8").splitlines() if CLAIM_ROW.match(line)}
        for claim in sealed["claims"]:
            pid, passages = ids[claim["posting"]], rows[claim["claim"]][2]
            if claim["type"] >= 5 and passages != claims_kit.NONE_FOUND:
                for quoted in passages.split("<br>"):
                    self.assertIn(quoted.strip('"'), texts[pid], claim["claim"])
        export = next(c for c in sealed["claims"] if ids[c["posting"]] == "a-3" and c["type"] == 5)
        self.assertEqual(rows[export["claim"]][2], f'"{EXPORT}"')  # whole, not cut after "U.S."
        lever = next(c for c in sealed["claims"] if ids[c["posting"]] == "l-1" and c["type"] == 1)
        self.assertEqual(rows[lever["claim"]][2], 'categories.commitment: "Full-time"')
        greenhouse = next(c for c in sealed["claims"] if ids[c["posting"]] == "7" and c["type"] == 2)
        self.assertEqual(rows[greenhouse["claim"]][2], 'location.name: "San Mateo, CA United States"')
        title = next(c for c in sealed["claims"] if ids[c["posting"]] == "a-1" and c["type"] == 3)
        self.assertEqual(rows[title["claim"]][2], f'title: "{self.raw["a-1"]["title"]}"')

    def test_the_same_seed_gives_the_same_kit_and_another_seed_only_another_order(self):
        first, second, other = self.build(5), self.build(5), self.build(6)
        for name in ("LABELS.md", "README.md", "INSTRUCTIONS.md", "sealed/checker-labels.json"):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)
        self.assertEqual(self.labels(first), self.labels(other))

    def test_a_kit_is_made_once(self):
        out_root = self.root / "claims-once"
        claims_kit.build(self.run["out"], out_root, 5)
        with self.assertRaises(SystemExit):
            claims_kit.build(self.run["out"], out_root, 5)


@unittest.skipUnless(COMMITTED.exists(), "the committed claims kit is not in this copy of the repo")
class CommittedClaimsKitTest(unittest.TestCase):
    """The committed kit is what its recorded seed rebuilds, its hash is in its README, and its sheet leaks nothing."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="job-agent-claims-committed-"))
        readme = (COMMITTED / "README.md").read_text(encoding="utf-8")
        cls.seed = int(re.search(r"seed \*\*(\d+)\*\*", readme).group(1))
        cls.fresh = claims_kit.build(REPO / "js3" / "filter-run" / RUN_ID, cls.tmp, cls.seed)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_committed_kit_rebuilds_from_its_seed(self):
        for name in ("README.md", "INSTRUCTIONS.md", "sealed/checker-labels.json"):
            self.assertEqual((self.fresh / name).read_bytes(), (COMMITTED / name).read_bytes(), name)
        fresh, committed = [blank_labels((d / "LABELS.md").read_text(encoding="utf-8"), CLAIM_ROW, 3)
                            for d in (self.fresh, COMMITTED)]
        self.assertEqual(fresh, committed)  # the same sheet, whatever labels Aravind has written into it since

    def test_the_sealed_files_hash_is_in_the_readme(self):
        digest = hashlib.sha256((COMMITTED / "sealed" / "checker-labels.json").read_bytes()).hexdigest()
        self.assertIn(f"`{digest}`", (COMMITTED / "README.md").read_text(encoding="utf-8"))

    def test_the_sheet_leaks_no_checker_label_or_score(self):
        sheet = (self.fresh / "LABELS.md").read_text(encoding="utf-8")
        rows = [cells(line) for line in sheet.splitlines() if CLAIM_ROW.match(line)]
        self.assertTrue(rows and all(r[3:] == ["", "", "", ""] for r in rows))
        sealed = json.loads((self.fresh / "sealed" / "checker-labels.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), len(sealed["claims"]))
        for claim in sealed["claims"]:
            self.assertNotIn(claim["why"], sheet)
        outside = "\n".join(line for line in sheet.splitlines() if not CLAIM_ROW.match(line))
        self.assertIsNone(re.search(r"(?i)\b(score|rank)\b", outside))
        self.assertTrue(all(not re.search(r"(?i)\b(score|rank)\b", r[0] + r[1]) for r in rows))


if __name__ == "__main__":
    unittest.main()
