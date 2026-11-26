# What moves the score (Chapter 9)

> Claude Code drafted this file from the code and result files it cites. Lines marked **My view** are for my own words.

## 1. Where every number came from

**Origins:**
- **hand-set**: chosen by a person (me, or Claude's suggestion that I accepted) without fitting it to labels;
- **fitted**: chosen to maximize agreement with my hand labels;
- **inherited**: carried over unchanged from JS1 or JS2;
- **default**: not set by anyone in this project; whatever the tool does.

| Number / object | Value | Where it lives | Origin |
|---|---|---|---|
| Title disqualifier words (F2) | Staff, Principal, Director, Manager, Head of, Intern, PhD, Contract, Temporary | `agent3/filter.py` `disqualify_title` | **inherited** (JS1 CONTRACT.md). Cutting the level words (C1) was measured and rejected. |
| Full-time values (F3) | Ashby `FullTime`; Lever `Permanent` | `fulltime_values` | **hand-set** from the field values seen in the Nov 10 responses |
| Role words (F4) | 9 phrases | `role_words` | 6 **inherited** (JS1 `target_titles`), 3 **hand-set** (Data Engineering, Analytics Engineering, Data Pipeline) |
| Role weight | **4** | `role_weight` | **hand-set** ("a title alone should not keep a posting", FILTER.md F7) |
| Topic groups and terms (F5) | 7 groups, 19 terms | `topic_groups` | **hand-set**. Guards for `streaming` (C3) and `orchestration` (C4) were measured and rejected. |
| Topic weight / cap | **+1** per group, at most **4** | `topic_cap` | **hand-set** |
| Skills (F6) | Jack's 8 | `skills` | **inherited** (JS1 persona) |
| Skill weight | **+1** each, no cap | `apply()` | **hand-set** |
| Employer-name exclusion (F6) | on | `skip_employer_skill` | **hand-set after a measurement**: the JS1 rule kept 45 Snowflake postings on the employer's name. Not fitted to labels. |
| Phrase gap (v1.1, C2) | whitespace → any punctuation | `phrase_gap` | **hand-set after a measurement**: found by the second-method recompute, adopted on audit agreement (+1 of 50) |
| **Keep threshold (F7)** | **6 → 5** | `threshold` | 6 was **hand-set**; 5 is **fitted** on the 50 audit labels (v1.2). 3 and 5 tied; the tie-break toward 6 was hand-set before the fit. |
| Close-call band (F9) | ±1 | `close_band` | **hand-set** |
| Shortlist size (F9) | 10 | `shortlist_size` | **hand-set** ("what I could read in a sitting") |
| Too-little-text limit (F8) | 300 characters | `min_content_chars` | **hand-set**. No posting in the corpus is below it (the shortest is 2,391 characters), so F8 never fired on real data. |
| Quote minimum (E1/E3) | 3 characters | `agent3/claims.py` `MIN_QUOTE_CHARS` | **hand-set** |
| Claude model | `claude-opus-5-5` | `agent3/claude.py` | **inherited** (my JS1 choice) |
| Judge prompt | `prompts/judge_v1.md` | | **inherited**, byte for byte, from JS1 `prompts/judge_revision.md` |
| Judge prompt, changed | `prompts/judge_v2_abstain.md` | | **hand-set**: one paragraph added, and "cannot_tell" added to the verdict line (`diff prompts/judge_v1.md prompts/judge_v2_abstain.md`) |
| Justify and check prompts | `prompts/justify_v1.md`, `check_v1.md` | | **hand-set**, written by Claude Code for JS3 and never tuned on labels |
| Claims per justification | exactly 1 core_work, 1 level, 1 employment, 1–4 has/lacks | `agent3/shortlist.py` | **hand-set** |
| Sampling settings, effort, max tokens | not set | `claude -p` | **default**: Claude Code CLI 2.1.316 exposes no temperature, and effort was left at the model default. The CLI also reported `claude-haiku-5-5` usage in some sessions (its own background calls); replies came from Opus. |
| Loop budgets | 5 boards, 10 requests, 60 s, 1 s floor | `agent3/config.py`, `loop.py` | **inherited** (JS2 GATE.md) |
| Sample sizes and seed | 30 / 10 / 10 / 15+15; seed 20261124 | `scripts/draw_sample.py` | **hand-set** (sizes chosen by me; seed = the date) |

**Only one number in the scorer is fitted: the threshold.** Everything else is hand-set or inherited. So most of the scorer is a set of opinions written down, and the labels judge it; they did not shape it.

## 2. One change to one object at a time, on the 30 held-out labels

**The held-out set** is 15 random v1.0 rejects + 15 random kept or close-call postings, drawn before any label and labeled blind with the rest. No rule, prompt, or setting was designed on it. Each change below was run on it **once**.

**Labels:** as labeled, under the 2026-11-25 definition. By Claude's reading, 15 of the 80 labels contradict that definition; how many fall in the held-out 30 is counted in section 3.

Of the 30 held-out labels, **5 are in the known-noise list** (#9, #30, #38, #44, #71).

## 3. Results (`out/experiments/REPORT.md`, all held-out runs 2026-11-25)

| # | Object changed | A → B | Agreement with my labels (95% CI) | Verdicts changed |
|---|---|---|---|---|
| 1 | **the filter file** | v1.0 → v1.1 (rule C2) | 14/30 → **14/30** | 0 of 30 |
| 2 | **a setting** | threshold 6 (hand-set) → 5 (fitted on audit labels) | 14/30 (28–66%) → **21/30** (51–85%) | kept 4 → 17; missed relevant 15 → 5 |
| 3 | **the prompt** | `judge_v1.md` → `judge_v2_abstain.md` (may answer `cannot_tell`) | 12/30 → **12/30** | **0**; `cannot_tell` used 0 times |
| 4 | **the context** | + one line: the filter's own score and matched words for that posting | 12/30 → **12/30** | **0**; 0 of 30 reasons mention the filter, score or keywords |
| 5 | **the tool list** | + `score_posting` (my MCP server, v1.2) | 12/30 → **12/30** | **0**; Claude made **0 tool calls** |
| 6 | **the prompt, definition only** | `judge_v1.md` → `judge_v3_definition.md`: the four-criterion paragraph replaced by my 2026-11-25 definition, nothing else (`diff`) | 12/30 → **20/30** (47–83%) | **14 flipped**: 11 toward my label, 3 away |
| A–A | nothing (baseline asked again) | | 12/30 → 12/30 | **0 verdicts**, but **0 of 30 reasons** had identical text |

All 180 Claude replies were valid (150, then 30 for row 6, which I approved after seeing rows 3–5; the prompt was committed before its run). Every condition used the same call shape (`agent3/claude.py` `ask_claude_isolated`): no setting sources, no skills, no built-in tools, the prompt as the whole system prompt, and an explicit MCP list (empty except in row 5).

### What the numbers say, and what they don't

- **Claude answered `not_relevant` on all 30 held-out postings, in every condition.** It agrees with me only where I labeled `not_relevant` (12 of 12) and never where I labeled `relevant` (0 of 18).
- **Why:** the judge prompt is inherited unchanged from JS1, and it encodes the **old** definition: "the main day-to-day work is data engineering… not people management, not Staff/Principal/Director…". My labels use the 2026-11-25 skills-overlap definition. **The object that holds the criterion was not among the four I changed**, and changing the other four moved nothing.
- **The only change that moved agreement was the one fitted to the labels:** the threshold. That is the weakest kind of evidence, because it was chosen on labels drawn from the same sample. It is also the only number tuned toward the loose definition.
- **0 flips does not mean the prompt, context and tool list "don't matter".** It means that for these 30 postings, under a prompt whose criterion already settles each case, they did not cross a verdict. With all 30 verdicts `not_relevant`, a change could only show up as a flip to `relevant` or `cannot_tell`, and none happened.
- **The A–A control is the yardstick.** Re-asking changed no verdict and every reason's wording. So a reworded reason is never evidence that a change worked. Only verdict flips beyond what re-asking produces count, and with 0 flips from re-asking, even one flip would have been notable.
- **Thirty postings.** 12/30 is consistent with a true agreement anywhere from 23% to 59%.
- **Row 6 is the change that moved Claude:** the definition paragraph. 14 verdicts flipped, against 0 from re-asking (A–A).
  - **11 flips went toward my label.**
  - **The 3 flips away from it** (#10, #18, #59) are technical Solution/Account Engineer roles I labeled `not_relevant` ("not data engineer role"). The definition I accepted says solution or sales engineering does not count against a posting, so those **labels** contradict the definition. They were added to `labels/label_noise.md` *after* this run, and marked so.
  - **Of the 10 disagreements left, 8 are labels in the noise list** (#9, #10, #18, #30, #38, #44, #59, #71).
- **Two instruments, one definition.** Under `judge_v3_definition.md`, Claude and filter v1.2 agree on **27 of 30**, though neither saw the other's output: v1.2's threshold was fitted to my labels, and Claude was only given the definition. Where they still disagree with me, it is mostly where my labels disagree with my own definition.
- **What moved the score, in one line:** the objects that encode the **criterion** (the definition in the prompt, the threshold fitted to labels that carry it). Instructions about *how* to answer (abstain), extra *evidence* (the score), and extra *capability* (a tool) moved nothing.

> **My view:** Made four trials on the incorrect object. The judge prompt is the definition which all cases use, and I had it over from JS1 and hadn't noticed that it contained the old standard. Rows 3-5 are not redundant: they reveal that prompt's criterion deciding the answer is enough, even if the person is refusing to take part or claiming that evidence is lacking, and that the tool is being used. But they're responses to a query that I didn't pose. I should have determined the location of the criterion before making any other modifications. The only rows that are moved are row 2 and row 6, neither of which are clean. The threshold was fitted to other labels from the same sample – this was a follow up, not part of the plan. The 27-30 deal between Claude and filter v1.2 feels like two instruments coming together; both were aimed at my definition, one of them by fitting to my labels. That only indicates that they have a criterion, it does not indicate that the criterion is correct. I don't like something that I see in three chapters. Every time they contradict themselves, it is the label that is explained away. In Chapter 8 I changed the definition to fit my labels. Here I added #10, #18 and #59 to the noise list after the run that disagreed with them. All steps used were defensible and the second step is noted as post hoc. However, the direction is always the same and I have no way of knowing whether my labels are "noisy" or whether my definition keeps "catching up". The other set is used up - I have run 7 conditions on the other set, and it is spent. The next fair move is another sample which, by the current definition, will be labelled blind, with no alterations made since then to make the sample fit.

## 4. What persistence is not proof of

`experiments/persistence.py`, `out/experiments/persistence.json`. Six fresh `claude -p` sessions, with the same model, prompt (`judge_v1.md`), and posting: a Snowflake "Senior Solution Engineer", **not** in the label sample.

| Session | What it was given | Verdict |
|---|---|---|
| A1, A2 | the posting | `not_relevant` ×2: "a pre-sales Solution Engineer role… customer demos, proofs of concept… closing deals" |
| B1, B2 | the posting + `experiments/persistence_note.md`, loaded the way a memory file is ("Solution Engineer roles… count as data engineering work") | **`relevant` ×2** |
| C1, C2 | the posting, the note no longer loaded | `not_relevant` ×2 |

**The behavior "persisted" from one session to the next only while a file carried it.** Nothing was trained.
- Every session started empty (`--no-session-persistence`), with the same model id. Remove the file and the old behavior returns.
- A changed answer across sessions shows that **something in the context changed**: a memory file, a CLAUDE.md, a tool result, a notes file. It is not evidence that the model learned, or that its weights or training changed.
- It also shows the cost. In B1, Claude wrote that the posting "describes presales work (demos, proofs of concept, closing deals)", and then followed the note anyway. **Context can outvote the posting's own text.** That is why the evidence rules check quotes against the posting, not against what Claude was told.

> **My view:** This will be my takeaway from this chapter. In B1, Claude wrote the role correctly as presales but then called it relevant, since a file said so. Changes my own perspective on my own setup. All memory files, CLAUDE.md and notes file that I give to an agent is part of the instrument, as much as FILTER.md and threshold are. Every one should be versioned, committed and reported with a name, don't leave them in the context where nobody checks them. It also tarnishes the reputation of row 6: I removed Claude's verdicts by moving them, just like the note. That's when the change becomes the definition I am living by. It's a risk if it's a change that I wrote myself without reading it against the posting. What I'd want and didn't build, is for Claude to raise the red flag instead of just being silent, for instance: "the note says X, the posting says Y". The evidence rules should be there to guard against posting, and not against what Claude was told. But Chapter 7 demonstrated for me that my own meaning check is the weak link there, so for now it's half-way effective.
