# TEST-EXPECTATIONS — written before any implementation existed

**Written by:** Vrajesh N. · **Started:** 2026-10-24 · **Rows filled:** 2026-10-31 from my CONTRACT.md choices, before Claude wrote any code

My first answer (chat, 2026-10-24): "for each row in the table given resume, I expect a job to apply."

| # | Given | Expect | Catches | Test name |
|---|---|---|---|---|
| 1 | first run on a board (no saved state) | 0 new, and the state file now holds every id | wrong version 1 (baseline reports all as new) | `test_baseline_reports_zero_new` |
| 2 | second run, same postings as before | 0 new | wrong version 2 (seen-state never saved) | `test_state_is_saved_and_repeat_run_is_zero` |
| 3 | second run, some new posting ids (10-14 then 10-23 Commure) | exactly the ids in 10-23 that are not in 10-14 | wrong version 1 + 2 | `test_second_run_reports_only_new_ids` |
| 4 | a host not on the allow-list | refused, nothing fetched | Refuses #1 | `test_off_allowlist_host_refused` |
| 5 | Claude's answer is not in the fixed schema | rejected, never shown | Refuses #3 | `test_validator_rejects_*` |
| 6 | a justification that does not cite a resume field and a posting field (or cites one that doesn't exist) | rejected | Out | `test_validator_rejects_missing_or_fake_citations` |
| 7 | "Account Executive, AI Sales" | not_relevant, fails R1 | Rule R1 | `test_rule_sales_title` |
| 8 | "Senior Software Engineer, Claims Intelligence" (USA, 5+ years) | not_relevant, fails R2 | Rule R2 | `test_rule_senior_title` |
| 9 | "Software Engineer" asking for 5 years | not_relevant, fails R2 | Rule R2 (years) | `test_rule_years` |
| 10 | "Software Engineer" in Brazil | not_relevant, fails R3 | Rule R3 | `test_rule_outside_us` |
| 11 | "Software Engineer", USA, new grad, "unable to sponsor", resume needs sponsorship | not_relevant, fails R4 | Rule R4 | `test_rule_sponsorship_blocker` |
| 12 | "Software Engineer", USA, no years asked | relevant | Rule all pass | `test_rule_entry_swe_relevant` |
| 13 | a real-looking resume (gmail address, no 555 number) | refused | Refuses #2 | `test_real_resume_refused` |
