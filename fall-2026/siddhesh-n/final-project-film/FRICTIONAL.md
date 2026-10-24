# FRICTIONAL — dated log

Honest notes on what happened, what broke, and what I did instead. Newest at the bottom.

## 2026-10-14 — picking the project, writing the plan (with Claude)
- Gave Claude the assignment and the toolkit link. Chose the project from three options it suggested from my GitHub: **CheckedSQL**, a checked SQL question tool for marketing data. It builds on my `marketing-campaign-analytics` repo.
- Claude cloned brutalist.art and read the show-tell skill. Two things in the toolkit would have broken the assignment rules:
  - show-tell's default greeting is "Liam, in for Bear".
  - The stock outro `ClaudeTitleOutro` hard-codes `@NikBearBrown` on screen; it has no prop to change it.
  The narration now says my name, and the outro is my own Manim title card. `bookend_check.py` still passes because it only checks the outro's props.
- Claude couldn't render the film: `pip` and `npm` downloads are blocked in its workspace (PyPI 403 through the proxy). So the film gets rendered on my Mac. Claude ran the gates that need no Manim (A, W, L, bookend), and all passed after one fix: B08's test page started outside the safe area, so it now fades in on stage instead.
- Open question: whether Kokoro says "Siddhesh Nikam" correctly. I'll listen to BIDEA and BOUT after the audio step.

## 2026-10-14 — install and render on my Mac
- Homebrew installed Python 3.15; I made a Python 3.13 environment (brutalist-env) and turned off Anaconda (conda deactivate) so Manim and Kokoro would install cleanly.
- ./setup --install worked. It hung at the end on its ElevenLabs file search, so I stopped it with Ctrl+C after all installs had finished.
- build_film.sh run 1: voice and all 14 scenes rendered; gates A, W, L, B, V passed. Gate T FAILED on BDEFS (terms card): smallest text 40px < 41px floor.
- Fix 1: reworded the three definitions so no word was all short lowercase letters. Gate T still failed at 40px.
- Fix 2: the real cause was ClaudeDefinitions drawing meanings at 48px, which puts EB Garamond's x-height at 40px at 4K. Changed meanSize 48 -> 52 in my local toolkit copy (runtime/remotion/src/scenes/ClaudeDefinitions.tsx), rebuilt. Gate T PASS.
- My build script looked for the master in the reel folder, but ./art final writes it to brutalist.art/renders/. Copied it over and ran the last gates by hand: MASTER PASS (3840x2160, 24fps, 188 s), LOUDNESS PASS, BOOKEND PASS.
- Final film: 3 min 8 s.

## 2026-10-24 — feedback, then the first runnable piece (with Claude)
- Got the grade: 41/50. Deductions: P2 unique value −1 (the chat-assistant comparison was described, not tested), P6 shown-not-asserted −0.5 (generic props), Frictional −1 (short log, template note left in). The professor's next step: ten questions with hand-computed answers including ROAS, and a checker printing a score table for my own queries.
- Built that next step in `checkedsql/` with Claude:
  - 24 rows of synthetic campaign data (3 channels × 2 devices × 4 weeks), small enough to check on a calculator.
  - Ten questions, two of them ROAS ratio questions.
  - An answer key computed in plain Python with no SQL (`answer_key.py`), so it doesn't share code with the queries it grades. `HAND-CHECK.md` lists every subtotal.
  - Ten baseline SQL queries (Claude drafted them) and `checker.py`, which refuses anything but a single SELECT.
- First design problem: I wanted the ROAS trap to actually change an answer, not just a decimal. I tuned the Email rows (four tiny-spend Mobile rows with 14–20× returns) until the row-average winner (Email, 9.75) differed from the total ÷ total winner (Search, 3.98).
- First checker run: **10/10**. Then I added two deliberately wrong queries that average ROAS row by row (Email 9.75 instead of 2.29). The checker failed both, so it does catch the risk named in my pitch.
- Looked at classmates' public pull requests and one classmate's film for the standard, not the content. The stronger ones carried evidence from something that ran, and they labelled what's real versus planned on screen. I did not copy anyone's visuals or text.
- Redesigned the film:
  - Each scene now has a top line naming which of the seven questions it answers, and an honesty badge: REAL (dated) or PLANNED (sketch).
  - Generic props were replaced with real things: the actual test question, the real file names, the real `python3 checker.py` command and score, a score-table card with the trap row, Email's eight real row ratios, and the true ROAS per channel.
  - The chat-assistant beat now shows my real test instead of a description.
- Claude still can't render here (package downloads blocked), so it ran the render-free gates (A static pre-flight, W contrast and margins, L beat lint, bookends): all clean. It hand-checked the layout and moved five labels that would have touched shapes.
- Ran the chat-assistant test myself:
  - Downloading `checkedsql.zip` from the chat didn't work, so I recreated `campaigns.csv` in Terminal. The first paste got cut off at `4,Social` and left the shell stuck at `heredoc>`, so I cancelled and pasted it in two smaller blocks.
  - In a new ChatGPT chat (GPT-6.1 Sol Light) with the CSV attached, I asked "Which channel had the highest ROAS in this data?" It answered **Search, 3.98×** (Email 2.29×, Social 1.05×), matching my key exactly. So it did not fall into the trap.
  - That changes what I can honestly claim. The difference isn't that a chat assistant gets it wrong; it's that one right answer isn't a measured hit rate, and I couldn't see its query. The film now says exactly that.
- Gate T can't exempt a screenshot (the exemption is a fixed list inside the toolkit, and I didn't want to edit the checker), and the full table's text would be under the 41px floor. So the film shows only the cropped answer sentence, large; the full screenshot is in `build/`.
- Checked the key by hand: 38860 ÷ 14185 = 2.74 (Q03), 6150 ÷ 2685 = 2.29 (Q07), 28000 ÷ 7030 = 3.98 (Search, Q06) on a calculator. All three match.
- **Correction:** v1 of the film and brief said the Tableau dashboard in my marketing-campaign-analytics project was "one I built". It wasn't; I made it with AI help. Fixed the narration (B02), the brief, and the fact-check, and the dashboard scene is now labelled a sketch.
- **Second correction, same reason:** v1 said "SQL, PostgreSQL and pandas, I already have", with my marketing-campaign-analytics repo as evidence. AI wrote most of that repo. Rewrote "Why this project?" as mostly learning: the repo shows the domain, not my coding. Writing and checking SQL myself is now listed as new, and from here on I write the queries for new test questions. Also changed B05 so it no longer says "which I already have".


## 2026-10-24 (afternoon) — v2 render on my Mac
- Downloading the v2 zip from the chat failed twice; the download page Claude made worked. Copied it into class-repo; checker 10/10.
- Render 1 (--fresh): all 15 scenes drew and Gate B was clean. Gate V BLOCKER on B10: edge-bleed at 85%, because pages dropped in from above the frame. Fix: pages fade in on stage instead (B01 and B10).
- Render 2: Gate V clean. Gate T FAILED on B03: my dark-mode ChatGPT screenshot read as one big text block with low-contrast text inside (1.43:1). Fix: show the same crop with colours inverted, labelled on screen.
- Render 3: every gate PASS (V, T, MASTER 3840x2160 24fps 214 s, LOUDNESS -24.56 LUFS, bookends). Film: 3 min 34 s.
- Before resubmitting, Claude audited the pushed v2 against the assignment and the feedback. Fixed: the brief was 1,161 words (two pages), now one page (704 words), with three leftover "my own SQL" claims corrected and the two lists separated; three visible layout mistakes in B00 (question text spilling out of its card), B01 (file names running into the next column) and B02 (label still fading in at the end). Re-rendered those three scenes; every gate PASS again.
