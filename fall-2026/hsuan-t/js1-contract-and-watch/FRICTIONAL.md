# Friction Log: job-search-agent

Scope: `job-search-agent`

### 2026-10-28: Reading the JS1 brief (retrospective, written 2026-10-29)

**What I tried and expected**

Read `_brief` and tell me what this week's assignment is about. Then I asked follow-ups because I didn't get parts of it: is "the watch" just keeping state of what I've already checked so the next run doesn't judge it again? What are the three reports? I didn't get the prompt experiment at all.

**What happened**

The AI summarized the brief as five steps (contract, watch, two judges, three reports, sign-off) and explained each with small tables. For the prompt experiment it walked through one fake example (6/10 on dev, 8/10 after the revision, 7/10 for both on held-out).

**My judgment calls**

- My first read of the prompt experiment was wrong: I thought I could keep revising until I was happy. The AI corrected me: only one revision, one change, and both prompts run on held-out. I accepted that.
- I pushed back that one revision seems too limited. The AI's answer: the point is learning how to tell whether a change helped, not getting a high score. I accepted it.
- Restated the whole flow in my own words to check I had it.

**What's next**

Pick the board and the persona, and set up a task log before planning.

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

- Let the AI run the live check this time (I had stopped the curl earlier).
- Accepted Python.

**What's next**

Write CONTRACT.md myself, with some guidance on what goes in each part.

### 2026-10-29: Board check and what goes in CONTRACT.md

**What I tried and expected**

Go ahead with the curl check on 5 companies. Use Python. I created an empty CONTRACT.md: give me some guidance so I know what to write.

**What happened**

The AI checked 5 Greenhouse boards live. Stripe and Databricks each had about 28 postings first published in the last day; Discord had 1 in a week, so it's a bad pick for showing a real change between runs. It pointed out the list endpoint has title and location but no job description unless you ask for it, which matters for a rule a TA can check by hand.

**My judgment calls**

- Asked why I should pick the persona before writing the rule.

**What's next**

Question the AI's advice: the tool is supposed to work for anyone, so a rule tailored to one persona would be useless.

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
- Asked whether the state file counts as input. The AI said it is both: read at the start (In), written at the end (Out).

**What's next**

Get today's raw data saved so tomorrow's run is a real second day, even if the contract isn't done.

### 2026-10-29: First CONTRACT draft and the 10/29 snapshot

**What I tried and expected**

I wrote some of the contract, take a look. Save both the plain and the full version of the board data, I want to see the full one and it might be useful later.

**What happened**

The AI first stopped to ask about order: the brief says the failure sentence comes before running anything. My draft already had a failure section, so the AI noted the file time and then fetched Stripe: 737 postings, a small list file and a 5.7 MB file with full job descriptions. It wrote down the URLs, hashes and the time. Then it reviewed my draft and listed gaps without rewriting it. The biggest one: my rule only uses the profile (title and location), but the brief wants the justification to name résumé fields too. Also my field names don't match between In, Out and the rule.
Trace: evidence/raw/2026-10-30T033237Z/README.md

**My judgment calls**

- Didn't push back on the review. Asked what Wrong versions means, then what makes the rule complete and whether it has to read the JD.
- The AI ran my own data to answer: of 18 "backend" Stripe postings, some JDs mention 3 of Aarav's skills and some mention 0, and locations are written many different ways ("US-Remote", "SEA, SF, NY").

**What's next**

Work out how title matching should work.

### 2026-10-30: How to match titles

**What I tried and expected**

My idea: lowercase everything, split titles into words (also split on "/" and other symbols, so "Backend/API Engineer" becomes backend, api, engineer), and call it a match if at least one word matches something in profile.target_roles. I want this so a company writing a longer title like "software dev of some kind" doesn't get marked not_relevant. I know it can misfire: if I write "Backend", then "Backend Quant Engineer" matches, and that's not something I can apply to. I'll accept that for the first version since I don't know a better way. Or is it better to treat each phrase as one item?

**What happened**

The AI kept my normalization but pushed back on "any one word matches", and tested it on the saved Stripe titles with sample targets from Aarav's profile. Any word: 163 of 737 match, including "Designer, Web Presence & Platform" and "Staff Security Engineer", because "engineer" or "platform" alone is enough. All words of one target phrase, in any order: 92. That plus a list of excluded words (senior, staff, quant, manager…): 62. The AI suggested the last one, with the excluded words living in the profile.

**My judgment calls**

- Accepted matching per target phrase instead of any one word. Had to ask twice how it works; it clicked with my own example: "market software engineer" still matches "software engineer" because both of its words are there.
- Haven't said yes or no to the excluded-words list yet.
- Asked the AI how to put the rule into words, then asked whether that explains how I judge, since it only listed steps.

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
- Didn't understand what "don't show a real résumé" means in Refuses.

**What's next**

### 2026-10-30: Running my rule on real data

**What I tried and expected**

Unify all the field names (profile.locations[], resume.<...>), put the status / summary output in the contract, use word splitting for location too, strip HTML before the skills check. Run my rule on real postings so I can see what comes out.

**What happened**

The AI ran my rule on the saved 10/29 Stripe data with a sample profile for Aarav Result: only 3 of 737 postings come out relevant. Location cuts the most among postings that pass the title check (56), because many say just "US" with no remote. The AI pointed out Greenhouse has no field for my job_types / job_style. For my "what else am I missing" note, it listed options: years required, visa, salary.
Trace: CONTRACT.md

**My judgment calls**

- Asked whether the profile should also have work mode (on-site / remote / hybrid). The AI checked: no field for it, remote only shows up in location.name (115 of 737), hybrid in 24 JDs. It suggested keeping remote in locations and leaving hybrid to the Claude judge.
- Asked why only one company. The AI: the brief says one board, and on Greenhouse one board is one company. The board name is an input, so more can be added later.
- Learned that hand-labeling 20 means picking 20, not reading all 737.
- Worried the skills check (search the cleaned JD for résumé keywords) misjudges a lot.

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
- Asked whether AI could do the skills check instead. Learned the brief wants two verdicts for each posting: my rule (anyone can recompute it) and Claude's. Claude can compare skills too, but it can't replace the rule, and the rule has to use some résumé field.
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

- Asked for a Chinese translation of the English "why" paragraph for the title check so I could check it. After recounting, it's "any single word of my targets" that let 163 through, not "engineer" alone.
- Said the work-mode limit was too detailed and didn't sound like me. Cut it down to: the Job Board API doesn't give this field, only some JDs mention it, so it isn't checked.
- Asked why Examples is a table instead of three examples. The brief doesn't set a number; each row is one example.
- Asked what "label" means in wrong version 1: it is the verdict given to each posting.
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

- Asked whether quote is a top-level field or inside each justification line: inside each line.
- Said OK, put it in the contract.

**What's next**

Still open: the PLAN draft, saving a 10/30 snapshot tonight, and which model the Claude judge uses.

### 2026-10-30: First commit, contract only

**What I tried and expected**

Asked what the driver's seat and the transcript are, and how a TA would know who did what if the transcript isn't handed in. Then: have I committed yet, should I commit first, and what goes in it.

**What happened**

The AI explained the driver's seat is a table of what Claude does, what I do, and why my part stays mine, with evidence. The evidence can be an edit, not only the transcript, so git commits are the strongest proof. The folder wasn't a git repo; I ran git init. The AI wrote a .gitignore (brief, real résumé, *.pdf, .env, caches), dry-ran `git add` to list exactly what would go in, and gave the commit message. It warned not to put the session transcript file in the repo, because it holds my real résumé text.

**My judgment calls**

- Left evidence/ out of the first commit. Committed .gitignore, CONTRACT.md and Frictional.md as a0d895e, before any code exists.
- Asked whether to write PLAN.md here or in a new session.

**What's next**

New session: approve the PLAN draft, then start step 1.

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

### 2026-10-31: Step 1, Aarav's files

**What I tried and expected**

Step 0b is done, start the next step.

**What happened**

The AI checked my commit, then wrote Aarav's résumé in JSON Resume format (converted from the repo example, same 17 skills as my contract), his profile with the demo values from my contract's Examples, the built-in skill spelling table (10 entries) and the 13 "no sponsorship" phrases. JSON can't hold comments, so it put a short README in each folder saying why the files exist. It checked every file parses, and left the step open until I review it.
Trace: personas/, data/

**My judgment calls**

- Only wanted to know whether the résumé follows the open JSON Resume standard. The AI validated it against the official schema: 0 errors.
- From now on, after each finished step the AI has to ask me to commit, with the files to add and a commit message in my git-commit format.
- The persona README says the code refuses any email that isn't @example.com. Asked whether real users would have to fake their email too. It's a rule for this assignment stage only; a real tool later needs a different guard (noted for the résumé converter idea).

**What's next**

Commit Step 1, then Step 2: the watch.

### 2026-10-31: Fetch only the new postings' JDs?

**What I tried and expected**

After the AI explained Step 2 in Chinese, I noticed the 10/29 raw data was fetched by the AI with curl, not by the agent. My idea for the tool: fetch the plain list first, find the new ids, and only then fetch the full content for those. Wouldn't that save download? Or is it not needed now and better kept as a proposal for later? Also: does the agent need to keep the whole raw JSON, or only the ids, since old postings' other info isn't needed?

**What happened**

The AI measured it: the plain list is 0.46 MB and the full one 5.7 MB, so with 20 new postings the two-step fetch would be about 0.6 MB, but 21 requests instead of 1, and the contract's raw file path would change. On keeping data: the brief requires the raw responses of both runs, a TA needs the JD text to recompute a verdict, and my hand labels read old postings, so the full raw stays. The state file is already the "ids only" store. Recorded the two-step fetch as proposal P3.

**My judgment calls**

- Before committing Step 2, asked whether every step's feature branch has to be merged back to main first, or we'd end up with lots of branches. Then asked how a fast-forward merge is any different from committing on main. The AI admitted the end result is the same history; a branch only helps to throw away half-done work or for PR review. Chose to commit directly on main.

**What's next**

Step 3 on main: my rule's six checks.

### 2026-10-31: Step 3, my rule in code

**What I tried and expected**

OK, keep it simple: do Step 3 directly on main.

**What happened**

The AI wrote the six checks with one shared word-splitting function, then ran them on all 737 postings from 10/29 before anything else: the counts at each check and the 3 relevant postings came out exactly as in my contract's Examples. A full trial run (outside the repo) found a real bug: two runs in the same second crash on the folder name, so it now refuses up front. It also moved the state update to the very end, after verdicts are saved. Preview of Run 2: 20 new postings, and my rule finds 0 relevant (sales, interns, managers).
Trace: job_agent/rule.py, job_agent/words.py

**My judgment calls**

- Asked what the AI's "tests" actually were. Learned that matching my contract's numbers only proves the code does what my rule says, not that my rule judges well; and both were written by Claude, so it isn't a fully independent check. My own hand calculation and hand labels are the real checks.
- Questioned why it judged all 737 when we agreed to judge only new postings. That was a one-off check against my contract's numbers; a real run only judges new ones (0 in Run 1, 20 in Run 2). The "only a few" limit is for Claude, which costs money.
- Asked whether I now have to check those 3 relevant postings. Not yet: hand-calculate one before sign-off, and hand-label in Step 7 without looking at the rule's answer.

**What's next**

Set a code standard before committing Step 3.

### 2026-10-31: Code has to follow a company standard

**What I tried and expected**

When writing code, follow company standards: reuse what can be reused, no tight coupling so later changes aren't painful; clear logic that's easy to read and extend; don't put everything in one file unless really needed. Good architecture overall.

**What happened**

The AI reviewed its own Step 3 code against that and listed the problems: one long function with all six checks, Greenhouse parsing and the allow-list inside the watch, check names written twice, the command line and the run mixed together. It split the code into small modules (network, board adapter, state, one function per check, one shared verdict shape for both judges, a pipeline the tests can call), then re-ran everything: same numbers as before.

**My judgment calls**

- Noticed the files were all still in one level, no folders. The AI grouped them into common/, watch/ and judges/, and moved the shared posting shape into common/ so the judges don't depend on the watch. Same results after the move.

**What's next**

Commit Step 3, then Step 4 (tests) in a new session.

### 2026-10-31: A real diagram, and the study note

**What I tried and expected**

Asked what checks.py is for: is it for testing, doesn't Python have its own tests? And what rule.py and verdict.py do. I wanted a clear explanation of the judges folder with a picture, and I meant a real drawn diagram, not text. Also, I remember asking for a study note and it hasn't been written. It must not be committed.

**What happened**

checks.py is not a test: "check" means my six rule checks; pytest tests come in Step 4 under tests/. The AI drew an interactive page that walks one real posting through the four files (words = scissors, checks = exam questions, rule = proctor, verdict = report card), with a switch between a posting that passes and one cut at check 4. It found no record of my study-note request in this task, so it wrote study_note.md now with my questions from today, in the format from my system design playbook, and added it to .gitignore.

**My judgment calls**

- Kept the diagram and the study note as they were and moved on. Committed Step 3 (58a93ee).

**What's next**

Start Step 4 (tests) in a new session.

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

### 2026-10-31: Step 5 in the same session, and who holds the API key

**What I tried and expected**

I think I can keep going in this session since I just started. For the Claude judge, do I have to give you the API key, or do I run it myself? I didn't really get it.

**What happened**

The AI said: don't paste the key in the chat. I save it once in a file outside the repo that only I can read; the AI's commands read it from there for the small capped test calls, and I run the real Run 1 and Run 2 myself. While I set that up, the AI wrote the Claude judge without needing the key: the SDK call in its own file, the validator as the 8 rows of my contract table, a first prompt file, and tests that use a fake Claude (a test can never call the real API, even if I have a key exported). 87 tests passed in its scratch run, and it planted 11 more bugs (one per validator row and a few in the judge); all caught. A no-key smoke run worked: the rule judged all 20 new postings, and Claude recorded errors that say why.
Trace: job_agent/judges/claude.py, validator.py, claude_api.py, prompts/claude_judge.v1.md, tests/test_claude_validator.py, tests/test_claude_judge.py

**My judgment calls**

- Didn't fully get it, so I asked for the architecture in Chinese with mermaid diagrams in my study note. Then I asked whether the validator is the same as the rule's checks. It isn't: the contract has two tables. The rule's 6 checks judge the posting; the validator's 8 rows only check Claude's answer (format and that the quote really exists).
- Wrote back my own summary (rule outputs JSON, Claude reads the same data and outputs JSON, validator checks it, bad format = error). The AI said that's right, and added that errors are kept (verdicts.json + raw reply), just not counted as relevant, and never retried.

**What's next**

Created the key file and installed the SDK in .venv, then asked the AI to check again and make the real call.

### 2026-10-31: First real Claude call: no credits

**What I tried and expected**

Done with what you asked (key file, SDK), check again.

**What happened**

The key file and SDK were in place. The AI ran the agent once for real (seeded baseline, then live, test cap 2), writing only to its scratch folder. Both Claude calls came back HTTP 400: "Your credit balance is too low." The key itself was accepted. The run still finished: rule verdicts for all 20 new postings, Claude marked as error for each with the API's message, raw replies saved. So the "Claude fails, rule still counts" path worked for real, but Claude hasn't judged anything yet.

**My judgment calls**

- Didn't know what "no credit" meant or whether I had to prepay. My school login only has an Individual Org in the Console, no school org, so there are no API credits.
- Asked if the assignment really needs an API key, or if Claude can run it another way. The AI checked the brief: it never mentions the API, only a prompt contract, a fixed format, a validator and fresh conversations. The AI tested `claude -p` (my Claude Code subscription, tools off) and it worked. The AI rejected having itself judge in this chat (not fresh, already saw the rule's answers, a TA can't rerun it). Accepted.
- Asked whether option B means "AI runs my code". No: Python runs everything, Claude only answers one question per posting, same as with the API.

**What's next**

Go with the CLI, because most people buy the desktop subscription, not the API, so it's more practical.

### 2026-10-31: Claude judge through the Claude Code subscription

**What I tried and expected**

OK, use the CLI way. Most people buy the desktop subscription now, not the API, so this is more practical.

**What happened**

The AI added one file that calls `claude -p` with tools off, no saved session, no settings, a fresh empty folder per call, and the API key removed from its environment (so it uses my subscription, not credits). The judge, validator and prompt didn't change; the API way stays as an option (`--claude-via api`). It checked my CLAUDE.md and memory don't leak into the judge. 96 tests pass, and removing any of the safety flags makes a test fail. Then a real run with the test cap: both Claude answers passed all 8 validator rows, both not_relevant, same as the rule. The AI flagged a trade-off: our program can't check the host of Claude Code's own requests anymore, so CONTRACT In and Refuses #1 need a dated edit.
Trace: job_agent/judges/claude_cli.py, tests/test_claude_cli.py

**My judgment calls**

- Told the AI to just make the CONTRACT edits itself, without date stamps.
- Worried my CLAUDE.md could change the results, since I have files that Claude always follows when it runs.

**What's next**

Check whether my CLAUDE.md affects the judge, and apply the CONTRACT edits.

### 2026-10-31: Does my CLAUDE.md leak into the judge?

**What I tried and expected**

Just edit the contract for me, no need to mark the time. And does my CLAUDE.md affect the results? I have some files that Claude always follows when it runs. (Also asked if I forgot to commit Step 4.)

**What happened**

The AI measured it instead of asking Claude: the same question with the judge's flags sent 608 input tokens and Claude answered NONE; with normal Claude Code settings it sent 2,819 and quoted the first line of my AGENTS.md. So without `--setting-sources ""` my instructions would leak in; with it they don't. It also checked that no MCP connector tools load, and added `--strict-mcp-config` anyway as a safeguard. My hooks only update the iTerm2 status. It applied the CONTRACT edits (Claude row, Refuses #1 limit, Out item 4, two validator examples). Step 4 was already committed (fcc0376), so nothing was missing.
Trace: CONTRACT.md, job_agent/judges/claude_cli.py

**My judgment calls**

- Kept the CONTRACT edits. Ran the tests myself: 96 passed. Asked why there are so many: 56 functions, and the validator alone has 15 rejected examples from my contract table; the Claude side has more ways to fail because its answer is text we don't control.
- Committed Step 5 (9be8f1c).

**What's next**

Asked what's next, in Chinese.

### 2026-10-31: Removing the 2-posting test cap before the real runs

**What I tried and expected**

OK, remove the limit of 2. Then let's run.

**What happened**

The AI first pointed out my Step 5 commit message had the whole `git commit -m "` pasted into its first line; I amended it (now ce9d196). Then it removed the test cap completely instead of just turning it off, so the "no TEST-ONLY before submission" check already passes, and replaced the cap test with one that checks every new posting goes to Claude. 96 tests still pass. It gave me the commands for Run 1 (seeded 10/29 snapshot) and Run 2 (live), with output saved to evidence/runs/.

**My judgment calls**

- Committed the cap removal and ran both runs myself.
- Noticed Run 2 fetched 745 and Run 1 737, but new postings was 20, not 8. Asked why.

**What's next**

Asked the AI to check the runs and explain 745 − 737 vs 20 new.

### 2026-10-31: Why 20 new when the board only grew by 8

**What I tried and expected**

Done running. Run 2 has 745, Run 1 has 737, so why does it show 20 new postings?

**What happened**

The AI recomputed it from the two raw files instead of trusting the program: 20 postings are only in today's file and 12 are only in the 10/29 file (closed since then), 725 are in both, so 737 − 12 + 20 = 745. "New" counts added postings, not the net change. The 20 ids the program judged are exactly those 20. State has 757 ids = both runs together. Run 1 reported 0 (baseline, seeded). All 40 verdicts (20 rule + 20 Claude) are ok and not_relevant, no disagreement, no validator rejections, all Claude calls went through the CLI on claude-sonnet-5-5.
Trace: runs/2026-10-31T214040Z, runs/2026-10-31T214118Z, state/stripe.state.json, evidence/runs/

**My judgment calls**

- Asked if the user should be told that 12 postings disappeared, since the numbers look off. The AI gave three options (one extra line, exact "closed since last run" with a state change, or nothing now). Picked C: keep it as is, explain it in the README, do it in the next layer.
- Asked what "all checks pass" meant and whether I have to check anything myself. The AI's checks only show the program ran and the numbers add up, not that any verdict is right. That part is mine, and it happens in Step 7 (my labels) and at the end (hand-calculate one rule verdict).
- Asked whether the commit message followed my /git-commit rules. Format yes, but the title said what, not why. The AI rewrote it, and I committed the runs (7b63b89).

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