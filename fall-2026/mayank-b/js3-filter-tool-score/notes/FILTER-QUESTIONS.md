# JS3 filter: your questions (answer these before any code exists)

**How to answer.** Under each question, write **A / B / C** or your own words after `→ Your answer:`. Short answers are fine, and "all ★" is a valid answer. The ★ marks my recommendation. **The decisions are yours.** The brief says `FILTER.md` comes before the build, and Chapter 1 says *"Claude can sharpen the gate. It cannot write it for you."* I'll turn your answers into `FILTER.md` **in your words**, list every edit I make (as GATE.md did in JS2), and we commit it as **JS3-CP1 before any code**.

Each block names the **midterm study-guide section** it practises (`~/Desktop/AgenticAI/Midterm_Prep/STUDY_GUIDE.md`).

Written by Claude Code on 2026-11-23. Every number on this sheet comes from your saved JS2 raw files and was counted today. None of it is a JS3 result.

---

## 0. Before anything: the due date

The brief in the repo (`assignments/assignment-js3-…md`, unchanged since 2026-10-11) says **"Due: Monday, November 23, 11:59 pm ET"**. **That's tonight.** You've told me the Canvas header says **"Due Wednesday"**, which would be November 25. Classmates are already committing JS3 folders (`fall-2026/{prasad-s,rayudu-h,smit-p,pavan-m,tushar-p}/js3-filter-tool-score/`).

  A. Check Canvas now. If it says Wednesday 11/25, plan for Wednesday, and screenshot the header for FRICTIONAL ★
  B. Assume tonight. I'll cut the plan to the minimum (see BUILD-PLAN.md, "Track T")
→ Your answer:

## 1. Language (decide first)

  A. **Python 3, standard library only**, the same as JS2. The course CI (`scripts/validate_course.py`) rejects `.js/.ts` outside `learning-artifacts/`. JS2 passed the validator's rules locally, and a TA can run it from a fresh clone with no install ★
  B. Something else (it will be flagged by CI)
→ Your answer:

## 2. What you start from (the brief: "Say what you started from")

  A. **Your JS2** (loop, allow-list, policy, raw + SHA-256, checker), plus **Lectern's filter as the model for FILTER.md**: `keywords.json` (`version`, `keep_rule`, `role_title`, `topic_text`, `ignore_words_by_company`, `removed_after_measurement`, `measured_before_adding`) and `title_families.json` (families with `expect` keep/reject/judge, and "FALSE FRIEND" notes) ★
  B. Your JS2 plus the Reallocation Engine's role scorer
→ Your answer:

## 3. The corpus (STUDY_GUIDE §15: what reaches Claude is a chain of omissions)

**The facts.** Your saved JS2 responses (not counting the SEEDED run) hold **959 unique postings**, de-duplicated by id with the newest run winning:
- **Anthropic (Greenhouse): 679.** 678 in the 11-11 second check, plus 1 that disappeared after the 00:26Z run.
- **HubSpot `hubspotjobs` (Greenhouse): 124.**
- **Notion (Ashby): 156.**

**Greenhouse posting text is missing.** JS2 fetched without `?content=true`, so the 803 Greenhouse postings have a title, a location and metadata but **no description**. Notion has `descriptionPlain` for all 156 (median about 7,500 characters).

  A. **One new allow-listed run of the JS2 loop with `?content=true`** for Greenhouse anthropic and hubspotjobs, plus Ashby notion, so all three boards share one date. That's **3 requests**, inside JS2's budget of 10 requests per run. Same two hosts, GET only, raw bytes + SHA-256 saved. A dated line goes in the decisions log. The 11-11 files stay as history ★
  B. Use only the saved 11-11 files. Title rules could then run on all 959, but **every Anthropic or HubSpot shortlist claim would be "insufficient" (no text)**, and Step 2.2 needs text.
  C. One request per job for details: about 800 requests. No.
→ Your answer:

**3b. Before the fetch, write your expected sources (Chapter 7: lock the prediction before you look).** For each board, write the count you expect and the fields you expect (title, location, text). → Your predictions, dated:

## 4. Priya's target: role words (title) and topic words (text)

The fictional persona `persona/priya-nair.resume.json` is an AI Engineer co-op (Staples), with an MS in Information Systems, Python, SQL, Databricks, LangGraph, MLflow and LLM evaluation. Her JS1 `search` block has these targets: `AI Engineer, ML Engineer, Machine Learning, Applied AI, Data Engineer, LLM`. It excludes `Senior, Staff, Principal, Lead, Manager, Director, Head of, Intern`.

**4a. Role words (title)**
  A. Keep the JS1 lists as v0.1, inherited and labelled so ★
  B. Change them. Add or remove: ____ (for example "Forward Deployed Engineer", "Solutions Engineer", "Software Engineer, AI")
→ Your answer:

**4b. Topic words (posting text).** Pick from these, or write your own: `python`, `sql`, `llm`, `rag`, `evaluation`, `mlflow`, `databricks`, `langgraph`, `agents`, `data pipeline`, `machine learning`. One line of reasoning per word.
→ Your list:

**4c. Company boilerplate (Lectern's `ignore_words_by_company`).** Words in nearly every posting on a board, such as "AI" at Anthropic, are not a signal.
  A. Measure each topic word's share per board after v0.1 runs. Any word in ≥ 90% of a board's postings goes on that board's ignore list, recorded as a measured change ★
  B. No ignore list
→ Your answer:

## 5. Title rules vs text rules, and the score's shape (STUDY_GUIDE §15, §22)

The brief asks for "the closest calls near your threshold", so you need a number with a threshold.

  A. **Lectern's shape.** Hard gates first: an exclude word in the title, or a location Priya won't take, means reject. Then **keep if a role word is in the title, OR at least T distinct topic words are in the text**. The score is the count of distinct topic words, so the closest calls are rejects with T−1. Every kept or rejected record stores the words that matched and where. ★ T = 3, Lectern's number, inherited and labelled.
  B. Weighted points (title hit +3, each topic word +1, keep at ≥ 4). It has more numbers, and each one needs an origin for Step 4.
  C. A Claude score (0–10). Its numbers are not recomputable by hand, and it has to be sampled more than once.
→ Your answer (and T):

**5b. Location.** JS2 showed that the JS1 rule misses "Remote - USA" (`runs/2026-11-11T02-24-39Z-second-check/`).
  A. Fix it in v0.1 from that dated evidence, accepting `Remote - USA`, `Remote - US`, `United States` and `US-Remote` ★
  B. Leave it, and fix it later as a measured change
→ Your answer:

**5c. Level from the text.** Phrases like "5+ years" in the posting text.
  A. **Not a filter rule.** It becomes a **shortlist claim** ("level fits early-career") that gets labelled supported, contradicted or insufficient ★
  B. Reject any posting that asks for ≥ N years
→ Your answer:

## 6. Evidence rules (STUDY_GUIDE §13, §15; Chapter 7 "Relevance and entailment are separate checks")

**6a. Labels.** Each claim in a shortlist justification gets one label, measured against **that posting's own text**:
- **supported:** a quoted passage states the claim, within its scope.
- **contradicted:** a quoted passage says the opposite. Example: the claim is "early-career OK" and the text says "7+ years".
- **insufficient:** the nearest passage is on topic but doesn't settle the claim. The row says what is missing.
- **not reviewed.** ★ Only you may mark a row supported, after reading the original.
→ Accept, or edit:

**6b. The claims per posting** (one sentence each, no "and"). ★ C1 the role matches Priya's target · C2 the location is one Priya accepts · C3 the level fits early-career · C4 the work uses a skill Priya has (it names which one) · C5 (yours?)
→ Your answer:

**6c. When must the agent say "I cannot tell"?**
  A. When the posting has **no text**, or the field a must-claim needs (C2 location, C3 level) is missing or insufficient. The posting then goes on a separate **"cannot tell"** list, never on the rejects and never on the shortlist ★
  B. Only when the text is missing
→ Your answer:

**6d. The abstention rule's known limit (the brief: "one counterexample").** ★ Candidate: a posting where C4 is lexically matched ("experience with LLMs") but the role is sales or support. Relevance passes and entailment fails. → Fine, or name another:

## 7. Expected sources, and what to answer when something is missing (STUDY_GUIDE §13)

  A. The boards are the three in Q3, plus JS2's deliberate bad slug (kept as a regression check). The fields are id, title, location, url, updated and text. Missing text means "I cannot tell" (Q6c), **never a silent reject**. Missing location means C2 is insufficient. A failed board follows **JS2's error policy unchanged** (error, not 0) ★
  B. Edit:
→ Your answer:

## 8. Wrong versions your tests must catch (≥ 2 required; pick, then add yours)

- [ ] **WF1 substring match.** `"intern" in title`. In your saved titles, substring "intern" hits **15** titles while whole-word hits **6**. One of the extra hits is "**Applied AI Architect, International Policy**", which an exclude-by-substring rule would throw away even though it carries a target term.
- [ ] **WF2 ranking by raw keyword count.** Counting repeats instead of distinct words lets a long posting that says "AI" 40 times outrank a short one that fits.
- [ ] **WF3 relevance treated as entailment.** A posting that matches C4's word is labelled "supported" for C3 or C4 without a quoted passage.
- [ ] **WF4 silent drop of postings with no text.** A posting with no text is scored 0 and lands in the rejects instead of "cannot tell".
- [ ] **WF5 boilerplate counted as a signal.** A company-wide word (Q4c) pushes every posting on one board over T.
- [ ] **WF6 the tool server answers before the handshake.** It sets `ready` inside `initialize` and so skips `notifications/initialized` (Chapter 8's first wrong version).
→ Yours:

## 9. The false friend (the brief requires at least one)

You have to **find** it in the audit, not decide it now. Candidates to watch: **"pipeline"**, which appears in **70 of 156** Notion postings' text (is it a data pipeline or a sales pipeline?) · **"training"** (model training vs teaching people, Lectern's own false friend) · **"agent"** (an AI agent vs a support agent) · **"evaluation"** (model evals vs performance reviews).
→ Nothing to answer now. Tick which ones you want the audit sheet to flag:

## 10. The reject audit (STUDY_GUIDE §23: what a sample can show)

  A. A **seeded uniform random sample of 30 rejects**, plus **every close call** (score T−1; if there are more than 15, a seeded 15), plus a **seeded 10 of the kept**. You fill in the verdict column by hand. The seed is committed before the draw. ★
  B. Bigger: 50 rejects
→ Your answer:

**10b. How you'll state the result** (you write the sentence; here is the arithmetic). If 0 of 30 random rejects are wrong, the one-sided 95% upper bound on the reject error rate *for that snapshot's reject pool* is about **9.5%** (n = 50 gives 5.8%). If k > 0, report k/30 with an exact interval. Never write "the filter misses X% of jobs."
  A. Use that wording ★
  B. Your own
→ Your answer:

## 11. The tool server (STUDY_GUIDE §16–19; Chapter 8)

**11a. The one capability**
  A. **`score_posting`**: read-only. The input is a posting id from the saved corpus, or a posting object. The output is the filter's record: verdict, score, matched words, and "cannot tell" reasons. **No network, no writes outside `runs/<id>/`**, and no send, apply or email ★
  B. `search_new_postings`, which fetches the boards live. That makes the tool a network actor, with more to defend.
→ Your answer:

**11b. Protocol shape.** ★ newline-delimited JSON-RPC 2.0 over stdio: `initialize` (protocolVersion `2025-11-25`) → `notifications/initialized` → `tools/list` → `tools/call`. "Unknown id" is a **result with `isError: true`**. Bad arguments, an unknown tool or a call before ready is a **JSON-RPC error** (-32602 / -32000). It needs real transcripts in both directions, plus one connection from a real client (Claude Code via `claude mcp add`, configured project-local).
→ Accept or edit:

**11c. The other tool server you evaluate** (the brief: "from a source you can name")
  A. **Chapter 8's teaching server**: `lessons/08-mcp-from-scratch/code/main.py` in the course repo, 72 lines, pinned to a commit. It's offline, and you can inspect and run it. It has known gaps: it ignores the requested version, drops a `tools/call` with no id, and lets a second `initialize` keep `ready` ★
  B. An **official MCP reference server** from `github.com/modelcontextprotocol/servers` (for example `src/time` or `src/fetch`, both Python). That needs one read-only clone. `fetch` is a stronger trust case (arbitrary URLs), but you only inspect it and never run it.
  C. A classmate's JS3 server. **Ask a TA first**, because of integrity concerns and because it might look like copying.
→ Your answer:

**11d. Trust decision format.** ★ Chapter 8's four ledgers (protocol / capability / permission / evidence). Each entry gets an evidence type (advertised / source-inspected / executed / uninspected), then allow, deny or pending, plus a re-review trigger.
→ Accept:

## 12. What moves the score: one change at a time (STUDY_GUIDE §22–23; Chapter 9)

**12a. Held-out labels.** JS1's 20 labels (8 held-out, only 1 of them relevant) were already used, so per Chapter 9 they're **development data now**.
  A. A **new seeded held-out set of 30**, stratified (10 drawn from v0.1-kept, 10 from close calls, 10 from random rejects), **labelled blind** (the sheet hides the filter's verdict and score), committed sealed **before** any rule is changed, and used once ★
  B. 40, the same design
→ Your answer:

**12b. Which object changes first** (only one, and everything else is held fixed)
  A. **The filter file**: the one rule change your reject audit suggests, measured on held-out (agreement, false keeps, false rejects, before vs after) ★
  B. The prompt (only if Q13 = yes)
  C. The context given to Claude (title-only vs title + text)
  D. A setting. Note that `temperature` is rejected by the current API (version 2026-10-21), so the setting would be `effort`.
→ Your answer (a second change is optional):

**12c. Persistence.** ★ "A saved filter file changing later runs is configuration persisting, not training: no weights moved." → Your wording:

## 13. Use a Claude prompt anywhere?

  A. **No Claude in the filter or the score.** Claude writes **one short justification per shortlisted posting**, from the posting text and Priya's search block, using model `claude-haiku-5-5` as in JS1 (current Haiku, $0.10 per million input tokens). Its claims are what you label in Step 2.2. **Budget: ≤ 40 calls**, 1 per shortlisted posting, plus one re-run of 5 to show variation. The key comes from the git-ignored `.env`. `api.anthropic.com` is allowed **only** for that script, never for the tool server ★
  B. No Claude at all. Justifications come from a template built from the match record. It's simpler, but relevance vs entailment is weaker to show.
  C. A Claude scorer (see Q5-C)
→ Your answer:

**13b. If A: SDK or raw HTTP?** ★ raw `urllib` (stdlib, no install, the JS2 allow-list pattern). The official `anthropic` SDK would add an install step for the TA. → Your answer:

---

## What only you can do (with time estimates)

| # | Task | When | Time |
|---|---|---|---|
| 1 | Check the Canvas due date (Q0) | now | 2 min |
| 2 | Answer this sheet (all ★ is fine; Q3b predictions and Q4b topic words must be yours) | now | 20–30 min |
| 3 | Read the FILTER.md draft and approve it, or edit it, before CP1 | after 2 | 10 min |
| 4 | Label the **blind held-out set** (30 postings) before seeing any filter output | after the fetch | 30–40 min |
| 5 | Judge the **reject audit** by hand: 30 random rejects + close calls (≤ 15) + 10 kept. Your verdicts, never pre-filled. Name the false friend | after the v0.1 run | 45–60 min |
| 6 | Label every shortlist claim S / C / I against the posting text, and write the deciding sentence where you disagree with Claude | after the shortlist | 30–45 min |
| 7 | Decide the trust verdicts (your server + the other one) | after the transcripts | 15 min |
| 8 | Run the review commands yourself and save the output (as JS2 `review/05-…`) | near the end | 10 min |
| 9 | FRICTIONAL in your own words, with more than one entry, and point to commits | throughout | 20 min |
| 10 | Sign or withhold, with a date; fill the driver's seat; OK the push | last | 10 min |

**Your total is about 3.5–4.5 hours.** When you've answered, tell me **"filter answers done"**.
