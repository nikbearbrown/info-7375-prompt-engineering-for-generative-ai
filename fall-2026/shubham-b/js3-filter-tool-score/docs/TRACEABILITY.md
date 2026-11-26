# Traceability: contract → code → tests

Each CONTRACT.md section, the module that implements it and the tests that check it. Every test name below exists in the suite; `test_traceability_doc_names_existing_tests` fails if one is renamed or removed.

| Contract | Module(s) in `src/job_search_agent/` | Test(s) |
|---|---|---|
| Preamble: discovery only; never apply, contact or log in | `pipeline`, `http` | `test_pipeline_issues_exactly_one_request`, `test_links_in_content_never_requested` |
| §1 exact fixture | `config`, `resume` | `test_committed_fixture_verifies`, `test_repo_config_loads_with_plan_values` |
| §2 board `stripe`, host, no hard-coded count | `providers/greenhouse`, `config` | `test_jobs_url_exact`, `test_parse_handcheck_raw_734`, `test_no_count_constant` |
| §3 inputs; configurable paths; state inside the data dir; validate before sending | `config`, `resume`, `judge` | `test_overrides_applied`, `test_state_path_outside_data_dir_refused`, `test_refused_resume_aborts_before_fetch_and_model` |
| §3/§11 no API-key fallback; `UNAVAILABLE` without the CLI | `judge/backend` | `test_env_strips_api_keys`, `test_not_on_path_unavailable`, `test_no_bare_flag` |
| §4 rule paths; roles from `$.target.roles`; `familiar_with_not_shipped` not counted; personal fields ignored | `resume`, `rule/title` | `test_title_families_derived_from_resume_roles`, `test_unknown_role_in_resume_raises_config_error`, `test_familiar_with_not_shipped_never_counted`, `test_rule_ignores_personal_fields` |
| §5 fields; missing optional → empty; invalid IDs reported; content cleaning; relative paths | `providers/greenhouse`, `text`, `jsonpath` | `test_missing_optional_fields_become_empty`, `test_missing_id_reported_not_invented`, `test_bool_id_invalid`, `test_duplicate_id_reported`, `test_posting_paths_relative_to_posting`, `tests/rule/test_text.py` |
| §6.1 title | `rule/title` | `tests/rule/test_title.py` |
| §6.2 skills and special cases | `rule/skills`, `text` | `tests/rule/test_skills.py` |
| §6.3 exclusions | `rule/exclusions` | `tests/rule/test_exclusions.py` |
| §6.4 location and rescue | `rule/location` | `tests/rule/test_location.py`, `tests/rule/test_location_all_strings.py` |
| §6.5 four-gate verdict; all failed gates recorded; sponsorship not guessed | `rule/verdict` | `test_match_requires_all_four_gates`, `test_all_failed_gates_recorded`, `test_rule_has_no_sponsorship_gate` |
| §7 record shape, location check, evidence pairing | `models`, `evidence_validator` | `tests/test_evidence_validator.py`, `test_every_record_passes_evidence_validator`, `test_record_keys_follow_contract_order` |
| §7/§8 model evidence paths are real | `judge/validator` | `test_resume_path_nonexistent`, `test_posting_path_nonexistent`, `test_path_to_field_not_sent` |
| §8 exact keys and labels; no fences or prose; retry once; no repair; first reply scored; `INVALID_OUTPUT`/`ERROR`/`UNAVAILABLE`; raw reply kept separately | `judge/validator`, `judge/judge`, `judge/rawlog` | `tests/judge/test_validator.py`, `tests/judge/test_judge.py` |
| §9 `BASELINE` semantics, cumulative IDs, distinct statuses | `pipeline`, `status`, `state` | `test_first_run_is_baseline_with_new_count_zero_and_no_judgments`, `test_baseline_reports_fetched_unique_and_state_saved`, `tests/test_status.py` |
| §10 state contents, cumulative set, pending, retry, safe writes | `state`, `fsio`, `pipeline` | `test_advance_unions_ids_cumulatively`, `test_disappeared_id_retained`, `test_reappearing_id_not_new`, `test_fetch_failed_preserves_state_bytes`, `test_atomic_write_preserves_old_on_failure` |
| §11 allow-list, HTTPS, redirects, no link following, no credentials in outputs, CLI-host limitation documented | `http`, `judge/backend`, `docs/NETWORK.md` | `tests/test_http.py`, `test_outputs_contain_no_credentials`, `test_stderr_with_credential_pattern_withheld`, `test_network_doc_names_the_cli_limitation` |
| §12 fixture checks, pinned digest, refuse before sending, privacy, `.gitignore` | `resume`, `privacy`, `fsio`, `cli` | `tests/test_resume.py`, `test_outputs_contain_no_resume_content`, `test_gitignore_rules_hit`, `test_gitignore_rules_miss`, `test_no_real_resume_tracked`, `test_pinned_digest_literal_matches_config` |
| §13 five hand checks on the committed raw file | `rule`, `providers` | `tests/test_golden_handcheck.py` |
| §14 wrong versions A and B are caught | `tests/contract`, `tests/wrong_versions`, `tests/meta` | `test_contract_suite_fails_on_wrong_a`, `test_contract_suite_fails_on_wrong_b`, `test_contract_suite_passes_on_real_impl` |
| §15 a failure is never `SUCCESS_NO_NEW` | `status`, `pipeline` | `test_fetch_failure_never_success_no_new`, `test_empty_response_preserves_state_and_is_not_success_no_new`, `test_invalid_response_preserves_state` |
| §16 hand labels via the rule; `RELEVANT` ↔ `MATCH` | `experiments/metrics`, `experiments/prompt_experiment` | `test_label_mapping_relevant_is_match`, `test_rule_vs_hand_audit_reported_after_seal` |

§14's two wrong versions live in `tests/wrong_versions/`: `title_only.py` (MATCH whenever the title passes, ignoring skills, exclusions and location) and `substring_count.py` (counts skills by substring after stripping punctuation). The meta-test runs the contract suite against each and checks that it fails.
