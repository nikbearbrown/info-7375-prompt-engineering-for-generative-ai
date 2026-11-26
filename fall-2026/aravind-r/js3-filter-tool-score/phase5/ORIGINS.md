# Where every number and prompt in the scorer came from (Phase 5)

**Origins:**
- **Hand-set:** chosen by reasoning; not fitted.
- **Inherited:** from JS1/JS2.
- **Fitted on labels:** none. **No number was fitted on labels.**
- Several values were changed after the audit (dev use of the audit sample), by hand and citing
  audit rows; they were never optimized.

| Object | Value (v1.1.0-e) | Origin | History |
|---|---|---|---|
| weights title / location / experience / topic | 0.40 / 0.25 / 0.25 / 0.10 | hand-set v1 | unchanged since `bb88c420` |
| threshold | 0.80 | hand-set | 0.70 in the draft, raised to 0.80 at Checkpoint 1, before any measurement (W13 reasoning) |
| near_band | 0.10 | hand-set | audit selection only; never decides |
| title tier values core / adjacent / none | 1.0 / 0.5 / 0 | hand-set | — |
| core title list | 6 PM titles | inherited (JS1 Gate 1) | TPM titles moved to adjacent in v1.1.0-e, citing A027, A044, A052 (audit, dev use) |
| adjacent title list | 11 titles | hand-set | TPMs added in v1.1.0-e |
| junior terms; junior range upper ≤ 2 | Associate, APM, Intern, New Grad; 2 | inherited (JS1 Gate 2) | — |
| experience tiers | ≤ 4 → 1, 5–6 → 0.5, ≥ 7 → 0 | hand-set from the persona's stated acceptance policy (`persona-prefs.json` `preferred_max_years` 4, `stretch_max_years` 6) | was ≤ 3 / 4 / ≥ 5 (inherited JS1 `years_pm` + 1); corrected after the v1.0.0 audit (v1.1.0-a, dev use) |
| experience impute (display only) / location impute | 0.5 / 0 | hand-set | never decides (W5) |
| topic terms; saturate_at | persona domains + "ecommerce"; 2 | inherited domains (JS1), cap hand-set | — |
| exclude_shared_lines_min_share | 0.2 | hand-set (same rule as the sheet excerpts) | added in v1.1.0-b |
| location aliases | SF, Bay Area, LA | hand-set | — |
| veto phrases | 7 sponsorship + 4 citizenship | inherited (JS1 Gates 5–6) | plus 1 phrase and 1 bounded pattern in v1.1.0-c, from the committed measurement `e0d80ff0` |
| min_text_chars | 200 | hand-set | — |
| range parse ("N–M+" reads N) | code | inherited regex (JS1 Gate 3), fixed | fixed in v1.1.0-d, citing A010 |
| Claude prompt | `prompts/justify.v1.md` | hand-written (Claude Code draft, Aravind approved) | decides nothing numeric (Option A) |
| model | requested `claude-sonnet-5-5` (inherited JS1); used Claude Opus 5.5 via claude.ai (manual route, self-reported) | inherited / deviation | FILTER.md §4 |
