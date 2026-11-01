# Job-Search Agent 1 (INFO 7375)

A job watch for Priya Nair, a fictional persona. It does five things:

1. Fetches the public Databricks Greenhouse board, from one allow-listed host.
2. Remembers which posting ids it has seen.
3. Reports new and removed postings on each run.
4. Judges each new posting for Priya with a fixed set of rules.
5. Offers a separate, isolated Claude judge whose verdict is compared with the rules afterward.

The rules are written in [CONTRACT.md](CONTRACT.md); the Final section supersedes the drafts below it.

- **Language:** Python 3.13.9, standard library only. There are no third-party packages.
- **Tests:** `unittest`. The network and the `claude` subprocess are mocked in every test.
- **Claude judge:** the `claude` CLI (v2.1.117), run as a subprocess in print mode. Model pinned to `claude-sonnet-4-6`, every tool disabled, run from an empty temporary directory.
- **Persona:** `persona/priya-nair.resume.json` and `persona/priya-nair.profile.json`, fictional, from the Reallocation Engine repo.

## Commands

Run from the repository root.

| command | what it does |
|---|---|
| `python3 -m unittest discover -s tests` | Runs all tests. No network and no Claude call. |
| `python3 -m js1 --baseline` | One live fetch from `boards-api.greenhouse.io`. Saves the raw response to `evidence/raw/<UTC stamp>.json` and records every posting id in `state/seen_ids.json`. No judging. Refuses (exit 3) if state already exists. |
| `python3 -m js1` | The watch run. Refuses (exit 5) without a baseline. Steps: 1) one live fetch; 2) save the raw response; 3) report fetched, new and removed posting ids; 4) run the rule judge on new postings only and save records to `evidence/rule/<UTC stamp>.json`; 5) only then update state, keeping the previous state file beside it. A failed fetch leaves state unchanged (exit 6). |
| `python3 -m js1.claude_judge --prompt baseline\|revised --posting-file FILE --posting-id ID` | One Claude judgment of one posting from a saved Greenhouse-shaped file, with one retry on an invalid reply. Saves every attempt and the result under `evidence/claude/`. Exits 0 if valid, 4 if invalid. |
| `python3 -m experiments.run_experiment --split dev` | Prompt experiment on the frozen development split (`LABEL_SET.md`). Runs the rule judge plus the baseline and revised Claude prompts on each posting and scores them against `labels/HAND_LABELS.md`. Writes `experiments/results_dev.md` and evidence under `evidence/experiment/dev/`. |
| `python3 -m experiments.run_experiment --split heldout` | Same, on the held-out split. Refused (exit 7) until `experiments/results_dev.md` exists. |
| `python3 -m experiments.sampling build` | Writes the full baseline prompt for each of the 5 sampling postings to `experiments/sampling/prompts/`. Uses the judge's own prompt-building code. No Claude call. |
| `python3 -m experiments.sampling check experiments/sampling/replies/*.txt` | Checks saved reply files with the judge's JSON validator. Prints valid plus the verdict, or invalid plus the reason. Exits 4 if any reply is invalid. |
| `python3 -m experiments.heldout_app build` | Writes the baseline and revised prompt for each of the 10 held-out postings to `experiments/heldout_app/prompts/`, byte for byte what the judge would send. No Claude call. |
| `python3 -m experiments.heldout_app score` | Checks the saved held-out replies in `experiments/heldout_app/replies/` with the judge's validator, scores them against `labels/HAND_LABELS.md` with the dev pass rule, runs the rule judge, and writes `experiments/results_heldout_app.md`. |
| `python3 -m experiments.watch_app build` | Writes the baseline prompt for each of the 10 new postings from the second watch run to `experiments/watch_app/prompts/`, byte for byte what the judge would send. No Claude call. |
| `python3 -m experiments.watch_app score` | Checks the saved replies in `experiments/watch_app/replies/` with the judge's validator and writes `experiments/results_watch_app.md`: the rule record next to the Claude judgment for each new posting. |
| `python3 -m experiments.sampling_report` | Prints the sampling results table used in `experiments/SAMPLING_REPORT.md`, computed from the reply files. |

**Choices Claude Code made where the contract left room:** see [IMPLEMENTATION_CHOICES.md](IMPLEMENTATION_CHOICES.md).

## Sign-off

### Checked

**Automated tests.** Claude Code wrote all the tests; I ran them. On 2026-10-31, before this commit, all 80 tests passed in the Eng_job repo. In the packaged copy (this folder), 79 pass and 1 is skipped: `test_persona.test_resume_is_an_unchanged_copy` needs the source-résumé path in a local Reallocation Engine checkout, which the copy does not have.

**Properties and the tests that check them:**

| property | test file | tests |
|---|---|---|
| Fetches only the allow-listed host; refuses other hosts, off-list redirects and path changes before any network call | `test_allowlist.py` | `test_board_url_is_allowed`, `test_refuses_other_hosts`, `test_fetch_refuses_before_any_network_call`, `test_redirect_off_the_allow_list_is_refused`, `test_board_token_cannot_change_the_path` |
| One request to the exact URL; raw response saved byte for byte | `test_fetch.py` | `test_one_request_to_the_exact_url_with_the_user_agent`, `test_raw_response_saved_byte_for_byte` |
| Baseline reports zero new, records every id, and cannot be run twice | `test_baseline.py`, `test_watch.py` | `test_baseline_saves_raw_records_ids_reports_zero_new`, `test_refuses_if_state_exists`, `test_second_baseline_is_refused`, `test_baseline_reports_zero_new_and_records_all_ids` |
| New since last run, by id; removed postings counted once | `test_watch.py`, `test_watch_run.py` | `test_new_since_last_by_id`, `test_same_response_twice_reports_nothing_new`, `test_new_postings_are_the_input_postings_unchanged`, `test_new_and_removed_are_counted_against_constructed_responses`, `test_removed_is_not_counted_again_on_the_next_run` |
| State changes only after a successful run; previous state kept; failed or unusable fetch leaves state untouched | `test_watch_run.py` | `test_missing_state_is_refused`, `test_state_updates_only_after_success_and_previous_state_is_kept`, `test_failed_fetch_leaves_state_untouched`, `test_unusable_response_is_saved_but_leaves_state_untouched`, `test_state_from_before_this_change_still_works` |
| Rule judge runs on new postings only | `test_watch_run.py` | `test_rule_judge_runs_only_on_new_postings` |
| Persona is fictional: refuses real-looking email and non-555 phone, including in free text | `test_persona.py` | `test_priya_persona_passes`, `test_resume_is_an_unchanged_copy`, `test_profile_contact_matches_resume`, `test_refuses_real_looking_email`, `test_refuses_email_hidden_in_free_text`, `test_refuses_phone_without_555`, `test_refuses_phone_hidden_in_free_text`, `test_refuses_unparseable_phone_field_without_555` |
| Wrong version 1: a Senior title with matching skills is not relevant | `test_rule_judge.py` | `test_senior_data_engineer_with_matching_skills_is_not_relevant`, `test_leading_does_not_trigger_seniority` |
| Wrong version 2: missing sponsorship text is "unknown", never yes or no | `test_rule_judge.py` | `test_no_sponsorship_text_gives_unknown` |
| Sponsorship denial phrases make a posting not relevant | `test_rule_judge.py` | `test_contract_denial_phrase_is_not_relevant`, `test_added_denial_phrase_is_not_relevant`, `test_will_not_provide_sponsorship_is_denied` |
| All seven checks always run and every failure is listed; each record keeps its posting id | `test_rule_judge.py` | `test_all_seven_checks_always_run`, `test_several_failures_are_all_listed`, `test_every_result_posting_id_matches_its_input` |
| Experience: a range uses its lower end; preferred years do not reject | `test_rule_judge.py` | `test_range_uses_lower_bound_and_preferred_years_are_ignored`, `test_years_bullet_under_preferred_heading_does_not_reject`, `test_preferred_heading_ends_at_next_heading`, `test_list_items_are_their_own_sentences` |
| Clearance: required rejects, preferred-only does not | `test_rule_judge.py` | `test_required_clearance_rejects`, `test_preferred_only_clearance_does_not_reject` |
| Skill matching: excluded and look-alike skills do not count; the company name alone does not count; every cited field is named | `test_rule_judge.py` | `test_ray_and_kubeflow_never_count`, `test_postgresql_does_not_match_sql`, `test_company_name_only_databricks_does_not_count`, `test_experience_with_databricks_counts`, `test_aws_alias_and_slash_title`, `test_offered_phrase_and_skill_cites_every_field` |
| Location is reported, with conflicts and "not specified" | `test_rule_judge.py` | `test_location_conflict_and_not_specified` |
| Claude judge: strict validator, wrong id rejected, exactly one retry, one bad posting does not stop the others | `test_claude_judge.py` | `test_valid_json_is_accepted`, `test_wrong_posting_id_is_rejected`, `test_validator_rejects_extra_keys_bad_verdict_and_familiar_citations`, `test_non_json_retries_exactly_once_then_invalid`, `test_retry_that_succeeds_is_valid`, `test_invalid_posting_does_not_stop_the_others`, `test_subprocess_failure_counts_as_a_failed_attempt` |
| Claude judge input: no email, phone or rule verdict; the two prompts differ by one line | `test_claude_judge.py` | `test_prompt_has_no_email_phone_or_rule_verdict`, `test_prompt_files_differ_only_by_the_one_added_instruction`, `test_revised_prompt_is_selected_by_name` |
| Claude judge isolation and evidence: tools disabled, empty temp dir, pinned model, every reply saved | `test_claude_judge.py` | `test_cli_call_disables_tools_and_runs_in_an_empty_temp_dir`, `test_model_is_pinned_in_the_command_and_recorded_in_every_result`, `test_every_raw_reply_and_the_result_are_saved`, `test_failed_call_records_stdout_and_stderr`, `test_invalid_reply_also_records_its_output` |
| Prompt experiment: frozen split, all 20 labels, pass = valid and matching, held-out refused before dev | `test_experiment.py` | `test_frozen_split_is_read_from_label_set`, `test_hand_labels_cover_all_twenty`, `test_pass_requires_valid_and_matching_verdict`, `test_invalid_result_is_a_fail`, `test_heldout_is_refused_before_dev`, `test_dev_run_scores_and_counts_correctly`, `test_heldout_runs_after_dev` |
| App-run prompts are byte for byte the judge's; saved replies use the judge's validator | `test_sampling.py`, `test_heldout_app.py`, `test_watch_app.py` | `test_build_writes_the_exact_judge_prompt`, `test_check_valid_and_invalid`, `test_build_writes_the_exact_judge_prompts`, `test_score_valid_invalid_missing`, `test_build_writes_the_exact_judge_prompt_for_each_record`, `test_score_puts_record_next_to_judgment` |

**Tests per file:**

| test file | tests |
|---|---|
| `tests/test_allowlist.py` | 5 |
| `tests/test_baseline.py` | 3 |
| `tests/test_claude_judge.py` | 15 |
| `tests/test_experiment.py` | 7 |
| `tests/test_fetch.py` | 2 |
| `tests/test_heldout_app.py` | 2 |
| `tests/test_persona.py` | 8 |
| `tests/test_rule_judge.py` | 22 |
| `tests/test_sampling.py` | 2 |
| `tests/test_watch.py` | 4 |
| `tests/test_watch_app.py` | 2 |
| `tests/test_watch_run.py` | 8 |

**Live runs, with their evidence commits:**

| commit | run | result |
|---|---|---|
| `6beef48` | Baseline, 2026-10-29T22:15:02Z | 905 postings recorded, 0 new |
| `0dd01ab` | Second live watch run, 2026-10-30T23:59:22Z | 901 fetched, 10 new, 14 removed; rule records saved. Claude judgments for these 10 new postings were not run before submission |
| `bb1f877`, `c047608` | Claude judge smoke test on CONSTRUCTED posting 8000002 | First run: "Not logged in" twice. Then valid. Then valid with the pinned model recorded |
| `d7411f4` | Prompt experiment, dev split | Baseline 10/10, revised 9/10, rule 9/10 |
| `4a46925` | Prompt experiment, held-out split, CLI | Rule 9/10. 38 of the 39 Claude calls made failed on the usage limit, so the Claude results are not usable |
| `f5c008d` | Prompt experiment, held-out split, rerun in the Claude app with the prompts from `71e8f56` | Baseline 10/10, revised 10/10, rule 9/10. One reply per prompt, no retry |
| `6064e8e` | Sampling in the Claude app, 5 dev postings × 4 chats | 19/20 valid, all "not relevant" |
| `3484999` | Action-surface comparison on 8546367002 | Included one live GET of that posting from Greenhouse. Also the two usage-limit smoke-test failures from 2026-10-31 |

### How

**My words (verbatim):**

**Q24.** I'll manually verify selected posting verdicts and inspect the saved response and state files. I'll use automated tests to check the contract's rules and compare their outputs with my own expectations. I'll distinguish tests based on my contract decisions from tests Claude Code wrote. [correction: all 80 tests in `tests/` were written by Claude Code; some encode my contract decisions, but the repo does not yet mark which ones.]

**What I ran myself, by commit:**
- **In Terminal:**
  - `6beef48`: the baseline run, `python3 -m js1 --baseline`.
  - `bb1f877`: the first smoke test, which failed with "Not logged in". I logged in with `/login` and reran (`NOTES_FOR_FRICTIONAL.md`).
  - `0dd01ab`: the second live watch run, `python3 -m js1`. I also made this commit.
  - `d7411f4`: the dev experiment. I also made this commit.
  - `4a46925`: the held-out experiment. I also made this commit.
  - `3484999`: the smoke test at 2026-10-31T01-36-35Z, which hit the usage limit.
- **In the Claude app:**
  - `6064e8e`: the 20 sampling chats, with the replies saved by hand. I also made this commit.
  - `f5c008d`: the 20 held-out chats, with the replies saved by hand. I also made this commit.

### Not checked

**My words (verbatim):**

**Q25.** I haven't verified redirects against every real-world scenario; redirect protection was tested only with simulated data. Experience requirements written as number words beyond "five" aren't handled by the current rules. [correction: `js1/rule_judge.py` handles number words "one" through "ten"; number words beyond "ten" are not handled.] I also can't directly control Claude's temperature through the CLI, so I can't guarantee identical outputs across repeated runs.

**Further gaps, from the evidence:**
- **Validator bug:** the validator rejects `resume_field: "resume_experience_tools"`, a key the judge's own input provides.
  - It caused the invalid sampling reply 8921476002-4.
  - In the dev run (`d7411f4`) it rejected 4 replies. Two of them were the revised prompt's two "relevant" replies on 8401114002, a Staff title, which showed up only as "invalid".
- **8546367002:** the rule judge passed it as "relevant" even though the description says it "is not intended for internship, new graduate, or entry-level applicants" (`results_dev.md`).
- **8760167002:** the rule judge passed it as "relevant" despite its Secret-clearance-eligibility requirement (`results_heldout.md`).
- **Unity Catalog:** it appears in the Databricks boilerplate of every posting (905 of 905 in the baseline, 901 of 901 in the second run), so it matches every posting.
- **Sponsorship:** no posting among the 905 mentions visa sponsorship. The word "visa" appears in none, and every "sponsor" match is business usage. So check 6 returned "unknown" for every live posting and never decided a verdict.
- **Hand labels:** all 20 are "not relevant", so no relevant posting has been tested against a hand label. A prompt that always answered "not relevant" would score 10/10 on both splits.
- **Claude judgments for the 10 new watch postings: not run before submission.** The prompts are built in `experiments/watch_app/prompts/`, but no replies exist, so there is no `experiments/results_watch_app.md`. Rule records exist for all 10 (`evidence/rule/2026-10-30T23-59-22Z.json`).
- **Held-out Claude results:** complete (`f5c008d`), but run in the Claude app with one reply per prompt and no retry, not through the CLI judge used for dev.

### Not claiming

**My words (verbatim):**

**Q26.** I'm not claiming that this agent can guarantee job eligibility, predict whether a company will hire someone, or submit applications. It only identifies potentially relevant new postings based on the supplied persona and documented rules.

Signed: Sreevarshan Sathiyamurthy, 2026-10-31

## Driver's seat

**My words (verbatim):**

**Q27.** I should decide the target roles, eligibility requirements, hand labels, success criteria, and whether the final results are acceptable. Claude Code can implement the program, generate test code, and help organize the reports. The final decisions stay with me because the agent is supposed to reflect my requirements, not make those decisions on my behalf.

**Q28.** The first contract commit, 8cfa417, predates implementation. The baseline evidence commit is 6beef48. I'll reference the actual final contract commit and the relevant transcript or edits to show which decisions I reviewed and approved.

**Final contract commit:** `b8a5b81` (Draft 8) is the last commit that changes `CONTRACT.md`.

**Who did what, by commit:**

| commits | what | who | co-author line |
|---|---|---|---|
| `8cfa417`, `d6c24ff`, `2860740`, `67d61b8`, `9b34061`, `c8c2772`, `4da69e5`, `dfb37a7`, `b8a5b81` | Contract Drafts 0–8 | My text, appended verbatim by Claude Code. In Drafts 6, 7 and 8 the same commit also folds my sentences into the Final section | none |
| `31d20fa`, `e7f7362` | Contract Final section (restructure, then the Draft 5 fold) | My sentences verbatim, arranged and source-tagged by Claude Code; I approved before commit | none |
| `ee73eca`, `04ef802`, `1110661`, `a4021ff`, `bb1f877`, `c047608`, `388e788`, `9b2ef89`, `f3399e8`, `3484999`, `71e8f56` | Code, tests, prompts, smoke-test evidence, sampling prompts and report, action-surface comparison, held-out app prompts and scorer | Claude Code | Claude Code |
| `24ffb13` | `LABELING_RULE.md` | My text | none |
| `f18cbae` | Label set: label sheets and the method paragraph in `LABEL_SET.md` | Written by Claude Code, committed with no co-author line (the exception) | none |
| `f55b88d` | `labels/HAND_LABELS.md` | My labels and reasons; ChatGPT formatted my notes into the table | none |
| `6beef48`, `0dd01ab`, `d7411f4`, `4a46925` | Live run evidence | Run by me in Terminal. I committed `0dd01ab`, `d7411f4` and `4a46925` myself | none |
| `6064e8e` | Sampling replies | Run by me in the Claude app and committed by me | none |
| `f5c008d` | Held-out replies and results | Run by me in the Claude app and committed by me | none |

The Final-section commits (`31d20fa`, `e7f7362`) and the fold parts of `4da69e5`, `dfb37a7` and `b8a5b81` also contain Claude Code's arrangement of my sentences without a co-author line. The words are mine; the ordering and source tags are Claude Code's.
