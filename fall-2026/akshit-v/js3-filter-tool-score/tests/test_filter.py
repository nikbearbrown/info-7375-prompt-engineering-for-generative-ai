"""FILTER.md v1.0 rule by rule (F2-F9). All postings here are CONSTRUCTED."""
import unittest

from agent3 import filter as flt

PAD = " Our team writes clearly, reviews code carefully, and ships steadily." * 6


def P(title, text, board="greenhouse:figma", et=None, pid="c"):
    return {"id": f"{board}:{pid}", "board": board, "title": title, "content_text": text + PAD, "employment_type": et}


class Rules(unittest.TestCase):
    def test_f2_title_disqualifier_whole_word(self):
        self.assertEqual(flt.apply(P("Staff Data Engineer", "Python SQL Spark"))["verdict"], "reject")
        # "Internal" must not match "Intern"; "Managerial" must not match "Manager"
        r = flt.apply(P("Data Engineer, Internal Tools", "Python SQL Spark"))
        self.assertEqual(r["disqualified_by"], [])

    def test_f3_structured_employment_type(self):
        self.assertEqual(flt.apply(P("Data Engineer", "Python SQL", "ashby:snowflake", "Intern"))["disqualified_by"],
                         ["employment_type:Intern"])
        self.assertEqual(flt.apply(P("Data Engineer", "Python SQL", "lever:spotify", "Short Term"))["disqualified_by"],
                         ["employment_type:Short Term"])
        # missing is unknown, never a reject
        self.assertEqual(flt.apply(P("Data Engineer", "Python SQL", "lever:spotify", None))["disqualified_by"], [])
        self.assertEqual(flt.apply(P("Data Engineer", "Python SQL", "greenhouse:figma", None))["disqualified_by"], [])

    def test_f5_topic_groups_count_once_and_cap(self):
        text = ("data pipelines, ETL, ELT, data warehouse, data lake, data modeling, orchestration, "
                "streaming, batch jobs, data quality")
        r = flt.apply(P("Engineer", text))
        self.assertEqual(len(r["topic_hits"]), 7)
        self.assertEqual(r["topics"], 4)

    def test_f6_whole_word_skills(self):
        r = flt.apply(P("Engineer", "PostgreSQL, NoSQL, Washington, Sparkle, sparkling"))
        self.assertEqual(r["skill_hits"], {})

    def test_f7_score_and_threshold(self):
        r = flt.apply(P("Analytics Engineer", "dbt and SQL"))
        self.assertEqual((r["role"], r["topics"], r["skills"], r["score"], r["verdict"]), (4, 0, 2, 6, "keep"))
        r = flt.apply(P("Software Engineer", "Python, SQL, Spark, Kafka, ETL"))
        self.assertEqual((r["role"], r["topics"], r["skills"], r["score"], r["verdict"]), (0, 1, 4, 5, "reject"))

    def test_f8_short_text_cannot_tell(self):
        p = {"id": "greenhouse:figma:c", "board": "greenhouse:figma", "title": "Data Engineer",
             "content_text": "x" * 299, "employment_type": None}
        self.assertEqual(flt.apply(p)["verdict"], "cannot_tell")
        p["content_text"] = "x" * 300
        self.assertNotEqual(flt.apply(p)["verdict"], "cannot_tell")

    def test_f9_ranking_ties(self):
        a = P("Data Engineer", "Python SQL", pid="a")                 # 4 + 2 = 6, role
        b = P("Engineer", "Python SQL Spark Kafka dbt AWS", pid="b")  # 0 + 6 = 6, no role
        c = P("Engineer", "Python SQL Spark Kafka dbt AWS Airflow", pid="c")  # 7
        res = flt.run([b, a, c])
        self.assertEqual(res["ranked"], [c["id"], a["id"], b["id"]])

    def test_close_call_band(self):
        r5 = flt.apply(P("Data Engineer", "Python"))
        r8 = flt.apply(P("Data Engineer", "Python SQL Spark Kafka"))
        self.assertTrue(flt.is_close_call(r5))
        self.assertFalse(flt.is_close_call(r8))

    def test_results_keyed_by_id_not_position(self):
        ps = [P("Data Engineer", "Python SQL", pid=str(i)) for i in range(3)] + [P("Recruiter", "people", pid="x")]
        res = flt.run(list(reversed(ps)))
        self.assertEqual(res["results"]["greenhouse:figma:x"]["verdict"], "reject")
        self.assertEqual({res["results"][p["id"]]["id"] for p in ps}, {p["id"] for p in ps})


if __name__ == "__main__":
    unittest.main()
