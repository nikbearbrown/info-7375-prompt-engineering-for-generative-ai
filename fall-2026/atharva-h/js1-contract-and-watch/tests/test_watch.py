import json
import os
import tempfile
import unittest
import urllib.request

from helpers import RESUME, posting

import persona
import watch


class Watch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.state = os.path.join(self.root, "state", "seen_ids.json")

    def tearDown(self):
        self.tmp.cleanup()

    def response(self, *ids):
        path = os.path.join(self.root, f"response_{'_'.join(map(str, ids))}.json")
        with open(path, "w") as f:
            json.dump({"jobs": [posting(pid=i) for i in ids], "meta": {"total": len(ids)}}, f)
        return path

    def run_on(self, *ids, label="seeded-test"):
        return watch.run(runs_dir=os.path.join(self.root, "runs"), state_path=self.state,
                         from_file=self.response(*ids), label=f"{label}-{len(ids)}", allowed_root=self.root)

    def test_first_run_is_a_baseline_that_reports_nothing_new(self):
        run_dir, meta = self.run_on(1, 2, 3)
        self.assertTrue(meta["baseline"])
        self.assertEqual(meta["new_ids"], [])
        self.assertEqual(json.load(open(self.state))["seen_ids"], [1, 2, 3])
        self.assertTrue(os.path.exists(os.path.join(run_dir, "raw.json")))

    def test_second_run_reports_only_unseen_ids(self):
        """CONTRACT failure sentence: a previously seen posting is never reported as new."""
        self.run_on(1, 2, 3)
        run_dir, meta = self.run_on(1, 2, 3, 4)
        self.assertEqual(meta["new_ids"], [4])
        records = [json.loads(line) for line in open(os.path.join(run_dir, "rule_verdicts.jsonl"))]
        self.assertEqual([r["posting_id"] for r in records], [4])
        self.assertTrue(os.path.exists(os.path.join(run_dir, "claude_prompts", "4.txt")))
        _, meta = self.run_on(1, 2, 3, 4, label="again")
        self.assertEqual(meta["new_ids"], [])

    def test_a_removed_posting_is_not_new_when_it_returns(self):
        self.run_on(1, 2, 3)
        self.run_on(1, 2)
        _, meta = self.run_on(1, 2, 3, label="back")
        self.assertEqual(meta["new_ids"], [])

    def test_raw_response_is_saved_byte_for_byte(self):
        path = self.response(5, 6)
        run_dir, _ = watch.run(runs_dir=os.path.join(self.root, "runs"), state_path=self.state,
                               from_file=path, label="bytes", allowed_root=self.root)
        self.assertEqual(open(path, "rb").read(), open(os.path.join(run_dir, "raw.json"), "rb").read())

    def test_writing_outside_the_agent_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            with self.assertRaises(watch.RefusedPath):
                watch.run(runs_dir=os.path.join(self.root, "runs"), state_path=os.path.join(elsewhere, "s.json"),
                          from_file=self.response(1), label="x", allowed_root=self.root)


class AllowList(unittest.TestCase):
    def test_only_the_allow_listed_https_host_is_fetched(self):
        watch.check_allowed("https://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs")
        for url in ("https://api.lever.co/v0/postings/x", "http://boards-api.greenhouse.io/v1/boards/x/jobs",
                    "https://boards-api.greenhouse.io.evil.example/v1", "https://example.com/"):
            with self.subTest(url=url):
                with self.assertRaises(watch.RefusedHost):
                    watch.fetch(url)

    def test_a_redirect_off_the_allow_list_is_refused(self):
        handler = watch._AllowListRedirect()
        req = urllib.request.Request("https://boards-api.greenhouse.io/v1/boards/x/jobs")
        with self.assertRaises(watch.RefusedHost):
            handler.redirect_request(req, None, 302, "Found", {}, "https://example.com/elsewhere")


class Persona(unittest.TestCase):
    def test_shipped_persona_is_valid_and_fictional(self):
        self.assertEqual(persona.validate(RESUME), [])

    def test_real_looking_contact_details_are_rejected(self):
        for change in ({"email": "someone@gmail.com"}, {"phone": "617-123-4567"}):
            bad = json.loads(json.dumps(RESUME))
            bad["basics"].update(change)
            with self.subTest(change=change):
                self.assertTrue(persona.validate(bad))

    def test_persona_not_marked_fictional_is_rejected(self):
        bad = {k: v for k, v in RESUME.items() if k != "_fictional"}
        self.assertTrue(persona.validate(bad))

    def test_seeded_file_without_label_is_refused_by_the_cli(self):
        with self.assertRaises(SystemExit):
            watch.main(["run", "--from-file", "x.json"])


if __name__ == "__main__":
    unittest.main()
