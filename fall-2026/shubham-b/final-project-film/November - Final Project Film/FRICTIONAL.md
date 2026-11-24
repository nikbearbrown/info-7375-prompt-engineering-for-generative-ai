# FRICTIONAL — A11yProof project film

A log of friction: what got in the way while making the film, and what was done about it. All entries are 2026-11-23, US Eastern time.

- **01:18** I chose to pitch an agentic system. I asked for options that would read as real impact for SWE and FDE roles, and asked to keep the project isolated from my other course work.
- **01:26** I asked for two more options, then picked the accessibility agent (named FixProof at the time).
- **01:37** The toolkit's bundled espeak-ng refused the session folder's path because it was over its 159-character limit. Claude wrote `tts.py`, a wrapper that runs Kokoro from a short path.
- **01:43** The first Remotion preview failed with a ZodError: the hesitant-writer props must be strings. Claude fixed it in the beat sheet.
- **01:46** The card stacks read out of order, because the stack component orders items centre, left, right. Claude reordered them. The typed summary also did not finish before the cut, so Claude shortened it.
- **01:49** GATE F refused to render without FACTCHECK.md, SHOTLIST.md and PROMPTS.md. Asked Claude draft them first.
- **01:50** Claude's helper agents were blocked: the context-mode plugin's hook modified agent prompts, and auto mode rejected them. The Opus 5.5 review ran in the same session instead. I had the plugin turned off.
- **02:05–02:41** GATE V flagged empty space (underfill) on B02 and B16, and an edge-bleed on B02. Claude fixed them with the verdict card's lecture layout, a three-panel summary, and 88 px text.
- **02:24–02:37** GATE T §8.1 (minimum text height) failed on tables. Enlarging the font made its reading smaller (40 to 37 px), so it is a false positive. Claude reverted the change and compiled the master directly with `compile.py`; GATE V still passed.
- **02:44** The first 4K master (4:31) and REVIEW.md were done.
- **~16:10** I confirmed the course name on the title card.
- **16:28** I renamed FixProof to A11yProof: reading the name, you could not tell it was about accessibility. The narration says "A-eleven-Y Proof" and explains a11y once. There is no speech-to-text model on the machine, so the pronunciation is unchecked by any tool.
- **16:52** The outro and table cards showed the professor's handle, @NikBearBrown, hardcoded in the toolkit. I had it replaced with my name through a new `handle` prop, and Claude re-rendered.
- **17:02** I found the "Final Project Film" folder I had made was empty, because the session had started without a folder. I moved the session there once the render and packet were done.
- **17:05** Setting `channel_title` in the beat sheet made the compiler stamp my name a second time under the title card. Claude removed it, but re-running `build_sheet.py` alone wiped the measured audio timings, and `compile.py` refused ("narration duration disagrees"). Lesson: after any `build_sheet.py` run, always re-run `tts.py` and `./art run` before compiling.
- **22:29** I watched the whole film end to end with sound.
- The film was build using Claude Code - Opus 5.5 using Brutalist toolkit by Prof. Nik Bear Brown.
