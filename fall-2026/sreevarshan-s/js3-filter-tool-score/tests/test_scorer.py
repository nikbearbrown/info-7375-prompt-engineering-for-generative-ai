from js3.scorer import score_posting


def result(reason, passed=True, description_available=False):
    return {"passed": passed, "reason": reason, "description_available": description_available}


def test_title_and_topic_with_description_scores_100():
    s = score_posting(result("title_and_topic", description_available=True))
    assert s["score"] == 100
    assert s["breakdown"] == {"title_match": 60, "topic_bonus": 20, "description": 20}


def test_title_match_without_description_scores_60():
    s = score_posting(result("title_match", description_available=False))
    assert s["score"] == 60
    assert s["breakdown"] == {"title_match": 60, "topic_bonus": 0, "description": 0}


def test_description_weight_zero_scores_80():
    s = score_posting(result("title_and_topic", description_available=True), weights={"description": 0})
    assert s["score"] == 80
    assert s["breakdown"]["description"] == 0


def test_failed_posting_scores_0_even_with_description():
    s = score_posting(result("no_match", passed=False, description_available=True))
    assert s["score"] == 0
    assert set(s["breakdown"].values()) == {0}
