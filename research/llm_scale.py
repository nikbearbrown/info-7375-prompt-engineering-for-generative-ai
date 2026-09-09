"""Offline scale derivations for chapter 1 Part 1.

Usage: python3 llm_scale.py
Prints JSON; no network, no credentials, no model calls.

Every headline "it would take N years" figure is a division whose inputs are
assumptions. This script makes the assumptions arguments so a reader can change
one and watch the answer move. Published model figures are cited; the reading
rate and the tokens-per-word ratio are stated conventions, not measurements.
"""
import json

SECONDS_PER_YEAR = 31557600  # Julian year, 365.25 days

# Brown et al., "Language Models are Few-Shot Learners", arXiv:2005.14165 (2020).
GPT3_PARAMETERS = 175_000_000_000
GPT3_TRAIN_TOKENS = 300_000_000_000
GPT3_TRAIN_FLOPS = 3.14e23  # Table D.1, total train compute for GPT-3 175B

WORDS_PER_TOKEN = 0.75      # Stated convention for English, not a measurement.
OPS_PER_SECOND = 1e9        # The hypothetical human calculator in the analogy.


def reading_years(tokens, words_per_token, words_per_minute):
    """Years of nonstop reading to consume `tokens`, under stated assumptions."""
    minutes = tokens * words_per_token / words_per_minute
    return minutes * 60 / SECONDS_PER_YEAR


def compute_years(flops, ops_per_second):
    """Years to perform `flops` operations at a fixed rate."""
    return flops / ops_per_second / SECONDS_PER_YEAR


def flops_for_years(years, ops_per_second):
    """Inverse: the compute budget a stated year-count implies."""
    return years * SECONDS_PER_YEAR * ops_per_second


rates = [150, 200, 250, 300]
result = {
    "mode": "offline arithmetic on cited published figures",
    "assumptions": {
        "seconds_per_year": SECONDS_PER_YEAR,
        "words_per_token": WORDS_PER_TOKEN,
        "ops_per_second": OPS_PER_SECOND,
        "reading_rates_wpm": rates,
    },
    "cited": {
        "source": "Brown et al. 2020, arXiv:2005.14165",
        "gpt3_parameters": GPT3_PARAMETERS,
        "gpt3_train_tokens": GPT3_TRAIN_TOKENS,
        "gpt3_train_flops": GPT3_TRAIN_FLOPS,
    },
    "reading_years_by_rate": {
        str(r): round(reading_years(GPT3_TRAIN_TOKENS, WORDS_PER_TOKEN, r), 1)
        for r in rates
    },
    "compute_years_at_one_billion_per_second": round(
        compute_years(GPT3_TRAIN_FLOPS, OPS_PER_SECOND), 2
    ),
    "flops_implied_by_one_hundred_million_years": flops_for_years(1e8, OPS_PER_SECOND),
}

# The point of the sensitivity table: the headline is a function of the rate.
assert result["reading_years_by_rate"]["150"] > result["reading_years_by_rate"]["300"]
assert 9 < result["compute_years_at_one_billion_per_second"] / 1e6 < 11

if __name__ == "__main__":
    print(json.dumps(result, indent=2))
