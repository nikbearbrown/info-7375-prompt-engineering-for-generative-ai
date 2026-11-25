# What moves the score (Step 2.4)

Drafted by Claude Code on 2026-11-25 from the committed files. Every number below can be regenerated with the command
next to it. Ashwin and Codex review it.

## 1. Where every number comes from

| Number | Value | Origin | Where |
|---|---|---|---|
| Title points for a qualifying role phrase | 3 | **Hand-set** (Codex draft of FILTER.md, approved by Ashwin) | `filters/v1.0.json` `weights.title` |
| Points per distinct topic group | 1 | Hand-set (same) | `weights.topic` |
| Topic cap | 4 | Hand-set (same) | `weights.topic_cap` |
| Location points: Boston or US-remote / other US / unresolved | 2 / 1 / 0 | Hand-set (same) | `weights.location_*` |
| Minimum distinct topic groups | 2 | Hand-set (same) | `weights.min_topic_groups` |
| Keep threshold | 7 (was 6) | Hand-set. Claude Code showed that 6 never binds; Codex suggested 7; Ashwin approved, before any code (FILTER.md section 10) | `weights.threshold` |
| The seven topic groups and their aliases | Python, Java, PostgreSQL, Redis, Docker, Kubernetes, Distributed Systems | **Inherited** from the fictional résumé `data/supriya-sharma.resume.json` (JS1/JS2) | `topic_groups` |
| Role phrases, seniority terms, level suffixes II–V / 2–5 | lists | Hand-set (FILTER.md section 2) | `role_phrases`, `seniority_terms`, `level_suffixes` |
| Seniority exception "mission manager" | 1 phrase | Hand-set after a demonstrated false match (v1.1, this report) | `filters/v1.1.json` |
| Claim prompt: 3–5 claims, first two on experience level and US remote | `prompts/claims-v1.md` | **Written by Claude Code**, never tuned; one live run (2026-11-25 13:23 UTC) | `jobfilter/claims.py` |
| Held-out draw: 20 engineering-like + 10 other titles, seed 20261125 | 30 | Hand-set by Claude Code; the 30 matches the brief's audit size | `jobfilter/heldout.py` |
| Audit strata sizes and seed 20261126 | 30 / 6 / 5 / 6 / 8 / 7 | 30 comes from the brief; the others and the seed were hand-set by Claude Code | `jobfilter/audit.py` |
| Wilson interval z | 1.96 | Inherited (the standard 95% value) | `jobfilter/audit.py` |

**Nothing was fitted on labels.** No weight, threshold or word list was chosen by optimizing against any label set.
The threshold of 7 was set before any label existed.

## 2. The one change, to one object

v1.1 is a separate change experiment. Three things stay on filter v1.0:
- the submitted shortlist (`SHORTLIST.md`);
- the claims;
- the tool server.

v1.1's 2 extra KEEPs have no claims.

- **Object:** the filter file. `filters/v1.0.json` became `filters/v1.1.json`, which adds only
  `"seniority_exceptions": {"manager": ["mission manager"]}`. The test `test_only_one_object_changed` checks this.
  Words, weights, sources, prompt, context, tool list and settings were held constant.
- **Why:** a demonstrated false keyword match. "manager" fired on Palantir's product name "Mission Manager"
  (`audit/FALSE-FRIENDS.md`).
- **Frozen at:** `78adf4b9`, before either version's held-out decisions were opened.
- **Development set:** 2 postings went from REJECT to KEEP, and nothing else changed
  (`changes/v1.1-mission-manager.md`).

## 3. Measured on the held-out labels (potentially contaminated)

From `python3 -m jobfilter.compare v1.0 v1.1`, which writes `changes/HELDOUT-v1.0-vs-v1.1.md`:

| Version | KEEP: Y / N / ? | REJECT: Y / N / ? | Precision (known labels) | Recall (known labels) |
|---|---|---|---|---|
| v1.0 | 0 / 1 / 0 | 7 / 18 / 4 | 0 / 1 = 0.0% | 0 / 7 = 0.0% |
| v1.1 | 1 / 1 / 0 | 6 / 18 / 4 | 1 / 2 = 50.0% | 1 / 7 = 14.3% |

Neither version marked any held-out posting REVIEW.

Ashwin labeled 7 held-out postings Y. This is what each version decided for them:

| Version | KEEP | REVIEW | REJECT |
|---|---:|---:|---:|
| v1.0 | 0 | 0 | 7 |
| v1.1 | 1 | 0 | 6 |

So v1.0 kept none of the seven and v1.1 kept one. That one is the Mission Manager posting, and the disclosure
below applies to it.

**What this shows.** Exactly one held-out posting changed: "Software Engineer - Mission Manager", labeled Y, went
from REJECT to KEEP.

**Why it is not clean evidence.**
- Claude Code had seen that posting's label before the change was chosen.
- The AI-assisted audit verdicts were inferred from these same labels.
- So the move from 0/7 to 1/7 is the change doing what it was built to do on a posting already known. It is not an
  independent accuracy gain.
- The set is reported as **potentially contaminated**, not held out (`drafting/EVALUATION-SETS.md`).
- No unused set can test this change. None of the Cloudflare snapshot's titles contains "mission manager", so both
  versions behave identically there.

**The bigger finding, independent of the change.** Apart from the Mission Manager posting, both versions reject
the other 6 postings Ashwin labeled Y. v1.0 rejects all 7. Why the reject audit missed this is explained in
`audit/REPORT-v1.0.md`. The 6:

| Reason | Count | Postings |
|---|---:|---|
| No qualifying role phrase | 2 | an intern title, a "Platform Engineer" title |
| 0 topic groups in the text | 2 | |
| Score 6, below threshold 7 | 1 | New Grad, San Francisco |
| Excluded seniority term "internship" | 1 | |

That points to the role list, the topic words and the threshold as the objects worth measuring next. Each would
need its own one-change run, and a clean evaluation set.

## 4. What persistence is not proof of

- **Not training.** v1.1 makes a different decision every time it runs, in any session, because a file in
  `filters/` changed. No model was trained, fine-tuned or updated; Claude's weights are the same as before. The
  same holds for a changed prompt, context, tool list or setting.
- **Not correctness.** The new behavior is persistent and reproducible. That shows the file is applied
  consistently. It does not show the decision is right for Supriya: these postings ask for "3+ years" and tech-lead
  experience.
- **Not an accuracy claim.** Without independent labels, a rule that persists cannot be called an improvement.
