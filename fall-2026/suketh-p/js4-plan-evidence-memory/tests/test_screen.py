"""FILTER.md v0.1 (the student's) as tests, written before jobwatch/screen.py existed.

Every posting here is CONSTRUCTED. The four cases in the 'Student's wrong versions' class
are the student's own, word for word from FILTER.md 'Wrong versions'. The other cases are
Claude Code's, each taken from a sentence of FILTER.md that the test names."""

import unittest

from jobwatch import screen


def item(title, description="", location="San Francisco, CA", board="greenhouse/anthropic", key="1"):
    return screen.Item(board=board, key=key, title=title, location=location,
                       description=description, captured_at="2026-11-24T22:36:19Z")


class StudentsWrongVersionsTest(unittest.TestCase):
    """FILTER.md 'Wrong versions': the cases that should catch them."""

    def test_wv1_model_serving_with_go_and_grpc_is_kept_with_score_3(self):
        # "Software Engineer, Model Serving lists Go and gRPC. Keep it with score 3."
        record = screen.score(item("Software Engineer, Model Serving",
                                   "<p>You will write Go and gRPC services.</p>"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 3))

    def test_wv2_generic_title_with_model_serving_in_description_is_kept_with_score_2(self):
        # "Software Engineer says 'Build model serving systems.' Keep it with score 2."
        record = screen.score(item("Software Engineer", "<p>Build model serving systems.</p>"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 2))

    def test_wv3_ai_in_hiring_text_is_rejected_with_score_1(self):
        # "Software Engineer, Internal Tools says 'We use AI to schedule interviews.' Reject it with score 1."
        record = screen.score(item("Software Engineer, Internal Tools",
                                   "<p>We use AI to schedule interviews.</p>"))
        self.assertEqual((record["fate"], record["score"]), ("rejected", 1))


class RoleAndLevelTest(unittest.TestCase):
    def test_a_title_without_engineer_or_developer_is_rejected_even_with_topic_points(self):
        # "Require engineer or developer in the title."
        record = screen.score(item("Research Scientist, Machine Learning"))
        self.assertEqual(record["fate"], "rejected")
        self.assertIn("role", record["reasons"])
        self.assertEqual(record["score"], 2)

    def test_developer_counts_as_a_role_word(self):
        record = screen.score(item("ML Developer"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 3))

    def test_engineering_is_not_the_whole_word_engineer(self):
        # "match whole words"
        record = screen.score(item("Machine Learning Engineering"))
        self.assertIn("role", record["reasons"])

    def test_each_level_word_rejects_the_title(self):
        # "Reject titles containing senior, sr, staff, principal, lead, manager, director, head, intern, or internship."
        for title in ("Senior ML Engineer", "Sr. ML Engineer", "Staff ML Engineer", "Principal ML Engineer",
                      "Lead ML Engineer", "ML Engineer Manager", "Director, ML Engineer", "Head of ML Engineer",
                      "ML Engineer Intern", "ML Engineer Internship"):
            with self.subTest(title=title):
                record = screen.score(item(title))
                self.assertEqual(record["fate"], "rejected")
                self.assertIn("level", record["reasons"])

    def test_a_senior_colleague_in_the_description_has_no_effect(self):
        # "a senior colleague mentioned in the description has no effect"
        record = screen.score(item("ML Engineer", "<p>You will pair with a senior staff engineer and a lead.</p>"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 3))


class TopicPointsTest(unittest.TestCase):
    def test_each_title_topic_earns_two_points(self):
        # "Add 2 points for machine learning, ml, ai, inference, model serving, data engineer,
        # data platform, or data infrastructure."
        for title in ("Machine Learning Engineer", "ML Engineer", "AI Engineer", "Inference Engineer",
                      "Model Serving Engineer", "Data Engineer", "Data Platform Engineer",
                      "Data Infrastructure Engineer"):
            with self.subTest(title=title):
                record = screen.score(item(title))
                self.assertEqual((record["fate"], record["score"]), ("kept", 3))

    def test_each_description_topic_earns_one_point_for_a_generic_title(self):
        # "If the title earns no topic points, add 1 point for machine learning, model inference,
        # model serving, ml infrastructure, data pipeline, data pipelines, or data platform."
        for phrase in ("machine learning", "model inference", "model serving", "ml infrastructure",
                       "data pipeline", "data pipelines", "data platform"):
            with self.subTest(phrase=phrase):
                record = screen.score(item("Software Engineer", f"<p>You will work on {phrase}.</p>"))
                self.assertEqual((record["fate"], record["score"]), ("kept", 2))

    def test_no_description_point_when_the_title_already_earned_topic_points(self):
        # "If the title earns no topic points, add 1 point"
        record = screen.score(item("ML Engineer", "<p>machine learning and data pipelines</p>"))
        self.assertEqual(record["score"], 3)

    def test_two_different_title_topics_earn_two_points_once(self):
        # Claude Code's reading of "Add 2 points for ... or data infrastructure": one award, not one per term.
        record = screen.score(item("ML Engineer, AI Inference"))
        self.assertEqual(record["score"], 3)

    def test_repeating_a_term_earns_no_extra_points(self):
        # "Repeating a term earns no extra points."
        text = "<p>" + "model serving " * 5 + "</p>"
        record = screen.score(item("Software Engineer", text))
        self.assertEqual(record["score"], 2)

    def test_whole_words_only(self):
        # "match whole words or consecutive word sequences": ai is not inside maintain or email,
        # ml is not inside html, and the words of a phrase must be consecutive.
        record = screen.score(item("Software Engineer, Email",
                                   "<p>Maintain HTML email templates. Model and serving teams.</p>"))
        self.assertEqual((record["fate"], record["score"]), ("rejected", 1))

    def test_html_is_decoded_before_matching(self):
        # "Decode HTML, lowercase the text"
        record = screen.score(item("Software Engineer", "&lt;p&gt;Build DATA&amp;nbsp;PIPELINES&lt;/p&gt;"))
        self.assertEqual(record["score"], 2)


class CutoffAndRankingTest(unittest.TestCase):
    def test_score_two_is_kept_and_score_one_is_rejected(self):
        # "Keep postings that pass the role and level rules and score at least 2."
        self.assertEqual(screen.score(item("Software Engineer", "<p>data platform</p>"))["fate"], "kept")
        self.assertEqual(screen.score(item("Software Engineer", "<p>web apps</p>"))["fate"], "rejected")

    def test_rank_by_score_then_board_then_key_as_text(self):
        # "Rank by descending score, then by board identifier and posting key."
        # Claude Code's reading: board and key compare as text, so "10" sorts before "9".
        records = [screen.score(i) for i in (
            item("Software Engineer", "<p>data platform</p>", board="ashby/linear", key="https://x/b"),
            item("ML Engineer", board="greenhouse/databricks", key="9"),
            item("ML Engineer", board="greenhouse/anthropic", key="9"),
            item("ML Engineer", board="greenhouse/anthropic", key="10"),
            item("ML Engineer", board="ashby/linear", key="https://x/a"),
            item("Software Engineer", "<p>web apps</p>", board="ashby/linear", key="https://x/c"),
        )]
        ranked = [(r["board"], r["key"]) for r in screen.rank(records)]
        self.assertEqual(ranked, [
            ("ashby/linear", "https://x/a"),
            ("greenhouse/anthropic", "10"),
            ("greenhouse/anthropic", "9"),
            ("greenhouse/databricks", "9"),
            ("ashby/linear", "https://x/b"),
        ])

    def test_rank_does_not_depend_on_input_order(self):
        items = [item("ML Engineer", board="greenhouse/anthropic", key=k) for k in ("3", "1", "2")]
        forward = [r["key"] for r in screen.rank([screen.score(i) for i in items])]
        backward = [r["key"] for r in screen.rank([screen.score(i) for i in reversed(items)])]
        self.assertEqual(forward, ["1", "2", "3"])
        self.assertEqual(backward, forward)

    def test_rejected_records_are_not_ranked(self):
        records = [screen.score(item("Senior ML Engineer")), screen.score(item("ML Engineer", key="2"))]
        self.assertEqual([r["key"] for r in screen.rank(records)], ["2"])


class BlankDescriptionTest(unittest.TestCase):
    def test_a_title_match_is_retained_when_the_description_is_blank(self):
        # "If the normalized description is blank, retain any title-based match"
        record = screen.score(item("ML Engineer", "<p>  </p>"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 3))

    def test_an_unresolved_topic_decision_stays_open_for_review(self):
        # "... and leave any unresolved topic decision open for review."
        record = screen.score(item("Software Engineer", ""))
        self.assertEqual(record["fate"], "review")
        self.assertIn("description blank", record["review_reasons"])


class LocationTest(unittest.TestCase):
    """FILTER.md: 'An explicit U.S. work location fits the search. A posting limited to locations
    outside the U.S. falls out of scope. Remote by itself leaves the country unresolved, so the agent
    keeps it visible for review.' The words come from the student's choice 'Country or state'."""

    def outcome(self, location):
        return screen.score(item("ML Engineer", location=location))

    def test_us_country_words_and_states(self):
        for location in ("United States", "Remote - US", "Remote (USA)", "U.S. (Remote)",
                         "San Francisco, CA", "Seattle, Washington", "New York City, NY"):
            with self.subTest(location=location):
                self.assertEqual(self.outcome(location)["location"]["outcome"], "us")
                self.assertEqual(self.outcome(location)["fate"], "kept")

    def test_only_other_countries_falls_out_of_scope(self):
        for location in ("London, United Kingdom", "London, UK", "Toronto, Canada", "Remote - Canada"):
            with self.subTest(location=location):
                record = self.outcome(location)
                self.assertEqual(record["location"]["outcome"], "outside")
                self.assertEqual(record["fate"], "rejected")
                self.assertIn("location", record["reasons"])

    def test_any_us_location_counts_as_us(self):
        record = self.outcome("London, UK | New York, NY")
        self.assertEqual((record["location"]["outcome"], record["fate"]), ("us", "kept"))

    def test_remote_regions_bare_cities_and_blank_go_to_review(self):
        for location in ("Remote", "North America", "Zurich", "", "Anywhere"):
            with self.subTest(location=location):
                record = self.outcome(location)
                self.assertEqual(record["location"]["outcome"], "unresolved")
                self.assertEqual(record["fate"], "review")
                self.assertIn("location unresolved", record["review_reasons"])

    def test_the_known_risk_two_letter_codes(self):
        # The option the student chose names this risk: "CA can mean Canada, IN India."
        # The code does what the option says, so these read as U.S. The reject audit and the
        # kept sample are where such false matches get measured.
        self.assertEqual(self.outcome("Toronto, CA")["location"]["outcome"], "us")
        self.assertEqual(self.outcome("Bengaluru, IN")["location"]["outcome"], "us")

    def test_a_non_us_location_does_not_change_the_score(self):
        self.assertEqual(self.outcome("London, UK")["score"], 3)


class RecordTest(unittest.TestCase):
    def test_the_record_shows_every_match_so_a_score_can_be_recomputed_by_hand(self):
        record = screen.score(item("Software Engineer", "<p>We build data pipelines.</p>"))
        self.assertEqual(record["parts"], {"role": 1, "title_topic": 0, "description_topic": 1})
        self.assertEqual(record["matched"]["role"], ["engineer"])
        self.assertEqual(record["matched"]["description_topic"], ["data pipelines"])
        self.assertEqual(record["filter_version"], "v0.1")


if __name__ == "__main__":
    unittest.main()
