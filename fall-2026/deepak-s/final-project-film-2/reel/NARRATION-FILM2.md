# CueGate film 2: narration (source for make_sheet.py)

Built from inputs-film2/FILM2-SCRIPT.md (2026-11-23) with Deepak's overrides of 2026-11-23:
branch A for E3 and V5b (RESOURCES item 5: no CueGate application code runs), the four
override-3 rewordings (M3, M4a, V2, V3), the resources line (M5b) filled from RESOURCES.md, Deepak's
STOP A decisions of 2026-11-23 (E2b, E3, M5b, M2, V4a, V4b), and the runtime trims listed in TRIMS below. One row per beat. Speaker is DEEPAK (Kokoro am_onyx) or
SKEPTIC (Kokoro af_bella). make_sheet.py reads this table verbatim.

| Beat | Script | Act | Speaker | Narration |
| --- | --- | --- | --- | --- |
| B01 | E1 | 1 | DEEPAK | On October fourteenth, I asked Claude to shorten one subtitle line, so a viewer could read it in time. It fit. It kept both negatives. And it still shifted the tone of what the character said. |
| B02 | E2a | 1 | SKEPTIC | It's one line. Who cares? |
| B03 | E2b | 1 | DEEPAK | Anyone who ships subtitles. Streaming platforms set hard limits on how fast a line can be read, and delivery guides say files that break them get sent back. In the tools I checked, shortening a line is still something a person does, one line at a time. |
| B04 | E3 | 1 | DEEPAK | So CueGate is the tool I'm going to build. You give it a subtitle file and the film. It will hand back a file where every line fits the rules, and anything it can't fix safely will go back to a person, with the reason. |
| B05 | E4a | 1 | SKEPTIC | And why would I trust it more than the AI button I already have? |
| B06 | E4b | 1 | DEEPAK | Because it won't just claim the line still means the same thing. It will measure how often it's wrong, and publish that number. |
| B07 | I1 | 2 | SKEPTIC | Hasn't someone already done this? |
| B08 | I2 | 2 | DEEPAK | Partly. Subtitle Edit and Editsub both have an AI action that shortens the line you're on. EZTitles runs automated checks that flag reading-speed problems. In all three, a person picks the line and decides. |
| B09 | I3 | 2 | DEEPAK | Researchers have worked on length too. In 2019, a team in Trento and at Amazon showed a translation model can be steered to write shorter output. In 2020, a Trento team found that for subtitles, hitting forty-two characters isn't enough. Timing and the rhythm of speech matter too. |
| B10 | I4a | 2 | SKEPTIC | So what's missing? |
| B11 | I4b | 2 | DEEPAK | What they got was shorter text. What none of the tools I checked publish is how often that shortening changes meaning. That's the gap CueGate will go after: a gate over the whole file, and a number you can check. |
| B12 | M1 | 3 | SKEPTIC | Okay. How? |
| B13 | M2 | 3 | DEEPAK | First, the data. The English subtitles of Tears of Steel, an open Blender film. The film is Creative Commons, but the subtitle file's own licence isn't stated, so I'll confirm it before it goes in the repo. If I can't, I'll write my own dialogue and label it synthetic. Clean files rarely break rules, so I'll squeeze their timing on purpose. That gives me failures where I still know the original line. |
| B14 | M3 | 3 | DEEPAK | Then the pipeline. Read the file and turn every time into exact frames. Check every rule. Fix timing first, because that changes no words. Only the lines timing can't save go to a small open model running on my laptop, with an exact character budget and a list of words it must keep. Every answer comes back through the same checker. |
| B15 | M4a | 3 | SKEPTIC | And when the model gets it wrong? |
| B16 | M4b | 3 | DEEPAK | It gets three tries, each with the reason it failed. After that, the line stays untouched and goes to a person. The gate fails closed. |
| B17 | M5a | 3 | SKEPTIC | Do you actually have what you need? |
| B18 | M5b | 3 | DEEPAK | No API key, and none needed to start: the rule checks and timing fixes need no model. Compute is my sixteen-inch MacBook Pro, M3 Pro, thirty-six gigabytes of memory, no cloud. The subtitle licence isn't confirmed; synthetic dialogue is the fallback. The models will be public models that download and run locally. I'll pick small ones here, after freeing disk space. |
| B19 | V1 | 4 | SKEPTIC | Last one. How will you know it worked? |
| B20 | V2 | 4 | DEEPAK | I'll run four versions on the same lines. A dumb cut at the budget. A single "shorten this" call to the same model. CueGate without its meaning check. And full CueGate. Then I'll label a hundred shortened lines myself, without knowing which version wrote them. |
| B21 | V3 | 4 | DEEPAK | It worked if full CueGate ships zero rule breaks, and changes meaning less often than that single call. It failed if it changes meaning just as often, however clean the timing looks. And if it sends most lines back to a person, it saved nobody any time. I'll report that as a failure too. |
| B22 | V4a | 4 | SKEPTIC | And who checks the checker? |
| B23 | V4b | 4 | DEEPAK | I'll count how often the meaning check waved through a line I marked as changed. That number goes in the report, even if it's ugly. |
| B24 | V5a | 4 | SKEPTIC | You say "will" a lot. |
| B25 | V5b | 4 | DEEPAK | Because most of it doesn't exist yet. Today there's the plan, the research, and that one dated Claude reply. No CueGate code runs. Everything else is "will", on purpose. |
| BOUT | OUT | 4 | DEEPAK | CueGate. Subtitles that fit the frame, or don't ship. I'm Deepak Kumaran. |

## TRIMS

None. Measured with Kokoro on 2026-11-23, after the STOP A decisions: 220.66 s of speech, 234.68 s (3:54.7) with the pad_audio.py pauses and the outro tail, under the 4:00 limit.
