# FRICTIONAL.md

Ashwin Thankachan · INFO 7375 · Final Project Film

My log of choosing the project and making the film — October's pitch first, then the final film in
November. Claude Code helped me turn my chat history and the command output into these notes. The
decisions and the reasons are mine.

**Which entries were written when.** The dated October entries were reconstructed at the end of that
week from my chat history, not written daily. The November entries were written the same day as the
work, except the two passages below marked *(written 2026-11-23, after the fact)*. Where an entry
quotes a number, that number comes from command output in this folder, not from memory.

**October (the pitch, 3:53) is sections 1 to 8. November (this film, 4:48) starts at *A different
assignment*.**

---

## 2026-10-09 to 10-10: too many ideas

I thought I'd pick a project in one evening. It took most of a week.

- **Oct 9.** I asked Claude for ideas that would help my resume. It suggested an API contract drift
  detector, an incident postmortem agent and a resume claim checker. None of them excited me. The resume
  checker was out anyway, because the assignment bans real resume, contact and tracker data.
- **Oct 10.** Over many rounds I went through about twenty more ideas: MBTA reliability, an apartment
  records checker, an OPT day tracker, an SEC filing extractor, a ticket-drop engine, an accessibility
  fixer, and others. I kept saying no.
  - The searches kept showing me that "original" ideas already existed. accessiBe launched an
    accessibility code agent in September 2026, Splitwise Pro already itemizes receipts, and Slido
    already groups similar questions.
  - I also thought I had to pick one of the Canvas examples. They're only examples. My auto-apply job
    pipeline is already my Reallocation Engine work, so I wanted something separate.

By the end of it I knew two things. I'm applying for SDE roles, not "AI engineer" roles, and I want the
project to teach me skills my resume doesn't show yet.

## 2026-10-11: ProvenDocs and the first film

I picked ProvenDocs. It would turn every sentence of a code explanation into a JUnit test and mark it
proven, false or untestable, scaled with Kafka, Redis and Kubernetes so I'd learn those too.

I built a full film for it with the Brutalist toolkit. Setup problems:
- manim 0.18 doesn't install on Python 3.13, so I moved to Python 3.12. That needed Homebrew `pango`, and
  pinning `av<16` for faster-whisper.
- The show-tell skill opens with the instructor's persona and ends on his handle. The assignment says to
  narrate as myself, so I replaced both. The outro card had the handle hardcoded, and no gate caught it; I
  only saw it by watching the frames. That led to `build/patches/ClaudeTitleOutro-handle.patch`.
- Gate T blocked twice on text size, once over a single lowercase "w" 1 px under the minimum.

It ran 3:55 and passed every gate. What I learned: passing the gates doesn't mean the film says what you
meant. You still have to watch it.

## 2026-10-11 (evening): a brutal second opinion

I pasted the ProvenDocs pitch into Codex (ChatGPT) and asked for brutal feedback. It gave it 6/10 and asked:
if the generated tests just get committed, what does the tool add beyond ordinary JUnit tests? It also said
I was adding Kafka, Redis and Kubernetes before showing the tool was useful. That was fair. I'd added them
to learn them, not because the project needed them. Its top alternative was an incident investigation
assistant.

## 2026-10-13 (morning): the final rubric changed how I looked at it

The final project (250 points, due Dec 20) asks for:
- a loop with a budget
- tools with permissions enforced in code
- saved state
- a stop condition that isn't "the model said it was done"
- a human approval gate
- a held-out evaluation
- a failure I trigger on purpose

ProvenDocs had no natural human gate, because nobody needs to approve a test result. So I went back to
brainstorming with Codex and other chatbots, pasting their pitches into each other for second opinions:

- **Dependency patching and schema migration agents.** The rubric fit was oversold, and Atlas, Bytebase
  and pgroll already cover much of migrations.
- **"Referee", a patch checker built on the EvilGenie paper.** The pitch claimed hidden tests fix reward
  hacking, but the paper found they help only a little.
- **"FaultLine", an incident agent.** I worried it looked like CloudPulse again.
- **Subscription reconciliation, FraudLens (streaming fraud), model routing, catalog matching.**
- **An outfit picker based on weather and trends.** Weather styling already exists, and my Northeastern
  Claude access doesn't include API credits.

By then I had too many ideas and didn't feel strongly about any of them. Each chatbot changed its
recommendation every time I pasted something new.

## 2026-10-13 (afternoon): deciding with real data

I asked Claude to stop pitching and look at evidence: my resume, and the jobs I've been applying to. My job
pipeline had 3,254 entry-level postings stored from Oct 8–12. Claude counted skill keywords across them
(a simple word count, so it's noisy):

| Skill | SWE postings | AI/ML postings |
|---|---|---|
| Agents / agentic | 12% | 52% |
| Kubernetes | 16% | 19% |
| Observability (Prometheus, OpenTelemetry, Datadog) | 13% | 18% |
| Evaluation, RAG, MCP | — | ~11–22% |
| Redis / Kafka | ~2% / ~4% | ~2% / ~4% |

My resume covers Python, Java, AWS, CI/CD and Spring Boot, and shows nothing for agents, evaluation or
observability. So I went back to the incident agent and named it **TraceCase**.

What made it feel right to me is that it builds on CloudPulse instead of copying it. CloudPulse answers "is
the service healthy?" TraceCase answers "why did it break, and what is safe to do?" I can explain both in an
interview.

Two changes from my earlier plans:
- **Redis stays only where it has a job:** the cache and queue inside the demo service. That gives the agent
  real failures to find, like a stale cache or a backed-up queue.
- **Kafka is out.** Kubernetes is a stretch goal.

## 2026-10-13: checking the alternatives

My draft brief said TraceCase is different because a person approves fixes. Claude checked the primary
sources, and I skimmed both GitHub pages myself.
- **HolmesGPT** (CNCF sandbox, Apache-2.0) is read-only by default. Its optional Kubernetes remediation
  toolset already puts "every mutating action gated behind human approval". So approval isn't my
  difference, and I took that claim out.
- **AIOpsLab** (Microsoft, MIT) is a research framework for evaluating these agents, and it runs on a
  Kubernetes cluster.

The film now says only what TraceCase will do:
- run on a laptop without Kubernetes
- ship its own service to break
- make every claim cite a real log line or trace
- void an approval if the fix or its evidence changes

It doesn't claim the others can't do these things. I haven't run HolmesGPT yet.

## 2026-10-13: first TraceCase draft

- **Script:** the first draft ran ~5:20 against a 4:00 limit. I cut it to 3:53.
- **Drawings:** 16 new scenes with one cast throughout: service, logs, trace, a magnifier for the agent, a
  fix card and a barrier gate. The first contact sheet showed four overlaps, which were fixed before
  rendering.
- **Gates:**
  - Gate B stopped the render twice: a label outside the safe area (B05), and a cross drawn over text (B11).
  - Gate T blocked the master once: it read wavy lines in B08 as overlapping text, so I swapped them for
    bars.
- **Something no gate caught:** the intro card never changed "is it down?" into "why is it down?". The
  trigger phrase included the "?", which the component strips before matching. Watching the frames caught
  it.
- **My voice:** the toolkit has no voice cloning, so I recorded the intro and outro with a script that
  replaces a beat. It took three tries:
  1. The script quit silently, because ffmpeg exits with an error after listing microphones.
  2. The next take was 17 s of silence, because the terminal inside the Claude app had no microphone
     access. The script now stops if a take is silent.
  3. The take recorded in the macOS Terminal app worked.

## 2026-10-13 (evening): drafts 2 and 3

I watched draft 1 and wasn't happy with two things:
- **My voice.** I didn't like how my recording sounded next to the rest of the film, so the whole film now
  uses one synthetic voice (Kokoro `am_michael`, 0.95 speed) reading my first-person script. My takes are
  kept, unused.
- **Some icons and the flow.** The mouse cursor was a stubby triangle that floated in mid-air (B03) or sat
  on a button's edge (B05), and nothing connected one picture to the next. Draft 2 added:
  - a proper pointer, placed on what's being clicked
  - flow arrows (service → evidence → fix → gate, API → Redis → worker → Postgres, and others)
  - direction arrows on the loop
  - one straight trace line in B10
  - a heading on every beat naming which of the seven questions it answers

Then Claude and I checked the film against the grading rubric and fixed what it was missing (draft 3):
- **Prompt contract:** the course term is now said out loud. Each agent step must match a fixed format that
  code checks.
- **Limitation:** an honest one is now stated. It will only be tested on failures I design, so it proves
  nothing about real production systems.
- **Skill labels:** the "why this project" shelves now name the skills (new: agents, tracing, evals; built
  before: Spring Boot, LLMs, Docker).
- **Empty openings:** a few beats opened on a nearly empty frame for a few seconds. Now each beat's main
  picture is there from its first frame.

Adding lines pushed the film to 4:01, so I tightened four sentences. It now runs 3:53.

Two more problems along the way:
- Watching the frames showed the "contract check" in B07 appearing 5 seconds after it was said. The code
  steps were in the wrong order.
- Gate T then blocked B07 twice: the new label was 1 px under the minimum, and the wavy lines in its claim
  cards read as text (the same false alarm as B08). I enlarged the label and swapped the lines for bars.

## 2026-11-21: a different assignment, so a different film

The pitch film was 18 beats and 3:53, organised around the seven brief questions. The final project film
asks for something else: four named parts, in order — executive summary, introduction with prior work,
methods, evaluation. That is not a trim of the pitch. The pitch answered "what is it and why"; this one
has to answer "who else tried this, how will you build it, and how will you know it worked".

So I rebuilt it: 25 beats, new narration, new drawings, four part markers on screen so a grader can see
which section they're in and how far through it they are. Target was about 4:30; it came out at 4:48 and
I let it stand, because cutting eighteen seconds would have cost either a prior-work beat or an
evaluation beat, and those are the two parts the rubric names.

Everything still runs locally and costs nothing: Manim for every drawing, Kokoro for the voice,
faster-whisper to align the words. No API calls, no stock assets, no paid anything.

## 2026-11-22: making it look like objects instead of clip-art

The first full cut passed the gates and still looked flat. Things floated. A laptop and a box next to
each other read as two icons pasted on cream, not a desk with kit on it.

What fixed it was unglamorous: a contact shadow under anything standing on the ground, a bench line under
the kit, plinths under the objects on display, ribs on the cylinders, a glow on the laptop screen. Also a
layout contract applied to every single beat — top rule at +2.82, bottom rule at −2.95, heading on the
left margin, part marker on the right — so no frame is an unbounded void.

I previewed at low resolution first and caught eight layout problems before spending any 4K render time:
labels printing over the plinths they belonged to, a label above the top rule and off-stage, axis labels
crossing the bottom rule, a box sitting on its own caption, tiles landing on a safe's dial, a seal hidden
behind the card it stamps.

**What the gates taught me, the hard way.** Two of them pull in opposite directions and I only found that
by tripping over it:
- Gate T reads a bordered rectangle as a text run that *encloses* whatever is inside it. I had added
  scribbled lines inside three claim cards to make them look like filled-in forms; all three failed at
  100% bbox overlap. Swapping my hand-rolled rect for the kit's card helper did not help, because the
  border is the problem, not my version of it. The cards went back to being empty.
- Gate T also flagged two beats where blobs had fused. I fixed one by lightening the shelf lines from INK
  to GHOST — and that broke Gate V, because lightening them raised the mean ink luminance of the frame
  and pushed the contrast below the 0.30 floor. DIM was the colour that satisfies both: dark enough to
  carry contrast, far enough from INK not to fuse.
- A global fix beats a local one. Rather than patch the one beat whose log-sheet scribbles were a pixel
  under the type floor, I dropped the scribble amplitude once in the shared helper. One beat had been
  sitting at exactly the 41 px minimum, which is not a margin.

Six 4K render cycles in all before everything was green at once.

## 2026-11-22 (evening): the thing no gate can check

I sent the cut over and got three screenshots back with "the circular arrow is wrong".

It was. **Both** circular arrows in the film were wrong, and in the same way. Manim's `Triangle` points
up, so to sit an arrowhead on a circle pointing along the path you rotate it by the angle minus 180°. My
code rotated by the angle plus 90°, which aims every head *radially inward, at the hub*. On the methods
ring that is four arrows all pointing at nothing. The loop arrow in the prior-work section was worse: its
head was parked at angle 0 while the arc it was supposed to terminate ends at 207°, so it wasn't even on
the end of the line.

Then the ring turned out to run the wrong way. Its stations are numbered 1→2→3→4 clockwise, but
`MoveAlongPath` on a bare `Circle` runs anticlockwise — so the dot travelled against its own numbering.
It also stopped exactly on a station, which is why a terracotta blob was covering the "2" in the
screenshot. Both arrows now come from one helper that takes an angle and a direction, so they can't drift
apart again.

The third report was "the percentage didn't show up". It had. I pulled a nine-frame filmstrip of that
beat and the 59% is on screen the whole way through. But the report was still pointing at something real:
the frame that got screenshotted was a beat *opening*, and several beats opened on nothing but their
heading for over a second — the worst was 1.75 s. Eight beats now lead their first reveal, so the picture
arrives with the words instead of a beat behind them. Longest blank opening is now 0.75 s.

This is the same lesson as October, and I clearly hadn't learned it: the gates check contrast, type size,
overlaps and frame edges. They have no idea whether an arrow points the right way. I had reported the
film as verified, and it was — verified against every check the toolkit runs, which is not the same thing. Someone has to watch
it.

## 2026-11-23: a second opinion, and the chart I'm least proud of

I did what I did with ProvenDocs in October: pasted the finished film into ChatGPT and asked for a brutal
read. Four of its findings were real.

**1. The prior-work chart was quoting numbers that don't exist.** This is the one that stings. The
headline on that beat is 59%, which is Flash's overall accuracy in the AIOpsLab paper. The four bars
underneath it were 93%, 62%, 42% and 33%. Only one of those is in the paper. Flash's detection is 100%,
not 93%; its RCA is 36.36%, not 42%; its mitigation is 54.55%, not 33%. The bars were a blend — some
agent's figure here, a different agent's there, one apparently rounded for looks — under a headline
belonging to a single named agent.

The film's entire argument is that a claim has to cite a real line or it doesn't ship. Its only chart was
doing exactly the thing it criticises, and no gate was ever going to catch it, because a fabricated bar
is the right size and the right colour.

I rebuilt it from Table 4 of arXiv:2501.06706v1. The narration speaks *ranges* across agents, so the
chart now draws ranges: a floor-to-ceiling band per task — detection 69.23–100%, root cause 36.36–45.45%,
mitigation 27.27–54.55% — against a labelled 100% ceiling and a 50% reference line, with the three agents
named on the frame and the source line in the corner. Nothing is averaged or blended. I dropped the
localisation bar because the narration doesn't quote localisation, and a bar nobody says out loud is a
bar nobody can check. I also recorded in the fact check *which* agent is excluded from the ranges
(GPT-3.5-w-Shell, weakest on every task) rather than leaving it implied.

**2. A frame contradicted its own narration.** On the resources beat I say model access is the open
question — my university Claude seat covers the assistant, not API calls from code. The frame next to
that sentence listed "billing" under *not needed*, with a cross through it. Billing is precisely the
thing that isn't settled. The row is gone; the column now lists exactly what the narration says isn't
needed, cluster and GPU, and nothing else.

**3. The paperwork had drifted away from the film.** `SCRIPT.md` was still the October draft: 26 beats,
different numbering, different wording from what is actually spoken. `FACTCHECK.md` opened by asserting
that every product sentence is future tense, which isn't true — one beat says "It's built so you can
check it", meaning *this is how it is designed*. Both are fixed: the script is now generated from the
same beat sheet the cut is built from, so it can't drift again, and the fact check states the tense rule
accurately instead of flatteringly.

**4. The submission zip in my course folder was the October pitch.** Dated Oct 13, containing
`tracecase-pitch.mp4` at 3:53. Had I submitted the file that was sitting there, I would have handed in
the wrong film.

**What I didn't take.** Two of its findings I think are wrong, and one is right about the project rather
than the film:
*(written 2026-11-23, after the fact.)* I first wrote this section claiming I had rejected two of its
findings. Going back to its actual words, I had misquoted both — and in both cases I had already done
what it asked.

- **On abstention** I wrote that it claimed the evaluation "lets the agent win for free by abstaining."
  It didn't. It wrote: *"'I don't know' should count as correct only on cases deliberately labeled as
  insufficient-evidence cases — not whenever the agent abstains."* That is a request to label the cases
  before tuning, which my narration does not cover, and it is now the written rule.
- **On the chart's ranges** I wrote that it claimed excluding GPT-3.5 flatters me, and argued back that
  excluding the weakest agent is conservative. It never said that. It wrote that the ranges *"exclude
  GPT-3.5 without stating that restriction"* — a disclosure problem, not a bias problem. I fixed it by
  naming the three agents on the frame and recording the exclusion in the fact check. So I complied with
  the finding and then logged it as rejected. That is the worse of the two mistakes.
- It's right that my baseline got pasted logs while TraceCase gets logs, traces and deploy history, so a
  win could have come from the extra evidence rather than from the agent. I first called that a hole in
  the *plan* rather than a defect in the film. That was a dodge: the film's fourth part **is** the
  evaluation plan, so a defect in the plan is a defect in the film. The narration is fixed now, not just
  the paperwork.

## 2026-11-23, later: the film was 48 seconds over the limit

*(written 2026-11-23, after the fact.)*

I asked Claude what runtime the assignment wanted and whether mine was inside it. It couldn't find the
brief anywhere on this machine, so it went looking in the course repo instead — at what my classmates
had written down. Three of them had quoted the rule:

> "Runtime: 2–4 minutes, hard ceiling 240 s."

and one had written "the assignment requires 2–4 minutes, and the assignment governs" while deciding
against a toolkit that suggested 60–180 s. Another logged trimming a film "from 3:58 to 3:51.7 to leave
a margin under the 4-minute limit." Then it measured all 22 films sitting in the repo: the shortest
2:06, the longest **3:59.6**. Not one over 240 s. My own October pitch was 3:53.

**My film was 4:48.** Forty-eight seconds over a hard ceiling, on the one check a grader can run in
three seconds without watching anything.

Nobody caught this. Not the toolkit's gates, which have no idea what the assignment says. Not the
second model I had been pasting the film into for review — it told me plainly it was working from a
brief with no stated point allocation, and I never gave it the runtime rule. And not me: on 2026-11-22
I asked for "4:30", which was already thirty seconds over, and nobody checked the number I had asked
for against the number I had been given.

That is the same failure as the blended chart and the wrong-way arrows, one level up. The gates check
the artifact against itself. Nothing was checking the artifact against the brief.

**The recut.** 694 words to 646, and the narration speed from 0.95 to 1.22 — the class had used 1.09,
so this is faster than most, which is the cost of keeping all 25 beats and all four parts rather than
dropping sections to fit. Final runtime **3:51.6**, 8.4 s inside the ceiling. I folded every outstanding
narration fix into the same pass instead of re-recording twice:

- **B04** stopped explaining the citation mechanism. Part 1 is supposed to be what it is and why it
  matters, *not how* — my own script file said so at the top of the section, and the beat broke the rule
  anyway. It now says the agent does the digging and I decide whether any fix runs, and the drawing
  changed with it: evidence, a magnifier, a diagnosis card, a gate that lifts.
- **B20** now states the fair baseline out loud.
- **B16** now separates what the checker enforces from what I score.
- **B14** gives the stopping rule a condition code can check instead of the phrase "supported evidence".
- **B22** names the metric: more correct causes than the baseline, not just "beats the baseline".
- **B08** says "detection, sixty-nine to one hundred percent" instead of "detection nearly solved",
  which was a generous read of a 69% floor.
- **B09** says "its SocialNetwork application alone runs twenty-eight microservices" instead of implying
  every local AIOpsLab run is 28 services. My own fact check had carried that caveat since 2026-11-21
  and the narration had never been corrected to match it.
- **B03** no longer calls CloudPulse "my last project". It was a four-person team project and had been
  flagged three times without my answering.

**What it cost.** The film is faster than I wanted it to be. 167 words a minute is brisk. I would rather
have cut a beat than speed the voice up, but every beat answers one of the brief's required sections and
I was not willing to drop a section at 9pm to buy breathing room.

## 2026-11-23, last thing: the closing frame said the opposite of the closing line

*(written 2026-11-23, after the fact.)*

I was looking at the final frame and couldn't tell what one of the objects was. It's a dark ring with a
solid hub, sitting between two isometric pages on a shelf labelled "exists". I had to read the scene
code to find out it was meant to be *this film* — matching the line "a brief, this plan, and this film".

Two things were wrong with it, and neither is the kind of thing a gate can see.

**The disc had no label and no history.** Every other object in the film belongs to a cast that gets
introduced and reused: the service stack, the log pages, the trace bars, the magnifier, the proposal
card, the gate arm, the seal. This one appears once, in the last beat, unlabelled. My own rule says
draw objects rather than labelled boxes — but that rule assumes the object is recognisable, and a ring
with a hub is not recognisable as a film. It now has "brief", "film" and "plan" under the three objects.

**The word "TraceCase" was sitting on the "exists" shelf.** It was placed on the same baseline as the
word "exists", directly under the right-hand page. So the bottom row read *exists: brief, film, plan,
TraceCase* — in the one beat whose entire job is to say "No TraceCase code exists yet." It is the same
defect as the "billing" row on the resources frame, found the same way: by looking at a frame and
reading it as a stranger would, rather than checking it against a rule. The wordmark moved up into the
empty band between the two shelves, where it reads as a closing title and labels nothing.

Three of this film's defects have now been found by someone looking at a picture and saying "what is
that?" — the two arrows, the billing row, and this. Every one passed every gate. That is the honest
summary of what the gates are for and what they are not for.

## What I took from Claude and Codex, and what I didn't

- **Accepted:**
  - Codex's critique of ProvenDocs in October, and ChatGPT's read of the finished film in November — the
    blended chart in particular.
  - Claude's keyword count, which settled the project choice.
  - The fact check that removed my "human approval" claim.
  - Claude's drawings and scripts, after I reviewed the contact sheet and the script for each beat. I did
    not inspect all 345 layout snapshots by hand; the gate reports did that. The one defect they could
    never catch — an arrow pointing the wrong way — I caught by watching.
- **Changed:**
  - Claude's first script ran 5:20 and had to be cut.
  - Its first drawings had icon and flow problems I pointed out, and in November both of its circular
    arrows pointed the wrong way in a cut it had already reported as verified.
  - It drafted this log, and I corrected it and gave my own reasons.
- **Rejected:**
  - About thirty project ideas.
  - Adding Kafka and Kubernetes just to have them on my resume.
  - Claiming human approval as my difference.
  - My own recorded voice.
  - Taking a second reviewer's wording wholesale. I checked each finding against the narration and the
    paper before changing anything — but see the correction above, where checking is exactly what I
    failed to do.

## Still open

Two items that were on this list this morning are **closed**: the film now says the fair baseline (B20)
and now separates what the checker enforces from what I score (B16). They were closed by re-recording,
not by writing them down somewhere else. What remains:

- **Model access is not settled.** My university seat covers the assistant, not calls from code. B18
  says so and names the fallback — the agent targets a model interface, so a local model can stand in —
  but a named fallback is not a tested one. Before the final project: either an API key with a stated
  spending cap, or a local model I have actually run against one of my own fault scenarios. Until one of
  those is done, the honest status is *blocked, with a route out*, and that is what the film says.
- **The support rubric does not exist yet.** The split is now stated — citation validity is enforced in
  code, claim support is scored by me, diagnosis accuracy is against the injected fault — but "scored by
  me" is only trustworthy if the rubric is written and fixed *before* the run. Writing it is the next
  evaluation task, not something to improvise while reading outputs.
- **The stopping rule needs code behind it.** B14 now says the agent stops when every claim cites a line
  that exists, which is a condition a program can check, rather than the phrase "supported evidence",
  which isn't. That is an improvement in the wording. It is still a sentence, not a function.
- **Which cases count as insufficient-evidence cases gets fixed before I tune anything.** "I don't know"
  counts as correct only on cases I labelled that way in advance, not whenever the agent abstains. With
  ten held-out cases one case moves accuracy ten points, so I'll report correct, incorrect and
  abstained separately rather than as a single number, and present it as what it is: a small controlled
  evaluation.
- Run HolmesGPT myself before the final project, so the comparison isn't based only on its README.
- Nothing of TraceCase is built yet. First piece: the demo service with one failure I can trigger, and a
  saved trace that shows it.
