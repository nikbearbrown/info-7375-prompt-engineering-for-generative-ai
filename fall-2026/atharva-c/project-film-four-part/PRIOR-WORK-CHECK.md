# Prior-work check: 2026-11-22

Done by Claude Code at Atharva's request, to back Part 2 (Introduction) of the four-part film. Atharva reviewed the findings, and on 2026-11-22 reran both pandera scripts with identical results.

## Summary

| Claim to check | Verdict | How checked |
|---|---|---|
| Deequ suggests checks from data | **Confirmed (docs only)** | AWS Big Data Blog and PyDeequ docs describe `ConstraintSuggestionRunner`. Not run: it needs Spark. |
| pandera drafts a schema from data | **Confirmed and run** | `pa.infer_schema()` run on the taxi sample, pandera 0.36.0 (results below) |
| Older Great Expectations suggested expectations | **Partly confirmed** | Legacy docs (0.15.50, 0.16.16) show the Onboarding Data Assistant and UserConfigurableProfiler. That they were removed in 1.0 is backed only by a GX community forum reply, not by release notes. |
| Mutation testing is the idea this borrows | **Confirmed** | DeMillo, Lipton and Sayward, "Hints on Test Data Selection", IEEE Computer 11(4):34–41, April 1978. Tools: mutmut (Python), PIT (Java). |
| Nobody scores data tests with planted faults | **False as a broad claim.** See below. | arXiv search |

## The finding that changes the pitch

**Akella, Kaul, Narayanam and Mehta (IBM Research), "Quality Assessment of Tabular Data using Large Language Models and Code Generation", arXiv 2509.10572, Sept 2025 (under review).**
Per the abstract and the part of the HTML paper that was read: an LLM writes data-quality rules, a second model turns each rule into a Python `check(df)` function, and the checks are scored by **injecting synthetic errors** into clean benchmark tables. The errors come from the REIN corruption model: typos, missing values, swapped cells and Gaussian noise, at 10/20/30% of cells. Results are reported as F1. Their baselines are error detectors (ED2, FAHES, KATARA, IQR, Isolation Forest…), not Great Expectations, Deequ, pandera or dbt. No code link was found.

So "LLM writes checks, then score them against planted errors" **has been done in research**. The pitch film's line, "in each tool, nothing told me what I'd missed", is still true for the three tools it named. The new film must not suggest the scoring idea is new.

**What is still different about Seeded Faults** (these are honest differences of focus, not claims that it is better):
1. **Target:** dbt tests, the format data teams actually ship, not standalone Python functions.
2. **Faults:** a fixed catalogue of *domain* faults for one real table (negative fares, drop-off before pick-up, duplicate trips, out-of-zone location IDs), locked before tests are written. The paper uses generic cell-level corruption (typos, noise).
3. **Report:** per-fault caught/missed plus false alarms on fresh clean data, rerun by one command.
4. **Baselines:** hand-written tests and pandera's inferred schema, the tools a data engineer would actually reach for.

## pandera run (evidence/2026-11-22-pandera-infer-schema/)

Data: the same NYC TLC Jan 2024 files from the 2026-10-09 sandbox. `trips_sample.csv` turned out to be exactly the first 2,000 rows of the parquet file (checked in `output_holdout.txt`).

1. **`pandera_sample.py`**: inferred a schema from the clean sample. Every column was set non-nullable, plus min/max range checks taken from the sample's own values. Clean sample: PASS. Faulted copy (50 planted nulls): FAIL, 50 `not_nullable` failures. So it caught all 50, the same as the hand-written checks in October.
2. **`pandera_holdout.py`**: validated that same schema against 5 new random samples of 2,000 rows each from the rest of January. Only rows with no missing values were used. **All 5 failed. 13, 17, 16, 13 and 25 rows were flagged**, mostly on `trip_distance`, `extra` and `tolls_amount`, because the ranges were fitted to the first 2,000 rows (for example `trip_distance <= 25.1`).

Careful wording: these flagged rows are *not yet judged*. Some may be real data problems, and others are normal trips outside the sample's range. The fair claim is: **"a schema inferred from one sample flagged 13 to 25 rows in every fresh sample of the same month's data."** That is exactly the false-alarm problem the evaluation will measure.

## Sources
- Deequ suggestions: [AWS Big Data Blog: Testing data quality at scale with PyDeequ](https://aws.amazon.com/blogs/big-data/testing-data-quality-at-scale-with-pydeequ), [PyDeequ on PyPI](https://pypi.org/project/pydeequ/1.1.0)
- pandera: [Schema Inference docs](https://pandera.readthedocs.io/en/stable/schema_inference.html)
- GX legacy: [Onboarding Data Assistant (0.16.16 docs)](https://legacy.017.docs.greatexpectations.io/docs/0.16.16/guides/expectations/data_assistants/how_to_create_an_expectation_suite_with_the_onboarding_data_assistant), [User Configurable Profiler (0.15.50 docs)](https://legacy.017.docs.greatexpectations.io/docs/0.15.50/guides/expectations/how_to_create_and_edit_expectations_with_a_profiler), [GX forum thread on profiling](https://discourse.greatexpectations.io/t/how-to-profile-data-and-put-profile-info-to-data-doc/1954)
- Mutation testing: [DeMillo, Lipton, Sayward 1978 (bibtex)](https://researchr.org/publication/DeMilloLS78-0/bibtex), [mutmut](https://mutmut.readthedocs.io)
- IBM paper: [arXiv 2509.10572](https://arxiv.org/abs/2509.10572)

## Limits (how the film handles each)
- GX removal in 1.0 is backed only by a forum reply, so the film says only "older versions of Great Expectations".
- IBM paper: Appendix A.8 (precision and recall) was not read. The film therefore describes only what the paper measures, not its scores.
- A search for a dbt-specific fault-injection package (2026-11-22) found none. The film does not claim that none exists.
