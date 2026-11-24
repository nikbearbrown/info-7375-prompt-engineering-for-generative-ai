# FILTER.md: Job-Search Agent 3

**Version 1.1, Nov 22, 2026.**
- v1.0 was written before any JS3 code (commit `12c826a`).
- v1.1 adds one rule change after the reject audit (section 6; `AUDIT.md`).
- This document **is** the filter. The code reads the fenced `filter` block in section 2 and nothing else.
- Every result records the filter version and the SHA-256 of this file.
- Changes are logged in section 6. Words that were added, cut or rejected are each logged with their measurement, following the format of the instructor's Lectern `keywords.json`.

**Who decided what:**
- **The rules in section 2** are Hemanth's answers to questions Q1–Q7 (section 7), asked one at a time on Nov 20–22.
- **Sections 3–5, and the rows marked "proposed by Claude"**, are Claude Code's proposal. The status line in section 7 records whether Hemanth accepted them.

**Hit counts:** every "hits" number in this file was measured on the frozen corpus (`CORPUS.sha256`): **1,176 unique postings** from three live snapshots (Oct 31, Nov 7, Nov 20) of Anthropic, Notion and Perplexity. Claude measured them with exploratory scripts on Nov 20–22, before any JS3 code existed. The filter code must reproduce them; a test checks this.

## 1. Who the filter is for

**Priya Nair**, a fictional persona (`persona/priya-nair.resume.json` and `persona/priya-nair.profile.yml`, both from the Reallocation Engine):
- **Education:** MS in Information Systems, completed Dec 2025.
- **Experience:** one 8-month job, "AI Engineer Co-op".
- **Skills:** Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake and AWS. She has not shipped Ray or Kubeflow.
- **Targets:** AI Engineer or ML Engineer first, then Data Engineer.
- **Location:** Boston, open to remote.
- **Visa:** needs sponsorship (F-1 OPT).

## 2. The filter

Matching is by whole word or whole phrase, ignoring case: `(?<![A-Za-z0-9])word(?![A-Za-z0-9])`, the same pattern as JS1's `rule.py`. A phrase may span any whitespace.

| # | Rule | Reason (one line) | Origin | Hits on the corpus |
|---|---|---|---|---|
| R1 | A **role word in the title** adds **+3.0**, counted once: AI, Engineer, Engineering, ML, Machine Learning, Data | These are the words of Priya's target roles and of her one job title | words: Hemanth, Q1 (Nov 20); 3.0: inherited (greenhouse-watch `weights.title`) | 491 titles |
| R2 | **Excluded before scoring** if the title has any of: Manager, Director, Head, Intern, Internship, VP, Vice President, Chief, Recruiter, Sales, Account, Counsel, Finance, Marketing, Partner | Management roles; internships and executive roles don't fit a graduate; job types that aren't engineering (Hemanth's own reasons in JS1: "recruiter position", "finance role") | Hemanth, Q2 = c (Nov 22). Manager/Director/Head come from JS1 `CONTRACT.md`; Intern/VP/Chief/Director from greenhouse-watch `exclude_title_patterns` | 507 titles |
| R3 | **Excluded before scoring** if the text has the phrase "security clearance" | Priya's profile excludes roles that need an active clearance | Hemanth, Q2 = c (from `profile.yml`) | 17 postings |
| R4 | Each **distinct skill** in the title or text adds **+1.0**, at most 8: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS | The skills Priya has shipped. Each counts once, however often it appears | words: Priya's résumé (JS1 rule); 1.0 and the cap of 8: inherited (`weights.skill`, `max_skill_hits`) | Python 302 · SQL 139 · AWS 124 · Databricks 6 · Power BI 6 · Delta Lake 1 · the rest 0 |
| R5 | **+0.5 once** if at least one R4 skill appears | Rewards any overlap at all | inherited (`weights.skill_any`) | — |
| R6 | Ray and Kubeflow add **+0.25** each but do **not** count as a skill for R8 | She knows them but hasn't shipped them | 0.25: inherited (`weights.skill_unshipped`); not counting for R8: JS1 rule (Hemanth, Oct 31) | 0 |
| R7 | **+0.5** if the text has "MS" | Priya's degree; a posting that names it fits her | inherited (`weights.degree`) | 15 postings |
| R8 | A posting with **no R4 skill** is never kept | A role with none of her skills is not for her | inherited ("a job with zero skill hits is never relevant") and the JS1 rule | — |
| R9 | A **seniority word in the title** subtracts **2.0**, counted once: Staff, Principal, Senior, Sr, Lead. **From v1.1, "Staff" inside "Technical Staff" doesn't count** | Priya is early-career (Hemanth's JS1 reason: "very senior position"). Perplexity calls every engineer "Member of Technical Staff", which is a title, not a level | Hemanth, Q3 = b (Nov 22); −2.0: hand-set (Claude's recommended default, which Hemanth accepted); the "Technical Staff" exception: Hemanth, X1 (Nov 22, after the audit) | 322 titles (v1.0); 66 of them are "Technical Staff" titles |
| R10 | **Kept** if the score is **≥ 3.0** and R8 holds | A role word plus one skill (4.5) passes. With a seniority word (2.5), it takes two skills. Without a role word, it takes three skills (3.5), or two skills plus "MS" (3.0) | 3.0: inherited (`threshold`); Hemanth, Q6 = a | — |
| R11 | **Location never decides.** It is shown and checked as claim C4 | Priya is open to remote; a location filter would throw out 94% of postings without anyone reading them | Hemanth, Q4 = a (as in JS1). The inherited ±1.0 location weight is **cut** | Boston 12 · remote 64 · elsewhere 1,100 |
| R12 | **Sponsorship is not scored.** It is checked as claim C5 | No posting states sponsorship for the specific role. Every Anthropic posting carries the same company-wide paragraph ("We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate"). Notion and Perplexity use "sponsor" only for events and partners | Hemanth, Q5 = b | 815 of 815 Anthropic postings carry that paragraph. Notion and Perplexity: 0 postings say whether they sponsor the candidate (Perplexity's "Global Mobility Lead" talks about visas only because that is the job's subject) |
| R13 | An empty title, or text shorter than 200 characters, gives **"cannot tell"**, never "rejected" | Missing text is missing evidence, not a reason to reject | proposed by Claude | 0 postings today |
| R14 | **The shortlist:** the top **10** kept postings that are still listed in the latest snapshot, by score. Ties go to more distinct skills, then to the posting key | What reaches Priya. The tie-break is arbitrary but fixed | 10: Hemanth, Q7 (default); tie-break: proposed by Claude | — |

```filter
{
  "filter_version": "1.1",
  "matching": "whole word or phrase, ignore case",
  "role_words_title": ["AI", "Engineer", "Engineering", "ML", "Machine Learning", "Data"],
  "exclude_title_words": ["Manager", "Director", "Head", "Intern", "Internship", "VP", "Vice President", "Chief",
                          "Recruiter", "Sales", "Account", "Counsel", "Finance", "Marketing", "Partner"],
  "exclude_text_phrases": ["security clearance"],
  "skills": ["Python", "SQL", "Databricks", "Unity Catalog", "Power BI", "LangGraph", "MLflow", "Mem0", "Delta Lake", "AWS"],
  "skills_unshipped": ["Ray", "Kubeflow"],
  "degree_terms": ["MS"],
  "seniority_title_words": ["Staff", "Principal", "Senior", "Sr", "Lead"],
  "seniority_ignore_phrases": ["Technical Staff"],
  "role_ignore_phrases": [],
  "weights": {"role_word": 3.0, "skill": 1.0, "skill_any": 0.5, "skill_unshipped": 0.25, "degree": 0.5, "seniority": -2.0},
  "max_skill_hits": 8,
  "threshold": 3.0,
  "require_skill": true,
  "min_text_chars": 200,
  "shortlist_size": 10
}
```

**How this differs from the inherited scheme** (greenhouse-watch `scheme.default.json`, `default-0.1`):
- Its `title` and `title_partial` features matched Priya's résumé title. R1's role words replace them.
  - Under that scheme, "AI Engineer Co-op" kept only "engineer": words of 3 letters or fewer are dropped, so "AI" never counted.
- The location weights are cut (R11).
- The exclusions are extended (R2, R3).
- The seniority penalty is new (R9).
- Its `ignore_skills` list stays empty.

## 3. Evidence rules (proposed by Claude)

**Claims.** Every shortlisted posting gets a justification made of these claims, and only these:

| Claim | Text | Role in the answer |
|---|---|---|
| C1 | "This is an engineering, ML, data or AI role." | required |
| C2 | "The posting asks for *skill*." One claim per matched R4 skill, at most 3, in résumé order | at least one required |
| C3 | "The level fits an early-career candidate (MS Dec 2025, one 8-month co-op)." | a dealbreaker when contradicted |
| C4 | "The role can be done from Boston or remotely." | shown only (R11) |
| C5 | "The employer will sponsor a work visa for this role." | shown only (R12) |

**Labels.** Each claim gets one label, judged only against **this posting's own** title, location and text:
- **supported:** a quote from the posting asserts the claim.
- **contradicted:** a quote from the posting asserts the opposite. Examples: "5+ years of experience" or a title with "Staff" against C3; "this role is based in San Francisco" with no remote option against C4; "we are unable to sponsor" against C5.
- **insufficient:** no quote asserts the claim or its opposite. This includes text where the word appears but doesn't assert the claim. For example, "AWS" naming a partner or customer doesn't mean the role asks for AWS; "Python" in a list of client SDKs doesn't mean the job is Python work.
- **Conflicting evidence:** if the same posting has both a supporting and a contradicting quote, the label is **insufficient**, and both quotes are recorded.

**Quote check.** A supported or contradicted label must carry its quote. The quote must appear verbatim in that posting after whitespace is normalized; if not, the label is rejected as ungrounded. An insufficient label carries no quote. A machine checks this; whether the quote actually asserts the claim is checked by hand (`SHORTLIST.md`).

**The answer for a shortlisted posting:**
- **"worth reading"**: C1 supported, at least one C2 supported, and C3 not contradicted.
- **"not for Priya"**: C1 or C3 contradicted.
- **"I cannot tell"**: everything else. That is: C1 insufficient, or no C2 supported, or R13 applies. The agent must then say "I cannot tell" and give the reason, never a guess.

C4 and C5 never change the answer.

## 4. Expected sources (proposed by Claude)

| Board | System | What the agent should see (the JS2 normalized shape) | When it's missing, the answer is |
|---|---|---|---|
| `greenhouse:anthropic` | Greenhouse Job Board API | `id`, `title`, `location.name` → location, `content` (HTML, double-escaped) → text, `absolute_url` | — |
| `ashby:notion`, `ashby:perplexity` | Ashby Posting API | `id`, `title`, `location`, `descriptionPlain` → text, `jobUrl`; postings with `isListed: false` are skipped when parsed | — |
| a missing **title** or **text** | | | "cannot tell" (R13), never "rejected" |
| a missing **location** | | | C4 insufficient; never rejected |
| a **board with no result** in a snapshot (failed, unverified, or not configured) | | | "no result for *board* (*reason*)", never "no relevant postings". JS2's two deliberate failures (`ashby:notion-does-not-exist-js2`, HTTP 404; `ashby:openai`, timeout) show up this way in every snapshot |
| a posting **gone** from the latest snapshot | | | still filtered and audited, but never shortlisted |

## 5. Wrong versions (proposed by Claude): plausible filters the tests must catch

| # | Wrong version | Why it's plausible | The test that catches it |
|---|---|---|---|
| W1 | **Substring matching** | Simpler than word boundaries | A title "AI Engineer" with the text "comply with employment Laws" must not score AWS. "Email" in a title must not count as "AI". (The Laws case really happened in JS1) |
| W2 | **Ranking by the raw number of matches** | More matches looks like a better fit | Posting A repeats "Python" 20 times; posting B names Python, SQL and AWS once each. B must rank above A |
| W3 | **Missing text scored 0 and rejected** | Zero evidence looks like a zero score | An empty text must give "cannot tell", never "rejected" |
| W4 | **A justification quote that isn't in that posting** (shifted pairing) | The quote is real, just from the neighbouring posting | The quote check must reject a quote found in posting B when the claim is about posting A |
| W5 | **Held-out labels leaking into tuning** | The more labels used, the better the fit seems | The audit sample and the held-out set must be disjoint, and the threshold fit must refuse any held-out id |
| W6 | **An exclusion applied after the score** | Every rule is "just a weight" | "Engineering Manager, Machine Learning" with Python and AWS (score 5.5) must be rejected by R2, never shortlisted |

## 6. Changelog: Added / Cut / Rejected

Each entry gives: date · version · change · who asked · measurement · decision. A rule that failed stays listed, because it is evidence about the corpus.

| Date | Version | Change | Who | Measured | Decision |
|---|---|---|---|---|---|
| Nov 22, 2026 | 1.0 | First version: R1–R14 | Hemanth (Q1–Q7), Claude (R13, tie-break, sections 3–5) | Hits in section 2; precision and misses **not measured yet** (that's the audit, `AUDIT.md`) | written before any JS3 code |
| Nov 22, 2026 | 1.0 | **Kept the bare word "Account"** in R2. Rejected the alternative: the phrases "Account Executive" and "Account Manager" | Hemanth: "c without phrases" | Claude measured this before the decision: "Account" also removes 3 engineering titles ("Staff+ Software Engineer, Account Abuse", "Staff+ Software Engineer, Account Abuse (Machine Learning)", "Staff+ Software Engineer, Account Creation") | kept; the audit will show the cost |
| Nov 22, 2026 | **1.1** | **Added (X1):** "Staff" inside "Technical Staff" is not a seniority word (`seniority_ignore_phrases`). **False friend:** Perplexity titles every engineer "Member of Technical Staff" | Claude proposed it after the audit; Hemanth: "X1 accept" | On the 55 audit labels (`AUDIT.md`): **39 → 42 correct** (+4 relevant postings now kept, +1 kept that Hemanth marked not relevant). Corpus: kept 194 → 212; 18 postings flip from rejected to kept, all Perplexity "Technical Staff" titles. The audit labels found the problem, so this in-sample gain flatters the change; the held-out test is in `SCORE.md` | **accepted** |
| Nov 22, 2026 | 1.1 | **Rejected (X2):** drop the seniority penalty (R9) entirely | Claude measured it as the alternative that follows Hemanth's verdicts (11 of 14 senior-titled audit postings marked relevant); Hemanth: "X2 reject" | 39 → 42 correct, no better than X1. Kept 194 → 254 (60 more). It would reverse Hemanth's Q3 answer | **rejected** |
| Nov 22, 2026 | 1.1 | **Rejected (X3):** drop "must name one of Priya's skills" (R8) | Claude; Hemanth: "X3 reject" | 39 → 40 correct; kept 194 → 266 (72 more). R8 rejected 7 of the random rejects that Hemanth wanted. Dropping R8 brings back only 2 of those 7; the other 5 still score below the threshold. It also adds a false keep | **rejected** |
| Nov 22, 2026 | 1.1 | **Rejected (X4):** "Data Center" doesn't count as the role word "Data" (`role_ignore_phrases`). **False friend:** "Data" in "Data Center" (35 titles) | Claude; Hemanth: "X4 Reject" | 39 → 39 correct; 0 corpus postings change, because every "Data Center" title is already rejected by R8. The false friend does no harm today only because another rule blocks it | **rejected**; kept here as a known false friend |
| Nov 23, 2026 | 1.1 | **Out-of-sample check of X1** (no rule change). Labels were drawn after X1 existed but never used to choose it | Claude proposed it (Hemanth: "1 and 2 plus 3"); Hemanth labeled 20 postings blind | On 10 never-labeled postings that X1 changes, Hemanth wanted **7**: v1.1 is right 7/10 (Wilson 40%–89%), v1.0 is right 3/10. On 10 unaffected controls, both versions are right 9/10 (`audit/x1-results.md`) | X1 stays; the in-sample gain held out of sample, on a small set |

## 7. Decision record

| Q | Asked | Hemanth's reply (verbatim) | Recorded as |
|---|---|---|---|
| Q1 | Role words | "b" | R1: JS1's words plus ML, Machine Learning, Data |
| Q2 | Exclusions | "I'm ok with c but what to I do with the sales and accounting roles?", then, after Claude's answer and measurement, "c without phrases" | R2 with the bare word "Account"; R3 |
| Q3 | Seniority | "whatever the default is which is recommended" | R9 (b: −2.0 for a title word; "5+ years" only contradicts C3) |
| Q4 | Location | (same reply) | R11 (a: never decides) |
| Q5 | Sponsorship | (same reply) | R12 (b: claim only) |
| Q6 | Threshold | (same reply) | R10 (a: inherited 3.0) |
| Q7 | Shortlist size | (same reply) | R14 (10) |

**Status of Claude's proposals** (R13, the R14 tie-break, sections 3, 4 and 5): **accepted by Hemanth** ("accept") on Nov 22, 2026, at 2:07 PM EST, without changes.

**After the reject audit** (Nov 22, 3:33 PM EST), for the measured changes X1–X4, Hemanth replied: "X1 accept, X2 reject, X3 reject, X4 Reject". Claude had recommended exactly this and had pointed out the tension with Q3 (section 6, X2).
