# FRICTIONAL — honest log

For JS3 I did the same thing I did in JS2: I wrote FILTER.md first, before touching any code. All the decisions were mine, and Claude Code wrote up the wording, the code and the tests based on them. The code turned out to be the easy part. What made this assignment difficult was realizing that I couldn't take anything at face value. My own labels needed checking, my own audit needed checking, and so did the labels Claude attached to its claims. I also learned that a sample of 30 tells you a lot less than it looks like it does. This log walks through those moments, along with the commits, prompts and tests that go with each one.

## 1. Starting point and the filter before the build

I started by creating a fresh local repo and bringing over only the pieces JS3 actually depends on: my JS2 code and its tests (113 passing), the config, the Evan Gordon persona and the Oct 31 baseline. The next thing I did was write FILTER.md v1, still before any JS3 code existed. When Claude filled the score with placeholder numbers, I told it "ask me the placeholder and i will answer them". The questions it came back with meant that what had been guesses became decisions I made myself.

## 2. My decisions on the filter

I asked "can you make it so the max is a 100 point system?", and that turned into 8 points per skill (capped at 8 skills), +16 for years, +10 for Boston or +5 for remote US, and +10 for visa sponsorship. After that I asked "is it possible to add visa sponsorship rule now in the new filter?". Claude suggested making it a hard rule, but I went a different way and told it "Allow all jobs that fit, just job that offer sponsorship get points for sponsorship". That means visa can only add points and never knocks a posting out. I also added the BI titles. Then I fixed the years preference: "3 years or less is preferred but consider and jobs asking for up to 5 years". Claude noticed that v1.1 had really been giving the bonus for 4 years or fewer, so this change became v1.2. I left "Data Engineering" out of the role phrases (matching on the whole phrase only), and later on it turned out to be a false friend.

## 3. The snapshot

The Greenhouse responses from JS2 didn't include job descriptions, which meant the filter had nothing to run on. I took a new snapshot with content=true, which needed 10 read-only requests and brought back 2,629 postings. Kraken came back empty again and the 404 board was "not observed", just as FILTER.md had predicted. The raw files added up to 33 MB, so I decided to gzip them, which brought them down to 2.7 MB. Every time the snapshot loads, the sha256 of the original bytes gets checked.

## 4. Shaping the label sheet

Instead of working from a smaller sample, I decided to label every data-related title, which came to 141 postings. After that I trimmed the set. First I said "remove the ones which are outside the US. Don't remove the remote jobs", and then "I don't what any job posting that requires 6 years of experience or more". Before deleting anything, Claude listed all 25 postings it was going to remove, each with the years phrase quoted. Going through that list, I spotted a posting the filter's own years rule would get wrong: "3+ years managing" followed by "7+ years in software development". Later I asked for the labeling tool to "also add years expereince requirement mentioned and also if sponsorship details are mentioned". The very first posting it showed me asked for "10+ years" and had made it past the cut, because the word "experience" sat more than 60 characters away. Ten more postings like that one were removed in place. Narrowing the sheet this way meant I lost the chance to test the location and years rules against my own labels, and REJECT_AUDIT.md says that openly.

## 5. Three labeling windows at once

While Claude was getting ready to remove those ten postings, it noticed that three copies of the labeling tool were open in my terminals. Since each copy writes out the entire file when it saves, they could have quietly overwritten each other's labels without anyone noticing. Claude held off on touching the file until I had closed all three, and afterwards it checked that my 12 saved labels and all the other rows were still exactly as they had been.

## 6. My labels broke my own rule

Once the first pass was done, 22 postings were labeled relevant, and 11 of those went against rule 1 of my own labeling rules: Data Scientists, a sales analyst, a customer-success analyst, a product manager. For most of them my note just said "data role". That's exactly the mistake I made back in JS1, labeling based on the title. I saved the first pass as a separate file and then did a second pass with --redo. In that pass I changed exactly the 11 postings Claude had listed, every one of them from relevant to not relevant. So the second pass was guided by Claude's list and only moved labels in one direction, and I want that on the record here. The held-out hash was locked in that same commit, before the filter had run on the snapshot even once.

## 7. The audit agreed with everything, which was the problem

I went through 36 postings for the audit: 30 rejects picked at random, the single closest call, and all 5 postings the filter kept. At first I marked all 36 as correct. One of them was the Zoox "Contract Student Worker - Data Analyst (Part-time)". When I labeled it blind, I had called it not relevant ("not data role"). In the audit, after I could see the filter had kept it, I called it a "relevent data role". Claude flagged that the two didn't match, and I asked "what do you recommend for this project?". I decided to go with the blind label, so the verdict for that row is now "wrong", and both of my answers are recorded in it. Getting 0 wrong out of 30 random rejects only puts an upper bound of roughly 9.5% on the error rate. The errors that really mattered, 7 of my 11 relevant postings being rejected by the role rule, never came up in the random sample at all. They only showed up through my labels.

## 8. The tool server's own claims

Claude built the server from scratch, tests first. The dry runs disproved two claims I was about to make. The tracing hook missed the persona file being read, since that happens while the code loads, and once the hook was installed earlier, the trace showed Python writing a .pyc cache file, so "writes no files" only held once the server was started with -B. The real transcript showed a third problem: a rejected Canada posting scores 64, higher than some kept postings. When I asked whether everything met the brief, Claude pointed out that the brief says to offer the capability "to Claude", but only its test script had ever called my server. I said "do 1 and 2". Claude added a project .mcp.json and a recorder that logs both directions, and I opened Claude Code in the JS3 folder and asked it to score three postings and say which one Evan should apply to. Claude Code tried a newer protocol first, then fell back to mine. It didn't rank by score and left the decision to apply to me. It also caught something we had both missed: the tool description still said "FILTER.md v1.2" while every answer said v1.3, a mismatch already present in the v1.3 transcript Claude had recorded. The fix was done test first, so the description now takes the version from the code and says the bucket, not the score, decides. Because this changed the signed sign-off, I re-signed it only after reading the updated files.

## 9. The other server

I chose to evaluate the official fetch server. At first Claude only read its source at a pinned commit, saying it couldn't run it because "this machine has 3.9.6", and that claim ended up in TOOL_SERVER.md and in the sign-off I had already signed. When I asked "isn't there a local python version which is 3.11 or newer that can be used?", Claude found 3.11, 3.13 and 3.14 already installed; it had only checked the default python3. I told it to run the server, and it did so in a throwaway Python 3.11 environment with files byte-identical to the source it had read, after first fixing the tracer, which had been skipping writes under /lib/python and would have hidden the install. What the source predicted was then observed: the tool description tells the model it now has internet access, a tool marked readOnlyHint ran npm install and added 33 packages on the first web page, and my restricted configuration (only the two job-board hosts, no Node.js reader) refused example.com and started nothing. My trust decision is no by default, and yes only in that restricted form, with its output treated as untrusted. I also had Claude record a second transcript of my own server under v1.3 so the evidence matches the current code.

## 10. What moved the score

I tried five single changes on the tuning labels. Only one of them, A, made any difference: it let engineer titles containing "Data" or "Pipeline" get past the role rule. I decided to give the baseline, A and D one look each at the held-out labels. A raised recall from 2/7 to 6/7, but it also let an internship through, because "intern" matched as a whole word doesn't match "Internship". D went the other way between the two sets: on the tuning labels the years bonus looked like it helped the ranking, but on the held-out labels it looked like it hurt. I adopted A, added "internship" while marking it as unmeasured, and rejected B through E.

## 11. What I accepted, changed and rejected from Claude

Looking back at the decisions: I rejected a hard visa rule (it became points only), "Data Engineering" as a role phrase and Claude's first guess at the score weights, and I changed the years preference from 4 to 3, cut the label pool from 141 down to 72, and had the labeling tool show the years and visa lines. I accepted gzip, the 25 removals, the blind label over my audit answer, change A, and running fetch and the Claude Code session, each only after checking it. I skipped fixing the claim checker's "list of alternatives" error, since Claude estimated about an hour and it would have reopened a third of the write-up after the held-out look, so the 22% error rate stays a documented finding. Because only Claude had judged the claim labels, I spot-checked 4 myself in audit/claim_spotcheck.csv, but I changed two answers after Claude pointed to my own FILTER.md §2 rule and picked the first option every time, so that check is small and steered, and SHORTLIST.md says so. I then checked all 39 new v1.3 claim labels by hand through 13 questions, with Claude's view hidden and the answer order varied, and found 3 wrong (8%), all the same "list of alternatives" error, recorded in audit/claim_check_v13.csv. Claude caught several of its own mistakes, including a stale "(v1)" heading, a wrong sign-off line about test order and 10 of 46 wrong claim labels from its checker, and in a final sweep I asked for, it found the driver's seat still quoting the old 22% figure and CONTRACT.md and GATE.md linking to folders from earlier submissions. Those were fixed and I re-signed after reading the change. The one mistake I caught myself was the false "only Python 3.9.6" reason for not running fetch, and since it was in a signed sign-off, I re-signed only after it was corrected.

## 12. What I learned, traceability, and what is still open

A sample that agrees with everything can be telling me about my own anchoring, not about the filter. My labels need the same checking
as Claude's, and a number that moves on tuning can reverse on held-out. Persisting across sessions is not learning: the scorer changed
because I edited a file, and Claude remembered my decisions because they were written to memory files.

**Traceability.** The prompts quoted above are from 2026-11-24 and 2026-11-25. Every step has its own commit, and `git log --oneline` lists them in order. The main ones, by commit message:
- "Starting point: JS2 code, tests, config, persona and the Oct 31 baseline"
- "FILTER.md v1" to "FILTER.md v1.2", all before the first JS3 code
- "Labels: second pass by Ethan…; held-out set locked"
- "FILTER.md v1.3 (Ethan's decisions after measuring)"
- "Step 5: second real transcript, recorded under filter v1.3"
- "Step 5: the official fetch server run in two configurations"
- "Step 5: Claude Code as a real client of my server"
- "Test first: the tool description must declare the filter version it runs", then "Fix: the tool description now takes the filter version from the code"
- the two hand checks of the claim labels and the final "SIGNOFF.md: re-signed by Ethan Gomes"

The tests are the full suite of 158, including test_W1–W10, the server tests and scripts/js3_sabotage_check.py (9/9). The server
evidence is in evidence/mcp/: three transcripts of my server (v1.2, v1.3 and Claude Code as the client) and both fetch runs.

**What is unresolved (known limits, not unfinished work):**
- the claim checker's bug itself: it still reads "such as A, B or C" lists as requiring each one. My hand checks are done and confirmed it (3 of 39 wrong), but the code was not fixed
- the "internship" fix is unmeasured
- the student-worker false friend is still kept
- what fetch's npm install downloaded was not reviewed, and its proxy and prompt paths were not run
- Claude Code connected to my server only once, and its fix was checked by a test, not a second session
- everything rests on one day's snapshot, with 7 relevant held-out postings
