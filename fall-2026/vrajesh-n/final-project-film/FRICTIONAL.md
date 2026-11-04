# FRICTIONAL — dated work log, Early Bird pitch film

> **Two parts.** Part 1 is the v0.2 build log (2026-10-13/14). Most of its prose was drafted by Claude from that session; the decision table is mine. It stays here unchanged as the record of that build. Part 2 (v1.0 rebuild, from 2026-10-23) is written by me.

# Part 1 — v0.2 build (graded 38.5/50)

Times are America/New_York. "Claude" = Claude Code (Claude Opus 5.5) in one session on 2026-10-14.

## 2026-10-13 — the first pitch (Doorman), kept as a draft
- Built a full pitch film for a different project, **Doorman** (AI-agent traffic for small stores). Never submitted; I deleted the draft folder on 2026-10-14 after choosing Early Bird. The Doorman code repo (`agent-doorman`) is separate and unchanged.

## 2026-10-14 — project change: Doorman → Early Bird
- **Why I changed:** JS1–JS5 build a job-search agent all semester; pitching that same agent makes the final project one continuous portfolio piece, and I am job hunting now, so I am its first user. The change is recorded here, as the assignment requires.

## Decisions, and Claude suggestions accepted / modified / rejected
| Time | Suggestion | Outcome |
|---|---|---|
| morning | Claude's first angle: "skip most postings; evidence-first verdicts" | **Rejected by me.** In this market I do not want to skip any software job. **Modified** into: keep every SWE/full-stack/AI posting, flag only hard blockers with a quoted line. |
| morning | I asked about Meta's Muse Spark as the "compute" | Claude found it is a paid public preview with a US waitlist and suggested it only as a second judge. **I dropped it.** |
| morning | Plain files (raw/, state/seen.json, reports/) and running it by hand | **Accepted.** A daily schedule can come later. |
| morning | My idea: use my downloaded LinkedIn connections to see who works at a company | **Modified:** only as a private, local, never-committed lookup with a synthetic public demo, in the final project. **Unresolved:** ask the TA whether this is acceptable. |
| midday | Use my resume as skill evidence | **Accepted with limits:** the file, contacts and every metric I cannot show (savings, coverage %) stay out. |
| midday | I asked Claude to re-check every answer | Claude found (1) the course's own **greenhouse-watch** already watches one board and keeps only résumé matches; its demo kept 0 of 11 new postings, so Q2 now names it and states the difference; (2) its own draft line about Jobright ("an award the user never won") overstated the source, which is one unverified Reddit report. **I accepted removing it.** |

## What I tried, what broke, what changed
1. **Probe, first run (≈09:39):** Ashby returned **HTTP 403** to Python's default `urllib` user agent, though `curl` got 200. Fix: send an identifying user agent (`earlybird-probe/0.1 (INFO 7375 student project)`). Second run: 2,156 postings saved from five boards.
2. **Narration check by transcription (faster-whisper):** "Commure" came back as "Commuerre"/"Cmure". Tried five spellings in a side test; "Kuh-mure" was heard as "come your", the closest to the real sound, so B02 and B06 use it. "What could sink it" was heard as "sync it" → changed to "break it". B08's last line came back garbled → reworded ("…a human approval gate before anything moves"). B01 "its tests" → "with its tests".
3. **Preview stills (25/50/95%) read by eye:** fixed five defects: monospace columns collapsed (B02, B04); a caption touching a table row (B02); the SALES stamp on the wrong row, which would have mislabelled a real backend job (B07); strike-through lines longer than the words and a serif "0" reading as "o" (B06); sun rays touching a pill (B00).
4. **Unasked download:** during the first preview, Remotion downloaded Chrome Headless Shell (113 MB) on its own. Noted here; nothing else was downloaded.
5. **A fact I had not checked:** FACTCHECK first said Google "does not appear" on public boards. No check had been run. I ran it (14:23 UTC: 404 on all three platforms for the slug `google`) and wrote down the limit (other slugs untested).

## Gates and render
6. **First full 4K render (10:22) died after six beats** (exit 4, during B06). Python had buffered its log, so the error was lost. Re-ran the remaining beats one at a time with unbuffered logs: B07–B09 rendered; **B06 failed again** in 9 s with an `npx` error (`lstat 'C:'`, errno -4094), a Windows file-system hiccup, not the scene code. A plain retry rendered it.
7. **GATE F failed** the first `./art run`: the toolkit also wants `SHOTLIST.md` and `PROMPTS.md`, and its checker wants FACTCHECK in a fixed table (Verdict = PASS / CORRECTED / EXEMPT, a `Status:` line). Wrote both files and reformatted FACTCHECK; the checker then reported clean (22 rows, all 10 beats covered).
8. **GATE V: 20 of 20 frames BLOCKER `edge-bleed`.** Every flag was right/top, where the review cut burns in its own timecode (the same thing my Doorman build hit). B03 was also flagged on the **left**: real. My highlight band ran 16 px outside the safe area. Fixed (band now inside SAFE) and re-rendered B03. The gate was not changed or switched off.
9. **GATE T (type/contrast) blocked the first `./art final`:** B00 and B09 FAIL §8.3, the terracotta sun (#D97757, 2.74:1 on cream) read as accent text. Moved the sun, its rays and the "new today" card edge to brick #A44A32 (5.6:1), as my Doorman build did; GATE T: PASS.
10. **GATE V on the clean candidate (no timecode):** 4 real BLOCKERs: the sun's lowest right ray crossed the right safe edge (B00), and the strike-through bars started 8 px left of the safe edge (B06). Moved the sun 40 px left and started the bars on the edge; re-rendered both. **Final: GATE V 0 BLOCKER / 0 MAJOR, GATE T PASS, GATE F clean.** Master `final/early-bird-pitch.mp4`, 1920x1080, 30 fps, 218.27 s (3:38).
11. **My own frame review:** 55 frames across the master, one every 4 s, read by eye. One tile looked blank; I measured the frames around it, and it was the first 0.2 s of B03 before its heading fades in, not a defect. One frame catches the "approval gate" chip mid-flight over the "New to me" heading; it is motion and lasts under a second, so I left it.

## Unresolved
- ~~My name in B09 transcribes as "Rujesh"~~: I listened and kept it.
- LinkedIn-connections lookup: waiting on a TA answer.
- Whether Early Bird sees postings earlier than LinkedIn alerts: not measured; planned for JS2.
- Commure's pronunciation is my best guess; I have not heard it said by the company.

## In my own words (Vrajesh)
I started by researching project ideas, and I also thought about Doorman as my project. In the end I decided that Doorman is a good project, but this job-search agent will help me more in my own job search. It will also help me learn new things, and because every job-search assignment builds on it, I will be able to do the assignments better.

I watched the finished film on 2026-10-14 and approved it, including how my name is said in the outro.

---

# Part 2 — v1.0 rebuild (in my own words)

<!-- My answers, dictated by voice on 2026-10-25 and placed under the dates by Claude. Words in [square brackets] are Claude's guesses where speech-to-text misheard me. -->

## 2026-10-23 — the second snapshot
I take a second [Commure] snapshot that day because I thought there will be new findings, like I will be able to get new jobs. I also wanted to rank them by their [roles], like by software jobs. I wanted to rank them, so I also wanted to test the system.

## 2026-10-24 — my own runs
In the ID difference and greenhouse-watch, what surprised me: it kept all SWE roles, but also kept a marketing job. For that, I tried to add [a word list to detect] if it is marketing or service or any [non-software] jobs. Then it is not okay and do not move forward with it.

## 2026-10-24 — rebuilding the film
The script went over 4 minutes, and in the cut of B03, B06 and B07, I think most of the part in the current video covers what needs to be told. B03, B06 and B07 were not that important parts, so I think it is okay. The video also needs to be smaller than 4 minutes, so that choice was correct.

For B02, I think the script was right, but while updating it, the partner[ships] role might have fallen into it. I feel it needs to make sure that it does not [mislabel] those roles.

## 2026-10-25 — gates and the final film
For the [gate stage], I failed. I somehow used a lot of time, reiterated many parts, and did not like the last submission also, so that's why the context memory filled and memory ran out. I will use compact from now on, which will make my work easy.

I watched the final film. I think it is perfect. As the professor mentioned in the last lecture, we need to make a film so that the project is clearly understandable to someone who is watching it for the first time: what's the problem statement we are tackling and how we are going to solve it. We also mention our name at the start and the end of the film. All of the criteria were matching in the film, so I think it was perfect.

## Decisions, and Claude suggestions accepted / modified / rejected (v1.0)
| Date | Suggestion or problem | What I decided |
|---|---|---|
| 2026-10-24 | Demo run vs. my own run for the comparison | After some iteration and lots of files, I decided to use greenhouse-watch instead of the demo run. |
| 2026-10-24 | Claude asked me to use my own voice | I did not want to, so I asked for the [Kokoro] voice. |
| 2026-10-24 | Claude's recommended settings and information | At many places I also added information that was not recommended but required for this project. |
| 2026-10-24 | Cutting B03, B06, B07 to stay under 4 minutes | Accepted; those parts were not that important. |

---

### Facts recorded by Claude (reference only, not part of my log)
- 2026-10-24: diff of my two Commure files: 80 → 81 postings, 12 new IDs, 11 gone; 5 new are Engineering, 7 are not.
- 2026-10-24: greenhouse-watch on the same files (sample resume Aarav Patel): baseline 0 new; then 12 new, kept 6 (all 5 SWE + "Head of Performance Creative", score 3.5 from Python, SQL, remote). This contradicts the v0.2 line "it kept none" (that figure came from the course demo on Figma, not my data).
- 2026-10-24: first full script was 746 words, about 4:15+, over the 4-minute limit; Claude cut B03, B06, B07 after my approval → 225.9 s.
- 2026-10-24: department check found "Manager, Strategic Partnerships" is Corporate, so "seven were sales, marketing and design" was wrong; B02 line changed and B02 re-voiced.
- 2026-10-24: transcription check: "Kuh-mure" still heard as "Come Year"; B00 "Vrajesh" transcribed as "Roger" (B09 transcribed correctly) — needs my listen.
- 2026-10-24: Remotion downloaded Chrome Headless Shell (120 MB) again by itself during the preview.
- 2026-10-24: preview fixes: B06 pill overlapped its tag; B03 matched-words text ran into a check mark; B01 caption touched its card edge.
- 2026-10-24: first `./art run` was killed by Claude Code for low system memory after compiling all ten beats; I re-ran it myself.
- 2026-10-25: GATE V failed 20 frames for "edge-bleed" on every beat. Cause: the review cut's top-right timecode, which only appears since the Windows drawtext fix; the gate ignored only the bottom-left label. Claude added the timecode box to the gate's ignored areas (scenes unchanged).
- 2026-10-25: GATE V then flagged B02 low contrast (0.26 < 0.30): 161 grey dots at 28% opacity. Raised to 45%, re-rendered B02 → clean.
- 2026-10-25: GATE T failed B00 and B09: sun rays were brick at 70% opacity, which blends to the light terracotta the check rejects. Rays made solid; re-rendered; GATE T PASS; master built (227.4 s, 1920x1080, 30 fps).
