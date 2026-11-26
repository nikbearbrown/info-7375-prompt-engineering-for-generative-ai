"""Tests written from FILTER.md v1 before jsagent3/filter.py existed. Each test names the rule it checks."""
import unittest

from jsagent3.filter import decide, is_us, level_excluded, load_rules, role_match, topic_hits

RULES = load_rules()


def P(title, body="", location="San Francisco, CA", pid="t:1"):
    return {"id": pid, "board": "t", "title": title, "body": body, "location": location, "url": ""}


STACK = "Requirements\n- Java and Spring Boot\n- SQL"


class RoleWords(unittest.TestCase):
    def test_each_role_phrase_matches(self):  # F-ROLE R1-R6
        for t, rid in [("Backend Engineer, Payments", "R1"), ("Java Developer", "R2"),
                       ("Software Engineer, Intern", "R3"), ("Full Stack Engineer, Link", "R4"),
                       ("Software Developer II", "R5"), ("Platform Engineer", "R6")]:
            self.assertEqual(role_match(t, RULES), rid, t)

    def test_spelling_variants(self):  # F-ROLE variants
        for t in ["Back-end Engineer", "Back End Engineer", "Full-Stack Engineer", "Fullstack Engineer"]:
            self.assertIsNotNone(role_match(t, RULES), t)

    def test_non_role_titles(self):
        for t in ["Account Executive", "Data Scientist", "Product Designer", "Engineering Manager"]:
            self.assertIsNone(role_match(t, RULES), t)


class WrongVersions(unittest.TestCase):
    def test_W1_engineer_alone_is_not_enough(self):  # FILTER.md s7 W1
        for t in ["Hardware Engineer", "Electrical Engineer", "Mechanical Engineer", "Solutions Engineer"]:
            d = decide(P(t, STACK + "\n- AWS"), RULES)
            self.assertFalse(d["keep"], t)

    def test_W2_java_mention_without_role_title_rejected(self):  # W2, filter half
        d = decide(P("Data Analyst", STACK + "\n- AWS\n- PostgreSQL"), RULES)
        self.assertFalse(d["keep"])

    def test_W3_javascript_is_not_java(self):  # W3
        self.assertNotIn("T1", topic_hits("We use JavaScript and TypeScript.", RULES))
        self.assertIn("T1", topic_hits("We use Java/Kotlin.", RULES))


class TopicWords(unittest.TestCase):
    def test_nosql_is_not_sql(self):
        self.assertNotIn("T5", topic_hits("Experience with NoSQL stores", RULES))
        self.assertIn("T5", topic_hits("Strong SQL skills", RULES))

    def test_rest_is_case_sensitive(self):
        self.assertNotIn("T3", topic_hits("Work with the rest of the team", RULES))
        for s in ["Design REST APIs", "RESTful services", "a REST API"]:
            self.assertIn("T3", topic_hits(s, RULES), s)

    def test_distinct_words_count_once(self):  # s2: each distinct word adds 1
        self.assertEqual(sorted(topic_hits("Java Java Java SQL", RULES)), ["T1", "T5"])


class LevelAndUS(unittest.TestCase):
    def test_L1_seniority_rejects(self):
        for t in ["Senior Software Engineer", "Staff Backend Engineer", "Principal Software Engineer",
                  "Lead Software Engineer", "Sr. Software Engineer", "Software Engineer, Tech Lead"]:
            self.assertIsNotNone(level_excluded(t), t)
            self.assertFalse(decide(P(t, STACK), RULES)["keep"], t)

    def test_L1_does_not_fire_on_substrings(self):
        self.assertIsNone(level_excluded("Software Engineer, Leadership Tools"))

    def test_U1_us_detection(self):
        self.assertTrue(is_us("San Francisco, CA"))
        self.assertTrue(is_us("US-Remote, Chicago, Seattle"))
        self.assertTrue(is_us("New York, New York (United States)"))
        self.assertFalse(is_us("Dublin"))
        self.assertFalse(is_us("Toronto, Canada"))
        self.assertIsNone(is_us(""))
        self.assertIsNone(is_us("N/A"))

    def test_U1_prefers_never_rejects(self):
        d = decide(P("Software Engineer", STACK, location="Dublin"), RULES)
        self.assertTrue(d["keep"])
        us = decide(P("Software Engineer", STACK, location="Seattle, WA"), RULES)
        self.assertEqual(us["rank"], d["rank"] + 1)


class Threshold(unittest.TestCase):
    def test_keep_needs_two_topic_words(self):  # s4
        self.assertFalse(decide(P("Software Engineer", "We use Java."), RULES)["keep"])
        self.assertTrue(decide(P("Software Engineer", "We use Java and SQL."), RULES)["keep"])

    def test_close_call_band(self):  # s4: score 1 or 2 with role match, not L1
        self.assertTrue(decide(P("Software Engineer", "Java."), RULES)["close_call"])
        self.assertTrue(decide(P("Software Engineer", "Java, SQL."), RULES)["close_call"])
        self.assertFalse(decide(P("Software Engineer", "Java, SQL, AWS."), RULES)["close_call"])
        self.assertFalse(decide(P("Account Executive", "Java."), RULES)["close_call"])

    def test_missing_body_is_reported_not_silent(self):  # s6
        d = decide(P("Software Engineer", ""), RULES)
        self.assertFalse(d["keep"])
        self.assertEqual(d["reason"], "body missing")

    def test_every_decision_has_a_reason(self):
        for p in [P("Account Executive", "x"), P("Senior Software Engineer", STACK), P("Software Engineer", STACK)]:
            self.assertTrue(decide(p, RULES)["reason"])


if __name__ == "__main__":
    unittest.main()
