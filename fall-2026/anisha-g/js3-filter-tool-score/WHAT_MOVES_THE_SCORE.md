# WHAT_MOVES_THE_SCORE.md (Chapter 9)
**Anisha Gaikar · JS3 · 2026-11-25.** Numbers regenerate with `python3 -m js3.report` (`out/report_original.md`, `out/report_corrected.md`). The Claude runs were real `claude -p` calls made on 2026-11-25 between 14:18 and 14:21 ET; every raw reply is in `runs/<experiment>/`.

## 1. Where every number came from
**Fitted on my labels: one experiment, not adopted (§2c).** No number in any adopted filter was tuned to my verdicts. The v1.1/v1.2 rules were *chosen* from audit items (v1.1 by Claude before my verdicts, v1.2 by me after them; FILTER.md §5), but no number in them was fitted.

| Number / object | Value | Origin | Where |
|---|---|---|---|
| Role words (R1) | analyst, analytics, business intelligence, BI, insights | **hand-set**: my choice (FILTER.md R1), from JS1's targets | `filters/filter_v1.0.json` |
| Seniority words (R2) | senior, sr, lead, staff, principal, manager, director, head, vp | **hand-set**: my choice; JS1 showed Lead/Senior asked for 5+ years | same |
| Skill list (R3) | the 10 core skills | **inherited**: `persona/resume.json` `skills.core` (JS1) | same |
| `min_skills` | 2 | **hand-set** (my choice) | same |
| `max_years` | 3 | **inherited**: the persona's `max_years_experience` (JS1) | same |
| Weights: title 3, per skill 1, skill cap 5, seniority −3, years −3 | | **hand-set**: Claude's proposal to reproduce my rule exactly (title + 2 skills = 5); I accepted it in FILTER.md §1.4 | same |
| `keep_threshold` | 5 | **hand-set** (= title + 2 skills). A **fitted** alternative (8) was tested and not adopted (§2c) | same; `tools/fit_threshold.py` |
| Close-call band | score 4–6, or exactly one failed rule | **hand-set** (FILTER.md §1.4) | `js3/filter.py:is_close_call` |
| R4 range reading in candidate v1.3 | bottom of a range | **hand-set** from my H2 reasons; **not adopted** | `filters/filter_v1.3.json` |
| `engineer` exclusion (R1b) | 1 word | **hand-set** by Claude at 14:21 from reading group C, **before** my verdicts; I accepted it after judging (v1.1) | `filters/filter_v1.1.json` |
| Education window | 40 characters after "N years" | **hand-set** by Claude, not tuned | `js3/filter.py:years_spans` |
| US / non-US marker lists (R5) | 69 / 73 place names | **hand-set** by Claude from the 406 distinct location strings in the **whole** corpus (which includes H's locations: a possible leak, see §4) | `filters/filter_v1.2.json` |
| Evidence cue words ("a plus", "preferred", "bonus", …) and heading words | | **hand-set** by Claude from FILTER.md §2's examples; the heading list was changed once, after a bug (SHORTLIST.md) | `js3/evidence.py` |
| Claude prompt (B) | JS1 `revised.txt`, unchanged | **inherited** (JS1) | `prompts/js1_revised.txt` |
| Claude prompt (E1) | JS1 `baseline.txt`, unchanged | **inherited** (JS1) | `prompts/js1_baseline.txt` |
| Model setting | `--model sonnet` (E3: `haiku`) | **hand-set** | `runs/experiments.json` |
| Context length (E2) | first 600 characters | **hand-set** | same |
| Boards, budget | 5 boards | **inherited** (my JS2 budget) | `boards.json`, `js3/collect.py` |
| Sample sizes and seed | A 30, B 10, C 6, H 30; seed 7375 | **hand-set**; 30 is the assignment's minimum | `tools/draw_sets.py` |
| Wilson z | 1.96 (95%) | convention | `js3/report.py` |

## 2. One change to one object at a time, measured on held-out labels
- **The held-out set H:** 30 postings drawn **before** any judging (commit `0810190`), judged blind among the other 46, and never used to choose a rule.
- **The scorers:** filters, the evidence-gated shortlist, and Claude, each predicting "worth Nadia's time" (kept / `relevant`) against my verdict.
- **The Claude plan:** every experiment was written in `runs/experiments.json` and committed (`f30af68`) **before any Claude call and before any hand verdict**. The Claude runs (`4b4dffd`) were also made before my verdicts existed.

**Held-out result: 30 labelled, 1 "y", 29 "n" (original verdicts).**

| Object changed | From → to | Scorer | TP | FP | FN | TN | Accuracy | Wilson 95% |
|---|---|---|---|---|---|---|---|---|
| — | baseline: **always "not relevant"** | | 0 | 0 | 1 | 29 | 96.7% | 83.3–99.4% |
| **filter file** | v1.0 | filter | 1 | 4 | 0 | 25 | 86.7% | 70.3–94.7% |
| **filter file** | v1.0 → **v1.1** (R1b + education years) | filter | 1 | 4 | 0 | 25 | 86.7% | 70.3–94.7% |
| **filter file** | v1.1 → **v1.2** (R5 US-only) | filter | 1 | **1** | 0 | 28 | 96.7% | 83.3–99.4% |
| (evidence gate) | filter v1.0 → filter v1.0 + evidence gate | shortlist | 1 | 2 | 0 | 27 | 93.3% | 78.7–98.2% |
| — | **B**: JS1 revised prompt, full text, sonnet, no tools | Claude | 1 | 2 | 0 | 27 | 93.3% | 78.7–98.2% |
| — (noise floor) | **B2**: exact repeat of B | Claude | 1 | 2 | 0 | 27 | 93.3% | 78.7–98.2% |
| **prompt** | B → **E1** (JS1 baseline prompt, no written rules) | Claude | 0 | 0 | **1** | 29 | 96.7% | 83.3–99.4% |
| **context** | B → **E2** (title + first 600 characters) | Claude | 0 | 0 | **1** | 29 | 96.7% | 83.3–99.4% |
| **setting** | B → **E3** (model haiku) | Claude | 0 | 1 | **1** | 28 | 93.3% | 78.7–98.2% |
| **tool list** | B → **E4** (offered my `score_posting` tool; it called it 30/30) | Claude | 1 | **1** | 0 | 28 | 96.7% | 83.3–99.4% |

**Disagreements, item by item** (`out/report_original.md`):
- **v1.2's R5 removed 3 false keeps** (Toronto WFM, Mexico City Credit Risk, Bengaluru Processing Cost).
- **E1 and E2 lost the one posting I said y to** (*Operations Insights, Business Partner Analyst*).
- **B's two false positives** were *Data Analyst, Intern* (my reason: "grad May 2027 outside Dec27–Su28 window") and *Analytics Lead, SCC*.
- **E4 dropped *Analytics Lead*** (the tool reports R2: "lead"), but kept *Data Analyst, Intern*.

### What these numbers can and can't show
1. **H has only one positive** (H2, §2b, has three). With 1 "y" in 30, "always say no" scores 96.7%, tied with the best scorer. Every accuracy interval overlaps every other. **No change here can be called an improvement in accuracy; the sample is too small for that.** Recall is 0% or 100% on one posting. My lesson: H should have been stratified to contain more likely positives (I drew it before knowing how rare "y" would be).
2. **What I can say is item-level and descriptive.** On these 30 postings:
   - v1.2's location rule turned 3 false keeps into correct rejects and lost nothing;
   - the prompt and context changes each turned the single true keep into a miss;
   - offering the tool removed one false positive.

   Those are counts on this sample, not rates.
3. **The noise floor is 0 of 30.** The exact repeat B2 agreed with B on every posting. So for sonnet on this task, the changes E1–E4 made (1–2 postings each) are larger than run-to-run noise *on this sample*. One repeat is still one repeat.
4. **R5 may be slightly flattered.** Its place lists were written from all 406 location strings in the corpus, including H's. The rule itself came from my audit reasons, not H, but the word lists saw H's locations.

### One more change, recorded but not measured on H: the tool description (context)
After my server evaluation (TOOLSERVER.md), I added what R1–R5 mean to the `score_posting` description (commit `d6a5279`). The same planted-injection prompt:
- **before the change:** Claude explained the R3 rejection **wrongly** in 1 of 1 run (`claude-run3`);
- **after it:** **correctly** in 3 of 3 runs (`claude-run5a–c`).

That's 1 run before and 3 after, so it's **an anecdote, not a measurement**.

## 2b. A second held-out set (H2), because H had only one "y"
- **Why and how:** after H turned out to hold a single "y", I drew **H2**: 24 postings, seed 7376 (`tools/draw_h2.py`). They came from the 34 **unjudged** postings whose title passes R1 with no seniority word, the pool most likely to hold postings worth Nadia's time.
- **Order:** the draw and the plan (`runs/experiments.json` → `_h2`) were committed **before** any H2 verdict or Claude call (`e7bff47`). I judged H2 blind myself, 15:59–16:06 (`labels/hand_verdicts_h2.jsonl`, frozen in `bf4c812`). The Claude runs came after (`runs/H2/`, 120 calls, $1.85).
- **What was run:** E3 (haiku) was left out to save calls.

**H2 result: 24 labelled, 3 "y".**

| Object changed | From → to | TP | FP | FN | TN | Accuracy | Wilson 95% |
|---|---|---|---|---|---|---|---|
| — | always "not relevant" | 0 | 0 | 3 | 21 | 87.5% | 69.0–95.7% |
| filter file | v1.0 = v1.1 = v1.2 (identical on H2) | 0 | 0 | **3** | 21 | 87.5% | 69.0–95.7% |
| (evidence gate) | shortlist v1.0 | 0 | 0 | 3 | 21 | 87.5% | 69.0–95.7% |
| — | Claude **B** | 1 | 1 | 2 | 20 | 87.5% | 69.0–95.7% |
| — (noise floor) | Claude **B2**, an exact repeat of B | 0 | 1 | 3 | 20 | 83.3% | 64.1–93.3% |
| prompt | B → **E1** (baseline prompt) | 1 | 0 | 2 | 21 | 91.7% | 74.2–97.7% |
| context | B → **E2** (600 characters) | 0 | 0 | 3 | 21 | 87.5% | 69.0–95.7% |
| tool list | B → **E4** (offered my tool) | 0 | 1 | 3 | 20 | 83.3% | 64.1–93.3% |

**What H2 shows (counts on 24 postings, not rates):**
1. **My filter catches none of my 3 "y" postings, and the reason is one rule.**
   - The three: *Renewals Analyst*, *AMER Data Analyst – Sales Strategy and Operations* and *Customer Success Operations Analyst*.
   - **R4** rejected all three: it counts the **top** of a range ("3–5 years" → 5). My own reasons accept them, e.g. "accepts 3–5 yrs analytics (3 ≤ limit)": I read a range by its **bottom**.
   - So FILTER.md R4 says something I don't actually believe. I only found that by judging postings near the boundary, which H didn't contain.
2. **The noise floor is real here.** B and B2, identical settings, disagreed on **1 of 24**: *AMER Data Analyst* was y in B and n in B2.
   - Every Claude change on H2 moved results by 0–1 postings, which is **no larger than the noise**.
   - So on H2 I can't attribute any difference to the prompt, the context or the tool list.
3. **Offering my tool pulled Claude toward my filter's blind spot.**
   - **On H2:** E4 found 0 of 3, where B found 1 of 3. With the tool, Claude followed `score_posting`'s R4 rejection. On *AMER Data Analyst* (both replies from 2026-11-25, in `runs/H2/`):
     - **B, without the tool:** "its minimum of 3 years does not exceed the candidate's max of 3" → relevant.
     - **E4, with the tool:** "the posting asks for 3–5 years…, which score_posting marks CONTRADICTED" → not relevant.
   - **On H:** the same anchoring removed a false positive (*Analytics Lead*: R2 "lead").
   - Adding the tool makes Claude **inherit the filter's judgment**, good and bad. That's within noise on these samples, but it's the mechanism visible in the item tables.
4. **A candidate filter v1.3 (R4 counts the bottom of a range)** was built from this finding, tests first (`logs/14` → `logs/15`):
   - **On H2** it catches 2 of 3 with no false keeps, but that is **circular**: the rule came from H2.
   - **On H**, where it can be tested cleanly, it is **identical to v1.2** (1 TP, 1 FP).
   - **So there's no clean evidence for v1.3, and it is not adopted** (FILTER.md §5). Testing it needs a third labelled set.

## 2c. A fitted number: the keep threshold fitted on my audit labels
`tools/fit_threshold.py` (`logs/42`, `out/fit_threshold.json`):
- **The fit:** the threshold was fitted on the 46 audit labels (A, B, C, with 1 "y") over thresholds 3–9; everything else is as in v1.2.
- **Result:** best dev accuracy at **threshold 8** (97.8%, versus 91.3% at the hand-set 5).
- **Measured on data the fit never saw:**

| Held-out set | hand-set 5 | fitted 8 |
|---|---|---|
| H (30, 1 y) | 96.7%: TP 1, FP 1 | 96.7%: TP **0**, FP 0, FN 1 |
| H2 (24, 3 y) | 87.5%: TP 0, FN 3 | 87.5%: TP 0, FN 3 |

**What this shows:** with a single "y" in the dev labels, the fit learns "keep almost nothing". It buys a lower false-keep count by giving up the one posting I wanted, so held-out accuracy doesn't move. **A number fitted on labels this lopsided isn't better than a hand-set one, just more confident.** I kept 5.

## 3. What persistence is not proof of
- **Every Claude call here was a fresh, separate session** (`claude -p`, one process per posting), with the same model flag.
- **Any change in behaviour came from what I put in front of the model:**
  - the prompt file;
  - the context (full text or 600 characters);
  - the tool list (E4);
  - the tool's description (run 5).
- **Nothing was trained.** The model's weights were the same in every call.
- **When a behaviour persists across sessions, it doesn't mean the model learned anything.** In run 5, Claude explained R3 correctly in three new sessions in a row only because the description **file on disk** changed, and every new session reads it. If I reverted the file, the old behaviour would be back. The same holds for anything Claude Code carries between sessions (CLAUDE.md, saved memory, MCP configs). That's stored context, re-read each time, not training.
- **Agreement isn't learning either.** B and B2 agreeing 30/30 shows the setup is **repeatable**, not that the model "learned" my preferences. Stable answers to a stable input are what you'd expect from an unchanged model.
