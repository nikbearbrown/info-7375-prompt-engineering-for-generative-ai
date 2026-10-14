# SHOTLIST — final-project-pitch-nishant-u
## Total: 3:53.9 (233.89s) · 15 beats · 16:9 · show-tell (2 Remotion bookends + 13 isometric Manim)

Durations are measured Kokoro `am_michael` narration (`mp3/timings.json`, 2026-10-14; BIDEA, B03, B05, B08, B11 and BEND re-voiced the same day; B05 and B11 again after their final wording). BIDEA includes its
0.8 s lead silence. No gaps or tail padding are added. Nothing is rendered yet; Manim classes are named
but `manim/scenes.py` is not written.

Show-tell rules kept: one isometric drawing per body beat (`templates/iso_kit.py`, Claude palette), labels
of 1–3 words with at most 3 per beat, text size ≥ 32, everything inside ±6.2 × ±3.3. No people are drawn
(the toolkit's portrait rule would put Professor Bear on screen), and there are no LinkedIn or Jobright logos,
only generic shapes with the names as text. Every picture of the agent's output carries an on-screen
**constructed** label, because none of it exists yet. No `ShowTellCard` beats.

| Beat | Start | Act | Lane | Medium | Source/Pattern | Duration | Labels on screen | Constructed | Notes |
|---|---|---|---|---|---|---|---|---|---|
| BIDEA | 0:00.0 | THE QUESTION | bookend | REMOTION | BrutalistHesitantWriter | 12.82s | (typed text) | no | Types "How do I find more job postings"; corrects "more job postings" → "postings worth my time" |
| BDEFS | 0:12.8 | TERMS | bookend | REMOTION | ClaudeDefinitions | 16.92s | Two verdicts · Evidence labels · Human gate | no | `folderLabel: ""`; `durationSeconds` 16.92 |
| B00 | 0:29.7 | WHAT IT IS | manim | MANIM | B00_Agent | 13.44s | job boards · agent · constructed | **yes** | Board stacks feed postings along a belt into the agent block; resume page beside it; one page into a shortlist tray |
| B01 | 0:43.2 | THE ARTIFACT | manim | MANIM | B01_Repo | 15.62s | GitHub repo · evidence packet | no | Open box; code page, test sheet, log page, ten-page stack, film frame rise out |
| B02 | 0:58.8 | ALTERNATIVES | manim | MANIM | B02_Alerts | 12.52s | LinkedIn Job Alerts · why? | no | Generic envelope drops postings; blank reason tags |
| B03 | 1:11.3 | ALTERNATIVES | manim | MANIM | B03_Jobright | 18.97s | Jobright · careery.pro review, 2026 | no | Generic dial-and-funnel machine; history ledger feeds the funnel. Source label on screen |
| B04 | 1:30.3 | THREE DIFFERENCES | manim | MANIM | B04_ThreeWays | 14.70s | supported · insufficient · constructed | **yes** | Quote bracket + check; open ring on a blank stretch; send arrow stopped at a gate |
| B05 | 1:45.0 | FIRST 60 SECONDS | manim | MANIM | B05_SixtySeconds | 18.01s | shortlist · skipped · constructed | **yes** | Laptop (no person); command types; three trays slide out |
| B06 | 2:03.0 | WHAT IT PROVES | manim | MANIM | B06_Proves | 17.54s | loop · budget · gate | no | Agent block laps a loop; budget meter drains; exit gate opens at a fixed lap; padlock on a tool port |
| B07 | 2:20.5 | THE EVIDENCE | manim | MANIM | B07_Evidence | 12.29s | tests · held-out eval · constructed | **yes** | Test sheet; evaluation sheet with five failure rows; a cross lands on the predicted row |
| B08 | 2:32.8 | OUT AND FIRST | manim | MANIM | B08_OutFirst | 17.77s | out · one board · state file | no | Send, mail, key struck through; one board + one resume remain; state file drops in |
| B09 | 2:50.6 | THE RISK | manim | MANIM | B09_Risk | 14.46s | insufficient · abstain · constructed | **yes** | Blank posting; hollow check becomes an open-ring tag; gauge rises |
| B10 | 3:05.1 | WHY THIS PROJECT | manim | MANIM | B10_Skills | 20.63s | I bring · new to me | no | Two shelves: solid blocks (existing), ghost blocks filling in (new) |
| B11 | 3:25.7 | EXISTS VS WILL | manim | MANIM | B11_ExistsWill | 14.95s | exists today · will exist | no | Three solid boxes with checks; ghost outline of the B01 repo box |
| BEND | 3:40.6 | CLOSE | manim | MANIM | BEND_Close | 13.25s | Nishant U · Job-search agent | no | Ghost repo box settles; name and working title land |

Persona bookends dropped at the author's request (I narrate as myself): no composer cold open, no verdict
card, no BHTF Your Turn, no BOUT `ClaudeTitleOutro` (its handle is hard-coded to `@NikBearBrown`). Declared in
`beat_sheet.json` `metadata.bookend_exempt`. Two skin-lint warnings (BIDEA cold open, BEND outro) are expected.
