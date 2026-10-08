# FRICTIONAL — Professor Bear's process log

## Executive summary

**What this is.** The honest process log for the work in this folder, written the way the course asks students to write theirs: what was tried, what went wrong, what changed, and who did what, the human or the AI.

**Why read it.** It's a real example of the log, not a constructed one. It shows the instructor's own work run through the same record students keep.

**What it records so far.** One working session on 2026-09-23, in three parts, and a check on 2026-09-26.
- **The assignment.** An audit of the Reallocation Engine against an old version of its student assignment turned up paths that no longer exist, commands that don't run on a fresh copy, and a scoring signal that counts for nothing. That led to a rewritten 100-point assignment: a recipe plus a rough working prototype, framed around the 3-3-2 split.
- **The demo.** Turning the CV into a facts file, and running the engine's job-board watcher on Figma with that CV. That part hit three points of friction. The first match looked wrong because it was wrong. The results didn't add up to the score because of a real bug. And the demo's first choice of résumé got replaced mid-session.
- **The dream-job recipe.** The folder README now holds an eight-step recipe (Figma first, then similar companies, gaps in my CV) mapped onto Assignment 2, with a first gap table built from quoted posting lines and quoted CV facts.
- **The check (2026-09-26).** The rewritten assignment existed but had never been pushed, so the version students saw still said "modes." Since then it's been rewritten as "The Reallocation Engine — Recipe Design Assignment," pushed to the course repo replacing the old recipe-step assignment, and a first worked recipe (my own Figma/advocate search) has been written against its required format, not yet pushed to the-reallocation-engine.
- **The portfolio (2026-09-26).** I decided to rewrite my figma-claude book as a Figma tutorial series, as portfolio evidence for the advocate roles. Then I moved it to a new repo, figma-for-educational-ai: a book, workshops and a YouTube playlist built on my Figma for Education account. There's a plan to review; nothing is drafted yet.
- **My own question.** A first recipe asking whether Figma has advocate or education work on flexible terms. The board's answer is no: both advocate roles are full-time, nothing mentions universities, and nothing is part-time or contract. So it's a networking question.

Every push to GitHub is listed at the bottom with its date and commit note.

---

## Entries

### 2026-09-23 — Auditing the Reallocation Engine and rewriting its assignment as a recipe plus a working prototype

- **Date and what I was working on:** Getting a detailed picture of the Reallocation Engine repository as it stands, using the original 25-point "Mode Design" assignment as the lens, and then turning that into this term's version of the assignment.
- **I tried / expected:** I expected the old assignment to still describe the repo, with maybe a stale path or two.
- **What happened:** It had drifted a long way.
  - **Wrong paths:** the assignment sends students to `modes/` and `modes/RUN_LOG.md`, and neither exists. Modes are now called *recipes* and live in `recipes/`. Student recipes go in `recipes/cases/<term>/`. Students log runs in `logs/runs/` and are not allowed to edit `logs/RUN_LOG.md`.
  - **Already superseded:** there was already a 100-point Summer 2026 successor ("Mode Build"), and this term's live assignment is Greenhouse Watch.
  - **Claims that checked out:** the 80 Days company table has 30,370 rows (the claim was "30K+"), the occupation table has 1,016 rows ("1,000+"), and the Playwright posting-liveness checker exists.
  - **Problems the check turned up:**
    - The role-quality signal has weight 0.0 in the scorer, so the "Cognitive Pivot" layer changes no Apply / Consider / Skip decision.
    - Only samples of the SEC Form D data ship with the repo.
    - `npm run bls:local-wage` fails on a fresh copy: it asks for a requirements file that isn't in the repo.
    - `scripts/sec/validate-h1b-join-sample.py` fails on a fresh copy: it needs a data file that is gitignored and not shipped.
    - `DOMAIN.md` lists both of those as runnable today.
    - `npm run score` overwrites two tracked example files unless it is given `--out-dir`. Running it did exactly that, and the files were restored.
    - The repo's CI calls test scripts in `scripts/test/` that don't exist.
    - The Greenhouse Watch brief links a `course/prerequisites/` folder that isn't in that repo.
    - `status.md` was last updated in June.
  - **Recent skills:** checked across the engine and Madison. The engine's only recent addition is `greenhouse-watch` (added Sep 17, extended Sep 19 to Ashby and SmartRecruiters boards). Madison has had no new skills since its last commit on Jul 2.
- **What I did:**
  - Had the old assignment rewritten as a 100-point, Fall 2026 assignment, `course/assignments/reallocation-engine-recipe-build.md` in the-reallocation-engine.
  - It calls everything a *recipe* now; "mode" survives only in a footnote explaining the rename.
  - The deliverable is **a recipe plus a rough working prototype.** The prototype must read real repo data, write both a JSON log and a Markdown report, label every value as record, model judgment, or your input, handle two named failure cases, and have an offline test. The easiest path is to feed the engine's existing scorer rather than rewrite it.
  - **A new opening section** explains what the engine is: the information-asymmetry problem, the fluency trap, the five kinds of evidence (two of them gates that can veto a role outright), and how the book, scripts, and recipes fit together.
  - **A "Facts about the engine that will bite you" list** covers the eight problems above. The "Before you start" commands include only ones seen to run on a fresh copy.
  - **The 3-3-2 argument** from my February 2026 essay: three hours networking, three building credibility, two researching and applying. The engine automates the research inside the "2," points the networking hours at funded sponsors with no open posting, and building the prototype *is* credibility work.
  - The essay's survey statistics are deliberately **not** carried in as facts. Students must trace any such number to its primary source or label it an assumption.
  - Each result must now say its next action (apply, network, or skip).
  - The domain justification must say which part of the two hours the recipe takes over.
  - A new example recipe, `network-targets`, turns the engine's rejects into a networking list.
- **What Claude or another person contributed:** Claude Code (Opus 5.5) audited the repo, ran every check, found and restored the overwritten files, and drafted the assignment. I set the direction:
  - a detailed summary first;
  - then the 100-point version;
  - rename everything to recipe;
  - require a rough working prototype;
  - add context on what the engine does;
  - frame it with the 3-3-2 argument. The tool can help most with the "2," so students can run a 3-3-2 day instead of applying all day, every day.

  The rubric weights (20 recipe, 20 prototype, 15 justification, 10 worked run, 15 presentation, 20 quartile) were Claude's proposal and are not yet confirmed.
- **What I understand now / still do not understand:** The engine's real product is time. Every skip it justifies is time moved back to networking and building. Still open:
  - the rubric weights;
  - whether role quality should carry weight in the scorer;
  - fixing `DOMAIN.md`, the missing CI scripts, and the broken prerequisite links in the engine repo.
- **Evidence and next step:**
  - Evidence: the assignment is at `course/assignments/reallocation-engine-recipe-build.md` in the-reallocation-engine. It is **not committed there yet**; that repo still needs my go-ahead for each push.
  - Next: confirm the weights and push the assignment; fix `DOMAIN.md` and the CI scripts.

### 2026-09-23 — greenhouse-watch demo on Figma, and the CV as facts

- **Date and what I was working on:** Building a small worked example in my course folder. It runs the Reallocation Engine's `greenhouse-watch` skill (new jobs on one company's board, matched to a résumé) so students can see the recipe-plus-prototype assignment done end to end.
- **I tried / expected:** A two-day watch on Figma's board, using a saved snapshot from 2026-09-19 as the first look and a live fetch on 2026-09-23 as the second. I expected a handful of new postings and one or two matches for an example student.
- **What happened:** Figma posted 11 new jobs in the four days and took down 3. For the example student Aarav, the one match was a **London** machine-learning job, flagged for a Boston F-1 student. The report's reasons for it also didn't add up: the lines summed to 6.0 and the score said 3.5. Partway through, I switched the demo to my own CV as "Professor Bear." With that résumé, **none** of the 11 new jobs matched. Treating the whole board as new, 3 of 160 matched, and the roles I'd actually look at (Designer Advocate, the agentic-experiences researcher) scored 0 and 0.5.
- **What I did:**
  - Had the skill's scoring checked against its rules. The score was right; the report hid one bonus line and printed the title credit twice.
  - Fixed the report lines in the skill and added a test proving the lines now add up to the score. The test failed on the old code and passes on the new; all 23 skill tests pass.
  - Committed and pushed that fix to the-reallocation-engine as `015843d` ("fix(greenhouse-watch): justification lines now sum to the score"), with an entry in its `logs/RUN_LOG.md`. Scores and verdicts from earlier runs are unchanged; only their printed reasons were incomplete.
  - Replaced the example-student runs with Professor Bear runs.
  - Wrote the CV as `facts/professor-bear-cv.json`, with contact details, links, DOIs, grant numbers, and other people's names removed, and derived the matching résumé from it.
  - Linked the duplicate board downloads to the two snapshots instead of storing four copies.
  - After the first push, added `CLAUDE.md` to this folder. It tells Claude Code to log every substantive change here in this file and add a line per push, and it spells out what counts as substantive, so the log stays complete without my having to ask each time.
  - Noticed on GitHub that the CV displayed nicely but the Figma jobs file was one 1.5 MB line. It isn't JSONL. It is ordinary JSON that Greenhouse sends minified, and the skill saved the exact bytes. Since the point of this folder is that students read and check it, I had every JSON file here reformatted indented: the Figma archive and both demo snapshots. The data was checked identical before and after, and the demo re-runs give the same results (152 at baseline; then 11 new, 0 relevant). `CLAUDE.md` now requires readable JSON for everything in this folder.
  - Started `figma/`, a dated archive of Figma's open jobs. The first file, `figma-jobs-2026-09-23.json`, is a fresh live fetch at 20:01 UTC: 160 jobs, the same set as the 19:54 UTC snapshot. Nothing changed in those seven minutes, which is expected; the archive's value comes from the days that follow.
- **What Claude or another person contributed:** Claude Code (Opus 5.5) ran every command, wrote the files, traced the scoring bug to its two causes, wrote the fix and the test, and drafted this entry. I chose the direction:
  - build something simple in my folder;
  - use the greenhouse-watch skill;
  - use my CV with personal information removed, as "Professor Bear";
  - keep the CV as a facts file;
  - keep this log, one line per push;
  - have a folder `CLAUDE.md` make updating this log automatic for any substantive change;
  - keep a `figma/` folder of the current jobs as JSON, named by date;
  - reformat all JSON as readable, because the point is for students to read it and check it;
  - commit the scoring fix in the-reallocation-engine and record it here, with links, as evidence;
  - give standing approval to push this folder after every substantive change, now written into `CLAUDE.md`. No token was needed: git on my machine was already authenticated.

  Later the same day I read `facts/professor-bear-cv.json` in full: accurate, no errors, and I will add more to it later. It is now marked `attested: true`. The job-matching résumé derived from it stays `attested: false`, because its skills list is Claude's selection from the CV and I have not reviewed that separately.
- **What I understand now / still do not understand:** A keyword scheme is honest but narrow. It explains every match, and it can't see that "teaches, runs workshops, builds AI tutors" describes an advocate. Its misses are exactly the roles I'd pick by hand, so the scheme is where students have to do the thinking. Still open:
  - whether the default scheme's rule of dropping every Director role is right for anyone but students;
  - how much a daily watch catches that a weekly one misses (only two snapshots so far).
- **Evidence and next step:**
  - Evidence: the demo is in `greenhouse-watch-demo/` (README, the run records and reports, both board snapshots), the facts file is `facts/professor-bear-cv.json`, the logging rules are in `CLAUDE.md`, and the dated job archive is in `figma/`. The skill fix and its test are in the-reallocation-engine, commit `015843d`.
  - Next: attest or correct the CV conversion; write a Professor Bear scheme (hard location gate, no Director exclusion, teaching-to-advocacy phrases) and re-run; run a third live fetch to get a real daily diff.

### 2026-09-23 — A recipe for my own question: flexible advocate or education work at Figma

- **Date and what I was working on:** Starting a recipe in `figma/README.md` for a question of my own. Does Figma have Designer Advocate or education-advocate work I could do on flexible terms: summer, contract, or part-time; going to universities to run workshops; or developing workshops for Figma?
- **I tried / expected:** I hoped the board would show at least one advocate or education role with flexible terms, or some university-facing work.
- **What happened:** Scanning the 160 postings saved at 20:01 UTC:
  - **Advocate roles:** 2 **Designer Advocate** roles. The one that states its terms is full time, from a US hub, with travel up to 25%. Both list $153,000–$317,000.
  - **Workshops:** *Designer Advocate, Partnerships* is the closest fit. It covers partner events and workshops, and equipping partners to educate their customers.
  - **Universities:** no posting mentions universities or campuses.
  - **Flexible terms:** no posting offers part-time, contract, temporary, seasonal, fixed-term, or freelance terms. The 9 "summer" or "hourly" matches are 8 internships and one full-time role paid hourly.
  - **No field to check:** the Greenhouse data has no employment-type field at all. Terms are only known when the posting text states them.
  - **A script bug:** the first version of the scan missed plurals. "workshop" didn't match "workshops," so the education table showed 5 postings instead of 10. Comparing it against an earlier rough search caught it.
- **What I did:**
  - Had the search written as a small script, `figma/find_roles.py` (offline, standard library only), instead of leaving the counts to a one-off query, so students can re-run it and check every number.
  - Fixed the plural bug and saved the report as `figma/roles-2026-09-23.md`.
  - Wrote the recipe into `figma/README.md`: purpose, inputs, steps, a human gate with three next actions (apply, network, skip), the first run's results, what it can and can't verify, and three open TODOs.
  - Gave the folder README an index.
  - Kept the two relevant postings, both Designer Advocate roles, in `figma/professor-bear-figma.json` alongside a readable `figma/professor-bear-figma.md`. A second small script, `figma/pick_postings.py`, copies chosen postings out of the day's file and uses the same word lists as the scan. The pay first came out as "Range:$153,000—$317,000" with its spaces lost, and each posting's text was one long escaped string in the JSON. Both were fixed before pushing: pay now reads "$153,000–$317,000 (annual base)," and the text is stored as one line per paragraph or bullet.
- **What Claude or another person contributed:** Claude Code wrote the script and the recipe draft, ran the scan, caught the plural bug by comparing against its own earlier search, and checked the missing employment-type field. The question, and what kind of work I want, are mine. So is the decision the recipe leaves open.
- **What I understand now / still do not understand:** The board answers the question honestly, and the answer is "not here." That makes this a networking question, not an application question, which is the 3-3-2 argument applied to my own search. Still open:
  - whether the word lists are right (the draft suggests adding "ambassador," "speaker," and "design education");
  - where, if anywhere, Figma announces contract or university work.
- **Evidence and next step:**
  - Evidence: `figma/find_roles.py`, `figma/roles-2026-09-23.md`, `figma/pick_postings.py`, `figma/professor-bear-figma.json` and `.md`, the recipe in `figma/README.md`, and the saved board `figma/figma-jobs-2026-09-23.json`.
  - Next: review the word lists; decide the next action for the two advocate roles; build the day-over-day diff.

### 2026-09-23 — The dream-job recipe, in steps, for Assignment 2

- **Date and what I was working on:** Turning the Figma work into a general recipe for finding advocate and education jobs: Figma first, later similar companies, then gaps in my CV. I also wanted it to feed Assignment 2 ("Plan Your Madison Project Like a Pro": dream job, gap analysis, PRD, architecture).
- **I tried / expected:** A step list I could follow, with the Figma steps already filled in.
- **What happened:**
  - The folder README now carries the recipe in eight steps:
    0. the CV as facts;
    1. watch one company;
    2. gap analysis;
    3. similar companies;
    4. gaps across roles;
    5. credibility work;
    6. networking;
    7. apply only when the terms fit;
    8. log every run.
  - Each step is marked done, first pass, or planned, and says which Assignment 2 part it feeds.
  - For Part 1, *Designer Advocate, Partnerships* is suggested as the dream job, as a judgment: it's the only role that builds certification and enablement programs and works at workshops. Its top three technical requirements are quoted from the posting.
  - For Part 2, a five-row gap table. A word search of the CV facts found **no** mention of Figma, design systems, tokens, prototyping, certification, enablement, or talks. It did find the Coursera course, the 700+ learner course, the 25+ AI course assistants, the workshops, and conference papers.
  - One claim in Claude's first draft was wrong and was fixed before pushing: the table called me a "full-time" Associate Teaching Professor, but the CV doesn't state hours.
- **What I did:** Directed the recipe's shape (Figma first; then similar companies; then gaps in the CV) and asked for anything from Assignment 2 that would make a better recipe.
- **What Claude or another person contributed:** Claude Code drafted the steps, mapped them onto the assignment, pulled the posting requirements and the CV matches as records, and proposed the gap judgments, the Madison ideas, and a three-agent architecture with an n8n outline. All are labeled as proposals. The "why this role" sentence, the hiring-manager research, confirming the gaps, and the PRD are left for me.
- **What I understand now / still do not understand:** The gap that matters most here isn't a skill. It's the terms: full-time with 25% travel against a teaching job. Skills gaps can be closed with credibility work; the terms gap needs a conversation. Still open:
  - whether the CV undersells public speaking (the original CV names a YouTube channel the facts file doesn't carry);
  - which n8n nodes hold up against n8n's own documentation.
- **Evidence and next step:**
  - Evidence: `README.md` (the recipe and the Assignment 2 table), `figma/professor-bear-figma.json` (the posting quotes), `facts/professor-bear-cv.json` (the CV quotes).
  - Next: write the "why this role" sentence; confirm the gaps; build the Figma board for Assignment 2 by September 25.

---

### 2026-09-26 — The assignment students see still says "modes"

- **Date and what I was working on:** Checking that the Reallocation Engine assignment reflects the recipe rename and the rewrite from September 23.
- **I tried / expected:** I pasted the old 25-point "Mode Design Assignment" and said: "I think these are called recipes rather than modes now. And we made those changes. There should be an update to the assignment reflecting ..." I expected the updated version to be in place.
- **What happened:** The update exists, but it never left my machine.
  - **The rewrite is there.** `course/assignments/reallocation-engine-recipe-build.md` in the-reallocation-engine is the September 23 version. It says "recipe" throughout, and "mode" appears only in its closing note on the rename.
  - **It is still accurate.** Every repo path it cites exists today, except `logs/gate-decisions/` and the full sponsorship data file. The assignment itself lists those two as missing. The engine repo has no commits since September 23.
  - **It was never committed or pushed,** so it isn't on GitHub. The 25-point text I pasted isn't in any local repo, so the copy students see is presumably the one on Canvas.
  - **Then two assignments, not one.** I said the paper version "should be called 'The Reallocation Engine — Recipe Design Assignment' … this is the first step. In a recipe implementation that will look more like this … write both assignments," and pasted a 100-point build version.
  - **Two facts in my pasted build version were out of date.** It said every top-level recipe is still DRAFT; five promoted Summer 2026 recipes are marked RUNNABLE-SAMPLE or RUNNABLE-LIVE (the core workflow recipes are DRAFT). It listed SmartRecruiters under `scripts/ats/`, which has Greenhouse, Lever and Ashby only; SmartRecruiters is read by the greenhouse-watch skill. Both were corrected.
  - **Which course, and why 25.** I clarified: "This 25 is to comp skep … going forward they will all be 100 … adjustments were made for students registering 2 weeks in." So both assignments are for INFO 7375 Computational Skepticism for AI, not this course, and the 25 points is a one-time scale-down for late registrants, not a policy conflict. Claude Code had wrongly flagged it as one. Both headers now name Computational Skepticism, and the design assignment says why it's 25 points.
  - **An unrelated loose end.** In this course's repo, the committed assignment `assignments/assignment-reallocation-engine-recipe-step.md` is deleted in the local working copy, uncommitted. Nothing in this log says why. It was left untouched.
- **What I did:** Pointed out that the assignment still says modes, and that the rename and the rewrite should show up in it. Then set the structure: a 25-point **Recipe Design Assignment** as step one (the old Mode Design, updated), and my pasted 100-point version as step two, the implementation.
- **What Claude or another person contributed:** Claude Code (Opus 5.5) found the rewrite, checked each path it cites against the repo, confirmed the engine repo hasn't changed, and spotted the local deletion. I haven't checked those findings yet. It then wrote both assignments in the-reallocation-engine: `course/assignments/reallocation-engine-recipe-design.md` (25 points, from the old text plus the September 23 audit notes: correct paths, the facts that bite, the 3-3-2 fit, gates vs. votes, ran-vs-simulated labels) and `course/assignments/reallocation-engine-recipe-build.md` (my pasted version, formatted, with the two corrections). It titled the second one **Recipe Build Assignment** so the two steps don't share a name; that title is its proposal, not mine yet. The September 23 draft of the build file was replaced by my version.
- **What I understand now / still do not understand:** Not yet stated by me.
- **Evidence and next step:**
  - Evidence: `course/assignments/reallocation-engine-recipe-design.md` and `course/assignments/reallocation-engine-recipe-build.md` in the-reallocation-engine (local, uncommitted); this entry.
  - Next, three decisions of mine: whether to push both assignments to the-reallocation-engine (each push there needs my go-ahead), whether the second title is right, and replacing the Canvas text. Also: why the recipe-step assignment is deleted locally.

### 2026-09-26 — Turning the figma-claude book into a tutorial portfolio for the advocate roles

- **Date and what I was working on:** Acting on the Figma recipe's answer (network, don't apply) by building portfolio work that fits the two Designer Advocate postings.
- **I tried / expected:** I asked what was in my `figma-claude` book, and said: "I want to rewrite this to be a series of tutorials for Figma for education." When Claude asked what "for education" meant, I said: "For my portfolio ... to build examples for applying to these types of roles," and pasted this folder's `figma/` README.
- **What happened:** The book is a finished 100,000-word handbook on the Figma API, in 14 chapters written for design-systems engineers. Most of it doesn't fit a tutorial series as written. The source texts in its `pantry/` and the design-system, token and MCP chapters can be reused.
- **What I did:** Set the goal: tutorials as portfolio examples for the roles in `figma/professor-bear-figma.md`.
- **What Claude or another person contributed:** Claude Code (Opus 5.5) did three things. It surveyed the book. It wrote `TUTORIALS-PLAN.md` in the figma-claude repo: 11 tutorials, each mapped to a quoted posting line, each in four formats (written guide, video, Community file, workshop version), with a Medhavy study screen proposed as the one running example. And it tagged the current handbook `api-handbook-v1` locally, so nothing is lost. I haven't reviewed the plan yet.
- **What I understand now / still do not understand:** Not yet stated by me.
- **Evidence and next step:**
  - Evidence: `TUTORIALS-PLAN.md` and tag `api-handbook-v1` in `bear-textbooks/books/figma-claude` (local, uncommitted); `figma/professor-bear-figma.md`.
  - Next, my GATE 1 calls: the tutorial list, the running example, rewriting in place or starting a new repo, and which pilot tutorial to build first.
- **Later the same day — a new repo instead:** I said: "Create a new repo Figma for educational AI. This will be used for a book, workshops and a YouTube playlist. Using my Figma for Education account, to basically do everything that the account can do that might be useful, particularly around using AI for education and agentic AI and design, including design for engineers and non-designers." I pasted Figma's September 10 email: my educator status is valid for two years, and students re-verify every year through SheerID.
  - **What Claude did (Claude Code, Opus 5.5):** It checked Figma's help pages as of today. As a higher-ed educator I have the Professional plan with AI: 3,000 AI credits a month (no rollover, no top-ups), the Figma agent, Make, one Site, and the MCP server at 200 calls a day. K-12 and high-school accounts get no AI. It created the private repo `nikbearbrown/figma-for-educational-ai` with `PLAN.md` (18 modules in 5 parts, each turned into a chapter, a workshop and a video), `CAPABILITIES.md` (what the account can do, with sources, and rows marked VERIFY to check in the account), `CLAUDE.md` and `research/sources.md`. The earlier `TUTORIALS-PLAN.md` is replaced by it. I haven't reviewed any of it yet.
  - **Next:** my GATE 1 in `PLAN.md`: the modules, the running example, the pilot module (suggested: Figma MCP + Claude Code), when to make the repo public, and a licence.
- **Later the same day — Figma already knows me:** I said: "The CEO of Figma has reached out in the past, so note that," and pasted the January–February 2026 email thread about SheerID verification problems for NEU students. Claude recorded it in the private repo (`FIGMA-RELATIONSHIP.md`): who was on the thread, what I promised (a sign-up video, and videos for engineers and MBA students, including Weave), and what Figma's Education team offered (to review the video). Contact details and the full thread are kept out of this public log. So Module 01 of the plan is now that sign-up video.
- **Then my first real question:** "OK, I have Figma for Education. I'm not a designer. I design agentic systems, but that includes websites and other things. How is Figma for Education useful for me?" Claude's answer is saved in the private repo as `research/why-figma-if-you-are-not-a-designer.md`. In short: for someone who builds agents, Figma is a structured picture of an interface that both people and agents can read and write, through the MCP server with Claude Code. I haven't checked it yet.
- **Then the direction:** "Is one of the earlier things to teach the Figma MCP server? I want to really focus on integrating Claude or Codex or other agentic tools directly with Figma." Claude reordered `PLAN.md` around that. Part 1 is now connect, read and write: set-up, connecting Claude Code, Codex and an editor-based agent, a frame read into code, and the agent writing to the canvas. The design basics come after, each one framed as the fix for a mistake the agent made. There are 19 modules, and the suggested pilot is modules 02–03.
- **Then the MCP server, and a film about it:** I ran `claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp` (it answered "Added HTTP MCP server figma … to user config") and said: "I think the MCP server function works, double check that. Create a show and tell video … on what the Figma MCP server does and does for you, and how somebody with an education account would connect to it," with the show-tell skill.
  - **What Claude found:** the server is registered, but `claude mcp list` says "Needs authentication". I still have to sign in (`/mcp` → figma → Authenticate) in an interactive `claude` session.
  - **What Claude built (Claude Code, Opus 5.5):** a show-tell film in the new repo, `youtube/show-tell-figma-mcp-server/`. It's about 145 seconds, with every claim checked against Figma's docs: reading a frame into code, writing to the canvas (free in beta), the Education limit of 200 calls a day, and the two connection steps. The film stops at the 4K master; staging and publishing are mine to decide. I haven't watched it yet.
  - **Then I said: "Stage and publish it."** Claude staged it and uploaded it unlisted to my @NikBearBrown channel: https://youtu.be/L8XX50b-8y4. It's in a new playlist, "Figma for Educational AI", with captions attached. Making it public is a manual step in YouTube Studio.
- **Then a research question:** "Research how Figma might be useful for all design, including agentic design and systems design. Engineers rarely use Figma, but with AI becoming more about design than coding ... how could Figma be useful ... comprehensive list." Claude (Opus 5.5) wrote `research/figma-for-engineers-and-agentic-design.md` in the private repo: 60 uses in 8 groups, each tagged with what my Education account allows, from Figma's own docs, plus where Figma is the wrong tool for engineers. It found two engineering features that aren't on Education: Code Connect (Organization and Enterprise only) and Make's GitHub pull-request flow (paid Full seats; unconfirmed for Education). I haven't read it yet.
- **Then two second opinions:** I pasted two AI-written answers to the same question and asked whether they add anything. Claude checked them against their sources. The first adds a little (component descriptions as instructions an agent reads, a drift-check loop, state machines) but overstates a lot: "deterministic", "the canvas becomes the IDE", and per-agent permission tiers that Figma doesn't have. The second adds real, sourced items: Figma's architecture-diagram kit, the FigJam-as-your-agent's-whiteboard post by a Figma backend engineer, the "Figma-last" critique, and Figma's recommended Claude Code setup. That setup is a plugin (`claude plugin install figma@claude-plugins-official`) that bundles Figma's skills with the server, which `claude mcp add` doesn't. Ten uses were added to the research file (70 total). Unverified claims, like a stock drop the week Google's Stitch launched, were kept out.
- **Then the playlist intro:** "Figma for Educational AI: I need a show-tell style video on what the playlist is about. I'm going to use my Figma for Education account and basically do everything I think it can do. Give honest evaluations of where it's strong and weak or in the middle. But really the focus is design: AI and a lot of engineering disciplines which typically don't use Figma (it's usually artists who use Figma) need to shift more to design. And Figma is a design tool. So I'm going to use it as a design tool, not just to design websites, but to design systems, software systems and engineering systems, and of course some websites as well, and really take the Figma for Education account through its paces and see what it can do. Use whatever examples we've come up with in the research as possibilities for future videos and projects." Claude is building it as the playlist's chapter 1 (`youtube/show-tell-figma-for-educational-ai/`, about 153 seconds).
  - **The film's on-paper scorecard, from Figma's docs, before any testing.** Strong: the MCP server works on every Education account. Middle: the Figma agent and Make run on 3,000 credits a month, with no top-ups, and much of it is beta. Weak: Code Connect and branching aren't on Education, agents get 200 MCP calls a day, and K-12 accounts get no AI.
  - **Result:** a 4K master of 153.5 seconds, with every gate passing. It isn't staged or published; that waits for my word.
  - **Then I said: "Looks great,"** and pasted my standard publish runbook ("Claude" playlist at the top, facts signed off, GATE T still applies, upload only from TOPOST, verify at forced 2160p). Claude published it unlisted: https://youtu.be/iikHWZjfqQE. It's at the top of "Claude & Agentic AI" and also of "Figma for Educational AI", as that playlist's intro (Claude's call, done with no re-upload). A few minutes later YouTube was serving both Figma films at 3840×2160 (format 313, checked with `yt-dlp -F`).
- **Then:** "List of things to try? A specific, detailed list of possible experiments or tasks?" Claude (Opus 5.5) wrote `EXPERIMENTS.md` in the private repo: 40 experiments in 7 groups (setup and budgets; design as spec; the agent writing to Figma; systems design in FigJam; agentic design; Make, Sites and Weave; teaching and critiques). Each has one question, a method, a measure, and its credit or call cost, and each ends in a strong/middle/weak verdict logged to `experiments/log.csv`. The suggested start: the plugin setup and the budget probes, then screenshot vs MCP (E04). I haven't picked yet.
- **Then:** "Can the cc-explainer skill be used to show how to connect via Claude Code?" Claude's answer: yes, it fits, since Figma's own setup is a Claude Code procedure. But three things come first. (1) It needs a real session (the skill's REAL-SESSION LAW), and the sign-in step on Figma's page is mine. (2) Figma still shows "Needs authentication", so I haven't signed in yet. (3) The Claude Code interface parts of the video kit exist only in the retired toolkit tree; the current toolkit reports them "NOT RENDERABLE", so they'd have to be ported first.
  - **My answer:** "brutalist.art yes ... commands .... what should I put in the session? Connect and have it draw an agentic diagram for this project ... the idea is the diagram will be updated through the semester," pointing at the master folder in the Computational Skepticism repo. Claude started porting the Claude Code video kit into brutalist.art, and wrote out the session: connect Figma through the plugin, check the account, have Claude Code read the Lectern project and write its agentic diagram as Mermaid in a `DIAGRAM.md` (the version that lives in the repo and gets updated), turn it into a FigJam board, then check the board against the code.
  - **The session ran (my own Claude Code, 2026-09-26).** First Claude Code's own login had been revoked (401), and I ran `/login`. `/mcp` → Authenticate connected Figma, and `whoami` showed my Education team as "Student tier, Full seat", plus a second Starter-tier team with only a View seat. Claude Code wrote `DIAGRAM.md` (Mermaid: 7 pipeline steps, 3 ATS groups, 3 classes, 5 human gates) and drew a FigJam board in one call. Then, asked to compare the board with the code, it listed 3 things on the board not in the code and 14 in the code not on the board (error paths, the allowed-hosts list, `--from-raw`, the fact that sync never commits, and more). I sent the comparison prompt twice by accident, and it said so. I haven't reviewed the diagram's accuracy yet. `DIAGRAM.md` and `SESSION.md` sit uncommitted in the Computational Skepticism folder. `SESSION.md` there has my email and the OAuth link, so Claude kept a redacted copy for the film instead.
  - **Then Cowork.** I asked whether Cowork can talk to Figma, then tried to connect it myself. I went to **Connectors** first, where the Figma row only says "Provided by the Figma plugin · Connects in sessions" and can't be connected. The right place is **Plugins → Figma → Connectors → "Not added"**. I sent seven screenshots and another AI's answer, and asked for two films: "make the cc-explainer film from the session and an ai explainer, Liam persona, on connecting Cowork to Figma, including my mistake of going to connectors rather than plugins." When Claude checked (2026-09-26), my account still had no Figma connector, and this session's Figma server still needed sign-in. So the Cowork connection isn't finished yet.
  - **Then, in my words:** "vercel I can do that with, not Figma." And: "This is my Bear Brown Max account ... I control ... I have an NEU account and that should be noted in the film, as many don't have two, only the uni account." The terminal had run on my NEU Claude Enterprise account; the desktop app and Cowork are on my personal Max account. The real cause: the bare `figma` server from my first `claude mcp add` was still in my user config, at the same address as the plugin's server. I ran `claude mcp remove figma -s user` and restarted the app. The session's `/mcp` panel then showed "figma · Provided by the Figma plugin · Connect", and after Connect, a ✓. Claude confirmed it from the desktop session: `whoami` worked, and it read the Lectern board back. The board has every section, gate and connector, but the drawing tool shortened all the labels.
  - **I said:** "yes this is very confusing and def worth its own film", then asked "what exactly is the difference between a plugin and a connector?" Claude's answer: a connector is the link to a service (an MCP server plus your sign-in); a plugin is a package that can bundle skills, agents, hooks and connectors. A plugin's connector "connects in sessions" through `/mcp`, and a leftover `claude mcp add` server can shadow it. That film is now being built (Liam, ai-explainer, stopping at the 4K master).
  - **Then I approved the board capture through my Chrome.** The Chrome extension wasn't connected, so Claude used Figma's own export instead: `get_screenshot` on the board returned a 6824 × 1553 render, with every section, gate and connector, and one truncated label ("GATE E - write FRICTION…"). The cc-explainer build started from my real session and that render. The film says it's Figma's export, not a screen recording.
- **Then, on Frictional:** I asked "does Figma keep track of changes?", pasted my *Measuring the Struggle* preprint, and said: "the idea is, if somebody really works on something, they're making a lot of changes ... not only turns in the final artifact, but turns in the whole version history ... every change ... and dates when it gets made ... and the student would put in reasons why they made them." Claude checked Figma's docs:
  - Checkpoints are saved every 30 minutes.
  - Named versions take a title and a description (the "why").
  - The REST API returns every version's date, label, description and user.
  - Education teams keep the whole history; Drafts and Starter keep only 30 days.
  - The limits: the MCP server has no version-history tool, and edits an agent makes through MCP are attributed to the student, so session transcripts have to travel with the log.

  Claude wrote `research/frictional-figma-version-history.md` and a small script (`examples/frictional-version-log/figma_version_log.py`) that turns a file's history into a `VERSIONS.md` table, in the private Figma repo. I haven't tried it yet.
- **Then:** "the frictional logs, the best you can. For everything that I do, we also need a video on frictional and Figma. Why is this important? Why not just the final artifact ... but the entire version history of how it was made, the reasonings, and if possible, dates ... the student can't make up the dates ... it's like GitHub. GitHub is putting in a date. You can't change the GitHub date. Hopefully with Figma, I can't tell it to make a date."
  - **Claude corrected two things:**
    - Git **commit** dates *can* be set by the author (`git commit --date`, `GIT_AUTHOR_DATE`); the date GitHub records on its own servers is the **push** time.
    - The MCP server doesn't write dates. Figma's servers stamp each version's `created_at`. Saving a version takes a title and a description but no date, and the REST API can only read versions, so there's no documented way to backdate one.
  - **The principle:** trust the server's clock, not the author's. A show-tell film for the Figma playlist is building with that correction built in.
  - **Three films finished the same evening,** each a 4K master with every gate passing. None is staged or published, and I haven't watched them yet.
    - "Plugin or Connector? Connecting Figma to Claude Cowork" (3:38).
    - "Claude Code + Figma: Connect It, Then Draw the Project" (7:41, built from my real session).
    - "Hand In the History, Not Just the Design" (2:34). It says out loud that git commit dates can be set by the author and that the date to trust is the server's.
- **Then: "push to the repo, Figma for Educational AI"**, and a deep-explainer film "in the Liam persona explaining what I'm doing":
  - What I'm doing: "I'm looking for consulting roles, either for me or my company, Bear Brown.co", while also "doing the assignments in three of the classes so that people can see my working on a real problem, which means I encounter real issues".
  - The market gap: "most companies do not understand the politics of universities ... the needs of universities, particularly with AI. But they have products they want to sell." I want to be "that maven, that connector". I teach five AI courses; I've run and I'm still on advisory committees for the university's AI direction; I know and use the tools.
  - My gap: "I don't have concrete examples of tutorials, workshops and educational materials made."

  Claude pushed the Figma repo. The films' sources, paperwork, evidence screenshots and captions went up (153 files, 5.3 MB); render output is git-ignored. The deep explainer is building, using my words, my attested CV facts, the gap analysis and the Figma board scan. My committee and five-courses claims are attributed to me, because the CV facts file doesn't list them.
- **Then I signed off the Cowork film ("Looks great")** and pasted my publish runbook. Claude published it unlisted: https://youtu.be/JlDHbERabOg. It's at the top of "Claude & Agentic AI", and third in "Figma for Educational AI" (after the intro and the MCP film; Claude moved it there after the upload put it first). Staging refused once because the sheet had no chapter number; chapter 3 was set.
- **Then I signed off the Claude Code film ("Looks great")** with the same runbook. It's published unlisted at https://youtu.be/FrI54hgrGp4, at the top of "Claude & Agentic AI" and fourth in "Figma for Educational AI" (intro → MCP → Cowork → Claude Code).
- **The context film is finished:** "Job-Hunting in Public, Without Needing a Job" (deep explainer, 6:24, 4K, every gate passing, not published). The builder changed my suggested title from first person, because Liam speaks about me. My own claims are spoken as mine, and the film says out loud that the committee work isn't in my CV facts file. Its gap check found 0 hits for Figma, design systems, certification or conference talks in that file. I haven't watched it yet.
- **2026-09-27: I signed off both remaining films ("Looks great")** and pasted my publish runbook for each. Both are published unlisted at the top of "Claude & Agentic AI":
  - "Hand In the History, Not Just the Design": https://youtu.be/saJieSuje84
  - "Job-Hunting in Public, Without Needing a Job": https://youtu.be/U6UdCOMBuUI

  The "Figma for Educational AI" playlist now runs: context film → intro → MCP server → Cowork → Claude Code → Hand In the History.
- **Then: "map out the next 15 films ... what's next?"** Claude wrote `FILMS-NEXT.md` in the Figma repo: 15 films, each tied to an experiment and a line in the Designer Advocate postings. The arc is setup and costs; screenshot vs frame; auto layout, variables and component descriptions as fixes for agent mistakes; the agent drawing while I merge; the Lectern diagram week over week; whiteboard to code; an agent's permissions; "I don't know" interface states; Make; Weave; and a real version log. Films 3–15 each need a real session I run. Suggested start: the sign-up film promised to Figma's Education team, then the cost film, then screenshot vs frame. I haven't picked yet.
- **Then: "overnight these 15 ... I'll look at them tomorrow."**
  - **What can't be done without me:** the terminal Claude Code isn't signed in to Figma, so none of these can be my typed sessions. Five are parked until I do them myself:
    - 5: my Codex account stays out of automated loops;
    - 9: needs a week of changes and my marks on the board;
    - 10: needs my own hand-drawn whiteboard;
    - 13: Figma Make runs in the browser only;
    - 15: needs a Figma token only I can create.
  - **What's being built overnight:** the other ten, as **experiment reports**. Agents run real tests on my Figma Education account (through the desktop session's Figma connection) and on headless Claude Code, then build each film from the real artifacts. Each film says an agent ran it and that I haven't reviewed it.
  - **Status:** `OVERNIGHT-REPORT.md` in the Figma repo. Nothing gets staged or published.
- **2026-09-27: what actually happened overnight.**
  - At about 3 am, six builders stopped on my account's **weekly usage limit**. When I said "Try again" at 12:56 pm, they resumed.
  - By mid-afternoon all ten masters were done, each 4K with every gate passing, none published.
  - The verdicts:
    - **strong:** 3 (the agent built far more faithfully from design data than from a screenshot: 26 vs 4 of 27 values), 7 (a component description steered the agent), 12 (the tutor's uncertainty states), 2 (the Education MCP budget is enough for classwork);
    - **middle:** 1, 6 and 8;
    - **weak:** 4 (a clean file made no real difference), 11 (the allow-list built from the permissions table enforced only 6 of 18 needs), 14 (Weave isn't reachable through MCP without a paid Weave account).
  - **Costs:** 61 Figma MCP calls; the CLI reported $3.27 at list price for the headless builds; no Figma AI credits.
  - **Waiting on me:** reviews, the student tests, the merge, the credit-meter reading, and a repeated "Merhaba" greeting on four films.
- **2026-09-27: my review of the ten overnight films, and what a real review should do.** In my words: "I reviewed them from an educational perspective. They look great." What I'd do in a real-world situation:
  - **Log my notes in Figma** if it can do this. "I agree with the point of all the films."
  - **Keep the note with the design.** I'm unlikely to be the only person deciding on a design, so the notes go "not just as random notes, but to Figma," "so it doesn't get lost. Doesn't get disassociated with the thing that it's a note of."
  - **Write a tool** "with whatever communication system the company uses" (email, Discord, whatever) "to notify whoever needs to look at it. If it's somebody other than me, that this change has been made and the note is in the file itself."
  - **Change the films:** "add that to all the films where you say I haven't looked at them yet. Now I've looked at them."
  - **What came of it (same day).**
    - **The notes:** my note is now in Figma, on the layer each film is about: six Review annotations, and a sticky on the FigJam board, which refused annotations. Films 1, 2 and 14 have no design file, so their note is in the experiment record.
    - **Did the note reach the next agent?** On frames, yes: the MCP server hands the note to it with "Do not ignore these annotation attributes." On component sets (films 7 and 12), no. On the FigJam board, only the sticky's first line came back as text.
    - **What the agent can't do:** it can't name a version, set "Ready for dev", or comment through the server.
    - **The tool:** `review_notify.py` sends a pointer, not the note, on Discord, Slack, email or a webhook, and it skips me as the reviewer. Nothing was sent.
    - **The films:** all ten are re-cut in 4K, with every gate passing and none published. Each now says I reviewed it and has a review beat. Films 8, 11 and 12 open with Ciao, Konnichiwa and Shalom instead of four Merhabas.
- **2026-09-27: sign-off on the ten re-cut films.** In my words: "Those look good. Those films look good. Publish the unpublished films on the Nick Bear Brown YouTube at 4K." So all ten go up unlisted on @NikBearBrown, in the Claude playlist and the Figma playlist, the same way as the first six.
  - **Done the same afternoon:** all ten are up, unlisted, native 4K, captions attached, in both playlists: films 1 VbICGMmMOak, 2 SKEollgJwTc, 3 vaaGNW3jepY, 4 PTbTHSFbo2U, 6 yq553zEjdBo, 7 HMRFC9AtWEM, 8 DPBrdel-5Bw, 11 pq4ZeONLJlc, 12 pv1ZpweUKcw, 14 9DbslHjLFDs (youtu.be/…). The YouTube API's daily quota ran out after the tenth upload, so the Figma playlist reorder and a caption check on film 2 wait for the reset.
- **2026-09-27, later:** "What are the next ten set of films?" The answer goes in the Figma repo as FILMS-NEXT-2.md.
- **2026-09-27, evening: build the next ten overnight.** In my words: "build those overnight, check the new show tell skill to make sure you have it up to date. Use the show tell skill to build those uh, through 25 overnight." Films 16 to 25. Eight of them need me or students, so the overnight builds do the agent's half honestly and say what's pending.
  - **11:40 pm:** four of the five builders died on my account's **session limit** (429, "resets 11:10pm"). Films 16 and 17 finished before that. I said "Try again"; the four are resumed from where they stopped.
  - **2026-09-28, about 1 am: all ten masters done,** none published. Verdicts: 16 strong (a note on a variant reaches the agent; on a set or a board it doesn't); 21 strong with a hole (tests caught 16 of 16 behaviour breaks and 0 of 2 wrong-reason probes); 24 middle (the review skill agreed on 4 of 6 findings across three runs); 17, 18, 19, 20, 22, 23, 25 pending my half (the token, Codex, a hand drawing, a week, students, the Make run, a class), each strong or settled on the agent's half. 24 Figma calls, about $5.50 of headless builds. Claude Code needs `claude update` before it will run Opus 5.5.

### 2026-09-26 — The assignment went out, and its first worked recipe

- **Date and what I was working on:** Closing the loop from the previous entry: getting the rewritten Reallocation Engine assignment onto GitHub, and checking it against a real case.
- **I tried / expected:** I said: "commit it to https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai." Claude found that this course repo already had a *different*, already-pushed Reallocation Engine assignment sitting there — `assignment-reallocation-engine-recipe-step.md`, deleted locally but never committed — and asked whether to replace it. I said replace it, then: "should be called 'The Reallocation Engine — Recipe Design Assignment.'" I then said: "this is the next assignment #3 build the recipe," pasted the assignment text back at Claude, second-guessed which class it belonged to ("whoops, sorry, you're right, it's this assignment, not the—"), and then confirmed: "No, you're right. For this class, that was the right assignment."
- **What happened:** The assignment is now live at `assignments/assignment-reallocation-engine-recipe-design.md` in the course repo, replacing the deleted one. Rewritten into this course's own Predict/Build It/Use It/Ship It/Verify spine and its standard 60/10/10/20 rubric, since the September 23 version used a different 20/20/15/10/15/20 split that would have been an unlogged rule change. Then, checking the assignment against a real case: the "find a dream job" recipe in this folder's own `README.md` (steps 0–2, already run for Figma) had never been written in the assignment's own required format — no lifecycle frontmatter, no phase gates, no output contract.
- **What I did:** Approved the replacement, named the assignment, and confirmed it was the right one for this class.
- **What Claude or another person contributed:** Claude Code pushed the assignment to `info-7375-prompt-engineering-for-generative-ai` (commit `009c53a`). Then, in `the-reallocation-engine-fresh`, it wrote `recipes/cases/2026fa/nikbearbrown-advocate-education-search.md` and its `.card.md`, formalizing this folder's existing Figma work into the assignment's required shape: an executive summary, phase gates (board freshness, relevance, flexible-terms-stated, CV-evidence-exists), an output contract, stop conditions, and a next-action table (Apply / Network / Skip / Build). It named honestly, in the recipe's own "Facts that will bite" section, that the scan and pick scripts still live in this course folder rather than under `scripts/contrib/` in the engine repo, and that steps 3–8 are open `[TODO]`s. It re-ran `figma/find_roles.py` and `figma/pick_postings.py` against the real saved board and confirmed both reproduce the checked-in output exactly, ran `node scripts/conformance.mjs` on both new files (passes), and logged the run in the engine repo's `logs/RUN_LOG.md`. Not pushed to the-reallocation-engine — that repo isn't covered by this folder's standing push approval and needs my separate go-ahead.
- **What I understand now / still do not understand:** Not yet stated by me.
- **Evidence and next step:**
  - Evidence: [commit `009c53a`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/009c53af9c3716aeb7d5ff24042d40e91e7da7bc); `the-reallocation-engine-fresh/recipes/cases/2026fa/nikbearbrown-advocate-education-search.md` and `.card.md` (local, uncommitted); `the-reallocation-engine-fresh/logs/RUN_LOG.md`, 2026-09-26 entry.
  - Next, my calls: whether to push the recipe to the-reallocation-engine; whether to port `find_roles.py`/`pick_postings.py` into `scripts/contrib/` there next, or keep building the recipe (the prototype, domain justification, worked run) first; and whether the 60/10/10/20 rubric remap is the one I want kept.

---

## Evidence

Where to check each claim in this log. Commits in this repository are listed in the push table below; their IDs are in `git log`, and the links here are added one push later, because a commit can't link to itself.

| What | Where |
|---|---|
| Demo, CV facts, first log | [`bfdb402`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/bfdb402) — `greenhouse-watch-demo/`, `facts/professor-bear-cv.json`, `FRICTIONAL.md` |
| Figma jobs archive, folder rules | [`1192ab5`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/1192ab5) — `figma/figma-jobs-2026-09-23.json`, `figma/README.md`, `CLAUDE.md` |
| Fix logged, evidence table, standing push approval | [`9512602`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/9512602) — `FRICTIONAL.md`, `CLAUDE.md`, `greenhouse-watch-demo/README.md` |
| Whole session logged, CV attested | [`e95cf63`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/e95cf63) — `FRICTIONAL.md`, `facts/professor-bear-cv.json`, `CLAUDE.md` |
| All JSON indented for reading | [`ad0d76e`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/ad0d76e) — `figma/figma-jobs-2026-09-23.json`, both demo snapshots, `CLAUDE.md` |
| Recipe started, scan added | [`0130421`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/0130421) — `figma/README.md`, `figma/find_roles.py`, `figma/roles-2026-09-23.md` |
| Relevant postings kept | [`986f39d`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/commit/986f39d) — `figma/professor-bear-figma.json`, `.md`, `figma/pick_postings.py` |
| The dream-job recipe | `README.md`: eight steps, gap table, Assignment 2 mapping |
| The Figma advocate / flexible-work recipe | `figma/README.md` (recipe), `figma/find_roles.py` (the scan), `figma/roles-2026-09-23.md` (first run), `figma/professor-bear-figma.json` + `.md` (the relevant postings) |
| CV facts checked by me | `facts/professor-bear-cv.json`: `attested: true`, 2026-09-23, "accurate, no errors; more to add later" |
| The Fall assignment rewrite | `course/assignments/reallocation-engine-recipe-build.md` in the-reallocation-engine (local, not yet committed) |
| The scoring-report fix and its test | [`015843d`](https://github.com/nikbearbrown/the-reallocation-engine/commit/015843d5047dbadff05068495e4c5db5cd9945f4) in the-reallocation-engine — `.claude/skills/greenhouse-watch/scripts/greenhouse_watch.py`, `tests/test_greenhouse_watch.py`, `logs/RUN_LOG.md` |
| The live board fetches | `greenhouse-watch-demo/snapshots/figma-2026-09-23.json` (19:54 UTC) and `figma/figma-jobs-2026-09-23.json` (20:01 UTC), both Figma's API response, indented for reading, with the data unchanged |
| The runs and their reasons | `greenhouse-watch-demo/runs/` and `greenhouse-watch-demo/whole-board/`: one JSON record and one Markdown report per run |

### 2026-09-26 — This folder stopped being a place to edit shared code

- **Date and what I was working on:** Keeping one live-coded project consistent across three classes.

- **I tried / expected:** I expected the three `nik-bear-brown` folders to be roughly the same.

- **What happened:** They had drifted. Branding had the collector, the watch list, the filter, and the ATS notes; Prompt Engineering had the CV facts and the earlier iterations but not the collector; Computational Skepticism had neither. I named **Computational Skepticism the canonical master**, which meant the master was the folder furthest behind at the moment it was declared.

- **What I did:** The shared spine now lives in the master and is copied here by its `lectern/sync.sh`. This folder gained a `SYNC.md` saying it is **not** the master, and a Rule 0 in `CLAUDE.md` saying the same. The files that are copies are named there. Everything specific to this class — this log, the README, the assignment folders, the dated run outputs — is never copied in either direction, because a log overwritten by another class's log is a destroyed record.

- **What Claude or another person contributed:** Claude Code (Opus 5) inventoried and diffed the three folders, built the sync script, and wrote the notes. I decided which class is master.

- **What I understand now / still do not understand:** Drift is invisible until something diffs it. Still open: the recovery path — a shared file edited in the wrong repo — has not been exercised.

- **Evidence and next step:** `SYNC.md` here, and `./lectern/sync.sh --check` in the master reporting all three in sync.

---

### 2026-09-28 — A show-tell film of Chapter 2, "Prompt contracts and evaluation"

- **Date and what I was working on:** Short course films, one per chapter idea, in the show-tell style already used for the Computational Skepticism films.

- **I tried / expected:** I dictated, as transcribed: "This team is Show tell Liam persona on chapter two of computational skepticism. , 'Prompt Contracts and Evaluation,' argues that an AI response can satisfy every programmed output requirement and still be factually wrong," pasted two AI summaries of the chapter, and the dictation trailed off into noise ("But you watch them yesterday, Rousseau's having a good year off the edge."). I expected a film on that chapter.

- **What happened:** Claude Code searched for the chapter and found it in this repo, not in Computational Skepticism, whose Chapter 2 is about probability. I then said: "My mistake. That's prompt engineering and generative AI. Not computational skepticism. My mistake."

- **What I did:** Confirmed the course. The film is built as an INFO 7375 Prompt Engineering course film, with the course credit spoken and on screen, from the chapter itself (the two pasted summaries are only a guide to emphasis). Brief: `youtube/SHOW-TELL-PROMPT-CONTRACTS.md`; reel `youtube/show-tell-a-valid-shape-can-still-be-wrong/`; working title "A Valid Shape Can Still Be Wrong," the chapter's own subtitle.

- **What Claude or another person contributed:** Claude Code wrote the brief and runs the builder; the chapter's fixture, validator and one-third rate are checked against `research/worked-examples.json`. Nothing staged or published.

- **What I understand now / still do not understand:** A dictated course name is a claim like any other; the search caught it before the film did. Still open: whether the older `claude-liam-show-tell-*` films here, which never speak the course credit, should be re-cut to match.

- **Evidence and next step:** the brief; once built, the reel folder's BUILD-LOG and FACTCHECK. Next: watch the master, then decide on publishing.

- **Later the same day:** the builder reached Claude Code's weekly usage limit at 13:33, after the second voicing of 26 beats and before any render; the reel folder holds the audio, the scenes, the sheet scripts and most of the paperwork, but no master. I asked for a "prompt to hand to codex to finish what needs to be done." It is `youtube/CODEX-HANDOFF-2026-09-28.md`: the exact state of this reel, the remaining steps in order, and the two Computational Skepticism films queued behind it, with the same no-publish, no-commit rules.

---

### 2026-10-07 — A shared file arrives that the sync had missed

- **Date and what I was working on:** The job-search example, kept in sync from the Computational Skepticism master.
- **I tried / expected:** Professor Bear asked for all three classes to be brought into sync and pushed: "All three classes should be in sync." I expected `lectern/` here to already match the master.
- **What happened:** Everything on the sync script's shared list matched. But `lectern/demand_report.py`, the script that ranks companies by demand rather than postings by fit (added to the master and Branding on 2026-09-26), had never been copied here: the master's `sync.sh` shared list had not been updated when the file was created, so the check could not see it.
- **What I did:** Nothing was edited here by hand. The master's list now includes the file, and the master's `sync.sh` was run for real for the first time, which placed `lectern/demand_report.py` in this folder. `SYNC.md` here is unchanged: this folder is still a copy.
- **What Claude or another person contributed:** Claude Code found the gap by comparing folders file by file rather than trusting the list, fixed the list in the master, ran the sync, validated this repo, and pushed under the standing approval and Professor Bear's instruction.
- **What I understand now / still do not understand:** A sync check reports on its list, not on the folder. Still open: nothing in this class; the fix lives in the master.
- **Evidence and next step:** `lectern/demand_report.py` now present and byte-identical to the master's; the master's `./lectern/sync.sh --check` reporting all three in sync.

### 2026-10-07 — The pitch-film assignment, and laying out my own project brief

- **Date and what I was working on.** 2026-10-07. Writing the 50-point Final Project Pitch Film assignment for students, then using its seven questions to lay out my own final project.
- **I tried / expected.** I asked for a short Brutalist film assignment, five days, worth 50 points with 10 of them the quality score, in which each student describes the portfolio piece they expect to build. I expected it to sit before the Reallocation Engine Mode Build. Then I asked for my own project laid out the same way, starting with an executive summary.
- **What happened.** Claude Code drafted the assignment from the Week 1 video brief (30 pitch, 5 Frictional, 5 GitHub, 10 Relative Quartile). I added two questions to it: a unique value proposition ("what makes this project special", asked of the project as something that might become real work) and, as a seventh, why the student picked it (new learning, existing skill on show, or a mix). The pitch points were rebalanced twice and now run 7, 5, 5, 4, 5 and 4. For my own project, I gave the executive summary, the test for any tool (honest use on real education problems, pluses and issues, shown on film, the viewer judges), the first audiences (students, and teachers evaluating real learning rather than the artifact), and the rule that every evaluation is published, passed or dropped, so others can add perspective. Along the way two things went wrong: my replies first linked files with relative paths that opened in the wrong place after the shell had moved into a subfolder, and I earlier logged my own messages as loose bullets under the push table instead of as entries (this entry replaces that habit; the bullets stay as the verbatim trace).
- **What Claude or another person contributed.** Claude Code wrote the assignment, its Canvas version, the instructor-decisions item 8 and the draft brief. The decisions were mine: the film, the 50 points, the five days, both added questions, the test, the audience, publishing dropped tools, and that my belief and experience decide what gets evaluated. I have not yet reviewed answers 2 to 7 in the draft brief. Two places in it are bracketed for me: the real alternatives I have compared, and which Google, Microsoft and OpenAI tools I already use.
- **What I understand now / still do not understand.** The seven questions force a student to separate what exists from what will exist, and my own brief shows it: Figma for Educational AI exists and the Google, Microsoft and OpenAI trials do not. Open: which of the pasted Mode Build brief and the committed recipe-design brief stands, whether the two video assignments make the syllabus's optional-video language obsolete, and whether the first Google trial should be NotebookLM.
- **Later the same day.** I pasted the shared-code rule for the three classes and said to look at what the other session had done, which was a status report and a handoff for the job-search project, and to make the films as a diary: on a date, this is the state of the project, and today's film is today's entry. Claude Code read the handoff and the status report, checked the headline numbers against the run outputs (3,446 postings, 97 kept, 18 sources) and the Figma repo (36 film folders), and wrote the diary rules and entry 1's script in `final-project-film/DIARY-ENTRY-2026-10-07.md`. It changed the brief's first milestone from a NotebookLM trial to this diary entry. I said "No PokeLM is" and Claude misread it as dropping NotebookLM; I corrected it: it is NotebookLM, Google's main educational tool as I understand it, and it stays in the project. No film is built yet.
- **Then, the same day: "ChatGPT has a Socratic mode. Research that."** My words: "I believe, and you need to do research on this, that ChatGPT has a Socratic mode. So we are going to, in particular, talk about ChatGPT in a Socratic mode, how to use that. Because I'm pretty sure that's a basic feature of the OpenAI toolset now." Claude Code searched. The feature is called Study mode (launched 2025-07-29); NotebookLM's counterpart is the Learning Guide (2025-09-23, read on Google's own blog). OpenAI's pages refused the fetch tool, so the how-to and the reports of an April 2026 disappearance are unverified; the film's trial is how they get settled. Written up in `final-project-film/RESEARCH-socratic-modes-2026-10-07.md`.
- **Then: "I think this is more than one film. So let's plan out films. Using the lecture skill, Liam persona, the first film is … Professor Bear Does His Assignments … film number one is, well, what am I doing? What is the whole point? … The film actually doing assignment three, I think it is. We'll probably be two or three films down the road … the overall idea and what has been done as of today's date."** Claude Code read the lecture skill and the three classes' logs and wrote `final-project-film/SERIES-PLAN-professor-bear-does-his-assignments.md`: a seven-film proposal and a full layout of film 1 in four acts, in third person, nothing built. I also said the working-indicator icon that showed a quill was "just a random one"; it is the app's own spinner and Claude Code did not make it. Open: which assignment is "assignment three", and whether film 1 is also the pitch film.
- **Then: "throughout the film series, emphasize … irreducibly human, conducting AI, computational skepticism … AI is doing the AI work, meaning it's going collecting jobs for you, it's doing a rough draft … But it's your human judgment and your guidance which is going to get a good product as opposed to AI slop … Having a perspective of doubt, and not believing things just because they look polished and they look good."** The series plan now has a through-line section: three ideas defined in plain words, a three-line ledger in every film (the AI did, the human decided, doubt caught, each from a real log entry), and rules against blurring who did what or claiming AI cannot do something in principle. Film 1's key terms, acts and Your Turn were changed to carry it, including the plain statement that Claude Code typed my answers in the specification session and I have not yet reviewed them.
- **Then: the series is uneven, and that is part of the lesson.** My words: "a real cleanup and I'll probably take the other older films and make them unlisted because some students have already commented on the film so I don't want to delete them or make them private … the part of the lesson is I get better at making films by making films … even though I'm using the exact same AI … so it's not just the tool, it's how you interact with the tool … the series is not too coherent now and part of the lesson there is that it's not just Claude doing this, it's Claude plus the person doing this, the whole Conducting AI idea … later on I'll clean up the YouTube and make a lot of films unlisted." The series plan now has a "Getting better by making films" section, an Act V in film 1, and the rule that the cleanup is mine and later: unlisted, never deleted or private. Nothing on YouTube was changed.
- **Then: the playlist.** My words: "this will be a new YouTube playlist. I'll probably just make the other ones unlisted. Professor Bear does his … assignments … we'll go with Professor Bear does his assignments." The plan names it and notes it is not created and that the publisher matches playlist titles exactly. Nothing on YouTube was created or changed.
- **Then: "I approve film one, I approve building film one."** My words: "I like film one being a general introduction without a particular date. And then film two is going to essentially be a log, a diary. What is done on whatever today is … Use the Liam persona, use the lecture skill … Build film one now." Film 1 is built as the general introduction (`youtube/claude-liam-lecture-professor-bear-does-his-assignments/`); film 2 will be the first diary entry. While capturing the tools' public pages for it, Claude Code found that NotebookLM is now called Gemini Notebook (Google's blog, 2026-07-16), so the research note and the brief were corrected. Claude's and ChatGPT's front pages blocked the capture, so the film does not show them.
- **2026-10-08: "The next film is not going to be a journal log. It's going to be a detailed overview of what is being built."** After the design document was pushed to all three folders I pasted its full text again without saying what to do with it. Claude Code read that as the source for film 2 and wrote a layout, not a build: `final-project-film/FILM-2-LAYOUT-what-is-being-built.md` (six acts, the not-built list as the longest, a through-line table, four open questions). The series plan now has film 2 as the overview and the diary as film 2b. Film 1's final 4K render stalled once overnight and was restarted; the type check had failed twice on the portrait in the "directs the work" scene (the photo's shirt area read as low-contrast text), so the portrait was cropped to face and neck and softened slightly. Film 1 is not yet cut or published.
- **Evidence and next step.** `assignments/assignment-final-project-pitch-film.md` and its `-canvas.md` twin, item 8 in `docs/instructor-decisions.md`, and `fall-2026/nik-bear-brown/final-project-film/PROJECT-BRIEF.md` `DIARY-ENTRY-2026-10-07.md`, `SERIES-PLAN-professor-bear-does-his-assignments.md` and `RESEARCH-socratic-modes-2026-10-07.md`. The assignment files are not yet pushed; they sit outside this folder, and the repo already holds other uncommitted edits. Next: I review the brief and fill the two brackets, then we write the film's beat sheet.

### 2026-10-07 — Gru's software design document for the whole project, in silent mode

- **Date and what I was working on:** 2026-10-07. A software design document for everything being built under the job-search project, to be the source for the next film. The next film is not a journal log; it is a detailed overview of what is being built.
- **I tried / expected:** I pasted the Gru prompt and said: "Run Gru in silent mode to generate a detailed software development document. Talk about Gru in a log after that … And add that SDD to the three folders on the GitHub." I expected a design document in the form Gru's `/g1` produces.
- **What happened:** Claude Code ran the Gru prompt in silent mode: no intake questions, no pushback, no phase gates. It read the collector, its configuration, the audit scripts, the sync script, the earlier Lectern design document, the status report, the engine's skill and the three logs, then compiled sixteen sections and a seventeenth that Gru's format does not have: where the earlier design and the built code disagree. That comparison found two real gaps. The earlier design describes a seen-id state file and a "what is new since last time" report, plus `--dry-run` and `--all` flags; `collect.py` has none of them. And the collector's docstring says it writes a quality report, but `main()` writes only the `all-jobs` and `jobs-of-interest` files; the dated quality report on file was written outside the collector. Need N2, "see only what changed since the last run", is therefore unserved by the built tool.
- **What I did:** The document is `SDD-job-search-project.md` in the Computational Skepticism folder, the master. I added it to `lectern/sync.sh`'s shared list and ran the sync, so the Branding and Prompt Engineering folders hold an identical copy; `sync.sh --check` reports all three in sync. Each repository is committed by hand with this entry. The Computational Skepticism push is on my word, given in the message above.
- **What Claude or another person contributed:** I supplied the Gru prompt and the instruction to run it silent, to log it, and to add it to the three folders. Claude Code ran the prompt, read the files, wrote the document, changed the sync list and wrote this entry. This is Claude Code's run of Gru, not my answers to Gru's questions, and I have not reviewed the document. Unfilled fields are marked `TODO`, not guessed.
- **What I understand now / still do not understand:** Not yet stated by me. What the compile found: the built tool and its earlier design differ in the two ways above; there are fourteen open questions in section 16, all mine. Claude Code did not run the collector, the audits or the sync for any counts in the document; they are quoted from the 2026-09-26 run files and the status report.
- **Evidence and next step:** `SDD-job-search-project.md` in each folder; `lectern/sync.sh` in the master. Next: I read it, decide the open questions that matter first (a schedule, the five unreadable companies, and whether to build the state and diff or strike it from the earlier design), and the next film is built from this document.

## GitHub pushes

One line per push to GitHub: the date and the commit note. The commit ID for each push is in `git log`; a commit can't contain its own ID.

| Date | GitHub note |
|---|---|
| 2026-09-23 | feat(fall-2026): add greenhouse-watch Figma demo, Professor Bear CV facts, and Frictional log |
| 2026-09-23 | feat(fall-2026): add dated Figma jobs archive and folder CLAUDE.md for Frictional logging |
| 2026-09-23 | docs(fall-2026): log the greenhouse-watch fix with commit evidence and standing push approval |
| 2026-09-23 | docs(fall-2026): log the whole session in Frictional and attest the CV facts |
| 2026-09-23 | style(fall-2026): indent every JSON file so students can read and check it |
| 2026-09-23 | feat(fall-2026): start the Figma advocate and flexible-work recipe with a checkable scan |
| 2026-09-23 | feat(fall-2026): keep the relevant Figma postings in professor-bear-figma.json and .md |
| 2026-09-23 | docs(fall-2026): add the dream-job recipe in steps with a first gap analysis for Assignment 2 |
| 2026-09-26 | docs(fall-2026): log that the rewritten Reallocation Engine assignment was never pushed |
| 2026-09-26 | docs(fall-2026): log the plan to rewrite figma-claude as a Figma tutorial portfolio |
| 2026-09-26 | docs(fall-2026): log the new figma-for-educational-ai repo for the book, workshops, and playlist |
| 2026-09-26 | docs(fall-2026): log the Figma relationship note and my first question about Figma for agentic work |
| 2026-09-26 | docs(fall-2026): point the log at the saved answer on Figma for agentic work |
| 2026-09-26 | docs(fall-2026): log the decision to teach the Figma MCP server and agent integration first |
| 2026-09-26 | docs(fall-2026): log the Figma MCP setup check and the show-tell film request |
| 2026-09-26 | docs(fall-2026): log the Figma MCP film going up unlisted on YouTube |
| 2026-09-26 | docs(fall-2026): log the research on Figma for engineering, systems and agentic design |
| 2026-09-26 | docs(fall-2026): log the check of two second opinions on Figma for engineers |
| 2026-09-26 | docs(fall-2026): log the request for the Figma for Educational AI playlist intro film |
| 2026-09-26 | docs(fall-2026): log the finished playlist intro master |
| 2026-09-26 | docs(fall-2026): log the pushed recipe design assignment and the first worked recipe |
| 2026-09-26 | docs(fall-2026): log the playlist intro going up unlisted on YouTube |
| 2026-09-26 | docs(fall-2026): log that both Figma films serve 2160p |
| 2026-09-26 | docs(fall-2026): log the Figma experiments list |
| 2026-09-26 | docs(fall-2026): note that shared code is canonical in the Computational Skepticism folder |
| 2026-09-26 | docs(fall-2026): log the two-step Reallocation Engine recipe assignments |
| 2026-09-26 | docs(fall-2026): note the Recipe Design assignment is Computational Skepticism's 25-point late-registration step |
| 2026-09-26 | docs(fall-2026): log the question about a cc-explainer film on connecting Figma |
| 2026-09-26 | docs(fall-2026): log the plan for the Figma connection session and its agentic diagram |
| 2026-09-26 | docs(fall-2026): log the Figma connection session and the first agentic diagram |
| 2026-09-26 | docs(fall-2026): log the Cowork connection attempt and the two film requests |
| 2026-09-26 | docs(fall-2026): log the Figma plugin-versus-connector fix and the film it became |
| 2026-09-26 | docs(fall-2026): log the board render and the start of the cc-explainer build |
| 2026-09-26 | docs(fall-2026): log the Figma version-history idea for Frictional |
| 2026-09-26 | docs(fall-2026): log the Frictional and Figma film request and the date correction |
| 2026-09-26 | docs(fall-2026): log the Figma version-history idea for Frictional |
| | ↑ **the row above is the subject this commit actually carries.** The subject intended for it was *"chore(fall-2026): sync the reject sampler from the master"*; a scripting error reused an earlier commit's subject line. The content is correct; history was not rewritten to fix a label. |
| 2026-09-26 | docs(fall-2026): log the three finished Figma films |
| 2026-09-26 | chore(fall-2026): sync the title auditor from the master |
| 2026-09-26 | chore(fall-2026): sync keywords v0.4.0 and the title families from the master |
| 2026-09-26 | docs(fall-2026): log the Figma repo push and the why-I-am-doing-this film request |
| 2026-09-26 | chore(fall-2026): sync the demand report and EDU_PRODUCT family from the master |
| 2026-09-26 | docs(fall-2026): log the Cowork film going up unlisted |
| 2026-09-26 | docs(fall-2026): log the Claude Code film going up unlisted |
| 2026-09-26 | docs(fall-2026): log the finished context film |
| 2026-09-27 | docs(fall-2026): log the last two Figma films going up unlisted |
| 2026-09-27 | docs(fall-2026): log the plan for the next 15 Figma films |
| 2026-09-27 | docs(fall-2026): log the overnight run of the next Figma films |
| 2026-09-27 | docs(fall-2026): log the overnight Figma films and their verdicts |
| 2026-09-27 | docs(fall-2026): log my review of the overnight Figma films and the notes-in-the-file idea |
| 2026-09-27 | docs(fall-2026): log where my Figma review notes went and the ten re-cut films |
| 2026-09-27 | docs(fall-2026): log the sign-off on the ten re-cut Figma films |
| 2026-09-27 | docs(fall-2026): log the ten Figma films going up unlisted |
| 2026-09-27 | docs(fall-2026): log the question about the next ten Figma films |
| 2026-09-27 | docs(fall-2026): log the order to build Figma films 16 to 25 overnight |
| 2026-09-27 | docs(fall-2026): log the session-limit stop and the retry on films 18 to 25 |
| 2026-09-28 | docs(fall-2026): log the ten finished Figma films from the second overnight run |
- **2026-09-28, noon: "it is after 3am."** The YouTube quota had reset, so the two blocked steps ran: the Figma playlist is in order (the six earlier films, then the ten new ones by film number), and every one of the ten has exactly one caption track, so film 2 has no duplicate. Four of the ten (1, 2, 3, 7) are now public, which I did in Studio; the publisher uploaded all ten unlisted.
| 2026-09-28 | docs(fall-2026): log the playlist reorder and caption check |
- **2026-09-28: sign-off on films 16 to 25.** In my words: "look great Ive reviewed publish all currently unpublished", with the usual runbook pasted. All ten go up unlisted on @NikBearBrown, in both playlists.
| 2026-09-28 | docs(fall-2026): log the sign-off on Figma films 16 to 25 |
  - **Done the same day:** all ten are up, unlisted, native 4K, one caption track each, in both playlists: 16 _-h7rkUej70, 17 YjoIfoOJgsk, 18 hQXXcFHSR04, 19 DnXiQWK8jc4, 20 j_yLifLc38k, 21 tYH92Pqw-MM, 22 zCHGiWw4L1s, 23 z5VC4u2K3gs, 24 urIYFefBWfM, 25 vos_5jXGQUs (youtu.be/…). Twenty-six films in the Figma playlist.
| 2026-09-28 | docs(fall-2026): log films 16 to 25 going up unlisted |
| 2026-09-28 | docs(fall-2026): log the Chapter 2 show-tell film and the course mix-up |
| 2026-09-28 | docs(fall-2026): log the Codex handoff for the Chapter 2 film |
- **2026-09-28: "Do the repo push."** The Figma repo is pushed: one commit (7183cb0) with the twenty reel folders (sources and paperwork; renders stay ignored), the two overnight briefs and reports, the review-notes tool and its tests, the workshop kit, the examples and the call ledgers. Local paths were scrubbed to ~/books in 98 files first; no Figma file keys were added.
| 2026-09-28 | docs(fall-2026): log the Figma repo push |
- **2026-09-28: "next 10 films?"** The answer goes in the Figma repo as FILMS-NEXT-3.md (films 26 to 35).
| 2026-09-28 | docs(fall-2026): log the question about Figma films 26 to 35 |
- **2026-09-28: "prompt to hand to codex to finish these films."** Films 26 to 35 go to my Codex account, the parallel track. The prompt is `figma-for-educational-ai/CODEX-BUILD-PROMPT.md`.
| 2026-09-28 | docs(fall-2026): log the Codex hand-off for Figma films 26 to 35 |
- **2026-09-28: "can claude make the films? create a filmloop like these for the show-tells in Liam persona?"** Yes: a shell loop, one fresh Claude session per film, like `anthropics/filmloop.sh` and `engineloop.sh`. The new loop is `anthropics/showtellloop.sh` with `SHOWTELL-LOOP-PROMPT.md`, queued from the Figma repo's FILMS-NEXT-3.md.
| 2026-09-28 | docs(fall-2026): log the show-tell film loop request |
  - **Same message, later:** "I think co-work is talking to Figma now. We had this issue before where only one of the two can speak to it … basically we have to unhook the MCP server." And: "I launch claude code from here make sure the are the correct paths" (`~/books`). Claude's answer: the two run on different Claude accounts, each with its own Figma sign-in, so both can be connected at once; the earlier break was a duplicate bare `claude mcp add figma` server, not a one-at-a-time limit. The terminal just needs its own /mcp → Connect. Nothing is unhooked.
| 2026-09-28 | docs(fall-2026): log the Figma-connection question for the film loop |
- **2026-09-28, evening: "quota just changed ... are there any films whose uploads were quota blocked?"** Google's compliance review finished and the upload cost dropped from 1,600 units to 100 per video. No upload was ever blocked: all twenty went up. Only two post-upload steps had hit the quota (the playlist reorder and a caption check). The reorder still returns quotaExceeded tonight, since today's usage was already counted at the old rate; it runs after the midnight-Pacific reset.
| 2026-09-28 | docs(fall-2026): log the YouTube quota change and the finished playlist order |
- **2026-10-06: the show-tell loop, resumed.** I pasted the terminal's report on film 26 ("Film 26 recovered — all clear … the agent put the final master in brutalist.art/renders/ instead of exports/landscape/") and said "Try again". Since 09-29 the loop had built films 26 to 29 on its own and stopped on film 30 at the session limit. The renders/ trap is now in the loop's prompt, and the loop is restarted for films 30 to 35.
| 2026-10-06 | docs(fall-2026): log the show-tell loop restart for films 30 to 35 |
  - **Afternoon:** films 30 and 32 finished (30 had been misread as a limit hit; the loop's check order is fixed). Film 31 was killed three times by another Claude session on the Mac running `pkill -f compile.py` and `pkill -f "art run"` to clear its own renders: the loop passed the whole prompt on the command line, and the prompt contains those words. The loop now feeds the prompt on stdin, and 31 is requeued.
| 2026-10-06 | docs(fall-2026): log the pkill collision that killed film 31 and the stdin fix |
  - **Evening: all ten masters (26 to 35) are done,** none staged or published. Three were accepted by hand after the loop misjudged them: 30 (the limit-message check), 33 and 35 (a stop hook recompiles the slate after the cut and re-stamps the beat sheet, so "master newer than the sheet" was the wrong rule; the loop now checks that the master was written during the session). The rubric draft is at CERTIFICATION.md, mine to edit and sign.
| 2026-10-06 | docs(fall-2026): log the ten finished Figma films from the show-tell loop |
- **2026-10-06, evening: sign-off on films 26 to 35.** In my words: "push to the Anthropics folder as well as the GitHub. Publish everything that's not been published at 4K to the Nick Bear Brown YouTube. They look great." So: the loop scripts go into the anthropics repo, the Figma repo gets films 26 to 35, and all ten go up unlisted on @NikBearBrown in both playlists.
| 2026-10-06 | docs(fall-2026): log the sign-off on Figma films 26 to 35 and the two pushes |
  - **Done the same evening:** both pushes (anthropics 4adec378, the Figma repo 783ba01) and all ten films up, unlisted, native 4K, one caption track each, in both playlists: 26 TRiMctnOQSE, 27 ePGXsvt9LhA, 28 pGkpWSUhOLQ, 29 SG4Y4srlgb4, 30 4lnhfDWG2hA, 31 7wwq6JK3mE4, 32 zU33OV5bQIA, 33 pezfmRyUClU, 34 2iCWJuiYFVE, 35 gN7pbmABQ1k (youtu.be/…). Thirty-six films in the Figma playlist.
| 2026-10-06 | docs(fall-2026): log films 26 to 35 going up unlisted and the two pushes |
| 2026-10-07 | chore(fall-2026): receive demand_report.py from the master in the first real sync |
- **2026-10-07: "it's two more assignments … The next assignment is going to be a film. Using Brutalist, on what you think your final project is going to be … a short film, 50-point assignment, 10 points of that is the quality score … It should be something that will help students get a job … Five days."** I pasted the Reallocation Engine Mode Build brief (the 100-point one) as the assignment that comes after. The film is the new one: `assignments/assignment-final-project-pitch-film.md` (with a Canvas paste at `-canvas.md`). 50 points on the syllabus proportions: 30 pitch, 5 Frictional, 5 GitHub, 10 Relative Quartile. The film answers five questions (what, who opens it, what it proves, scope and first milestone, what could sink it) and has to keep exists-versus-will-exist honest. Logged as item 8 in the instructor decisions. Drafted only; not committed or posted to Canvas. Open: the pasted Mode Build brief says "mode" and uses a 24/20/16/20 rubric, while the repo's committed recipe-design brief says "recipe" and uses the 60/10/10/20 spine; which one stands is not decided.
| 2026-10-07 | docs(fall-2026): log the request for the 50-point final project pitch film |
- **2026-10-07: "I like the fact that you added what it proves about you. But … this is also a project that they might take into an actual project. Why would anybody care about this project? … in business, that's called a unique value proposition. What makes this project special? … I would add a question related to a unique value proposition."** The pitch film now asks six questions, not five. The new one is second: why would anyone care, and what makes it different from something that already exists, naming at least one real alternative the student looked at. It carries 6 of the 30 pitch points; the other criteria were trimmed to 8, 6, 5 and 5. Both briefs updated, not yet committed in the assignments folder.
| 2026-10-07 | docs(fall-2026): log the unique value proposition question added to the pitch film |
- **2026-10-07: "a seventh question … why are you doing this? … why did you pick this project … because you want to learn a new skill … or because you want to show off what you already know … Is this something new that you're learning? Is it a combo? Are you showing off skills that you already have?"** The pitch film now asks seven questions. The new one is last: why this project, new learning, existing skill on show, or a mix, with the new skills separated from the held ones and the held ones backed by something real. No answer is preferred. It carries 4 of the 30 pitch points; the other criteria are now 7, 5, 5, 5 and 4.
| 2026-10-07 | docs(fall-2026): log the seventh question added to the pitch film |
- **2026-10-07: laying out my own final project, starting with the executive summary.** I described it as learning materials bridging Figma, Claude, Google (NotebookLM), Microsoft, OpenAI and maybe others, promoting only tools I believe in. Then I answered the test and the audience questions: "the test is pretty much always I show the tool in actual honest use, with both issues and with pluses, on real problems that are used in education … from the perspective of a student doing an assignment, … a teacher making assignments and grading assignments, … administrators wanting to log real learning … if a company is making this product, targeted to education, they want … good feedback on what works and does not work … Showing real results through film. And then letting whoever's watching that film judge for themselves." On audience: "no group comes first necessarily … right now I am doing my assignment in class … So the perspective there is students. I'm also using you right now to write the assignment for students … We'll hold off on the administrators and the companies to later because they're not directly involved. But the first two groups will be students using this to do work where they're learning. And teachers using it to evaluate real learning as opposed to just the artifact." Executive summary revised to match; the other six answers are next.
| 2026-10-07 | docs(fall-2026): log the project executive summary and the test and audience answers |
- **2026-10-07: two answers on the project's rules.** On belief deciding what gets evaluated: "my belief … gets discussed or even what gets evaluated, but I also am an expert in this … based on a lot of experience in doing this and being on Northeastern's educational committees, which drive the educational tools." On dropped tools: "maybe somebody thinks I should not have dropped the tool. They're free to comment on the YouTube or wherever to say maybe revisit this … we put dropped tools out there as well. Both successful and dropped. We don't filter. The whole thing is I try to evaluate it as honestly as I can. Admitting that I'm a human being. And, you know, I have a perspective. But encourage people, and that's part of the reason why we put it public and on YouTube, so other people can add their perspectives." Executive summary updated: every evaluation is published, passed or dropped.
| 2026-10-07 | docs(fall-2026): log the answers on expert judgment and publishing dropped tools |
| 2026-10-07 | docs(fall-2026): add my pitch-film project brief draft and log the process |
| 2026-10-07 | docs(fall-2026): add diary entry 1 for the project film and point the brief at it |
| 2026-10-07 | docs(fall-2026): research ChatGPT Study mode and NotebookLM Learning Guide for the project film |
| 2026-10-07 | docs(fall-2026): plan the Professor Bear Does His Assignments series and lay out film 1 |
| 2026-10-07 | docs(fall-2026): add the Conducting AI, irreducibly human and skepticism through-line to the series plan |
| 2026-10-07 | docs(fall-2026): add getting better by making films and the later YouTube cleanup to the series plan |
| 2026-10-07 | docs(fall-2026): name the Professor Bear Does His Assignments playlist in the series plan |
| 2026-10-07 | docs(fall-2026): add the project software design document, written by Gru in silent mode |
| 2026-10-08 | docs(fall-2026): lay out film 2, the overview from the design document |
