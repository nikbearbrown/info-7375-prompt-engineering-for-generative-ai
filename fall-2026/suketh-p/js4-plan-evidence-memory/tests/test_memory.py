"""The JS4 memory: jobwatch-state/3 with a revision rule (MEMORY-GATE.md, PREMORTEM.md, PLAN.md v0.2).

Each test names the gate item, plan step or premortem line it checks. Claude Code wrote these tests on
2026-11-25, after the student's memory gate (aa5d3f62) and before writing jobwatch/memory.py. They write
only inside temporary folders. The approvals in them are simulated fixtures, not the student's: every
real state write still needs the student's own approval."""

import copy
import hashlib
import json
import tempfile
import threading
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

from jobwatch import memory
from jobwatch.errors import StateError

ROOT = Path(__file__).resolve().parent.parent
T1 = "2026-11-08T11:17:26Z"   # the Nov 8 Anthropic capture time
T2 = "2026-11-24T22:36:19Z"   # the Nov 24 Anthropic capture time
T3 = "2026-11-25T12:00:00Z"   # a later, constructed time
NOW = "2026-11-25T23:59:00Z"
SHA_A, SHA_B, SHA_C = "a" * 64, "b" * 64, "c" * 64
GH, DB = "greenhouse/anthropic", "greenhouse/databricks"
LISTED = "Listed as of the capture time"
MISSING = "Missing from this list. Status unknown."
CLOSED = "Closed in the seeded fixture as of the stated time"
CANNOT_TELL = "I cannot tell"
GATE_FIELDS = ["board", "posting_key", "fact_type", "value", "captured_at", "capture_run_id",
               "recorded_by_run_id", "source_kind", "source_path", "source_sha256", "source_locator",
               "verification_ref"]


def capture(board, keys, at, run, sha=SHA_A):
    return memory.Capture(board=board, keys=[str(k) for k in keys], captured_at=at, capture_run_id=run,
                          source_path=f"runs/{run}/raw/{board.replace('/', '-')}.body.gz", source_sha256=sha,
                          verification_ref=f"replay/runs/{run}/verify.json#{board}")


def closure(board, key, at, label="SEEDED CLOSURE FIXTURE: constructed, not a board response"):
    return memory.Closure(board=board, key=key, closed_at=at, fixture_id="FIXTURE-closure",
                          fixture_path="fixtures/closure/closure.json", fixture_sha256=SHA_B, label=label,
                          verification_ref="replay/runs/S3/checks.json#closure")


def advance(state, run_id, captures=(), unusable=(), closures=()):
    """Propose and apply without touching the disk (the commit tests below use the writer)."""
    proposal = memory.propose(state, run_id, captures, unusable=unusable, closures=closures)
    return memory.apply(state, proposal, base_sha256=SHA_C, label="TEST", committed_at=NOW)


def facts_of(state, key, fact_type):
    return [f for f in state["facts"] if f["posting_key"] == key and f["fact_type"] == fact_type]


class RecordTest(unittest.TestCase):
    """MEMORY-GATE.md A1: what every remembered fact holds."""

    def test_an_empty_replay_state_is_revision_0_with_nothing_remembered(self):
        state = memory.empty_state()
        self.assertEqual(state, {"schema": "jobwatch-state/3", "revision": 0, "imported_from": None,
                                 "boards": {}, "runs": [], "facts": []})
        self.assertIsNone(memory.validate(state))
        self.assertEqual(json.loads(memory.encode(state)), state)

    def test_a_listed_fact_carries_the_twelve_gate_fields(self):
        state = advance(memory.empty_state(), "S1", [capture(GH, [1, 2], T1, "R-nov8")])
        self.assertEqual(facts_of(state, "1", "listed"), [{
            "board": GH, "posting_key": "1", "fact_type": "listed", "value": LISTED, "captured_at": T1,
            "capture_run_id": "R-nov8", "recorded_by_run_id": "S1", "source_kind": "saved capture",
            "source_path": "runs/R-nov8/raw/greenhouse-anthropic.body.gz", "source_sha256": SHA_A,
            "source_locator": "jobs[].id = 1",
            "verification_ref": "replay/runs/R-nov8/verify.json#greenhouse/anthropic"}])
        self.assertIsNone(memory.validate(state))
        self.assertEqual(json.loads(memory.encode(state)), state)

    def test_an_ashby_fact_points_at_the_job_url(self):
        url = "https://jobs.ashbyhq.com/linear/x"
        state = advance(memory.empty_state(), "S1", [capture("ashby/linear", [url], T1, "R-nov8")])
        self.assertEqual({f["source_locator"] for f in state["facts"]}, {f"jobs[].jobUrl = {url}"})

    def test_a_fact_without_its_source_is_refused(self):
        state = advance(memory.empty_state(), "S1", [capture(GH, [1], T1, "R-nov8")])
        for field in GATE_FIELDS:
            missing = copy.deepcopy(state)
            del missing["facts"][0][field]
            self.assertIsNotNone(memory.validate(missing), field)
            empty = copy.deepcopy(state)
            empty["facts"][0][field] = ""
            self.assertIsNotNone(memory.validate(empty), field)
        for field, bad in (("fact_type", "rumoured"), ("source_kind", "a model's reading"),
                           ("source_sha256", "abc"), ("captured_at", "November 8"),
                           ("recorded_by_run_id", "S-never-committed"), ("board", "greenhouse/unknown")):
            wrong = copy.deepcopy(state)
            wrong["facts"][0][field] = bad
            self.assertIsNotNone(memory.validate(wrong), field)


class NewPostingsTest(unittest.TestCase):
    """MEMORY-GATE.md B4 'Is this new?' and A2's last paragraph (a returning key)."""

    def setUp(self):
        self.s1 = advance(memory.empty_state(), "S1", [capture(GH, [1, 2, 3], T1, "R1")])
        self.s2 = advance(self.s1, "S2", [capture(GH, [2, 3, 4], T2, "R2")])

    def test_a_boards_first_usable_capture_is_its_baseline_with_no_new_postings(self):
        self.assertIsNone(memory.new_keys(memory.empty_state(), GH, ["1", "2"]))
        self.assertEqual(self.s1["runs"][0]["boards"][GH], {"outcome": "usable", "jobs": 3, "baseline": True,
                                                           "new": [], "missing": [], "returned": []})
        self.assertEqual(sorted(f["posting_key"] for f in self.s1["facts"] if f["fact_type"] == "first seen"),
                         ["1", "2", "3"])

    def test_a_later_capture_records_new_and_missing_keys(self):
        self.assertEqual(self.s2["runs"][1]["boards"][GH], {"outcome": "usable", "jobs": 3, "baseline": False,
                                                           "new": ["4"], "missing": ["1"], "returned": []})
        [gone] = facts_of(self.s2, "1", "missing from the list")
        self.assertEqual((gone["value"], gone["captured_at"], gone["source_locator"], gone["capture_run_id"]),
                         (MISSING, T2, "all jobs[].id", "R2"))

    def test_a_returning_key_is_not_new_and_keeps_its_first_seen_record(self):
        s3 = advance(self.s2, "S3", [capture(GH, [1, 2, 3, 4], T3, "R3")])
        self.assertEqual(s3["runs"][2]["boards"][GH]["returned"], ["1"])
        self.assertEqual(s3["runs"][2]["boards"][GH]["new"], [])
        self.assertEqual([f["captured_at"] for f in facts_of(s3, "1", "first seen")], [T1])
        self.assertEqual([f["captured_at"] for f in facts_of(s3, "1", "listed")], [T1, T3])
        self.assertEqual(memory.new_keys(s3, GH, ["1", "5"]), ["5"])

    def test_a_board_given_twice_in_one_run_is_refused(self):
        with self.assertRaises(StateError):
            memory.propose(self.s2, "S3", [capture(GH, [1], T3, "R3"), capture(GH, [2], T3, "R3")])


class LivenessTest(unittest.TestCase):
    """MEMORY-GATE.md A2: what memory may say about whether a posting is still open."""

    def setUp(self):
        s1 = advance(memory.empty_state(), "S1", [capture(GH, [1, 2, 3], T1, "R1")])
        self.s2 = advance(s1, "S2", [capture(GH, [2, 3, 4], T2, "R2")])

    def test_a_listed_key_is_listed_as_of_its_capture_time(self):
        said = memory.liveness(self.s2, GH, "2")
        self.assertEqual((said["statement"], said["as_of"]), (LISTED, T2))

    def test_a_key_missing_from_the_later_list_has_unknown_status_and_keeps_its_history(self):
        said = memory.liveness(self.s2, GH, "1")
        self.assertEqual((said["statement"], said["as_of"]), (MISSING, T2))
        self.assertEqual(said["first_seen"]["captured_at"], T1)
        self.assertEqual(said["last_listed"]["captured_at"], T1)

    def test_fresh_is_not_true_a_later_closure_fixture_closes_a_listed_key(self):
        self.assertEqual(memory.liveness(self.s2, GH, "3")["statement"], LISTED)
        s3 = advance(self.s2, "S3", closures=[closure(GH, "3", T3)])
        said = memory.liveness(s3, GH, "3")
        self.assertEqual((said["statement"], said["as_of"]), (CLOSED, T3))
        self.assertEqual(said["latest"]["source_kind"], "seeded fixture")
        self.assertEqual(said["last_listed"]["captured_at"], T2)

    def test_a_closure_that_is_not_later_than_the_last_listing_conflicts(self):
        s3 = advance(self.s2, "S3", closures=[closure(GH, "2", T1)])
        said = memory.liveness(s3, GH, "2")
        self.assertEqual(said["statement"], CANNOT_TELL)
        self.assertIn("conflict", said["reason"])

    def test_unknown_keys_and_boards_cannot_be_told(self):
        self.assertEqual(memory.liveness(self.s2, GH, "999")["statement"], CANNOT_TELL)
        self.assertEqual(memory.liveness(self.s2, "greenhouse/unknown", "1")["statement"], CANNOT_TELL)

    def test_a_failed_board_cannot_be_told_and_keeps_its_last_verified_observation(self):
        s3 = advance(self.s2, "S3", unusable=[GH])
        said = memory.liveness(s3, GH, "2")
        self.assertEqual(said["statement"], CANNOT_TELL)
        self.assertIn("unusable", said["reason"])
        self.assertEqual(said["last_listed"]["captured_at"], T2)
        self.assertEqual(s3["runs"][2]["boards"][GH], {"outcome": "unusable", "jobs": None, "baseline": False,
                                                      "new": [], "missing": [], "returned": []})
        self.assertEqual(len(s3["facts"]), len(self.s2["facts"]))

    def test_a_closure_must_be_a_labelled_fixture_naming_a_remembered_board_and_key(self):
        for bad in (closure(GH, "3", T3, label=""), closure(GH, "3", T3, label="closed per a recruiter"),
                    closure(GH, "999", T3), closure("greenhouse/other", "3", T3)):
            with self.assertRaises(StateError):
                memory.propose(self.s2, "S3", closures=[bad])


class PurityTest(unittest.TestCase):
    """Chapter 12: a read returns a copy, and proposing an update never changes the state it read."""

    def test_proposing_does_not_change_the_state_it_reads(self):
        s1 = advance(memory.empty_state(), "S1", [capture(GH, [1, 2], T1, "R1")])
        before = json.dumps(s1, sort_keys=True)
        memory.propose(s1, "S2", [capture(GH, [2, 3], T2, "R2")], closures=[closure(GH, "2", T3)])
        memory.apply(s1, memory.propose(s1, "S2", [capture(GH, [3], T2, "R2")]), base_sha256=SHA_C,
                     label="TEST", committed_at=NOW)
        self.assertEqual(json.dumps(s1, sort_keys=True), before)

    def test_a_read_returns_a_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_bytes(memory.encode(memory.empty_state()))
            memory.load(path)["facts"].append("changed in memory only")
            self.assertEqual(memory.load(path)["facts"], [])


class CommitTest(unittest.TestCase):
    """MEMORY-GATE.md B3 (the writer) and C trigger 1; PREMORTEM.md lines 1-5."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.path = self.root / "state" / "state.json"
        self.path.parent.mkdir()
        self.path.write_bytes(memory.encode(memory.empty_state()))
        self.sha0 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.state0 = memory.load(self.path)

    def approve(self, run_id, revision, sha, path="state/state.json"):
        return memory.WriteApproval(run_id=run_id, path=path, revision=revision, sha256=sha)

    def commit(self, approval, proposal, target="state/state.json", **kwargs):
        return memory.commit(self.root, target, approval, proposal, f"runs/{proposal.run_id}", label="TEST",
                             clock=lambda: NOW, **kwargs)

    def sha_now(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_a_commit_advances_the_revision_once_and_records_its_base(self):
        proposal = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        receipt = self.commit(self.approve("S1", 0, self.sha0), proposal)
        data = json.loads(self.path.read_bytes())
        self.assertEqual(data["revision"], 1)
        self.assertEqual(receipt, memory.Receipt("state/state.json", 1, self.sha_now()))
        self.assertEqual(memory.receipt(self.root, "state/state.json"), receipt)
        run = data["runs"][0]
        self.assertEqual((run["run_id"], run["base_revision"], run["base_sha256"], run["revision"],
                          run["committed_at"], run["label"]), ("S1", 0, self.sha0, 1, NOW, "TEST"))

    def premortem_refusal(self):
        """PREMORTEM.md line 2: two updates with different posting keys, each with its own run ID and an
        approval tied to the same revision 0 and starting SHA-256; Anthropic commits first."""
        anthropic = memory.propose(self.state0, "PM-anthropic", [capture(GH, ["a1"], T1, "R1")])
        databricks = memory.propose(self.state0, "PM-databricks", [capture(DB, ["d1"], T1, "R1")])
        self.commit(self.approve("PM-anthropic", 0, self.sha0), anthropic)
        after_first = self.path.read_bytes()
        with self.assertRaises(memory.StaleWrite) as caught:
            self.commit(self.approve("PM-databricks", 0, self.sha0), databricks)
        return databricks, after_first, caught.exception

    def test_the_premortem_stale_write_is_refused_and_changes_nothing(self):
        _, after_first, error = self.premortem_refusal()
        self.assertIn("expected revision 0", str(error))
        self.assertIn("found revision 1", str(error))
        self.assertEqual(self.path.read_bytes(), after_first)            # PREMORTEM.md line 4: same bytes
        data = json.loads(after_first)
        self.assertEqual(data["revision"], 1)
        self.assertEqual({f["posting_key"] for f in data["facts"]}, {"a1"})
        [listed] = facts_of(data, "a1", "listed")
        self.assertEqual((listed["source_path"], listed["source_sha256"], listed["recorded_by_run_id"]),
                         ("runs/R1/raw/greenhouse-anthropic.body.gz", SHA_A, "PM-anthropic"))
        refusal = json.loads((self.root / "runs" / "PM-databricks" / "write-refused.json").read_text())
        self.assertEqual(refusal["expected"], {"revision": 0, "sha256": self.sha0})
        self.assertEqual(refusal["found"], {"revision": 1, "sha256": hashlib.sha256(after_first).hexdigest()})
        self.assertIs(refusal["approval_void"], True)
        self.assertIs(refusal["state_changed"], False)

    def test_a_refused_runs_approval_stays_void(self):
        databricks, _, _ = self.premortem_refusal()
        reset = memory.encode(memory.empty_state())      # even a reset back to the approved revision 0
        self.path.write_bytes(reset)
        self.assertEqual(hashlib.sha256(reset).hexdigest(), self.sha0)
        with self.assertRaises(memory.ApprovalVoid):
            self.commit(self.approve("PM-databricks", 0, self.sha0), databricks)
        self.assertEqual(self.path.read_bytes(), reset)

    def test_a_changed_hash_at_the_same_revision_is_refused(self):
        self.path.write_bytes(self.path.read_bytes() + b"\n")   # still revision 0, other bytes
        changed = self.path.read_bytes()
        proposal = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        with self.assertRaises(memory.StaleWrite) as caught:
            self.commit(self.approve("S1", 0, self.sha0), proposal)
        self.assertIn("sha256", str(caught.exception))
        self.assertEqual(self.path.read_bytes(), changed)

    def test_an_approval_must_name_this_run_and_this_path(self):
        proposal = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        for approval, target in ((self.approve("S9", 0, self.sha0), "state/state.json"),
                                 (self.approve("S1", 0, self.sha0, path="state/other.json"), "state/state.json"),
                                 (self.approve("S1", 0, self.sha0, path="../state.json"), "../state.json")):
            with self.assertRaises(memory.ApprovalProblem):
                self.commit(approval, proposal, target=target)
        self.assertEqual(self.sha_now(), self.sha0)
        self.assertFalse((self.root / "runs").exists())

    def test_a_proposal_built_on_an_older_revision_is_refused_even_with_a_fresh_approval(self):
        first = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        receipt = self.commit(self.approve("S1", 0, self.sha0), first)
        stale = memory.propose(self.state0, "S2", [capture(GH, [2], T2, "R2")])   # built on revision 0
        with self.assertRaises(memory.ApprovalProblem) as caught:
            self.commit(self.approve("S2", 1, receipt.sha256), stale)
        self.assertIn("revision 0", str(caught.exception))
        self.assertEqual(self.sha_now(), receipt.sha256)

    def test_an_approval_for_an_older_revision_is_refused_as_stale_and_voided(self):
        """Another run committed revision 1 after this approval named revision 0. The proposal itself was
        built on revision 1. MEMORY-GATE.md trigger 1: the mismatch voids this run's approval."""
        first = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        receipt = self.commit(self.approve("S1", 0, self.sha0), first)
        on_one = memory.propose(memory.load(self.path), "S2", [capture(GH, [1, 2], T2, "R2")])
        with self.assertRaises(memory.StaleWrite) as caught:
            self.commit(self.approve("S2", 0, self.sha0), on_one)
        self.assertIn("found revision 1", str(caught.exception))
        self.assertEqual(self.sha_now(), receipt.sha256)
        self.assertTrue((self.root / "runs" / "S2" / "write-refused.json").exists())

    def test_a_committed_run_cannot_commit_again(self):
        first = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        receipt = self.commit(self.approve("S1", 0, self.sha0), first)
        again = memory.propose(memory.load(self.path), "S1", [capture(GH, [2], T2, "R2")])
        with self.assertRaises(memory.ApprovalProblem) as caught:
            self.commit(self.approve("S1", 1, receipt.sha256), again)
        self.assertIn("already committed", str(caught.exception))
        self.assertEqual(self.sha_now(), receipt.sha256)

    def test_a_damaged_state_is_an_error_not_a_fresh_start(self):
        good = json.loads(memory.encode(memory.empty_state()))
        damaged = [b"{", b'{"schema": "jobwatch-state/2"}']
        for revision in (True, 1.0, "0", -1, 1):      # 1: no committed run backs revision 1
            damaged.append(json.dumps(dict(good, revision=revision)).encode())
        proposal = memory.propose(self.state0, "S1", [capture(GH, [1], T1, "R1")])
        for raw in damaged:
            self.path.write_bytes(raw)
            with self.assertRaises(StateError):
                memory.load(self.path)
            with self.assertRaises(StateError) as caught:     # the approval names these exact bytes
                self.commit(self.approve("S1", 0, hashlib.sha256(raw).hexdigest()), proposal)
            self.assertNotIsInstance(caught.exception, (memory.StaleWrite, memory.ApprovalVoid))
            self.assertIn("damaged", str(caught.exception))
            self.assertEqual(self.path.read_bytes(), raw)
        self.assertFalse((self.root / "runs").exists())       # no refusal record: nothing was voided

    def test_the_approval_names_the_run_the_path_the_revision_and_the_sha256(self):
        text = "SEEDED-2026-11-08:replay/state/state.json:0:" + SHA_A
        approval = memory.WriteApproval.parse(text)
        self.assertEqual(approval, memory.WriteApproval("SEEDED-2026-11-08", "replay/state/state.json", 0, SHA_A))
        self.assertEqual(str(approval), text)
        for bad in ("S1:replay/state/state.json:0", "S1:replay/state/state.json:x:" + SHA_A,
                    "S1:replay/state/state.json:-1:" + SHA_A, "S1:replay/state/state.json:01:" + SHA_A,
                    "S1:replay/state/state.json:0:" + "A" * 64, "S1:replay/state/state.json:0:abc",
                    ":replay/state/state.json:0:" + SHA_A, "S1::0:" + SHA_A,
                    "S1:replay/state/state.json:0:" + SHA_A + ":extra"):
            with self.assertRaises(ValueError, msg=bad):
                memory.WriteApproval.parse(bad)


class ConcurrencyTest(unittest.TestCase):
    """PREMORTEM.md line 3 and Chapter 12's wrong version: the compare must happen inside the lock."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.path = self.root / "state" / "state.json"
        self.path.parent.mkdir()
        self.path.write_bytes(memory.encode(memory.empty_state()))
        self.sha0 = hashlib.sha256(self.path.read_bytes()).hexdigest()

    def race(self):
        """The Anthropic writer compares, then waits inside its write while the Databricks writer starts
        from the same revision 0."""
        state0 = memory.load(self.path)
        jobs = {"a": memory.propose(state0, "RACE-anthropic", [capture(GH, ["a1"], T1, "R1")]),
                "d": memory.propose(state0, "RACE-databricks", [capture(DB, ["d1"], T1, "R1")])}
        a_compared, d_done, results = threading.Event(), threading.Event(), {}

        def hold():
            a_compared.set()
            d_done.wait(timeout=0.5)

        def writer(name, hook):
            proposal = jobs[name]
            approval = memory.WriteApproval(proposal.run_id, "state/state.json", 0, self.sha0)
            try:
                results[name] = memory.commit(self.root, "state/state.json", approval, proposal,
                                              f"runs/{proposal.run_id}", label="TEST", clock=lambda: NOW,
                                              before_write=hook)
            except StateError as error:
                results[name] = error
            finally:
                if name == "d":
                    d_done.set()

        first = threading.Thread(target=writer, args=("a", hold))
        second = threading.Thread(target=writer, args=("d", None))
        first.start()
        self.assertTrue(a_compared.wait(timeout=5))
        second.start()
        second.join(timeout=10)
        first.join(timeout=10)
        keys = {f["posting_key"] for f in json.loads(self.path.read_bytes())["facts"]}
        return results, keys

    def test_two_writers_from_the_same_revision_one_commits_one_is_refused(self):
        results, keys = self.race()
        self.assertIsInstance(results["a"], memory.Receipt)
        self.assertIsInstance(results["d"], memory.StaleWrite)
        self.assertEqual(keys, {"a1"})

    def test_a_writer_that_compares_outside_the_lock_loses_an_update(self):
        """The planted wrong version: without the lock both writers pass the compare, both report
        success, and one update is lost. The test above is the one that catches it."""
        with mock.patch.object(memory, "_exclusive", lambda lock_path: nullcontext()):
            results, keys = self.race()
        self.assertIsInstance(results["a"], memory.Receipt)
        self.assertIsInstance(results["d"], memory.Receipt)
        self.assertEqual(keys, {"a1"})      # d1 was committed, then overwritten


class MigrationTest(unittest.TestCase):
    """PLAN.md v0.2: a jobwatch-state/2 record copied into revision 0 as legacy sightings."""

    V2 = {"schema": "jobwatch-state/2",
          "boards": {GH: {"ats": "greenhouse", "slug": "anthropic", "first_snapshot_run": "L1",
                          "last_snapshot_run": "L2", "seen": {"1": "L1", "2": "L2"}}},
          "runs": [{"run_id": "L1", "finished_at": "2026-11-01T10:00:00Z", "boards": {}},
                   {"run_id": "L2", "finished_at": "2026-11-02T10:00:00Z", "boards": {}}]}

    def test_a_state2_record_migrates_into_revision_0_as_legacy_sightings(self):
        raw = json.dumps(self.V2).encode()
        sha = hashlib.sha256(raw).hexdigest()
        state = memory.migrate_v2(raw, source_path="state/state.json", run_id="MIGRATE-1",
                                  verification_ref="fixtures/migration/record.json#check")
        self.assertEqual((state["revision"], state["runs"]), (0, []))
        self.assertEqual(state["imported_from"], {"path": "state/state.json", "sha256": sha,
                                                  "schema": "jobwatch-state/2", "migrated_by": "MIGRATE-1",
                                                  "runs": self.V2["runs"]})
        self.assertEqual(facts_of(state, "2", "first seen"), [{
            "board": GH, "posting_key": "2", "fact_type": "first seen",
            "value": "First seen by run L2 (legacy record: the time is that run's finish time)",
            "captured_at": "2026-11-02T10:00:00Z", "capture_run_id": "L2", "recorded_by_run_id": "MIGRATE-1",
            "source_kind": "legacy import", "source_path": "state/state.json", "source_sha256": sha,
            "source_locator": 'boards["greenhouse/anthropic"].seen["2"]',
            "verification_ref": "fixtures/migration/record.json#check"}])
        self.assertIsNone(memory.validate(state))
        self.assertEqual(memory.liveness(state, GH, "1")["statement"], CANNOT_TELL)   # liveness starts unknown
        self.assertEqual(memory.new_keys(state, GH, ["1", "3"]), ["3"])   # legacy sightings are not new

    def test_a_damaged_state2_record_is_refused(self):
        with self.assertRaises(StateError):
            memory.migrate_v2(b'{"schema": "jobwatch-state/2"}', source_path="state/state.json",
                              run_id="MIGRATE-1", verification_ref="x")

    def test_the_real_state2_file_migrates_with_every_seen_key(self):
        raw = (ROOT / "state" / "state.json").read_bytes()
        expected = sum(len(board["seen"]) for board in json.loads(raw)["boards"].values())
        self.assertEqual(expected, 675 + 922 + 32)      # the Nov 8 baseline, hand-checked
        state = memory.migrate_v2(raw, source_path="state/state.json", run_id="MIGRATE-real",
                                  verification_ref="x")
        self.assertEqual(len(state["facts"]), expected)
        self.assertEqual(state["imported_from"]["sha256"], hashlib.sha256(raw).hexdigest())


class TwoDayDiffTest(unittest.TestCase):
    """MEMORY-GATE.md B4 'What changed between the two days?'"""

    def test_the_diff_names_new_missing_and_returned_keys_and_the_revisions_it_links(self):
        s1 = advance(memory.empty_state(), "S1", [capture(GH, [1, 2, 3], T1, "R1"), capture(DB, [7], T1, "R1")])
        s2 = advance(s1, "S2", [capture(GH, [2, 3, 4], T2, "R2"), capture(DB, [7, 8], T2, "R2")])
        self.assertEqual(memory.run_diff(s2, "S2"), {
            "run_id": "S2", "base_revision": 1, "base_sha256": SHA_C, "revision": 2,
            "boards": {GH: {"outcome": "usable", "jobs": 3, "baseline": False, "new": ["4"], "missing": ["1"],
                            "returned": []},
                       DB: {"outcome": "usable", "jobs": 2, "baseline": False, "new": ["8"], "missing": [],
                            "returned": []}}})
        with self.assertRaises(StateError):
            memory.run_diff(s2, "S-unknown")


if __name__ == "__main__":
    unittest.main()
