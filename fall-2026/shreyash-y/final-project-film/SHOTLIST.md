# SHOTLIST — Quote It or Refuse.

## Executive summary

The work order for the film: what fills each of the 14 beats. Every beat is made by the
free local pipeline (Remotion or Manim). There are no open slots, no stock footage, no
screenshots, and no AI-generated images.

| Beat | Idea (brief question) | Fill | Component / scene |
|---|---|---|---|
| B00 | Cold open: the examiner's question; nothing is built (Q1) | Remotion | `ClaudeComposerAsk` (output lines say no answer is shown) |
| B01 | One-sentence summary (Q1) | Remotion | `BrutalistHesitantWriter` ("a smarter chatbot" → "a citation checker") |
| B02 | The problem: a citation nobody checks (Q2) | Manim | `B02_UncheckedCitation` — CONSTRUCTED |
| B03 | What it is: the planned pipeline (Q1) | Manim | `B03_Pipeline` — PLANNED |
| B04 | The prompt contract (Q4) | Remotion | `ClaudeCodeBeat` — PROPOSED |
| B05 | Alternatives I tried (Q2) | Manim | `B05_Alternatives` |
| B06 | Who opens it; first sixty seconds (Q3) | Manim | `B06_FirstMinute` — CONSTRUCTED MOCK-UP |
| B07 | What it proves, and what it doesn't (Q4) | Manim | `B07_SkillsToEvidence` |
| B08 | In / out / first (Q5) | Manim | `B08_Scope` |
| B09 | Risk and mitigations (Q6) | Manim | `B09_Risk` |
| B10 | Why this project: have vs new (Q7) | Manim | `B10_HaveVsNew` — real Dovetail test output |
| BVDT | Exists today vs will exist | Remotion | `ClaudeVerdictArtifact` |
| BHTF | Your turn: a prompt to try | Remotion | `ClaudeComposerAsk` |
| BOUT | Title restate, my name, course | Manim | `BOUT_Title` (replaces `ClaudeTitleOutro`, which hard-codes the instructor's handle) |
