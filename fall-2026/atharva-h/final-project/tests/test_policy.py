"""CONTRACT.md tests 1-4: the read-only permission policy."""

import tempfile
import unittest
from pathlib import Path

from sponsorsql import policy, udf
from tests import fixtures


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = fixtures.build(Path(cls.tmp.name) / "fixture.sqlite")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.con = policy.open_readonly(self.db)

    def tearDown(self):
        self.con.close()

    # 1. non-SELECT statements are denied before execution
    def test_write_and_schema_statements_are_denied_by_text_check(self):
        for sql in ("DELETE FROM lca", "UPDATE lca SET CASE_STATUS='x'", "INSERT INTO lca VALUES (1)",
                    "DROP TABLE lca", "ATTACH DATABASE 'x.db' AS x", "PRAGMA table_info(lca)",
                    "CREATE TABLE t (a)", "VACUUM"):
            with self.subTest(sql=sql):
                self.assertFalse(policy.check_text(sql).allowed)
                with self.assertRaises(policy.PolicyDenied):
                    policy.execute(self.con, sql, 2, 5)

    # 2. a second statement after a semicolon is denied
    def test_hidden_second_statement_is_denied(self):
        verdict = policy.check_text("SELECT COUNT(*) FROM lca; DROP TABLE lca")
        self.assertFalse(verdict.allowed)
        self.assertIn("more than one statement", verdict.reason)
        self.assertTrue(policy.check_text("SELECT COUNT(*) FROM lca;").allowed)

    # 3. other tables are denied by the authorizer at execution time
    def test_other_tables_are_denied_by_authorizer(self):
        for sql in ("SELECT * FROM metadata", "SELECT * FROM sqlite_master",
                    "SELECT * FROM pragma_table_info('lca')"):
            with self.subTest(sql=sql):
                self.assertTrue(policy.check_text(sql).allowed)  # text layer lets it through
                with self.assertRaises(policy.PolicyDenied):     # SQLite layer stops it
                    policy.execute(self.con, sql, 2, 5)

    # 4. a runaway query is interrupted by the time budget
    def test_runaway_query_is_interrupted(self):
        sql = "SELECT COUNT(*) FROM lca a, lca b, lca c, lca d, lca e, lca f, lca g"
        with self.assertRaises(policy.BudgetExceeded):
            policy.execute(self.con, sql, 0.05, 5)

    def test_reads_are_allowed_and_literals_are_not_keywords(self):
        result = policy.execute(self.con, "SELECT COUNT(*) FROM lca WHERE JOB_TITLE = 'delete me'", 2, 5)
        self.assertEqual(result.rows, [(0,)])
        result = policy.execute(self.con, "WITH x AS (SELECT * FROM lca) SELECT COUNT(*) FROM x", 2, 5)
        self.assertEqual(result.rows, [(12,)])

    def test_comments_and_recursion_are_denied(self):
        self.assertFalse(policy.check_text("SELECT 1 -- hide").allowed)
        self.assertFalse(policy.check_text("SELECT /* x */ 1").allowed)
        with self.assertRaises(policy.PolicyDenied):
            policy.execute(self.con, "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM r) "
                                     "SELECT COUNT(*) FROM r", 2, 5)

    def test_connection_is_read_only_even_without_the_text_check(self):
        with self.assertRaises(Exception):
            self.con.execute("DELETE FROM lca")

    def test_row_cap_counts_but_does_not_keep_extra_rows(self):
        result = policy.execute(self.con, "SELECT sheet_row FROM lca", 2, 5)
        self.assertEqual((result.total_rows, len(result.rows), result.truncated), (12, 5, True))


class TitleMatchTests(unittest.TestCase):
    def test_title_has_matches_whole_normalized_phrase(self):
        self.assertEqual(udf.title_has("Data-Analyst", "data analyst"), 1)
        self.assertEqual(udf.title_has("Senior Data  Analyst II", "data analyst"), 1)
        self.assertEqual(udf.title_has("Metadata Analyst", "data analyst"), 0)
        self.assertEqual(udf.title_has("Data Analysts", "data analyst"), 0)
        self.assertEqual(udf.title_has(None, "data analyst"), 0)
        self.assertEqual(udf.title_has("Data Analyst", ""), 0)


if __name__ == "__main__":
    unittest.main()
