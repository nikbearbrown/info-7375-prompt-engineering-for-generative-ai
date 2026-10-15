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

<!-- ADD YOUR OWN ENTRIES BELOW, ONE PER WORK SESSION, WITH THE REAL DATE. Write what you ran, what broke (paste the exact error line), what you changed. Delete this comment. -->

## 2026-10-14 — install and render on my Mac
- Homebrew installed Python 3.15; I made a Python 3.13 environment (brutalist-env) and turned off Anaconda (conda deactivate) so Manim and Kokoro would install cleanly.
- ./setup --install worked. It hung at the end on its ElevenLabs file search, so I stopped it with Ctrl+C after all installs had finished.
- build_film.sh run 1: voice and all 14 scenes rendered; gates A, W, L, B, V passed. Gate T FAILED on BDEFS (terms card): smallest text 40px < 41px floor.
- Fix 1: reworded the three definitions so no word was all short lowercase letters. Gate T still failed at 40px.
- Fix 2: the real cause was ClaudeDefinitions drawing meanings at 48px, which puts EB Garamond's x-height at 40px at 4K. Changed meanSize 48 -> 52 in my local toolkit copy (runtime/remotion/src/scenes/ClaudeDefinitions.tsx), rebuilt. Gate T PASS.
- My build script looked for the master in the reel folder, but ./art final writes it to brutalist.art/renders/. Copied it over and ran the last gates by hand: MASTER PASS (3840x2160, 24fps, 188 s), LOUDNESS PASS, BOOKEND PASS.
- Final film: 3 min 8 s.
