# For Shubham: what is left, in order

> **Historical.** This is the checklist Claude left on 2026-11-09. Shubham completed it on
> 2026-11-10; the commits are in `docs/js2/BUILD_LOG.md` and the git log.

Everything Claude could do is committed locally on `main`. **Nothing is pushed and nothing is
submitted.** JS2 is due **Tuesday 2026-11-10, 11:59 pm ET**. These parts are yours by the
course AI policy and the assignment's own wording; plan on about 1–2 hours.

1. **Read and adopt `GATE.md`** (10 min). It is Claude's draft (v0.1 + amendments A1–A4; A3 holds the review fixes, A4 the second-audit fixes). Change anything
   you disagree with, then change the header from "draft" to v1.0 and say what you changed.
   Commit it yourself. If you change a number (a budget, a floor), tell Claude: the plans and
   tests use those numbers.
2. **Check the wrong board by hand** (5 min). Open `https://ramp.com/careers` and see where its
   job links go. Open `https://boards-api.greenhouse.io/v1/boards/ramp/jobs` and see the one
   stale posting. Confirm or fix `checks/expectations.toml`.
3. **The review packet** (20 min), `docs/js2/review/REVIEW_PACKET.md`:
   - Run the five commands in §5 yourself and paste what they print.
   - Read the patch: `git show 8259d8b -- src/job_search_agent/watch.py`.
   - Write your decision in §6: accept, revise or reject, with the evidence. (Claude recommends
     accept; the optional revision is described there.)
4. **The one approved write** (2 min). At a terminal: `uv run jsa watch reset greenhouse/ramp`,
   type `greenhouse/ramp` when asked. That clears the stale ID the wrong-board runs saved. Commit
   the result (`git add -A data/watch && git commit`). This is your evidence for B18 in real use.
5. **Optional but strong:** write or rewrite one test yourself before reading the code it tests,
   so the sign-off's "by a test I wrote before reading Claude's code" names something real.
6. **`FRICTIONAL.md`, JS2 section** (20–30 min). Your own account. Facts with commits are in
   `docs/js2/BUILD_LOG.md`.
7. **`SOURCES.md`, "What I wrote (JS2)"**, and the two `[Shubham: …]` notes there.
8. **Sign-off and driver's seat in `README.md`** (15 min). Facts and candidate limits are in
   `docs/js2/FACTS_FOR_SIGNOFF.md`. Fill the "Why that part stays mine" column in your words.
   Sign or withhold.
9. **Read `docs/js2/REVIEW_BY_AGENT.md`**, the independent reviewer's report (verbatim), and the
   list at its end of what Claude fixed and what is left to you. Its score estimate and its
   suggestion for the relative-quartile points are worth reading before you write anything.
10. **Optional:** one more live run later today, `uv run jsa watch run`, so a run shows new
    postings on a different day. Commit `data/watch`.
11. **Push and submit.**
    - Push this repo: `git push origin main`.
    - Build the course folder and zip: `scripts/package_js2.sh` (it refuses while a
      `[Shubham` placeholder remains in README, FRICTIONAL, SOURCES, GATE or `docs/js2/`, while the
      sign-off is unsigned, or while `GATE.md` still says it is a draft).
    - In the course repo: commit and push `fall-2026/shubham-b/js2-loop-tools-diff`.
    - Canvas: upload `Bagwe_Shubham_INFO7375_JS2.zip`; paste the GitHub folder link, the final
      commit hash the script printed, and the run commands from `README.md`.

Things Claude did not do on purpose: write your sign-off, decision, driver's-seat reasons or
Frictional entries; push; submit; run the reset (it needs you at a terminal).
