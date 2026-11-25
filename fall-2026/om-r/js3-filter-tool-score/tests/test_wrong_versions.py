"""The two "Wrong versions" tests from FILTER.md, written BEFORE the real
filter and grounding modules existed.

Implementations are chosen by environment variable (defaults are the real
modules):

    JS3_FILTER_IMPL=js3.wrong_stub_filter \\
    JS3_GROUNDING_IMPL=js3.wrong_stub_grounding \\
        python3 -m unittest -v tests.test_wrong_versions

Interface every implementation must provide (fixed here, before the code):

  filter module
    classify(posting) -> result dict
        result["bucket"]   "relevant" | "rejected" | "insufficient_data"
        result["id"], result["board"], result["title"]
        result["reasons"]  [str, ...]  why it landed in that bucket
    run_filter(postings) -> {"results": [...], "relevant": [...],
                             "rejected": [...], "insufficient_data": [...]}
    reject_sampling_pool(filter_output) -> [result, ...]
        the postings the reject audit may sample from

  grounding module
    label_claims(posting, claims) -> [labeled claim, ...]
        claims:  [{"claim": str, "quote": str | None}, ...]
        labeled: {"claim", "quote", "label", "field"}
        label in "supported" | "contradicted" | "insufficient"

A posting is {"board", "id", "title", "content", "url"}; content is the raw
field from the board (Greenhouse: HTML-escaped HTML; Lever: descriptionPlain).
All postings below are CONSTRUCTED fixtures; no network.
"""
import importlib
import os
import unittest

FILTER_IMPL = os.environ.get("JS3_FILTER_IMPL", "js3.filter")
GROUNDING_IMPL = os.environ.get("JS3_GROUNDING_IMPL", "js3.grounding")


def posting(pid, title, content, board="gitlab"):
    return {"board": board, "id": pid, "title": title, "content": content,
            "url": f"https://example.invalid/{pid}"}


# Content that clearly fails rule 1 (0 of 6 skill words) - a genuine reject.
NON_MATCHING = "&lt;p&gt;Manage vendor contracts and quarterly budget reviews.&lt;/p&gt;"


class WrongVersion1RejectBucketDropsInsufficientData(unittest.TestCase):
    """FILTER.md wrong version 1: an empty-content posting must be flagged
    insufficient_data - never "not relevant" - and must be excluded from the
    rejected bucket AND from the reject audit's sampling pool."""

    @classmethod
    def setUpClass(cls):
        cls.impl = importlib.import_module(FILTER_IMPL)

    EMPTY_CASES = [
        posting(101, "Backend Engineer", ""),                 # empty string
        posting(102, "Backend Engineer", None),               # null
        posting(103, "Backend Engineer", "   \n\t  "),        # whitespace only
        posting(104, "Backend Engineer", "&lt;p&gt; &lt;/p&gt;"),  # Greenhouse HTML with no text
        # Title alone would satisfy rule 1 - still no default verdict without content.
        posting(105, "Python LLM Engineer", ""),
        posting(106, "Python LLM Engineer", None, board="palantir"),
    ]

    def setUp(self):
        self.control = posting(200, "Procurement Manager", NON_MATCHING)
        self.postings = self.EMPTY_CASES + [self.control]
        self.out = self.impl.run_filter(self.postings)
        self.empty_ids = {p["id"] for p in self.EMPTY_CASES}

    def test_each_empty_posting_is_flagged_insufficient_data(self):
        for p in self.EMPTY_CASES:
            with self.subTest(id=p["id"], content=p["content"]):
                self.assertEqual(self.impl.classify(p)["bucket"], "insufficient_data")

    def test_empty_postings_are_in_neither_relevant_nor_rejected(self):
        rejected = {r["id"] for r in self.out["rejected"]}
        relevant = {r["id"] for r in self.out["relevant"]}
        flagged = {r["id"] for r in self.out["insufficient_data"]}
        self.assertEqual(self.empty_ids & rejected, set(), "empty-content postings leaked into rejected")
        self.assertEqual(self.empty_ids & relevant, set(), "empty-content postings leaked into relevant")
        self.assertEqual(flagged, self.empty_ids)

    def test_reject_sampling_pool_excludes_insufficient_data(self):
        pool = {r["id"] for r in self.impl.reject_sampling_pool(self.out)}
        self.assertEqual(self.empty_ids & pool, set(), "you can't hand-judge a posting with no text")
        # The control is a genuine reject and MUST be in the pool, so the test
        # can't pass by putting nothing anywhere.
        self.assertEqual(pool, {200})

    def test_buckets_partition_every_posting_exactly_once(self):
        ids = [r["id"] for b in ("relevant", "rejected", "insufficient_data") for r in self.out[b]]
        self.assertCountEqual(ids, [p["id"] for p in self.postings])


class WrongVersion2ClaimsLabeledWithoutGroundingCheck(unittest.TestCase):
    """FILTER.md wrong version 2: every claim must actually be checked against
    the posting's own text. "Supported" requires the cited quote to be an
    exact substring of posting.title or posting.content; anything else may
    not be labeled supported."""

    @classmethod
    def setUpClass(cls):
        cls.impl = importlib.import_module(GROUNDING_IMPL)

    POSTING = posting(
        300, "Senior ML Engineer, Search",
        "&lt;p&gt;You will build retrieval systems in Python and PyTorch.&lt;/p&gt;"
        "&lt;p&gt;This role is on-site in our Denver office five days a week.&lt;/p&gt;",
    )

    def label(self, claim, quote):
        out = self.impl.label_claims(self.POSTING, [{"claim": claim, "quote": quote}])
        self.assertEqual(len(out), 1)
        return out[0]

    def test_claim_with_exact_quote_in_content_is_supported(self):
        r = self.label("Uses PyTorch", "Python and PyTorch")
        self.assertEqual(r["label"], "supported")
        self.assertEqual(r["field"], "content")

    def test_claim_with_exact_quote_in_title_is_supported(self):
        r = self.label("Search-focused ML role", "ML Engineer, Search")
        self.assertEqual(r["label"], "supported")
        self.assertEqual(r["field"], "title")

    def test_claim_whose_quote_is_not_in_posting_is_not_supported(self):
        # Plausible, never mentioned: visa sponsorship.
        r = self.label("Sponsors visas", "visa sponsorship available")
        self.assertNotEqual(r["label"], "supported")
        self.assertIsNone(r["field"])

    def test_claim_with_no_quote_is_not_supported(self):
        r = self.label("Team uses LangChain", None)
        self.assertNotEqual(r["label"], "supported")

    def test_empty_or_blank_quote_is_not_supported(self):
        # "" is a substring of every string; it must not count as grounding.
        for q in ["", "   "]:
            with self.subTest(quote=q):
                self.assertNotEqual(self.label("Uses PyTorch", q)["label"], "supported")

    def test_paraphrased_or_recased_quote_is_not_supported(self):
        # FILTER.md: exact substring. A recased quote is not an exact substring.
        r = self.label("Uses PyTorch", "python and pytorch")
        self.assertNotEqual(r["label"], "supported")

    def test_mixed_batch_is_labeled_per_claim_not_uniformly(self):
        out = self.impl.label_claims(self.POSTING, [
            {"claim": "Uses Python", "quote": "in Python and PyTorch"},
            {"claim": "Remote-friendly", "quote": "fully remote"},
            {"claim": "Builds retrieval", "quote": "build retrieval systems"},
        ])
        self.assertEqual([r["label"] == "supported" for r in out], [True, False, True])


if __name__ == "__main__":
    unittest.main()
