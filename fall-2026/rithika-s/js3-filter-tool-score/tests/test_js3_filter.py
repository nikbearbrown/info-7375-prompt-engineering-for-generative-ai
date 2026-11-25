"""JS3 filter tests (FILTER.md v1.0) on CONSTRUCTED postings."""

import html
import tempfile
import unittest

import js3_fixtures as fx
from js3 import corpus
from js3.filter import evaluate

CONFIG = fx.CONFIG


def run(title, body):
    return evaluate(fx.post(title, body), CONFIG)


def words(result, rule):
    return sorted({m["word"] for m in result["matches"] if m["rule"] == rule})


class ConfigTranscribesFilterMd(unittest.TestCase):

    def test_v1_0_values(self):
        r = CONFIG["rules"]
        self.assertEqual(CONFIG["version"], "1.0")
        self.assertEqual(CONFIG["threshold"], 4)
        self.assertEqual(r["R1"]["words"], [
            "ai engineer", "ml engineer", "machine learning",
            "data engineer", "ml infrastructure", "ml platform"])
        self.assertEqual((r["R1"]["weight"], r["R1"]["field"]), (3, "title"))
        self.assertEqual(r["R2"]["words"], [
            "llm", "pytorch", "tensorflow", "inference", "training",
            "embedding", "retrieval", "mlops", "model", "spark"])
        self.assertEqual((r["R2"]["weight_per_distinct_word"],
                          r["R2"]["cap"]), (1, 3))
        self.assertEqual(r["R3"]["words"], ["clearance"])
        self.assertEqual(r["R3"]["fields"], ["title", "body_text"])
        self.assertEqual(r["R4"]["words"],
                         ["manager", "director", "head of", "vp"])
        self.assertEqual(r["R4"]["field"], "title")


class R1RoleWords(unittest.TestCase):

    def test_title_role_word_scores_3_with_exact_span(self):
        res = run("Senior ML Engineer, Search", "We ship features.")
        self.assertEqual(res["rule_scores"]["R1"], 3)
        self.assertIn("R1", res["fired"])
        [m] = [m for m in res["matches"] if m["rule"] == "R1"]
        self.assertEqual((m["word"], m["field"], m["span"]),
                         ("ml engineer", "title", "ML Engineer"))
        self.assertEqual("Senior ML Engineer, Search"[m["start"]:m["end"]],
                         "ML Engineer")

    def test_counted_once_even_with_several_role_words(self):
        res = run("Machine Learning Engineer, ML Platform", "Nothing.")
        self.assertEqual(words(res, "R1"), ["machine learning", "ml platform"])
        self.assertEqual(res["rule_scores"]["R1"], 3)
        self.assertEqual(res["score"], 3)

    def test_no_role_word_scores_0(self):
        res = run("Software Engineer", "Nothing.")
        self.assertEqual(res["rule_scores"]["R1"], 0)
        self.assertNotIn("R1", res["fired"])


class R2TopicWords(unittest.TestCase):

    def test_one_point_per_distinct_word(self):
        res = run("Analyst", "model, model and MODEL with PyTorch")
        self.assertEqual(words(res, "R2"), ["model", "pytorch"])
        self.assertEqual(res["rule_scores"]["R2"], 2)
        # every occurrence is still reported with its span
        spans = [m["span"] for m in res["matches"] if m["word"] == "model"]
        self.assertEqual(spans, ["model", "model", "MODEL"])

    def test_cap_of_3(self):
        res = run("ML Engineer",
                  "LLM training, inference, embedding and retrieval")
        self.assertEqual(len(words(res, "R2")), 5)
        self.assertEqual(res["rule_scores"]["R2"], 3)
        self.assertEqual(res["score"], 6)

    def test_spans_index_body_text(self):
        body = "Work on large-scale Inference systems."
        res = run("Analyst", body)
        [m] = res["matches"]
        self.assertEqual(body[m["start"]:m["end"]], "Inference")
        self.assertEqual(m["field"], "body_text")

    def test_topic_words_in_title_do_not_count(self):
        res = run("Model Training Lead", "Nothing here.")
        self.assertEqual(res["rule_scores"]["R2"], 0)


class R3Clearance(unittest.TestCase):

    def test_clearance_in_body_rejects_high_score(self):
        res = run("ML Engineer", "PyTorch, LLM, inference. Active "
                                 "security clearance required.")
        self.assertEqual(res["score"], 6)
        self.assertEqual(res["decision"], "rejected")
        self.assertIn("R3", res["fired"])
        self.assertEqual(res["reason"], "excluded by R3")

    def test_clearance_in_title_any_case(self):
        res = run("ML Engineer (CLEARANCE)", "PyTorch, LLM, inference.")
        self.assertEqual(res["decision"], "rejected")
        [m] = [m for m in res["matches"] if m["rule"] == "R3"]
        self.assertEqual((m["field"], m["span"]), ("title", "CLEARANCE"))

    def test_clearance_matches_anywhere_not_only_whole_word(self):
        # FILTER.md: "clearance anywhere", no whole-word condition for R3.
        res = run("ML Engineer", "PyTorch, LLM. Clearances needed.")
        self.assertEqual(res["decision"], "rejected")


class R4ManagementTitles(unittest.TestCase):

    def test_each_word_rejects(self):
        for title in ("ML Engineering Manager", "Director, Machine Learning",
                      "Head of ML Platform", "VP, Machine Learning",
                      "vp machine learning"):
            with self.subTest(title=title):
                res = run(title, "PyTorch, LLM, inference.")
                self.assertEqual(res["decision"], "rejected")
                self.assertIn("R4", res["fired"])

    def test_whole_words_only(self):
        for title in ("ML Engineer, VPN", "ML Engineer, Managerial Tools",
                      "ML Engineer, Head Office"):
            with self.subTest(title=title):
                res = run(title, "PyTorch, LLM, inference.")
                self.assertNotIn("R4", res["fired"])
                self.assertEqual(res["decision"], "kept")

    def test_r4_body_mention_does_not_reject(self):
        res = run("ML Engineer", "Report to the director. PyTorch.")
        self.assertEqual(res["decision"], "kept")


class Threshold(unittest.TestCase):

    def test_score_3_title_only_is_rejected(self):
        res = run("Data Engineer", "Build pipelines.")
        self.assertEqual((res["score"], res["decision"]), (3, "rejected"))

    def test_score_3_topic_words_only_is_rejected(self):
        res = run("Analyst", "LLM inference and training.")
        self.assertEqual((res["score"], res["decision"]), (3, "rejected"))

    def test_score_4_is_kept(self):
        res = run("Data Engineer", "Build Spark pipelines.")
        self.assertEqual((res["score"], res["decision"]), (4, "kept"))
        self.assertEqual(res["reason"], "score 4 >= 4")


class EmptyBody(unittest.TestCase):

    def test_empty_and_blank_body_abstain(self):
        for body in ("", "   \n ", None):
            with self.subTest(body=body):
                res = run("ML Engineer", body)
                self.assertEqual(res["decision"], "abstain")
                self.assertEqual(res["reason"], "no body")
                self.assertIsNone(res["rule_scores"]["R2"])
                self.assertEqual(res["score"], 3)

    def test_exclusion_still_rejects_without_body(self):
        res = run("ML Engineering Manager", "")
        self.assertEqual(res["decision"], "rejected")


class WholeWordPhrases(unittest.TestCase):

    def test_phrase_inside_longer_words_does_not_match(self):
        for title in ("HTML Engineer", "Thai Engineer",
                      "Machine Learnings", "XML Platform"):
            with self.subTest(title=title):
                self.assertEqual(run(title, "x")["rule_scores"]["R1"], 0)

    def test_phrase_matches_across_any_whitespace_and_punctuation(self):
        for title in ("Machine  Learning Engineer", "ML\tEngineer",
                      "Applied AI Engineer", "ML/AI Engineer",
                      "Engineer (Machine Learning)"):
            with self.subTest(title=title):
                self.assertEqual(run(title, "x")["rule_scores"]["R1"], 3)

    def test_topic_word_inside_longer_word_does_not_match(self):
        res = run("Analyst", "Models, LLMs, embeddings, sparkle, pretraining")
        self.assertEqual(res["rule_scores"]["R2"], 0)

    def test_non_latin_neighbour_is_a_boundary(self):
        res = run("Analyst", "LLMを活用したモデル")
        self.assertEqual(words(res, "R2"), ["llm"])


class Corpus(unittest.TestCase):

    def test_html_to_text_unescapes_strips_and_collapses(self):
        raw = html.escape("<p>Use&nbsp;<b>PyTorch</b>&amp;\n\n Spark</p>"
                          "<p>daily</p><script>x()</script>")
        self.assertEqual(corpus.html_to_text(raw), "Use PyTorch & Spark daily")

    def test_hash_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx.make_corpus(tmp, corrupt=True)
            with self.assertRaises(corpus.CorpusHashMismatch):
                corpus.load(tmp)

    def test_matching_hash_loads_postings(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx.make_corpus(tmp)
            data = corpus.load(tmp)
        self.assertEqual(len(data["postings"]), 120)
        first = data["postings"][0]
        self.assertEqual(set(first), {"board", "id", "title", "location",
                                      "url", "body_text"})
        self.assertEqual(first["body_text"], "You will use PyTorch and Spark.")
        self.assertEqual(data["boards"]["constructed"]["status"], "evaluated")

    def test_missing_file_is_not_evaluated_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx.make_corpus(tmp, missing=True)
            data = corpus.load(tmp)
        info = data["boards"]["constructed"]
        self.assertEqual(info["status"], "not evaluated")
        self.assertNotIn("postings", info)

    def test_board_outside_manifest_is_not_evaluated(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx.make_corpus(tmp)
            data = corpus.load(tmp)
        self.assertEqual(data["boards"]["constructed-404"]["status"],
                         "not evaluated")

    def test_frozen_corpus_files_match_manifest(self):
        for rel_path, expected in corpus.read_manifest():
            with self.subTest(file=rel_path):
                self.assertEqual(corpus.sha256_of(corpus.ROOT / rel_path),
                                 expected)


if __name__ == "__main__":
    unittest.main()
