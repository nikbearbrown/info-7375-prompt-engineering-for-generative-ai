# FRICTIONAL — dated work log, Early Bird pitch film

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
