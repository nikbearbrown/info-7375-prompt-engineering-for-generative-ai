# FRICTIONAL — honest log

For this film I had to explain DataSentry in four fixed parts, in this order: an executive summary, what others have done, the methods, and the evaluation. All of it had to fit in four minutes. I stuck with the same project I pitched in October, and I built the film on 2026-11-23 using Claude Code and the Brutalist toolkit. I worked in a new folder so my graded pitch wouldn't be touched.

The hardest part was deciding what actually mattered enough to go in. Four minutes isn't much when you have four parts to cover, and every beat I added meant cutting words somewhere else. So every idea had to justify being there. I had to decide which prior work to show and which numbers to use, how much of the method to explain, which results to put on screen, and what to move to the appendix. Two other things were also hard: building the loop the TA asked for and then checking that its result was real, and making sure the film never claimed more than the evidence supported. A few things went wrong along the way. My first narration ran too long, the type gate blocked the final cut three times, and one result I was happy with turned out to have been measured on the same data it was tuned on. In this log I go through each of these, along with the prompts, files, tests and runs behind them.

## 1. Starting point

I started by pasting the assignment and asking "Go through this and let me know what needs to be done". After that I
told Claude Code to "Create a new folder and make the video for this assignment using Brutalist libraray", mentioned
that "it is the same project", gave the length as four minutes, and added "Free claude subscription". That last part
turned out to matter for the Methods section, since it asks whether I have the credits, accounts and compute I need.
The new folder, `Final_Project_Film/`, got a copy of the `first-run/` evidence from my pitch: the planter, the scorer,
and Claude's two hand-run rounds from 2026-10-25 along with their recorded results. It did not get the pitch's Python
environment or the downloaded data.

## 2. What others have done, and what I could actually read

Part 2 asks who has tried something like this and what results they got, so I needed actual numbers and not just
names. Claude Code searched for the prior work and summarised it. That covered mutation testing, from DeMillo, Lipton
and Sayward in 1978; Amazon's Deequ from 2018; Meta's TestGen-LLM from 2024, where 75% of its tests built and 57%
passed reliably; and Meta's ACH from 2025, where engineers accepted 73% of its generated tests. I only read the
abstracts and summaries, not the full papers, so SOURCES.md marks those rows as "abstract". The comparison grid in
the film is built from these sources, so on screen it's labelled "constructed from the sources · in what I found". I
didn't want it to come across as a claim that no tool like this exists anywhere.

## 3. Fitting four parts into four minutes

The first full narration, timed from the generated audio, came out at 4:13, which was over my limit. Cutting eight
beats got it down to about 3:59, but that was still too close to four minutes, so three more were cut to bring it to
about 3:56. None of the cuts removed any facts, only words. The rule I stuck to was that the narration length sets
the clock, so whenever it ran long the fix was to rewrite and re-voice it, never to speed anything up by hand. Later
that day I asked "can you make it to around 3 minutes 50 seconds ?". Nine more beats were reworded, which brought it
to 3:51, and adding the end screen took it to its final length of 3:54.

## 4. The type gate blocked the final cut three times

Every gate passed on the review cut, but Gate T, the type lock, rejected the final master three times, each time on
the same beat, B14. It was reading the bordered cards around two lines of text as one large text block with a smaller
label sitting on top. Increasing the line spacing didn't fix it, and making the cards taller didn't either. What
finally worked was removing the card borders and keeping only the text, the tick and the dot. I kept the three failed
final logs in gate-reports/earlier-runs, saved as art-final-gateT*-FAILED.log, so that history isn't hidden.

## 5. Building the loop the TA asked for

I just the TA's suggested next step which was to "build the loop that feeds the clean-copy
false alarms back automatically". I asked Claude Code to "Consider the feedback given and tell me if changes need to
be made", and then told it to "Make this change first". The tests came before the loop. The file
first-run/tests/test_loop.py holds 13 tests, and they were written before loop.py even existed. They check three
things. First, that the code policy accepts Claude's two real replies and rejects anything that opens files, imports
os or subprocess, or reads the answer key. Second, that the loop's feedback builder recreates my hand-written round-2
prompt word for word from the recorded round-1 results, without ever mentioning the defects. Third, that the pass and
stop rules work correctly. Replaying the two saved replies through the loop with ./run_loop.sh --fixture claude-checks
gave back the 2026-10-25 scores exactly. Two smaller issues showed up along the way. Claude Code wasn't on my
terminal's path because it lives inside the VS Code extension, so the loop has to look for it there. And a fresh
install pulled in pyarrow 26.0.1 instead of 26.0.0, which saved the clean sample with a different file hash even
though the 10,000 rows were exactly the same.

## 6. My live run, and checking that the pass was real

I ran ./run_loop.sh myself in my terminal. It took three rounds. Round 1 caught all five
defect types but flagged 94 good trips, round 2 flagged just one, and round 3 flagged none while still catching all
five on both plantings, so the loop stopped on "pass line met". That run is saved in
first-run/loop-runs/2026-11-23_182418. I was happy with it, but then I realised the "zero good trips flagged" result
was measured on the same clean copy whose results had been fed back to Claude, so that part was in-sample. Claude
Code then wrote heldout_clean.py, which draws a second, completely separate clean copy of 10,000 trips with no rows
in common, and ran the round-3 checks on it. The result was still zero. Round 2's single false alarm didn't appear
there either, while round 1 flagged 96. I also went through the round-3 checks myself. They still have a rule for
every defect type, and the only thing dropped was the fare-versus-distance rule that had rejected a good trip, so the
pass wasn't a trick. One cosmetic bug, where the output said "1 trips", was fixed in the code afterwards, but the
recorded run was left exactly as it originally ran.

## 7. Checking the agentic use in this project

While I was looking for ways to improve the project, I checked how agentic DataSentry actually is. The honest answer
was not yet. The loop has exits, state, a stop condition and a code policy, but Claude doesn't pick any tools and
there's no human gate. I decided the four-part film should describe the agent I'm actually going to build. So it now
presents DataSentry as an agent that a person approves, and it includes a beat on tools and permissions, a beat on
the human gate marked "planned", and a beat on at least five deliberate failure cases plus one controlled failure. To
free up space for these, mutation testing was folded into the comparison grid. Building the tool menu and the gate
is the next stage of the project, and the film only needs the plan for now. To keep track of that work, I had Claude
Code put together a reference PDF with a build plan, just for my own use and kept outside the submission.

## 8. The Food Inspections link

In the pitch feedback, the TA asked for a link to my Food Inspections project. I asked "also is food inspections
mentioned anywhere in the video?", and it wasn't, since none of the four parts is a "why this project" section. At
first I said "then don't include the food inspections link if its not in the video", but then I changed my mind and
said "just keep it in the readme as a note". When that note ended up saying "not in the film", I said "don't mention
not in the film , just keep it as a note". So the README now ends with a one-line note and the link.

## 9. Small fixes I only found by looking

Some problems only showed up when I looked at the frames, not in the gates. The four-part list on the title card only
appeared in the last half-second, so I had it moved earlier. Gate A then rejected the first attempt at that because
the frames had stopped changing, and drawing the rule and the dot in two separate steps fixed it. After the
rewording, three scene cues no longer matched their narration: "All caught" had turned into "all caught", "only the
clean" had turned into "Only the clean", and the "count which ones" line in BSIMPLE was gone completely. Claude Code
then checked every cue in all 20 scenes against the narration. At one point a title-card clip rendered from old code
by a build that had been stopped almost got reused, so that build was stopped and the stale clip was deleted before
going further. In B03, once it was shortened, the results panel sat empty for around eight seconds, so now the tool
rows appear at the moment each tool is named. While watching, I also noticed that the last bar in B01's chart was
hanging past the baseline. The bars were centred on the card and the baseline was extended past both ends, and I
checked that frame in the finished film.

## 10. The end screen and the cost question

I asked Claude Code to "just add a end screen after the end saying with thank you with the project title and my name
and the final project film written". The end screen is silent, so the subtitles stayed the same, and it added three
seconds to the film. Before zipping everything up, a scan of the files showed that Claude Code's raw replies include
a total_cost_usd field, which came to about $0.49 across the three rounds, so I asked "Will this cause a problem , as
in a mismatch in information?". It doesn't actually contradict the film's "no API key, no credits", because that
number is what the calls would cost at API rates, and my subscription doesn't charge per call. Still, a grader could
read it as a mismatch, so a one-line explanation was added to APPENDIX.md and SOURCES.md, and the evidence files
themselves were left exactly as they were recorded.

## 11. What I accepted, changed and rejected

I accepted the loop design once its tests passed and the fixture replay matched my recorded scores, and I accepted
the second clean copy check because it dealt with my own concern that the pass was in-sample. I turned down putting
the Food Inspections reason into the film, and after that I also turned down the "not in the film" wording in the
README. For the length, I didn't go with any of the three cut options I was offered. Instead I asked for about 3:50,
which meant only trimming words and not removing anything. I changed the commit title to "Final project film
submission" rather than the one that was suggested, and I picked the folder name final-project-film-2 so my graded
pitch folder would stay exactly as it was. I watched the finished film, signed off on the fact-check, and told Claude
Code to name the zip Ethan_Gomes_INFO7375_Final_Project_Film_23_Nov_2026.

## 12. What I learned, traceability, and what is still open
The biggest thing I learned is that a pass has to be checked on data the system was never tuned on. "Zero false
alarms" was true on the feedback copy, but it only really meant something once it held up on a second one. I also
learned that the gates catch layout rules, but only actually looking at the frames catches things like a panel
sitting empty or a bar hanging over the edge. And four minutes forces every claim to justify being there. All the
prompts quoted above are from 2026-11-23. The live loop run is in first-run/loop-runs/2026-11-23_182418, the fixture
replay is the -fixture run right next to it, and the second clean copy results are saved beside each round as
loop-roundN-heldout-clean files. The tests are the 13 in first-run/tests/test_loop.py, and they run before every
loop. The gate history is in gate-reports, including the three failed Gate T logs. The film was first pushed as
commit f69a209 in fall-2026/ethan-g/final-project-film-2, and this log and the project brief were added after that.
A few things are still open, and they're the next improvements to make. A tool menu that Claude chooses from, a human
gate, a held-out set from a different month, deliberate failure cases and a controlled failure are all planned but
not built yet. The pass comes from one run on one table with five planted defect types, and the model might not do
the same thing twice. And I only read the abstracts of the Meta and Deequ papers.