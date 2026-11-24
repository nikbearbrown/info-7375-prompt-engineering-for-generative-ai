# FRICTIONAL — DayThread Final Project Film (2026-11-23)

Dated log for the Final Project Film (Canvas "Final Project Film", 25 points, due Monday
2026-11-23 23:30). Entries are written as the work happened. Claude kept the log; Aditya's
decisions are quoted or paraphrased from Aditya's messages in this session. Earlier entries for the
October pitch film are in `../final-project-film/FRICTIONAL.md`.

## 2026-11-23 ~15:15 EST · What the new film has to do

- **Aditya's starting point:** the October pitch film (seven questions) no longer fits. The new
  assignment asks for four parts in a fixed order: executive summary, what others have done,
  methods, evaluation. The professor also named two requirements for the final project: a
  **delegation contract** and a **custom-trained model** (a Hugging Face model fine-tuned by the
  student).
- **What Claude checked first:**
  - The course repo for the terms. It found no page titled "delegation contract". Chapter 10
    defines delegation as "a contract, not a partition of labor" with a testable handoff
    condition on each edge. The plan uses that definition.
  - The professor's Frictional repo. It is an evidence-audit tool (artifact vs process evidence),
    not a grader. Nothing says it will be used on this submission.
  - Aditya's folders. No DayThread code exists beyond the 2026-10-25 replay; no `final-project/`
    folder exists in the course repo.
- **Aditya's decisions (answers to Claude's questions):** keep the name DayThread; finish and
  upload tonight; Kokoro voice again, roughly the same length as before; use the recommended
  checker task (flag concerning sentences, not a summary-faithfulness model).

## 2026-11-23 ~15:40 · A source I dropped

- **Tried:** adding one published study on AI summaries of clinical text to part 2, so it would
  report what others *got*, not just what they sell.
- **What happened:** the article page returned a login redirect to the fetcher; nothing was read.
- **What I did:** dropped it. Neither Aditya nor Claude has read it, so the film can't cite it.
  Part 2 uses only the four Lifeline and DailyCall pages Aditya read on 2026-10-14, plus Aditya's own
  replay result.
- **Still open:** part 2 has no independent research result. That is a real gap for the final
  project's background section.

## 2026-11-23 ~15:45 · Facts checked before writing the script

- `distilbert/distilroberta-base`: licence Apache-2.0, public (Hugging Face API, no login).
- Laptop: MacBook Pro, Apple M3 Pro, 18 GB (`sysctl`).
- **Unexpected:** PyTorch is **not** installed in the film's conda env, and the system `python3`
  is an Intel build. The film therefore says training *will* run on the laptop, not that it
  does. Installing an arm64 PyTorch is the first technical step after the film.

## 2026-11-23 15:57 · Script v1, then narration

- Claude drafted `SCRIPT.md` (18 beats, four parts, 594 words). Past tense only for the replay;
  everything else future tense.
- Narration measured at 192 s against a 238 s word-count estimate. Kokoro reads faster than the
  October pace suggested.
- **Machine transcript problems:**

  | Beat | Heard | Fix |
  |---|---|---|
  | B11 | "SQLite" as "Escuelite" | spelled S-Q-Lite for the voice |
  | B14 | "go in on purpose" as "going on purpose" | reworded: "will be included on purpose" |
  | BOUT | "Aditya Raj" as "addediraj" | reused the October film's audio for the identical line |

  The October BOUT audio is *also* heard as "addediraj" by this small.en transcriber, so this is
  a transcriber limit, not a voice change. "Claude Code" heard as "clawed code" was left alone:
  that's how Claude is pronounced.

## 2026-11-23 16:10–16:31 · Render and gates

- **GATE F failed:** no FACTCHECK.md / SHOTLIST.md / PROMPTS.md yet. Wrote them and re-ran.
- **GATE B (layout) failed twice**, on labels outside the safe area: B02 "meaning changed: 9 of
  10", then B07 "bound to what was seen". From the measured width (about 0.2 units per
  character) Claude predicted two more in B12 and fixed all four before the next run. The next
  run passed.
- **GATE T failed** on B16: the claim slip (an outlined paper with a scribble) read as two
  overlapping text blocks at the midpoint frame. The October B03 had the same problem. Fix: the
  slip enters after the midpoint. Re-run: PASS.
- **Claude's own frame check** (15/50/90 % of every beat): B06's "stop" label sat under
  "handoffs" and read as one block. It was moved above the bar and B06 re-rendered.
- **Final master:** all gates pass (F, L, A, W, B, V, T). 3840×2160, 24 fps, 193.1 s, full
  decode clean. SHA-256 `71cd2573…0faf`.

## Human and AI contributions

- **Aditya:** the project and its October brief; the replay prediction and review; the four
  decisions above; the voice and length choice; watching and approving or rejecting the film
  (pending).
- **Claude:** reading the two rubrics and the course repo; the plan; script v1; scene code;
  paperwork; running the toolkit and checks; this log.
- **Accepted / changed / rejected:**
  - Aditya accepted the recommended checker task over a faithfulness model.
  - Claude rejected citing an unread paper.
  - Aditya chose upload tonight over building a slice first, so nothing new is shown as built.

## Next (after Aditya watches the film)

- Approve or ask for changes.
- On approval: post the folder to `fall-2026/aditya-r/final-project-film-2/` and upload the MP4
  to Canvas. Neither has happened.

## 2026-11-23 ~16:50 EST · Aditya approved the film; posting

- **Aditya, after watching:** "I like the video that you have created, so we are going to push this
  to both GitHub and Canvas."
- **Aditya's request:** push the video and the relevant content to the GitHub folder under the
  name, and prepare a ZIP plus the Canvas details.
- **One change from the request:** the course repo's `.gitignore` excludes every `*.mp4` and
  `*.mp3` (lines 32–33). The final-project spec also says "keep MP4s out of GitHub". So the
  film and narration go in the Canvas ZIP only, as in October. Claude did not force-add them.
- **Posting (Claude; written before the push):**
  - copy this folder to `fall-2026/aditya-r/final-project-film-2/`;
  - commit with the same author identity as earlier submissions;
  - push to `main` without force;
  - build the Canvas ZIP from this same folder.

  The commit hash and the ZIP checksum go in the Canvas text, since a file can't contain its own
  hash.
