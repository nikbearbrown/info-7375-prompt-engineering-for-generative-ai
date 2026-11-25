# Friction Log: job-search-agent

Scope: `job-search-agent`

### 2026-10-29: Board, persona, and a résumé-to-JSON idea

**What I tried and expected**

Use the most common board. Is Greenhouse the biggest? What's a persona for? Then: the persona résumé could be any common résumé format turned into JSON. Maybe build a tool for that, since real users will upload their own résumé and it needs to be reliable. Keep it as a proposal for now, don't build it.

**What happened**

The AI said it has no reliable market-share numbers, but Greenhouse is common and its public API needs no login. It explained a persona is a fictional job seeker, because my real résumé can't go on GitHub. It recorded Greenhouse as decision D1 and the converter as proposal P1 (not approved). The AI added notes for later: which JSON schema to use, and that an AI conversion is a judgment that needs a validator.

**My judgment calls**

- Kept Greenhouse. Want to see the repo's persona JSON format next to my own résumé before picking a persona.
- Caught that the AI's requirements file only had a link to `_brief/`. If I delete the brief, it's gone. I want the requirements written down once, in short plain sentences, as an answer key. The AI admitted the convention had two rules that contradicted each other, and rewrote both the convention and this task's checklist (R1–R33 to do, S1–S14 to submit).

**What's next**

Asked why there's no plan yet. The AI drafted a 14-step plan and four open questions (company, persona, language, friction scope).

### 2026-10-29: Company, language, friction scope

**What I tried and expected**

I don't know which company to use. Do big companies not use Greenhouse? Is Python really the easiest? If TA convenience isn't the main thing, what else would you suggest? And yes, add this project as a friction scope.

**What happened**

The AI registered `job-search-agent` as a friction scope and created this log. On companies, the AI said (from memory, not checked) that the biggest names like Google, Amazon, Meta, Apple and Microsoft mostly run their own hiring systems, while many mid-to-large tech companies use Greenhouse, and offered to check a few live. On language, the AI still suggested Python, with TypeScript as the option if I want to reuse the Reallocation Engine code later.

**My judgment calls**

- Accepted Python.

**What's next**

Write CONTRACT.md myself, with some guidance on what goes in each part.

### 2026-10-29: The rule should work for any résumé, not one persona

**What I tried and expected**

The AI said to pick the persona before writing the rule. But isn't this tool supposed to fit everyone who uses it? If it's customized to one person, nobody else can use it.

**What happened**

The AI agreed and corrected its earlier advice. The rule should be written against résumé field names (for example "title matches one of resume.target_roles"), so the values come from whoever's résumé is loaded. The persona is only the test data that fills those values for the demo and the hand labels. What the AI actually needs first is the résumé JSON schema (which fields exist), not a specific person.

**My judgment calls**

- Accepted that the rule uses field names, not one person's values.
- Didn't get why a résumé JSON would hold a target job. I thought it was just the résumé in JSON. The AI admitted it had mixed two things: the résumé (what I've done) and job preferences (what I want).
- Asked the AI to check JSON Resume instead of going from memory. The AI fetched the official schema: it has skills with keywords, but no job preferences section.

**What's next**

Pick the format and decide résumé only vs résumé plus a profile.

### 2026-10-29: JSON Resume, plus a profile file

**What I tried and expected**

Go with JSON Resume, the more people use a format the better. Do we still need a tool to turn a normal résumé into JSON Resume? I can test it with my own. I pick B: résumé plus profile. And confirm all of this is inside the instructor's rules.

**What happened**

The AI recorded both decisions. It checked them against the brief: the brief says In is "a board name, a résumé as JSON, and what it needs", so a profile file is fine as long as CONTRACT lists it. The AI said the converter is not needed for JS1, since the persona can be written by hand, and kept it as a proposal for later. It pointed out that testing it on my real résumé is fine only locally, and that sending it to the Claude API is sending it to an outside service.

**My judgment calls**

- Accepted that the converter isn't needed for JS1. Put it on the later to-do list.

**What's next**

Use the example persona converted to JSON Resume, so I don't have to make one up. Aarav Patel and Stripe.

### 2026-10-29: Aarav Patel on Stripe, conversion held until the contract exists

**What I tried and expected**

Can I use the example persona and fit it into the JSON Resume format, so I don't have to invent one? Use Aarav Patel and Stripe. Do what you suggested. Put the tool on the later to-do list.

**What happened**

The AI recorded Aarav plus Stripe. Before converting, it pushed back on its own plan: the brief says to write CONTRACT.md before asking Claude to write anything, and the profile's fields are something my contract defines. So the AI held off writing the files and only showed, in chat, how Aarav's data would map onto JSON Resume fields, so I have real field names to use when I write the rule.

**My judgment calls**

- Went along with holding the conversion. Asked the AI to explain in Chinese what In, Out, Refuses and the rule actually need and why, then wrote a first draft of CONTRACT.md myself.

**What's next**

Get today's raw data saved so tomorrow's run is a real second day, even if the contract isn't done.

### 2026-10-30: How to match titles

**What I tried and expected**

My idea: lowercase everything, split titles into words (also split on "/" and other symbols, so "Backend/API Engineer" becomes backend, api, engineer), and call it a match if at least one word matches something in profile.target_roles. I want this so a company writing a longer title like "software dev of some kind" doesn't get marked not_relevant. I know it can misfire: if I write "Backend", then "Backend Quant Engineer" matches, and that's not something I can apply to. I'll accept that for the first version since I don't know a better way. Or is it better to treat each phrase as one item?

**What happened**

The AI kept my normalization but pushed back on "any one word matches", and tested it on the saved Stripe titles with sample targets from Aarav's profile. Any word: 163 of 737 match, including "Designer, Web Presence & Platform" and "Staff Security Engineer", because "engineer" or "platform" alone is enough. All words of one target phrase, in any order: 92. That plus a list of excluded words (senior, staff, quant, manager…): 62. The AI suggested the last one, with the excluded words living in the profile.

**My judgment calls**

- Accepted matching per target phrase instead of any one word.
- Haven't said yes or no to the excluded-words list yet.

**What's next**

Put the word-matching explanation at the top of the rule, then wrote most of CONTRACT.md myself in Chinese and asked for a review.

### 2026-10-30: Review of my Chinese CONTRACT draft

**What I tried and expected**

I've written most of CONTRACT.md, in Chinese. Review it and tell me the problems. Then translate it to English at the end (that part still counts as my writing).

**What happened**

The AI reviewed it and listed problems, without editing the file. The biggest: my rule section has two versions of title matching (the new per-phrase one at the top, my old "any one word" text below), and my skills check can't be done as written. Greenhouse has no skills list, only the JD as HTML, so "the JD lists five skills" can't be counted without AI. The AI checked the saved data: of 62 postings that pass the title check, none would have half of Aarav's 17 skills in the JD; 42 have at least 1 and 22 have at least 2. Other problems: field names still differ between In, Out and the rule, wrong version 2 brings in an "unknown" verdict that Out doesn't allow, and the failure section has no date and isn't one sentence.

**My judgment calls**

- Deleted the old "any one word" text myself.
- Accepted counting résumé skills found in the JD instead of "half of the JD's skills", with at least 1 match.
- For an empty JD: not_relevant plus a reason. My own idea: add a status / error_message field, so a verdict only means something when judging succeeded.
- Wanted the output to also show the state file path, name and update time, plus a summary table of how many passed and how many got cut at each step, "so I know what you're doing".

**What's next**

### 2026-10-30: Keep the simple skills check, write down its limits

**What I tried and expected**

Isn't searching the cleaned JD for résumé skills going to misjudge a lot? Is there another way? After the AI's numbers: keep it as is and add known limits. But the different spellings of one skill need fixing: either users write all the spellings, or the tool comes with them already (postgres = PostgreSQL, etc).

**What happened**

The AI measured it on the saved data. Searching only the requirements section changed 2 of 60 postings, and word splitting already keeps "java" from matching "javascript". The real problems are that a keyword showing up doesn't mean it's required, the threshold of 1 is loose, and synonyms (2 JDs say "postgres"). It suggested writing these down as known limits, including work mode (hybrid not checked).

**My judgment calls**

- Picked C for synonyms: the tool ships a small built-in table, and users can add their own in the profile. Also said the tool has to tell users where they can add them.

**What's next**

Users get told where to add spellings in three places: a README section, a hint line at the end of every run summary, and the justification showing which spelling matched. "node" is not an alias for Node.js, for the same reason as "go": it's a normal word ("each node").

### 2026-10-30: Go and node are normal words, so the rule skips them

**What I tried and expected**

Should the tool just use "golang" for Go and "nodejs" for Node.js, or is there another way?

**What happened**

The AI counted it on the saved data: "golang" is in only 3 of 737 JDs, but "go" is in 283, mostly "Go-to-Market", and even after removing that, 106 still mix "Python, Go, Java" with "go further". It gave four options: safe aliases only, strip fixed phrases first, a context rule, or leave it to the Claude judge. It also found 11 JDs share the sentence "We work mostly in Java, Ruby, JavaScript, Scala, and Go", so Java can pass from company boilerplate.
Trace: CONTRACT.md

**My judgment calls**

- Picked A + D: only safe aliases in the rule, and Claude decides when "Go" means the language. The other ways were too complicated.
- The AI then suggested an "only_search_aliases" list so the rule wouldn't search "go" itself. That confused me, so I went back to simple: search every skill and every alias, go included.
- Thought about raising the threshold from 1 to 3. Kept 1 after the numbers: 3 → 1 relevant, and the postings with 1 hit really did ask for Java.
- Accepted that "Go" will misfire as a known limit. The AI checked: among the 60 engineering titles, only 2 of the 27 "go" hits were just Go-to-Market.

**What's next**

Search every skill and alias, keep the threshold at 1, and write the Go misfires down as a known limit, with those numbers.

### 2026-10-30: More checks from my profile: years, visa, salary

**What I tried and expected**

Asked why work mode and job type were taken out. Said the profile locations should include "us". Years can be checked: the user writes a number in the profile, but how much higher should the filter allow? 5 years and 8 years are close enough to still apply, unless the gap is really big. Visa: add a profile field for what you need (H-1B / sponsorship) and search the JD for words like "no sponsorship". Salary: check it if the JD gives one, skip if it doesn't.

**What happened**

The AI measured each idea on the saved Stripe data before changing anything. Adding "us" gives 4 relevant instead of 3. Years are in 654 of 737 JDs, often as a range like "2–12+ years". Stripe never mentions visa sponsorship (the word "sponsor" shows up only as "executive sponsor"). Only 24 of 737 JDs list a salary. Job type mostly shows up in the title (13 "intern", 5 "contract"), so the exclude words already cover it.
Trace: CONTRACT.md

**My judgment calls**

- Didn't believe Greenhouse has no work-mode field: the job pages I see show tags like "In person". Sent a screenshot and asked the AI to run it, and to drop the field only if it really isn't there.

**What's next**

The AI fetched the exact job from my screenshot through the public API. No work-mode field anywhere; the tag only exists on Greenhouse's web page, and that job's text even says "hybrid, four days a week". So work mode stays out.

### 2026-10-30: Years, visa, and salary become checks 4–6

**What I tried and expected**

Go with the AI's plan: add the known limits and the years check. For visa, a simple filter with a fixed list of "no sponsorship" phrases: if one shows up, fail; if none shows up, pass.

**What happened**

Checks 4–6 use optional profile fields (skip the check if the field isn't filled) and a built-in phrase file. The AI pointed out visa needs whole-phrase matching: with normal word matching, "no" and "sponsorship" could both be found somewhere in a JD that doesn't mean that. It re-ran all 737 postings: still 3 relevant. The years check drops 8127182 ("5–12+ years"), and adding "us" brings in 6176758. Visa and salary drop nothing on Stripe.
Trace: CONTRACT.md

**My judgment calls**

- Said the work-mode limit was too detailed and didn't sound like me. Cut it down to: the Job Board API doesn't give this field, only some JDs mention it, so it isn't checked.
- For the lowercase wrong version, the AI's test ran a whole posting and expected "relevant", which needs all six checks to pass. I said the checks all call the same word-splitting function, so test that one function directly, with inputs shaped like what each check sees.

**What's next**

Wrong version 4 now: every check calls the same word-splitting function, and the test feeds it five inputs (a title with a tab and "/", a location, JD text, a résumé keyword, a visa phrase) and checks the word list it returns.

### 2026-10-30: Claude's verdict has to show its evidence

**What I tried and expected**

Claude can read the whole posting, but I need a way to judge how well it read it, so it should give evidence, not just "relevant". And why not use the same Out format I already defined? Also asked to write the visa check as plain whole-phrase matching ("no sponsorship", "we do not sponsor").

**What happened**

The AI agreed on the same format and suggested a `quote` on each justification line: text copied from the posting. It explained the validator: a piece of code that checks Claude's answer before it is saved, and rejects it if the format is off or the quote isn't really in the posting. The validator can only prove the evidence exists; whether it supports the verdict is still my call in the reports. Whole-phrase matching is what I meant for visa; the example is "No degree required. Visa sponsorship is available." (both words are there, but it means sponsorship IS available).
Trace: CONTRACT.md

**My judgment calls**

- Said OK, put it in the contract.

**What's next**

Still open: the PLAN draft, saving a 10/30 snapshot tonight, and which model the Claude judge uses.

### 2026-10-30: The plan is agreed

**What I tried and expected**

New session: continue the task and write the PLAN from the draft.

**What happened**

The AI read the contract and the draft, then asked me the two open choices instead of picking them itself. It wrote PLAN.md: every requirement from the brief (R1–R33 to do, S1–S14 to hand in) is mapped to a step and has a concrete way to check it. It added a step 0 for things before code: the contract (already committed) and committing the saved 10/29 data. The 10/30 backup snapshot was dropped, since a live run on 10/31 is already a different day.

**My judgment calls**

- Claude judge uses Sonnet 5.5.
- Commit the 10/29 raw data now, before any code, so git shows the data came first.

**What's next**

Asked whether I need to give the AI an API key, and what "about 60 calls" means.

### 2026-10-31: Claude judges only 2 new postings while I'm testing

**What I tried and expected**

Even if lots of new postings show up, this is only a test, so running one or two is enough. If Claude judges 40, I can't check them one by one, so that run is wasted. Only while testing: when there are more than 2 new postings, skip the rest, mark it clearly, and take it out before uploading. The prompt experiment comes later, so I won't worry about it now.

**What happened**

The AI had warned that the brief wants a Claude verdict for every new posting. It recorded my call as a test-only limit: the skipped postings get an error saying the test limit skipped them, the run summary says how many Claude judged, and the code carries a "remove before submission" mark that gets checked before upload.

**My judgment calls**

- A test run is only worth it if I can check every answer, so 2 is the limit while testing.

**What's next**

Whether Claude judges every new posting for the version I hand in: decide after testing is done. Committed the 10/29 data myself (34c1deb), then asked the AI to start Step 1.

### 2026-10-31: Fetch only the new postings' JDs?

**What I tried and expected**

After the AI explained Step 2 in Chinese, I noticed the 10/29 raw data was fetched by the AI with curl, not by the agent. My idea for the tool: fetch the plain list first, find the new ids, and only then fetch the full content for those. Wouldn't that save download? Or is it not needed now and better kept as a proposal for later? Also: does the agent need to keep the whole raw JSON, or only the ids, since old postings' other info isn't needed?

**What happened**

The AI measured it: the plain list is 0.46 MB and the full one 5.7 MB, so with 20 new postings the two-step fetch would be about 0.6 MB, but 21 requests instead of 1, and the contract's raw file path would change. On keeping data: the brief requires the raw responses of both runs, a TA needs the JD text to recompute a verdict, and my hand labels read old postings, so the full raw stays. The state file is already the "ids only" store. Recorded the two-step fetch as proposal P3.

**My judgment calls**

- Before committing Step 2, asked whether every step's feature branch has to be merged back to main first, or we'd end up with lots of branches. Then asked how a fast-forward merge is any different from committing on main. The AI admitted the end result is the same history; a branch only helps to throw away half-done work or for PR review. Chose to commit directly on main.

**What's next**

Step 3 on main: my rule's six checks.

### 2026-10-31: Code has to follow a company standard

**What I tried and expected**

When writing code, follow company standards: reuse what can be reused, no tight coupling so later changes aren't painful; clear logic that's easy to read and extend; don't put everything in one file unless really needed. Good architecture overall.

**What happened**

The AI reviewed its own Step 3 code against that and listed the problems: one long function with all six checks, Greenhouse parsing and the allow-list inside the watch, check names written twice, the command line and the run mixed together. It split the code into small modules (network, board adapter, state, one function per check, one shared verdict shape for both judges, a pipeline the tests can call), then re-ran everything: same numbers as before.

**My judgment calls**

- Noticed the files were all still in one level, no folders. The AI grouped them into common/, watch/ and judges/, and moved the shared posting shape into common/ so the judges don't depend on the watch. Same results after the move.

**What's next**

Commit Step 3, then Step 4 (tests) in a new session.

### 2026-10-31: Step 4, tests for the six wrong versions

**What I tried and expected**

Continue Step 4: tests for wrong versions 1 to 6, the allow-list, and the real résumé guard. Claude writes them, I run them.

**What happened**

The AI wrote one pytest file per wrong version plus one for the Refuses rows, with fake board data so no test touches the real board, the network, or the repo's state/ and runs/. The Claude-side halves of wrong versions 2 and 5 are marked skipped until the Claude judge exists (Step 5). In its own scratch venv: 54 passed, 2 skipped. Then the AI broke the code on purpose 11 ways (for example: state ignored, no lowercase, visa matched word by word, allow-list removed) and every one was caught by its matching test file. It also added pytest.ini, requirements-dev.txt (pytest 8.4.2) and .venv/ in .gitignore. My official run is still to do.
Trace: tests/, pytest.ini, requirements-dev.txt

**My judgment calls**

- Asked why it says 54 passed when I only listed 16 tests. Two reasons: each row of a parametrized test counts as one test, and the AI had added 18 test functions I did not ask for, without asking first.
- The AI suggested keeping them (they guard rules the contract does state, like board and state failures) and listing them as "contract" vs "extra" in the README. Accepted.

**What's next**

Still a bit confused, so I asked the AI to walk me through one test to see how it actually works. After the walkthrough I ran the full suite myself in a .venv (54 passed, 2 skipped) and committed it. Step 5 (Claude judge) next.

### 2026-10-31: No API credits, so Claude runs through my Claude Code subscription

**What I tried and expected**

The first real Claude call failed: "credit balance is too low". My school login has no API credits. Does the assignment really need an API key, or can Claude run another way? Then: use the CLI, because most people buy the subscription now, not the API. And does my CLAUDE.md leak into the judge?

**What happened**

The AI checked the brief: it never mentions the API, only a prompt contract, a fixed format, a validator and fresh conversations. It added a judge that calls `claude -p` with tools off, no settings, a fresh folder per call and the API key removed; the API way stays as `--claude-via api`. The AI rejected having itself judge in this chat (not fresh, already saw the rule's answers, a TA can't rerun it). It measured the leak: with normal settings Claude quoted my AGENTS.md; with `--setting-sources ""` it didn't. The trade-off: our program can't check the host of Claude Code's own requests, so CONTRACT got edits.
Trace: job_agent/judges/claude_cli.py, CONTRACT.md

**My judgment calls**

- Went with the CLI. Accepted the AI's refusal to judge in this chat.
- Told the AI to make the CONTRACT edits itself, without date stamps.

**What's next**

Remove the 2-posting test cap and do the real runs.

### 2026-10-31: Why 20 new when the board only grew by 8

**What I tried and expected**

Done running. Run 2 has 745, Run 1 has 737, so why does it show 20 new postings?

**What happened**

The AI recomputed it from the two raw files instead of trusting the program: 20 postings are only in today's file and 12 are only in the 10/29 file (closed since then), 725 are in both, so 737 − 12 + 20 = 745. "New" counts added postings, not the net change. The 20 ids the program judged are exactly those 20. State has 757 ids = both runs together. Run 1 reported 0 (baseline, seeded). All 40 verdicts (20 rule + 20 Claude) are ok and not_relevant, no disagreement, no validator rejections, all Claude calls went through the CLI on claude-sonnet-5-5.
Trace: runs/2026-10-31T214040Z, runs/2026-10-31T214118Z, state/stripe.state.json, evidence/runs/

**My judgment calls**

- Asked if the user should be told that 12 postings disappeared, since the numbers look off. The AI gave three options (one extra line, exact "closed since last run" with a state change, or nothing now). Picked C: keep it as is, explain it in the README, do it in the next layer.

**What's next**

Didn't understand the Step 7 explanation, asked for it again in Chinese.

### 2026-10-31: My labeling rule, and how the 20 postings get picked

**What I tried and expected**

Write the first step for me. Here is what I usually look at, in order: 1) title, only engineer-related ones; 2) location, is it in the US; 3) skills, jump to the skills part or search the whole post, and if two or three are ones I know, keep going; 4) sponsorship; 5) salary; 6) other requirements, like years of experience. I liked the idea of mixing in the ones that passed or were relevant, otherwise there's nothing to check against. How do I pick them? Do I find the passing ones and go look up their URLs? Is it a separate file, and is it 10 I pick plus 10 something else?

**What happened**

The AI typed my six steps into labels/LABELING_RULE.md, from Aarav's point of view, with the first failing step meaning not_relevant. I don't have to look anything up: a script picks all 20 from today's saved raw file with a fixed random seed (5 the rule keeps or cuts late, 10 engineering titles cut only by location, 5 clear title rejects), shuffles them, and writes their text and link into one file without any verdicts, plus an empty labels.csv for my label and reason. All 20 are labeled the same way; the 10 dev / 10 held-out split is done randomly by a script after I finish, so the split can't bias my labels.
Trace: labels/LABELING_RULE.md, labels/select_postings.py, labels/postings_to_label.md, labels/labels.csv

**My judgment calls**

- OK'd the three details the AI filled in from Aarav's profile: US remote counts as US, minimum salary $75,000, "clearly more experience" means more than 4 years.
- Added one more rule: nice to have counts as must have. If a posting lists it, it's expected, because someone who has it will apply.

**What's next**

Add the nice-to-have rule, then commit the rule before labeling.

### 2026-10-31: No location means pass, in my labels and in the rule

**What I tried and expected**

A bare Remote counts as a pass. Contract: option B. Re-run, but wait until I finish labeling.

**What happened**

The AI added the missing-location line to my labeling rule, with a note that it came after I labeled rows 1 to 3 (those three all had a location). It changed check 2 in the code and the contract: empty, N/A, na or a bare Remote now pass with "skipped: no location in posting", the same direction as checks 4 to 6. New tests; 106 pass. It re-ran the contract Examples on the 10/29 data: relevant went from 3 to 5 (two engineering postings with location `na`), location cuts from 55 to 49; the 8 example rows didn't change, and Run 2's 20 new postings are still all not_relevant. It noted that the posting-picking script used the old rule, so re-running it now would pick a different 20; the committed file is the record.
Trace: job_agent/judges/checks.py, CONTRACT.md, labels/LABELING_RULE.md

**My judgment calls**

- Kept the change and finished labeling the rest myself.

**What's next**

Have the AI review my labels.

### 2026-10-31: Sampling: 5 postings, 4 fresh conversations each

**What I tried and expected**

OK, move to Step 8. You said you'd pick 5 and run each 4 times. Does the teacher say to record them?

**What happened**

Yes: the brief says "Record every verdict" and compare against my hand label. The AI pointed out the 5 must come from dev only, otherwise I'd see Claude's answers on held-out early. It picked them by a fixed rule: the 4 dev postings where the contract rule disagrees with my label, plus 1 engineering posting I labeled not_relevant. 20 fresh `claude -p` calls, all accepted by the validator. Every posting got the same verdict all 4 times. Claude agreed with me on 4 of 5 (it reads NYC / Seattle / SF as US, unlike the rule), and disagreed 4 times out of 4 on the Solutions Architect posting, calling it a pre-sales role. The AI drafted the report with what can and can't be concluded, and left a section for my review.
Trace: reports/sampling.py, reports/sampling/results.json, reports/sampling/raw.jsonl, reports/sampling_report.md

**My judgment calls**

- Agreed Claude is right that Solutions Architect is pre-sales, but to me it's still software-related, not necessarily development, so I'd apply. Asked whether the prompt should say a role doesn't have to match strictly, since the job seeker may just not have thought of a related role, or whether to leave it.
- The AI said leaving it isn't an option (the brief needs one revision), and suggested running v1 on all 10 dev postings first to choose the change from evidence.

**What's next**

Pick the one change for v2.

### 2026-10-31: Prompt v2: relevant unless clearly a bad fit

**What I tried and expected**

Go with B. Anything that isn't clearly a bad fit counts as relevant; close or related is enough, the job seeker may not have thought of that kind of role. For example, I do backend development, and if a posting suddenly asks for ML tools and requirements, you know that won't work.

**What happened**

Baseline v1 on the 10 dev postings: 8/10. Both misses were v1 being stricter than me (the Solutions Architect title, and a "security domain" minimum requirement). The AI wrote v2 by replacing only the one paragraph that sets how strict the verdict is, using my wording and my backend-vs-ML example. v2 on dev: 9/10; it fixed the security one, but still calls Solutions Architect sales-focused. The held-out set hasn't been run: the script refuses until I say v2 is final.
Trace: prompts/claude_judge.v2.md, reports/experiment.py, reports/experiment/claude_judge.v1.dev.json, reports/experiment/claude_judge.v2.dev.json

**My judgment calls**

- Didn't tweak v2 again for the Solutions Architect miss (that would be a second change, tuned on dev). Declared v2 final.

**What's next**

Run held-out with both prompts.

### 2026-10-31: Held-out: v1 6/10, v2 10/10

**What I tried and expected**

v2 fixed, run held-out.

**What happened**

v1 got 6/10 on held-out, v2 got 10/10, no rejected answers. All four of v1's misses were it being strict (security experience, ISO 8583, three languages, and a New Grad experience cap). The AI checked that last one against the files: the posting allows at most 18 months of professional experience, and Aarav has about 25 at Infosys, so v1's reason is a fact and my "relevant" label may be the mistake. Its report says v2 mainly matches how lenient I am, that matching my label isn't the same as being right, that v2's risk of letting bad fits through wasn't tested because the held-out negatives were all easy, and that 10 cases show very little. It left a section for my review.
Trace: reports/experiment/claude_judge.v1.held_out.json, reports/experiment/claude_judge.v2.held_out.json, reports/prompt_experiment.md

**My judgment calls**

- Checked the New Grad point: I really did miss it. not_relevant is the right label. Asked what to do now.

**What's next**

Fix the wrong label without hiding that it was fixed.

### 2026-11-07: Plan first, then GATE.md

**What I tried and expected**

OK. Write a plan first, or do you need me to write GATE.md first?

**What happened**

The AI said plan first, since a plan is steps, not code, and GATE.md is step 2 of it, written by me. It drafted the plan as a proposal (not approved yet): boards check, GATE skeleton, I write GATE.md and the boundary-test expectations before any code, then second ATS adapter, permission policy with 10+ boundary tests, the loop, a real run with a failing board, the finished-wrong demo, the review packet, README and sign-off, export. It left four questions: deadline, which boards, whether the Claude judge runs inside the loop, and which change becomes the review packet. The AI suggested using the finished-wrong bug fix as the review-packet change.
Trace: AI_Task_Logs/job-search-agent-js2/01-action-plan.md

**My judgment calls**

- Due 11/10.
- Accepted the AI's suggestion to keep the Claude judge off by default in the loop.
- Didn't pick boards myself. Asked the AI to find Greenhouse companies that are active and have lots of engineering roles.

**What's next**

Board picks from the AI, and the review-packet question explained again.

### 2026-11-07: Picking the boards

**What I tried and expected**

Due 11/10. Find Greenhouse companies that are active and have more engineering roles. Go with your Claude judge suggestion. I didn't understand question 4.

**What happened**

The AI checked 18 public boards live (12 Greenhouse, 4 Ashby, 2 Lever, plus Plaid, which is not on Lever and gave a 404). It suggested Stripe and Cloudflare on Greenhouse and OpenAI on Ashby (the brief needs at least two ATSs), plus a misspelled board name as the one that fails on purpose. It also found that a wrong board name gets a real 404 on all three systems, so it's an error case, not a "finished but wrong" case. That one needs a 200 with an empty list. It explained question 4 again.
Trace: AI_Task_Logs/job-search-agent-js2/02-boards.md

**My judgment calls**

- Accepted the boards: Stripe, Cloudflare, OpenAI, and a misspelled name.
- Didn't just accept the empty-board bug for the review packet. Asked where the Step 7 test comes from, and whether I can design my own.

**What's next**

List all the errors a loop can hit, not just one.

### 2026-11-07: What can go wrong in the loop

**What I tried and expected**

Can I design new tests? Where does the Step 7 test come from, the instructor? My idea: the run can look finished but never actually get anything. The board may not exist on Greenhouse, the connection may fail, the data may come back empty (finished but no output), or the download may be too big and slow, so it needs a timeout. Since this is a loop, it has error handling, and every error-handling branch is a failure reason it should report. These are the ones I can think of now. What do you think?

**What happened**

The AI said the empty-board example comes from the brief (Step 2.2), not a ready-made test, so I can design my own. It sorted my cases into two kinds: ones the agent knows failed (404, connection error, timeout), which should end as error or incomplete, and ones where the agent thinks it worked but is wrong (200 with an empty list), which is the finished-wrong kind. It added more: rate limiting (429), server errors (5xx), broken JSON, a changed response shape (no `jobs` key read as zero jobs), a list shorter than Greenhouse's own `meta.total`, a sudden big drop from the last run, a redirect to another host, the budget running out partway, and the same URL fetched twice. It checked live that Greenhouse returns `meta.total` (Stripe 765) and Ashby doesn't. It said picking which ones go into GATE.md is my call.

**My judgment calls**

- Liked the A/B split. Not picking cases yet. Want them saved so I can plan later.

**What's next**

Write the plan, give me the GATE.md skeleton, and save the cases to a file.

### 2026-11-08: GATE.md review

**What I tried and expected**

GATE.md is done. Take a look. If nothing's wrong, move to Step 3.

**What happened**

The AI did not move to Step 3. It timed each board twice: all under 1 second (OpenAI is 13.6 MB), so my 10-second timeout has lots of room, but saved raw is about 28 MB per run. It raised three points before commit. (1) My `finished` only needs one board to succeed, so 3 timeouts plus 1 success would still say finished. It suggested `finished` only when every board succeeds, and said it's my call either way. It also pointed out that I use `incomplete` for both a board and a run. (2) Boundary test 3 uses `jobs/` but my policy's writable folders are `runs/`, `evidence/raw/`, `state/`. (3) No wrong version covers the brief's own example (empty list read as no new jobs) or a failed board showing 0 jobs. Smaller notes: `api.anthropic.com` for `--claude-via api`, the error-code list is incomplete, and the `meta.total` gap is a natural finished-wrong source for Step 7.

**My judgment calls**

- Accepted (1): picked B, `finished` only when every board succeeds. Board status renamed so it doesn't clash with the run exit.
- Accepted (2): my folders in Section 5 were examples, so the mismatch was expected, but the test should use the real folder.
- Accepted (3): add both wrong versions.

**What's next**

Have the AI make the three edits, and explain the API note.

### 2026-11-08: GATE fixes in, API host question

**What I tried and expected**

Your suggestions make sense. Go with B, and rename the board status so it doesn't clash with the run exit. Section 5's folders were examples, but do it your way. Add the wrong versions. I don't get the Claude-via-API note.

**What happened**

The AI made the edits in my GATE.md: `finished` now needs every board `ok`; board status is `ok` / `failed` / `skipped`; an order for which exit wins when more than one fits (the AI wrote this, I should check it); test 3 now uses `runs-evil/` next to `runs/`; WV3 (empty list or no `jobs` key read as 0) and WV4 (failed board shown as 0 jobs); a new code `202`. It explained the API note: JS1 can reach Claude two ways, and only the API way makes our own program call `api.anthropic.com`, which GATE's host list doesn't include.
Trace: GATE.md

**My judgment calls**

- Picked (a): allow `api.anthropic.com` only with `--claude-via api`. The AI added the line.

**What's next**

Before committing, asked about the AI's earlier note on where Step 7's finished-wrong run comes from.

### 2026-11-08: Empty fetch vs zero new jobs

**What I tried and expected**

Maybe I shouldn't block my "empty board". What I meant: if the fetch comes back with nothing, that's an error, because it isn't reasonable. But if the fetch is fine and after comparing there are no new jobs, don't raise an error. No new jobs is also an answer: it tells the user there's nothing to act on. Does that solve Step 7?

**What happened**

The AI said GATE already works that way (empty list is error 201; 0 new on an `ok` board is a normal result), so it doesn't change anything, and on its own it doesn't create a finished-wrong run. But it said my split points at where one hides: because "0 new jobs" is a valid answer, nobody questions it. The Step 7 demo can be a run that says `finished, 0 new` while new postings were actually in the part of the list that got cut off. An outside check on the raw file catches it. It suggested adding my sentence to GATE so "0 new is not an error" is written down.

**My judgment calls**

- Accepted adding the sentence to GATE.
- Picked option A: GATE doesn't check `meta.total` yet. Step 7 shows that gap, Step 8 fixes it as the review-packet change.

**What's next**

Commit GATE.md, then Step 3.

### 2026-11-08: What adding offices to location would change

**What I tried and expected**

Option (a) sounds better. But what would it change? If JS1's results come out different, how do I change it the right way?

**What happened**

The AI recomputed the rule on the saved JS1 raw files, old location vs location plus offices. First it corrected itself: its earlier "almost every Cloudflare job gets cut at the location check" was wrong. 443 of 464 are cut earlier at the title checks, and only 21 reach the location check. Adding offices doesn't change Cloudflare at all, because its offices say "United States" and my profile matches "us". For Stripe it changes a lot: over all 745 postings in Run 2's raw file, 23 rule verdicts change and relevant goes from 5 to 20 (Stripe offices say "US"). The 20 verdicts I submitted in JS1 don't change. Against my 20 hand labels, the rule goes from 13 to 15 right (3 fixed, 1 newly wrong: the New Grad job, which is cut for experience, something the rule can't read). Its suggestion for doing it right: don't rewrite the JS1 runs, record a decision, note the change in CONTRACT, show a before/after table in the JS2 README, and add a test.

**My judgment calls**

- Went with (a). JS1's limits came from that assignment. The goal now is JS2, so if an old rule doesn't fit, change it. JS2 should run smoothly instead of being held back by what the old rules said.

**What's next**

Make the change.

### 2026-11-08: Does a new job system mean changing old code?

**What I tried and expected**

Is this a good design? If I add another application system, do I have to go back and change the old code again? Is there a better way? Discuss first, don't rush to change things.

**What happened**

The AI said no code changed. It split this round's edits into two kinds. One is a one-time cost: the first second system exposed assumptions JS1 had baked in (job ids are integers). The other was fixing Greenhouse's own incomplete mapping (offices), which would have been needed anyway. With the current design, a third system like Lever is a new adapter file, one registry line, board-list lines, and one allow-list line, which it says should stay a deliberate permission decision. It listed what could still leak and suggested one cheap improvement: a shared test every adapter must pass, using a saved sample response. It argued against a config-only generic adapter (the systems differ in logic, not just field names). It mentioned country codes as a sturdier fix for location matching, but said that's a bigger change for later.

**My judgment calls**

- Accepted the shared adapter test (A) into the plan.
- Accepted country codes (C) as a later item, not for JS2.

**What's next**

Step 3c, the shared adapter test.

### 2026-11-08: Permission policy in code, plus a map of the whole project

**What I tried and expected**

Next step. Before writing code the AI asked two things GATE didn't settle: what to do with a résumé path outside the allowed folders, and which existing files need my y/n before an overwrite. I asked what goes in data/ and personas/ and where a real résumé would go. Then I said OK to refusing for now (my_resume/ is for after JS2) and to option A. I also asked for one file that explains the whole project: which file does what and how they fit. I'm a bit lost and only want to check the big picture is right. I asked whether to write it once at the end or update it every step, and let the AI decide.

**What happened**

The AI explained that data/ is the agent's own settings and personas/ is the fake job seeker, and that a real résumé can't be used at all yet (JS1 contract). For the map it picked updating every step, because each update is small while the code is fresh, and writing it at the end means rereading everything after the session gets compacted. It wrote ARCHITECTURE.zh.md. For Step 4 it added one policy object that every network call and file read/write has to ask first: allowed hosts, allowed read/write folders, a y/n before overwriting a run's report or raw evidence, and refusal when there's no terminal. It wrote 30 boundary tests, one per row of my GATE table plus extras. It planted 17 bugs in a scratch copy and the tests caught all 17. A live fetch through the policy still worked, and striqe still gave 404. It also added a dated note to CONTRACT because the allow-list changed.
Trace: job_agent/common/policy.py, tests/test_policy.py, ARCHITECTURE.zh.md, DECISIONS D15 D16

**My judgment calls**

- Before committing I questioned the design: why build a policy every run, shouldn't the policy be fixed? The AI said the rules are fixed and only this run's values change (output folder, Claude on or off, who answers y/n, what I already said yes to). I kept the design.

**What's next**

Step 5, the loop.

### 2026-11-08: Design the loop before coding it

**What I tried and expected**

Done, step 5.

**What happened**

For Step 5 the AI didn't write code yet. It proposed a structure (a new loop/ folder with error codes, budgets, trace, exits, and the runner) and asked me to decide the error-code list, whether the command runs every board by default, and whether to split Step 5 into the loop first and the Claude switch second.

**My judgment calls**

- Accepted all three suggestions: the code list, every board by default, and splitting into 5a and 5b.
- Wanted a document that says what each error code means. It became ERROR_CODES.md, kept equal to the code table by a test.

**What's next**

Do 5a in this session.

### 2026-11-08: Rule misses as a known limit, pinned by a test

**What I tried and expected**

In 5b, Claude only got postings my rule called relevant. Before committing I questioned that: Claude can catch the rule's false positives but never its misses, so a posting my rule wrongly cuts is marked processed and sinks. The AI agreed and gave three fix options. Then: I think this is a known limit. Don't fix it now, but add it to the docs. It's also a real "ran fine but was wrong" case, so see if you can add it as a test. Put it in the plan so we can look at how to fix it later.

**What happened**

The AI added it to CONTRACT's known limits (dated) and to ARCHITECTURE.zh.md. It wrote tests/test_known_limits.py: a Seattle, WA posting is cut at check 2, Claude is never asked, the run ends `finished`, and the next run doesn't show it. The test asserts today's wrong outcome on purpose, so it will fail when someone fixes the limit. It put the three fix options in the plan under Later, with B (re-judge saved raw when the rule changes) as its pick, and recorded D19. No program behavior changed. 262 tests pass.
Trace: tests/test_known_limits.py, CONTRACT.md, DECISIONS D19

**My judgment calls**

- Kept it as is.

**What's next**

Step 6, the real run of all four boards.

### 2026-11-08: Should Claude judge every new posting? (discussion)

**What I tried and expected**

Now the Claude column is all `off`. Maybe it should still follow the teacher's requirement and run on every new posting. That's also why we limit the Claude budget: so it doesn't use too much. Don't change anything yet, let's discuss.

**What happened**

The AI checked the briefs. "Two verdicts for each new posting" is in the JS1 brief; the JS2 brief doesn't mention Claude, but it says to build on JS1, and 5b relaxed that JS1 rule with only a CONTRACT note. The AI pointed out that even with `--claude` this run would make 0 calls, because 0 postings were rule-relevant. It agreed the budget should be what limits Claude, not the rule filter, and that this also gets at the D19 problem (rule misses never reach Claude). It suggested keeping Claude off by default so a fresh clone runs without Claude, and when it's on, letting every new posting be eligible (rule-relevant first) up to the budget, with the rest marked "not sent: budget". That is a GATE §2 change, so it needs my written decision first. Nothing changed.

**My judgment calls**

- Accepted keeping Claude off by default. Modified the AI's selection idea: no "rule-relevant first", just every new job in order. Set my own numbers instead of the AI's 3 calls x 300 s.

**What's next**

Change GATE so every new job goes to Claude, with a 300 s total and 30 calls.

### 2026-11-08: Claude judges every new job, 30 calls and 300 s in total (D20)

**What I tried and expected**

Just change it. Edit the GATE for me. Don't wait until the rule is done judging to send things to Claude: new jobs go straight into Claude's budget. Make the total time 300 s, because 300 s should already cost a fair amount of tokens. Set the call limit to 30: if there are 30 new jobs, it runs 30 times.

**What happened**

The AI wrote D20 and changed GATE §2 first (480 s total with Claude: 120 boards + 300 Claude + 60 report), then the code. Where I didn't say, it made its own calls and flagged them for me: each call's timeout is whatever Claude time is left, so the last call can be cut short; boards still finish before Claude starts; any new job the budget never reached gets 304 ("not sent: budget") and the run ends `budget-exhausted`. Six tests that encoded the old "three rule-relevant" rule were rewritten. The D19 known-limit test now pins the limit with Claude off, and a new test shows that with Claude on the miss appears as a disagreement but still never comes back. Out of 12 planted bugs, the first pass missed 2, so it added tests. 266 tests pass. It pointed out that my Claude-off run already moved Stripe's state to today, so a `--claude` run now would have almost nothing new to send.
Trace: GATE.md §2, job_agent/loop/budget.py, job_agent/loop/claude_step.py, tests/test_claude_budget.py, DECISIONS D20

**My judgment calls**

- Accepted all three of the AI's own calls (timeout = Claude time left, boards first, unsent = 304 and `budget-exhausted`).

**What's next**

Question whether a job still needs to come back once it's already on the report.

### 2026-11-08: If it's on the report, isn't it handled?

**What I tried and expected**

One thing at a time. The AI says a job the rule cuts still goes into state, so even if Claude catches the mistake, it never comes back. But if it already shows up on the report, that should be enough. Whether the rule or Claude flags it, it counts as handled, so it goes into state. Showing up on the report means it was handled, so why keep the id out for the next run? And if disagreements stayed out of state, then once Claude's budget runs out, everything left counts as a disagreement, lots of ids get re-run, and a re-run still disagrees. So what's the point?

**What happened**

The AI agreed and took back its "only half fixed" framing. The report is where the agent hands a job to me. If Claude disagrees on the report, the job has been handled. Leaving it out of state would only re-send the same job to the same rule and the same Claude for more tokens and the same answer, and the 304 jobs would pile up every run. A re-judge only makes sense when the rule itself changes (plan Later B). What's actually left of D19: with Claude off, or for a job the budget never reached, nothing flags the miss. It's still on the report, but only as one `not_relevant` row among 86. Nothing changed yet. The AI offered to reword D19 in CONTRACT, ARCHITECTURE and the test docstring.

**My judgment calls**

- Agreed with the rewording. The AI dropped "never comes back" in CONTRACT, ARCHITECTURE and test_known_limits (names and docstrings only, assertions unchanged, 266 pass) and added my reasoning to D19.

**What's next**

Back to Step 6: pick how to do the `--claude` run.

### 2026-11-08: The run with Claude on (option A), 30 calls per run kept

**What I tried and expected**

Go with A: put Stripe's state back to 10/31 and run all four boards again with `--claude`.

**What happened**

The run ended `budget-exhausted` at 30 of 30 Claude calls, not the 300 s (about 4 s per call). Claude judged the first 30 of Stripe's 86 new postings and agreed with the rule on every one; the other 56 got 304. The AI recounted from raw with its own script and everything matched. It found the summary said `seconds 129.1/120`, which looked like a broken budget but was only the board-phase limit; it fixed that display.
Trace: runs/2026-11-08T234257Z/, job_agent/report.py

**My judgment calls**

- Wanted the seconds line fixed before committing.
- The AI pointed out both limits are per run, so Stripe, listed first, can use all 30 calls. Kept 30 calls per run anyway.
- Accepted the AI's D18 readings: a Claude failure is only that posting's error and is never retried; SDK retries off.

**What's next**

Step 7, the finished-wrong demo.

### 2026-11-09: What the agent does when the list disagrees with `meta.total` (Step 8)

**What I tried and expected**

Start Step 8, the review packet. Before any test, the AI asked me three things.

**What happened**

The AI asked: what to do when the job list and `meta.total` differ, what to do when there's no `meta.total`, and who writes the test, each with a recommended answer. It drafted `tests/test_meta_total.py` without touching `job_agent/`: 4 tests fail for the right reason, 3 guard tests already pass, one uses the real Step 7 file (680 jobs vs 766).
Trace: tests/test_meta_total.py, commit 3c4aa5a

**My judgment calls**

- Any mismatch, either way, fails that board with a new code 203. No `meta.total` means "can't check".
- The AI drafts the test; I read it, run it red, and commit it alone before the patch. The packet says who typed it.

**What's next**

Commit the red test, then let the AI write the patch.

### 2026-11-09: Claude's patch, my review: accept (Step 8)

**What I tried and expected**

After the red test was committed, let the AI write the patch. Then I read the diff and ran the tests and the Step 7 file through the patched agent myself.

**What happened**

The patch touched 5 files: Greenhouse's parser compares the list with `meta.total`, and the loop gives a mismatch code 203. All 7 tests went green (279 total). On the Step 7 file: Stripe `failed 203`, no counts, state untouched. The AI said the other odd bits I saw (`source: null`, the skill hint) are old behaviour outside this change. It wrote `REVIEW_PACKET.md` and dated notes in GATE, CONTRACT and the demo README.
Trace: commit ee3018e, REVIEW_PACKET.md

**My judgment calls**

- My reading of the diff: the agent checks `meta.total` if it exists; if the count is different it reports an error; if not, it's ignored, because not every ATS has it.
- Within scope. Accepted the patch as is, and left the old trace and hint issues alone.

**What's next**

Steps 9 and 10: README, sign-off, export.

### 2026-11-09: Sign-off for JS2 (Step 9)

**What I tried and expected**

Do Steps 9 and 10 in one go, and only stop where I have to step in.

**What happened**

The AI wrote the JS2 README (what I started from, toolchain, exact commands, the two real runs, where each part of the brief is, tests), rewrote SOURCES.md, and drafted the sign-off and the driver's seat with my quotes and commit ids. It dry-ran the export into a scratch folder: a fresh venv, 279 tests passed, an offline replay ran, the independent check still found the seeded mismatch, and the zip matched the folder. Then it asked me to decide the sign-off.
Trace: README.md, SOURCES.md

**My judgment calls**

- Accepted the sign-off as drafted: five Checked items, five Not checked (a list and its total both stale, Ashby has no total, retries only tested with fakes, a non-integer total, the hosts `claude -p` contacts), five Not claiming.
- Signed it: Hsuan-Hung (Isaac) Tai, 2026-11-09.

**What's next**

Export, push and submit on Canvas. After a review of the submission, fix three wording points (sign-off row, the commit-order check in the review packet, the demo's rerun note) and push again.

### 2026-11-22: Picking the final project, and what makes it different

**What I tried and expected**

The final project film brief came in. My October pitch was a sponsor lookup, but I can't answer "why would anybody care": there are already lots of job search tools online, so mine isn't different. I still want to build something I would really use. That is the core goal, not just a requirement. If it isn't different, I'd just use someone else's tool.

**What happened**

The AI read the Canvas final project page and checked existing tools. Free tools already do the sponsor lookup (USCIS hub, H1BGrader, Interstride, FrogHire, Jobright). It verified Jobright's weak points on Jobright's own pages: the "H1B Sponsor Likely" label is company history, not the posting, and no accuracy is published. Claims about stale listings and fake résumé skills only came from competitor blogs, so it marked them unverified. The AI suggested a "sponsor-first company watcher" (DOL records, then watch those companies' boards, then a Notion log). It also suggested `autonomous-agent-loop` as a different project.
Trace: AI_Task_Logs final-project-film/02-prior-work.md, DECISIONS.md D1 to D4

**My judgment calls**

- Rejected the sponsor-first watcher. Jobright already exists, so what would be the point of using mine? (Jobright also has a job tracker, so my Notion idea is covered too.)
- No time to try Jobright myself, so I asked a friend. Jobright's filter picks jobs by title, location and other options, not by my résumé, so I still read every JD. And it pushes adding missing skills to the résumé. Many skills aren't on my résumé because I can't do them, so even if that gets an interview, I probably won't get in. So filtering by whether my résumé fits the JD is the difference.
- The AI checked: Jobright does have a résumé match score, but no published formula. So the difference has to be "filter out with evidence, never pad, measure accuracy". Accepted.
- Rejected `autonomous-agent-loop`: I don't want to hand in its source code to the course repo, and it has no FRICTIONAL.md.

**What's next**

Use `job-search-agent` for the final project and remake the film in the 4-part format.

### 2026-11-23: Whole final project in one task, film remade in 4 parts

**What I tried and expected**

OK, use job-search-agent, and widen the task to the whole final project (Q7). The film needs updating too. The old pitch film has outdated info and probably doesn't follow the teacher's format, so it must follow the 4 parts: executive summary, introduction, methods, evaluation.

**What happened**

The AI widened the task log to the whole final project (system, packet, film) and added the job-search-agent repo to its project path. It listed what is outdated in the pitch film (project, 7-question order, ChatGPT-only comparison, "exists today", risk, one-line evaluation) and drafted a 4-part outline. Numbers for the pass/fail lines were left as X for me to choose.
Trace: AI_Task_Logs final-project-film/04-film-outline.md, DECISIONS.md D5

**My judgment calls**

- Kept the 4-part outline.
- Caught a gap: the executive summary doesn't say why anybody would care.

**What's next**

Rewrite the executive summary so it answers "why would anybody care".

### 2026-11-23: The executive summary has to say why anybody cares

**What I tried and expected**

The executive summary doesn't say why anybody would care.

**What happened**

The AI agreed: v1 only said it was my own pain. It looked up facts and checked each on the page: LinkedIn gets about 11,000 applications a minute, up 45% in a year; LinkedIn's CEO said it's "harder and harder for employers to know who can actually do the job"; on OPT you get 90 days of unemployment (DHS). It dropped one number it couldn't find on any page (73% of HR). It rewrote Part 1 in three layers: the application flood, padding makes it worse, and the F-1 clock. It also flagged that LinkedIn does something close (shows how well you qualify), so that has to go in Part 2.
Trace: AI_Task_Logs final-project-film/04-film-outline.md

**My judgment calls**

- Modified the AI's v2: kept the opening, the CEO quote, the padding line and the closing line. Cut the 11,000 applications a minute number and the OPT 90-day line.

**What's next**

Add more of the tool's strengths to the summary.

### 2026-11-23: A list waiting for me at 8 am

**What I tried and expected**

The summary could say more strengths. It could watch a few companies and run on its own. I thought other tools make you look yourself and don't match automatically, so that's a strength too. Every morning at 8 I'd get a list of today's job applications, then handle them one by one. No filtering, no reading JDs, nothing. The only thing I need to do is file the application. How about that?

**What happened**

The AI checked my premise first and it was wrong: LinkedIn has daily job alerts and "Top applicant" jobs, and Jobright has "Perfect Match Found" alerts matched to the résumé, so a daily matched list is not new. The AI kept the morning list as a feature but said the difference is still what's on the list (only jobs I meet, with JD line and résumé line, nothing padded). It wrote summary v3 with the morning list. It flagged three things: "no reading JDs" is only as true as the eval shows, and I still approve each item at the gate; a daily run needs the Mac awake and a bigger budget than 4 boards; I don't have a company list yet.
Trace: AI_Task_Logs final-project-film/02-prior-work.md, 04-film-outline.md, DECISIONS.md D6

**My judgment calls**

- Liked the v3 opening and kept it, including the AI's softer wording ("don't have to read the JD to decide").
- Modified one line: "Why does that matter?" became a question to the viewer ("why do you care?"), so it speaks to the person watching. The AI wrote it as "Why should you care?".

**What's next**

Write Part 2 (what others have done).

### 2026-11-23: Just cut everything under 80

**What I tried and expected**

The AI found that Jobright and LinkedIn already compare the résumé with the JD on paper. I think the difference is: Jobright gives you a match like 80, and I still see some lower-scored jobs, so I might still go look at why they're low. My tool would just delete everything under 80. Is that a real difference, or can Jobright already do that?

**What happened**

The AI searched and found no Jobright setting to hide jobs under a score, but it couldn't check inside the app. It pushed back on a plain score cut: it's easy for Jobright to add, anyone can ignore low scores by hand, and it would be a cut on someone else's black-box score. It suggested cutting by must-haves instead of an overall score: a job that misses one must-have is dropped even at 82 (one review shows 82 = experience 100, skill 69, industry 80), and each dropped job keeps a one-line reason, so I don't need to go look.
Trace: AI_Task_Logs final-project-film/02-prior-work.md

**My judgment calls**

- Accepted the AI's must-have cut instead of my score cut. If I build it myself, it can write the reason, so I know why a job was cut and don't have to open it.
- Accepted the new "why mine" line for Part 2.

**What's next**

Add two more differences to Part 2: company-first, and showing what decided each verdict.

### 2026-11-23: Start from companies, and show what decided it

**What I tried and expected**

Another big difference: it tracks companies. On Jobright you look for jobs, not companies. You often see a job, apply, and only then research the company. My tool decides which companies to follow first, then watches their jobs. Different starting point, different way of using it. And the tool tells you which parameters decided the verdict, so you don't have to guess what a score means.

**What happened**

The AI checked: no company-follow feature found for Jobright (search only, not in the app). LinkedIn does have job alerts for a company, so company-first alone isn't new against LinkedIn; the mix of chosen companies, must-have cut and written reasons is. Jobright shows a score breakdown (experience, skill, industry) but not the rule behind it. The AI rewrote the end of Part 2 with both points, added LinkedIn's company alerts to the "what exists" part, and closed the open issue about differentiation. It noted again that I don't have a company list yet.
Trace: AI_Task_Logs final-project-film/04-film-outline.md, DECISIONS.md D7 D8

**My judgment calls**

- Kept the "why mine" ending.
- Didn't like the opening paragraph of Part 2: not focused, a viewer would wonder why I'm telling them this. It needs a punchy opener like "What is already out there?", then straight to Jobright (scores against your résumé, rewrites your résumé), then LinkedIn.

**What's next**

Rewrite the opening of Part 2 that way.

### 2026-11-23: Count the missing required skills, cut at three

**What I tried and expected**

I didn't get the conflict the AI described at first. After its example, I changed the approach: count how many skills are missing. Missing three or more and it's cut; three is already a lot. Only count Required skills.

**What happened**

The AI had found that my JS1 labeling rule already does most of this (six checks in order, one-line reason each), but it passed skills at "2 to 3 known" and counted nice-to-have as must-have, which clashed with "one missing, cut". With a made-up example (Required Python, Go, Kubernetes; résumé has Python and Kubernetes) it showed the two rules give opposite answers. It asked two follow-ups (3+ or 4+, Required only or both). It updated Part 2 and Part 3 of the script to the new rule. It flagged that my 20 JS1 labels were made under the old rule, so the eval needs new labels, and that the rule file and `checks.py` in the repo are not changed yet.
Trace: AI_Task_Logs final-project-film/DECISIONS.md D9, 04-film-outline.md

**My judgment calls**

- Kept the rule and moved on to Part 3.

**What's next**

Fix Part 3 of the script.

### 2026-11-23: Methods should say how I build it, not how I use it

**What I tried and expected**

Cut the sentence about the base I built in the course (four job boards, budget, permission policy, 279 tests). The question is "how are you going to build it?", and the AI's steps read more like how I'll use it. Also cut "my real résumé never leaves my laptop", it's not important.

**What happened**

The AI rewrote Part 3 as seven build pieces in order: company list linked to job boards, a requirement reader (Claude pulls out required skills, location, visa line, salary, years, each with its sentence), the rules in plain code, a quote check, a morning run on a scheduler, the approval step, and a hand-labeled test set locked away before tuning. It flagged two of its own choices that I haven't decided: Claude reads the requirements while the rules stay in code, and the scheduler.
Trace: AI_Task_Logs final-project-film/04-film-outline.md

**My judgment calls**

- Rejected the format: this is a script for a film, a bullet list doesn't work.
- Five and six still describe how I use it. I didn't understand seven.
- Accepted the AI's idea that Claude pulls out the requirements and code decides with my rule.
- But in job-search-agent the teacher said to run it with code and with AI and compare the results. How does that fit?

**What's next**

Rewrite Part 3 as a spoken script, and work out how the code-vs-AI comparison fits.

### 2026-11-23: Keep the code-vs-AI comparison

**What I tried and expected**

I agree Claude pulls out the requirements and code decides. But I remember the teacher saying in job-search-agent to run it with code on one side and AI on the other, then compare. If we do it this way, how do we adjust?

**What happened**

The AI suggested two readers: a plain program (requirements section and skill words) and Claude (quotes the sentence for each requirement). Both go into the same rules in code. When they disagree, the job is flagged for me with both answers instead of decided silently, and the eval measures each reader against my labels. It rewrote Part 3 as spoken prose with that design, cut the usage parts, and moved the test set (old "seven") to Part 4.
Trace: AI_Task_Logs final-project-film/04-film-outline.md, DECISIONS.md D10

**My judgment calls**

- Questioned the two readers: what's the point of comparing? Some things AI is just better at, so shouldn't the two be combined? Why did the teacher split them?
- The AI checked the JS1 brief: the split was about telling a record (anyone can recompute it) from a judgment (label it as one), not about which is better. It then dropped its own two-reader idea.
- Accepted: let the AI analyze the JD, let code do what it's good at. Combining the two gives the better result. The code-only version becomes the baseline in the evaluation.
- Cut two lines from Part 3: the daily run and review step, and the data line.

**What's next**

Finish Part 3 and move on.

### 2026-11-24: JS3 FILTER.md, the AI drafts the reasons first

**What I tried and expected**

For FILTER.md, the AI can write down the reasons it thinks first. I'll read them and fix the wrong ones. That's faster.

**What happened**

The AI wrote FILTER.md v1 from the code at 3f72e7e, with no code change: the six checks plus the empty-posting rule, evidence rules, expected sources, and four wrong-version candidates (substring match, missing field = cut, rank by keyword count, years off by one). Each reason is tagged by where it came from: my CONTRACT, my LABELING_RULE, or the AI's own draft. It flagged that the skills check passes with 1 résumé word while my LABELING_RULE says two or three, and left that to be measured in the audit.
Trace: FILTER.md

**My judgment calls**

- Kept the draft and started reading it rule by rule.
- Asked about the location limit: can't I just list the cities in the profile? The AI said yes (`profile.locations`), and checked: since JS2 reads every listed place, only 1 of 54 engineering postings cut at location is really in the US (Stripe SDKs, `Toronto, NY, SEA, SF`). So the "Seattle, WA" limit in the draft was out of date.
- The AI first warned that abbreviations like "sea" could cause wrong matches. I asked if that's true. It measured and took it back: rule 2 only reads the location field, all 7 postings that flip are in the US, 0 non-US let in. Only real risk left is "SEA" meaning Southeast Asia on some future board.

**What's next**

Record the city names and abbreviations as a v2 candidate, and fix §1.3.

### 2026-11-24: City abbreviations as a FILTER v2 candidate

**What I tried and expected**

OK, record it as a v2 candidate, and correct §1.3 too.

**What happened**

The AI fixed the location line in FILTER.md §1.3 to the JS2 reality (54 cut at location, 53 outside the US, 1 miss) and added candidate L1 to §5: add ny / sea / sf / nyc / seattle / san francisco / new york to `profile.locations`, with the numbers and the Southeast Asia risk. Not applied: the profile is unchanged until the reject audit. It saved a script that recomputes the numbers.
Trace: FILTER.md §1.3 and §5, AI_Task_Logs job-search-agent-js3/v2_location_candidate.py

**My judgment calls**

- Kept it as is and moved on to §2.
- The AI's §2 draft had an "I cannot tell" case when the claim that decides the posting is insufficient. It asked me whether a JD that never mentions visa should become "I cannot tell".

**What's next**

Decide the abstention rule for missing information.

### 2026-11-24: Missing info passes and is labeled insufficient, not "I cannot tell"

**What I tried and expected**

Keep the current rule: not written counts as a pass. Just label the claim insufficient.

**What happened**

The AI dropped the abstention case for an insufficient deciding claim from FILTER.md §2. "I cannot tell" now only covers no text to judge (empty JD, or no saved raw file to quote). Missing years / visa / salary passes as in v1, and the shortlist shows those claims as insufficient next to the verdict.
Trace: FILTER.md §2

**My judgment calls**

- Kept it and read §3 and §4.

**What's next**

Pick the wrong versions.

### 2026-11-24: W1 and W2 as the wrong versions

**What I tried and expected**

W1 and W2 are enough. Also, does section 3 even need to exist? Does the brief say FILTER.md has to have it?

**What happened**

The AI quoted the brief: Step 1 asks for "the expected sources", so §3 stays. Before I picked, it measured W1 on the 2,046 saved postings: substring matching would turn 937 rule-3 cuts into passes ("AWS" inside "laws", "Rust" inside "trusted", "Java" inside "JavaScript"). It rewrote §4 with W1 and W2 and listed W3 and W4 as considered but not chosen. It wrote one test file for each: both pass on v1 (full suite 292 passed), and fail when the code is patched in memory into W1 (3 failed) or W2 (5 failed). The numbers come from a new script, reports/filter_v1_measure.py. Not committed yet.
Trace: FILTER.md §4, tests/test_js3_wrong_w1_substring.py, tests/test_js3_wrong_w2_missing_field.py, evidence/js3/f1_wrong_versions_red.txt, reports/filter_v1_measure/result.md

**My judgment calls**

- Accepted §3 staying, since the brief asks for it.
- Read the rest of FILTER.md and signed it off as mine.

**What's next**

Sign off FILTER.md and hand the build to agent-loop.

### 2026-11-24: Sign off FILTER.md, build the rest with agent-loop, my tasks later

**What I tried and expected**

OK, I've read it all, I can sign off. Use agent-loop for the rest: do everything that can be done first, and leave the things I have to do for later, all at once.

**What happened**

The AI marked FILTER.md as signed off by me and committed it with the W1/W2 tests and the measuring script (d876d64, merged 6de8e12), before any JS3 build code. It wrote one agent-loop batch with three parts: run the filter on every saved posting and build the hand-judging sheet (30 random rejects, close calls, kept, verdicts hidden), a shortlist builder that turns each kept posting's reasons into claims with a code-proposed label and quote, and the MCP server from scratch. While checking the MCP spec it found that the current version (2026-07-28) dropped the initialize handshake; the brief asks for initialize, so the server speaks the older 2025-06-18 handshake. It put everything only I can do in one list, ISAAC_TODO.md.
Trace: commit d876d64, AI_Task_Logs job-search-agent-js3/ISAAC_TODO.md

**My judgment calls**

- Approved the agent-loop tests. I asked where the résumé went when the test summary said it wasn't checked: the AI had left it out of the drafter's context. The tests still read the real résumé, so I kept the draft as it was.
- The AI found a bug when it ran the new code on real data ("Node.js" cut in two by the sentence split). It said its own spec caused it, not the agent. It suggested merging first and fixing after. I accepted and merged.
- Hand-judged all 50 samples myself with my LABELING_RULE.md.

**What's next**

Pick the false friend and measure the v2 rule candidates.

### 2026-11-25: S20 as the false friend, measure A, B and C

**What I tried and expected**

S20 is the false friend. Measure A, B and C. Commit for me.

**What happened**

My 50 labels: 1 of 30 random rejects disagreed with the filter, and 3 of 10 close calls and 4 of 10 kept. 7 of the 8 disagreements were the filter keeping postings I wouldn't apply to. The AI suggested S20 ("0-1 years of experience"): the rule reads it as "min 0 years, pass", but it means Aarav is too experienced. It measured the three candidates on all 2,123 postings and my labels. A (experience ceiling) cut 3 and fixed S01 and S20 without breaking any. B, read only "(6) years", changed nothing because the rule still takes the smallest number. B with the largest number cut 8 and fixed S16. C (at least 2 skills) cut 22 and fixed 4, but broke 5 that I had labeled relevant. I count by meaning ("CI/CD" for Jenkins, "containers" for Docker) and the code counts words. The AI noted that the S50 reason I wrote says Python, but that JD has no "Python". It warned that the candidates came from these same samples, so "fixed" is not an independent test.
Trace: reports/filter_v2_measure.py, reports/filter_v2_measure/result.md, audit/AUDIT.md

**My judgment calls**

- Kept S20 as the false friend.
- Accepted A (experience ceiling): it fixed 2 and broke nothing.
- Rejected C (at least 2 skills): it broke 5 of my relevant labels, because the code counts words and I count meaning.
- Left B2 open until I see the 7 postings it would cut that I never labeled.

**What's next**

Look at the 7 B2 postings, then decide B2.

### 2026-11-25: Adopt A, reject C, show me B2's 7

**What I tried and expected**

Adopt A, don't adopt C, show me those 7 B2 postings.

**What happened**

The AI pulled the years sentences from the 7 postings and checked Aarav's résumé (MS from Northeastern, 2 years of work). In 5 the largest number really is the requirement ("Minimum requirements 5+ years", "8+ years of industry experience"). One JD (Intelligence & Investigations) says both "7+ years" and "4+ years" in different sections. In one (High Availability and Disaster Recovery) the 5 years is the Bachelor's path, and the Master's path needs 3 years. Aarav has an MS, so taking the largest number cuts a job he fits.
Trace: reports/filter_v2_measure/result.md

**My judgment calls**

- Didn't pick one of the three B2 options. I came up with my own idea instead: I'd apply when my years aren't too far off, for example 6 years for a 10-year job, or 5 for 8+. I asked whether to cut when the gap is 3 years or more.

**What's next**

Work out the years threshold with the AI.

### 2026-11-25: Judge years by ratio, the way I actually decide

**What I tried and expected**

Cut when Aarav's years are 3 or more below the minimum requirement (2 years: cut at 5, keep at 4)? Then I said yes, I mainly look at the ratio, and it's subjective. If everything else fits I'd still apply with fewer years. 5+ years feels about the same as 8 or 9, but 10+ is a real gap, and there I might give up. I asked what the best design would be.

**What happened**

The AI showed that a 3-year gap is the same line as today's rule for Aarav (2 + 2 = 4), and that it would cut both of my examples (6 for 10, 5 for 8). It guessed that I think in ratios, and checked that "at least half" fits all four of my examples. Only an exact half is a gray zone: 2 of 4 I keep, 5 of 10 I might skip. "Other things make up for fewer years" can't be done by a filter that cuts one rule at a time. It proposed: at least half, plus A, plus B2, and leave the degree-alternative case as a known limit. When I asked whether this keeps more postings, the AI re-judged all 2,123 to check. It keeps fewer (70 → 59) but disagrees with me less (8 → 5), and the ratio alone changes nothing for Aarav.
Trace: scratchpad ratio_measure.txt

**My judgment calls**

- Accepted the proposal: at least half, plus A, plus B2.
- Asked to measure L1 too.

**What's next**

Build v2 and measure L1.

### 2026-11-25: Go with the proposal, measure L1

**What I tried and expected**

OK, go with the proposal, and measure L1 too.

**What happened**

The AI built rule 4 v2 (ceiling cut and largest number, "(6) years" read), with tests that fail on v1 and pass on v2. It re-ran all 2,123 postings: 59 relevant, 5 disagreements with my labels, none new. It kept the v1 run in audit/v1 because my audit judged v1. L1 changed 0 verdicts under v2: the one posting it rescues at rule 2 asks for 6 years and is cut at rule 4. The AI did not rename years_stretch to a ratio field. It found that the field is also in CONTRACT.md and the Claude judge prompt, so renaming would change the scorer F5 has to measure. For Aarav the result is the same either way. It wrote my ratio reasoning into FILTER.md's rule 4 instead, and is asking me.
Trace: commits 14a0b41, a0d024d (merged 095fba1), FILTER.md §5, reports/filter_v2_measure/result.md

**My judgment calls**

- Agreed to hold off on renaming the field, but not to keep the old prompt forever. I pushed back: JS1's results can just be re-run, and if the new way is better there's no reason to keep the old one. I moved the rename into F5, as a measured change.

**What's next**

Do F5, with the ratio change as one of its experiments.

### 2026-11-25: F5 on fresh held-out labels, ratio prompt as a measured change

**What I tried and expected**

Hold the rename until F5, change it there, and finish F5 too. For the held-out set I picked fresh labels only (20 new postings), not JS1's 10. Midway I didn't get why there was so much extra work just to build a job search agent, and asked the AI to explain what I've been doing since JS1. Then I labeled the 20 and said run E2.

**What happened**

The AI drew 20 postings that reach the JD checks and committed the sample before I labeled it. It explained the course point: each assignment asks whether the AI's decisions can be trusted and checked, and the job agent is just the subject. After my labels it fixed prompt v3 (only the years line, as "at least half") before any run. E1, rule v1 to v2, went from 12 to 13 of 20, but the AI found its own mistake: the one posting that changed (H11) was one of the 7 B2 postings I had already seen, so on unseen postings v2 moved nothing. E2, prompt v2 to v3, gave 13 and 13, with the same verdict on all 20. So v3 isn't better, and by my own rule the old prompt and field stay. My held-out labels turned up a new false friend: rule 5 cuts all 8 of its postings on Cloudflare's "without sponsorship for an export license" sentence, which is about export law, not visas. The rule and Claude both scored 13/20 but made opposite mistakes.
Trace: commits de5824c, 66d2c73, a1eb594 (merged 04b7184), reports/what_moves_the_score.md

**My judgment calls**

- Pushed back on "v3 isn't better": I thought the ratio should be better, and asked if the sample was too small. The AI said it isn't the sample. Claude under v2 already read "5+ years, including 3+" as 5, and for 2 years the ratio and 2 + 2 draw the same line. Only 3 new-grad postings in all the data could differ.
- Chose to adopt v3 for consistency with the rule, not for its score, and without another run.

**What's next**

Adopt v3, fix the rule-5 false friend, sign off v2.

### 2026-11-25: Adopt v3 for consistency, replace the rule-5 phrase, sign off v2

**What I tried and expected**

Adopt v3 for consistency, no extra run. Rule 5: drop "without sponsorship" and use a better phrase. Switch the agent's default prompt (is there a v3 now?). L1 OK as rejected. I sign off FILTER.md v2.

**What happened**

The AI set the agent's default prompt to v3 (it had still been v1 since JS1). It first replaced the phrase with "without visa sponsorship", but an old JS1 test failed. CONTRACT posting B says "authorized to work without sponsorship", a real refusal with no "visa" in it. So it used two phrases: "work without sponsorship" and "without visa sponsorship". None of the 2,123 JDs actually refuses a visa. All 8 old cuts were the export-license sentence, so 8 Cloudflare postings are now kept (59 → 67). The held-out score went down, 13 to 12: H01 is fixed, but H06 and H16 had been cut right by accident. The AI wrote that the rule's reason is now true but its score is lower, and that the held-out number is no longer unseen because H01 was read to find this. FILTER.md is v2.1, marked signed off for v2.
Trace: commits 4a62b61, 7cedca6 (merged 31df8f1), FILTER.md §5 v2.1

**My judgment calls**

- Kept the result as is, including the lower held-out score.

**What's next**

F3: pick the relevance vs entailment example.

### 2026-11-25: Privy's AWS as the relevance vs entailment case

**What I tried and expected**

I pick AWS. It isn't listed as a requirement, but knowing the skills the company uses is still a good plus.

**What happened**

The AI split my answer in two. Does the sentence support "the JD asks for AWS"? No, it says the company uses AWS, so the label is insufficient (FILTER §2 already says the company intro doesn't count). Is it relevant to Aarav's fit? Yes, as my plus. It recorded that in shortlist/review.csv, apart from the generated file so a re-run can't erase it. It noted that AWS was this posting's only rule-3 skill, so the posting reached the shortlist on a sentence that asks nothing of Aarav. For the abstention counterexample it used S16: under v1, "insufficient" for years meant the reader couldn't see "six (6) years", not that the JD was silent.
Trace: commit 30b4054, shortlist/REVIEW.md, shortlist/review.csv

**My judgment calls**

- Kept the review as written.

**What's next**

F4: connect Claude Code to the server and pick the other server to evaluate.

### 2026-11-25: Real Claude Code session, and fetch as the other server

**What I tried and expected**

I registered the server with the command the AI checked against --help, ran a Claude Code session that scored Privy and tried board "../../etc", and chose the official fetch server for the second evaluation (the AI suggested fetch or filesystem).

**What happened**

The transcript has 11 messages both ways. Claude Code first tried the new 2026-07-28 handshake (server/discover). Our server said method not found, and the client fell back to the old initialize, so the risk flagged in planning didn't block anything. Claude Code sent the "../../etc" call without stopping it, and our server refused it (-32602). The AI read fetch's source at a pinned commit (it did not run it). Its tool says read-only, but it reaches any public host by default. Its description tells the model to set aside its earlier advice not to go online. The AI drafted both evaluations and left the two trust decisions blank for me. It replaced my username in the saved mcp add output before committing.
Trace: commit ba4bcea, MCP_EVAL.md, transcripts/mcp-2026-11-25.jsonl

**My judgment calls**

- I didn't follow the first explanation, and asked for it in Chinese and whether I had to run tests on fetch. The AI showed the brief only asks to evaluate a named server the same way, not to run it.
- Trusted our server as is (option a).
- Don't connect fetch (option a, the AI's suggestion). My agent may only reach the boards on its allow-list, and fetch reaches any site.

**What's next**

F6: sign-off, README, submission.


### 2026-11-25: Sign-off for JS3 (F6)

**What I tried and expected**

Do F6, then check whether everything meets the Assignment 3 requirements. After reading the summary of the drafted sign-off: sign it for me, then commit.

**What happened**

The AI wrote the JS3 README (started from, toolchain, commands, what ran, where each part is), SOURCES, a sign-off draft with 5 "Not checked" and 5 "Not claiming" items, and the driver's seat table. It ran the commands from a clean copy: 326 passed and the report scripts rewrote the same files, except E1, which now compares v1 with v2.1. Its honesty pass found one false claim in MCP_EVAL: the "no network" test it cited was agent-loop's acceptance test, not a test in this repo. It corrected that. It also found that the "../../etc" call at the start of the session was refused by our server, not by Claude Code. A re-run and a health check had changed two committed files, and I restored them with git. The AI added my signature.
Trace: commits dcb3638, cb079e8, README.md "Sign-off — Job-Search Agent 3"

**My judgment calls**

**What's next**
