# Sampling report: generated tables

**Repeatable is not correct.** A label Claude gives every time can still disagree with the hand label; such rows are marked *unanimous and wrong*.

Prompt `judge.v1` (sha256 `2da84890daded0ba…`), model requested `claude-sonnet-5-5`, served `claude-sonnet-5-5`. 20 calls, 4 per posting, first reply only, every session ID distinct (0 call(s) had no session ID).

Hand labels are the CONTRACT.md §13 verdicts; confirmed by the student: Shubham Bagwe (2026-10-30).

| Posting | Hand | n | RELEVANT | NOT_RELEVANT | INVALID | Modal | Unanimous | Agreement k/n | Distinct evidence-path sets | First-reply format acceptance |
|---|---|---|---|---|---|---|---|---|---|---|
| 8249901 | MATCH | 4 | 0 | 4 | 0 | NO_MATCH | yes (unanimous and wrong) | 0/4 | 4 | 4/4 |
| 7543868 | NO_MATCH | 4 | 0 | 4 | 0 | NO_MATCH | yes | 4/4 | 4 | 4/4 |
| 8175099 | NO_MATCH | 4 | 0 | 4 | 0 | NO_MATCH | yes | 4/4 | 4 | 4/4 |
| 8127182 | NO_MATCH | 4 | 0 | 4 | 0 | NO_MATCH | yes | 4/4 | 3 | 4/4 |
| 8234357 | NO_MATCH | 4 | 1 | 3 | 0 | NO_MATCH | no | 3/4 | 4 | 4/4 |

Unanimous and wrong: 8249901.

All replies INVALID (a format or outage case, not a wrong label): none.

## Conclusion

### 1. How much the verdicts and evidence vary across fresh conversations
Across the 20 first-reply calls (5 postings from `CONTRACT.md §13` $\times$ 4 fresh `claude -p` conversations in round-robin order, `--no-session-persistence`, no retries, 20 distinct session IDs), all **20/20 first replies passed the §8 schema and JSONPath validator** (`4/4` format acceptance on every posting; `0` `INVALID` replies). Variation across fresh sessions separates cleanly into two layers:
- **Top-level label variation (`RELEVANT` vs. `NOT_RELEVANT`):** Four of the five postings (`8249901`, `7543868`, `8175099`, and `8127182`) were unanimous (`4/4` `NOT_RELEVANT`). Only one posting split: **`8234357` (`Full Stack Engineer, Revenue`, location `N/A`) returned `3 × NOT_RELEVANT` and `1 × RELEVANT` (`3/4` agreement with my `NO_MATCH` hand label)**. That split was driven by how strictly each fresh session weighed the posting's `"2–5+ years of industry software engineering experience"` (excluding internships/co-ops) and project-leadership scope against Kiran's `New Grad` through `SWE II` target levels: 3 calls rejected the role as too senior for Kiran's target levels, while 1 call treated the 2-year lower bound and strong `TypeScript` / `React` / `HTML` / `CSS` match as worth considering at the `SWE II` level.
- **Evidence-path variation (`distinct_evidence_path_sets`):** Even when the binary label did not vary at all, the cited `(resume_path, posting_path)` pairs varied on nearly every call. Across the 20 calls, **19 out of 20 cited a distinct set of evidence paths** (`4/4` distinct path sets on `8249901`, `7543868`, `8175099`, and `8234357`, and `3/4` on `8127182`). Across fresh sessions, `claude-sonnet-5-5` shifts between citing parent array paths (such as `$.target.levels` or `$.skills.cloud_devops`) and specific element indices (such as `$.target.levels[0]` or `$.skills.cloud_devops[0]`), and varies which matched skill or target array it pairs with `$.title`, `$.content`, or `$.departments[0].name`.

### 2. Why repeatability does not prove correctness (Comparison against hand labels)
Comparing the 20 verdicts against my `CONTRACT.md §13` hand labels (`15/20` overall label agreement) demonstrates both directions of the gap between repeatability and contract correctness:
1. **Unanimous and wrong (`8249901`, `0/4` agreement):** Under `CONTRACT.md §6.5` and `§13 Case 1`, `8249901` (`Software Engineer`, `Seattle, WA`) is a deterministic `MATCH`: the title passes with no excluded seniority marker, 3 eligible skills match in `$.content` (`Java`, `Python`, `AWS`), no §6.3 exclusion phrase appears, and `, WA` establishes `US_BASED`. Yet all 4 fresh calls returned `NOT_RELEVANT` (`NO_MATCH`), citing the body's requirement of 3 years of experience across AWS/Azure, Go/Python/Java, Linux, distributed systems, and tier-0 AMI/EC2 on-call infrastructure. As noted in `CONTRACT.md §13 Case 1`, the deterministic rule does not gate on years of experience in the description, whereas `judge.v1` asks broadly whether the posting is *"worth Kiran considering given the résumé's target roles, levels, locations, exclusions and skills."* Repeating `NOT_RELEVANT` 4 out of 4 times proves only that `claude-sonnet-5-5` repeatably applies its own seniority judgment under `judge.v1`—not that `NOT_RELEVANT` agrees with the contract rule.
2. **Right label for the wrong reason (`8127182`, `4/4` agreement, and `8234357`, `3/4` agreement):** Repeatability on the `NO_MATCH` side also masks rule divergence:
   - On **`8127182`** (`Software Engineer, Revenue and Financial Automation`), my hand label is `NO_MATCH` solely because the posting fails the §6.2 skill threshold (only 1 eligible skill, `Java`, matches in `$.content`, since `Go` is in `$.skills.familiar_with_not_shipped`). All 4 Claude calls returned `NOT_RELEVANT` (`4/4` label agreement), but every call rejected it on the `"5–12+ years of experience"` and mentorship requirements—none counted whether fewer than two eligible skills matched.
   - On **`8234357`** (`Full Stack Engineer, Revenue`), my hand label is `NO_MATCH` solely because `location.name` is `"N/A"` (`NOT_ESTABLISHED` under §6.4, with no rescue phrase in `$.content`). None of the 4 Claude calls treated `"N/A"` as a reason to reject; all 4 followed `judge.v1`'s `uncertainty_rules` instruction and recorded the `"N/A"` location only in `uncertainties`. The 3 `NOT_RELEVANT` calls agreed with my `NO_MATCH` label only because they rejected on `"2–5+ years of experience"`, while the 4th call voted `RELEVANT`.

### 3. What we CAN conclude from this sampling study
- **A single call is not a stable citation of "Claude's reasoning" (`19/20` distinct evidence sets, `3/1` split on `8234357`):** Even when the binary verdict is repeatable on 4 of the 5 postings, a single call on `8234357` has a 25% observed chance in this sample of flipping to `RELEVANT`, and on almost every call the exact set of cited `(resume_path, posting_path)` evidence pairs changes.
- **Prompt `v1`'s `label_definition` systematically diverges from the 4-gate rule in `CONTRACT.md §6.5`:** Because `judge.v1` defines `RELEVANT` as *"worth Kiran considering"* and tells the model to place unestablished facts in `uncertainties`, `claude-sonnet-5-5` uses prose experience-year requirements (`3+`, `2–5+`, `5–12+` years) as its primary rejection gate while ignoring the two-skill count threshold (`8127182`) and demoting unestablished `"N/A"` locations (`8234357`) to `uncertainties`. This directly motivates replacing `label_definition` in `judge.v2.md` with the explicit four-gate criteria from `CONTRACT.md §6.5`.
- **First-reply format compliance is high (`20/20`) without `--json-schema`:** Under `judge.v1`, `claude-sonnet-5-5` produced valid raw JSON with existing payload JSONPaths and no echoed sensitive résumé values on all 20 first replies.

### 4. What we CANNOT conclude from this sampling study
- **We cannot estimate board-wide agreement or accuracy from 5 hand-picked postings:** The 5 postings in `CONTRACT.md §13` were purposively chosen to cover 1 positive case and 4 specific failure modes, not sampled at random from the 734-posting Stripe board (where the base rate of `MATCH` is roughly 16/734).
- **We cannot treat `4/4` unanimity as proof of zero variance or correctness:** At $n = 4$ calls per posting, a `4/4` rate still carries a 95% Wilson score interval of $[0.51, 1.00]$ (and `0/4` carries $[0.00, 0.49]$), meaning a 15–25% flip rate can easily go unseen in 4 trials—and as `8249901` shows, `4/4` unanimity can be `0/4` correct against the hand label.
- **We cannot generalize beyond this prompt, model, and board snapshot:** These 20 calls reflect only `claude-sonnet-5-5` with `prompts/judge.v1.md` on 5 Stripe Greenhouse postings captured on October 29, 2026.
