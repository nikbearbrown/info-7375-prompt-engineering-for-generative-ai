"""FILTER.md 'Wrong versions' as code: plausible filters and rankings that must NOT pass.

WV1-WV4 are the student's (FILTER.md). C1-C7 are Claude Code's additions, each built from
a sentence of FILTER.md. tests/test_js3_wrong_versions_caught.py swaps each one in and
checks that every test named for it fails, the same mechanism JS2 used."""

from jobwatch import evidence, location, screen
from jobwatch.normalize import contains_phrase, tokens

_REAL_SCORE = screen.score
_REAL_FINAL_LABEL = evidence.final_label
_REAL_CLASSIFY = location.classify

JS1_SKILLS = ("sql", "spark", "pytorch", "aws", "docker")


# WV1 (student): keep the old Python-plus-one-skill gate.
def score_with_the_old_skills_gate(item):
    record = _REAL_SCORE(item)
    words = tokens(item.description)
    if not (contains_phrase(words, "python") and any(contains_phrase(words, s) for s in JS1_SKILLS)):
        record = dict(record, fate="rejected", reasons=record["reasons"] + ["skills"])
    return record


# WV2 (student): look for topics only in titles.
def no_description_topics(description_tokens):
    return []


# WV3 (student): count any mention of AI in the description.
DESCRIPTION_TOPICS_WITH_AI = screen.DESCRIPTION_TOPICS + ("ai",)


# WV4 (student): treat an exact quote as sufficient evidence.
def quote_found_means_supported(human_label, quote_check):
    if quote_check == "quote found":
        return "supported"
    return _REAL_FINAL_LABEL(human_label=human_label, quote_check=quote_check)


# C1: rank worst-first.
def rank_worst_first(records):
    eligible = [r for r in records if r["fate"] in ("kept", "review")]
    return sorted(eligible, key=lambda r: (r["score"], r["board"], r["key"]))


# C2: break ties by insertion order instead of board identifier and posting key.
def rank_ties_by_insertion_order(records):
    eligible = [r for r in records if r["fate"] in ("kept", "review")]
    return sorted(eligible, key=lambda r: -r["score"])


# C3: match substrings instead of whole words ("ai" inside "email").
def substring_matches(text_tokens, phrases):
    joined = " ".join(text_tokens)
    return [p for p in phrases if p in joined]


# C4: check the level words in the description too.
def score_with_level_words_in_the_description(item):
    record = _REAL_SCORE(item)
    words = tokens(item.description)
    if any(contains_phrase(words, w) for w in screen.LEVEL_WORDS):
        record = dict(record, fate="rejected", reasons=record["reasons"] + ["level"])
    return record


# C5: give the title topic points once per matching term.
def points_per_term(hits, points):
    return points * len(hits)


# C6: add the description point even when the title already earned topic points.
def description_point_always(description_hits, title_topic_points):
    return screen.DESCRIPTION_TOPIC_POINTS if description_hits else 0


# C7: let any non-U.S. place decide before the U.S. words are read.
def classify_outside_first(text):
    result = _REAL_CLASSIFY(text)
    if result["countries"]:
        return dict(result, outcome="outside")
    return result


ALL = {
    "WV1 old skills gate": ("jobwatch.screen.score", score_with_the_old_skills_gate),
    "WV2 topics only in titles": ("jobwatch.screen._description_topic", no_description_topics),
    "WV3 any AI mention counts": ("jobwatch.screen.DESCRIPTION_TOPICS", DESCRIPTION_TOPICS_WITH_AI),
    "WV4 exact quote is enough": ("jobwatch.evidence.final_label", quote_found_means_supported),
    "C1 worst first": ("jobwatch.screen.rank", rank_worst_first),
    "C2 ties by insertion order": ("jobwatch.screen.rank", rank_ties_by_insertion_order),
    "C3 substrings": ("jobwatch.screen._matches", substring_matches),
    "C4 level words in description": ("jobwatch.screen.score", score_with_level_words_in_the_description),
    "C5 points per term": ("jobwatch.screen._award", points_per_term),
    "C6 description point always": ("jobwatch.screen._description_points", description_point_always),
    "C7 outside first": ("jobwatch.location.classify", classify_outside_first),
}

_S = "tests.test_screen."
_E = "tests.test_evidence."
CAUGHT_BY = {
    "WV1 old skills gate": [_S + "StudentsWrongVersionsTest.test_wv1_model_serving_with_go_and_grpc_is_kept_with_score_3"],
    "WV2 topics only in titles": [_S + "StudentsWrongVersionsTest.test_wv2_generic_title_with_model_serving_in_description_is_kept_with_score_2"],
    "WV3 any AI mention counts": [_S + "StudentsWrongVersionsTest.test_wv3_ai_in_hiring_text_is_rejected_with_score_1"],
    "WV4 exact quote is enough": [_E + "LabelTest.test_wv4_an_exact_quote_is_not_sufficient_evidence",
                                  _E + "LabelTest.test_an_unlabelled_claim_stays_not_reviewed_even_with_a_found_quote"],
    "C1 worst first": [_S + "CutoffAndRankingTest.test_rank_by_score_then_board_then_key_as_text"],
    "C2 ties by insertion order": [_S + "CutoffAndRankingTest.test_rank_does_not_depend_on_input_order"],
    "C3 substrings": [_S + "TopicPointsTest.test_whole_words_only"],
    "C4 level words in description": [_S + "RoleAndLevelTest.test_a_senior_colleague_in_the_description_has_no_effect"],
    "C5 points per term": [_S + "TopicPointsTest.test_two_different_title_topics_earn_two_points_once"],
    "C6 description point always": [_S + "TopicPointsTest.test_no_description_point_when_the_title_already_earned_topic_points"],
    "C7 outside first": [_S + "LocationTest.test_any_us_location_counts_as_us"],
}
