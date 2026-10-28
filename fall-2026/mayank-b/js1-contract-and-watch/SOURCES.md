# SOURCES: Job-Search Agent 1

## What I used
- **Persona:** Priya Nair, fictional, from The Reallocation Engine (`search/examples/priya-nair/resume.example.json` and `profile.yml`). My copy adds a `search` block (see CONTRACT.md, In).
- **Board:** Anthropic's public Greenhouse job board API, `boards-api.greenhouse.io/v1/boards/anthropic/jobs`. Public, no login.
- **Library:** `@anthropic-ai/sdk` 1.3.0 (Anthropic's official JavaScript SDK) for the Claude judge.
- **Course material:** the JSA 1 brief, Chapters 1 to 3, and Professor Bear's AI policy.
- **My earlier project:** Applications Made Easy (my job-aggregator workflow). The whole-word matching rule and the substring and paired-items bugs behind W1 and W2 are lessons from it.

## What I wrote
- My answers to the contract questions (`notes/contract-questions-with-my-answers.md`): the board choice, the relocation change to the persona, the inputs, the output, the refusals, the rule, the wrong versions W1, W2, W5 and their test cases, and the failure sentence.
- _pending: my hand labels and labeling rule, the prompt revision, the action-surface comparison, the sign-off, the driver's seat, FRICTIONAL.md._

## What Claude contributed (Claude Code, model Claude Opus 5.5)
- **Contract help:** the guided question sheet (explanations, options, suggestions, and facts about the board checked on 2026-10-28). It then rewrote my answers into CONTRACT.md in clearer sentences at my request and made the six corrections listed at the end of CONTRACT.md.
- **Code:** all of `src/`, `scripts/` and `prompts/judge-v1.md`, written against CONTRACT.md after it was committed.
- **Tests:** all test code in `tests/`. The W1, W2 and W5 cases (inputs and expected results) are the ones I specified in CONTRACT.md before any code existed. Claude added the extra tests (whole-word edge cases, location splitting, the validator, the allow-list, the persona checks, writes outside the folder) and the constructed fixtures.
- **Drafts:** README.md (structure, toolchain and commands) and this file's structure. The FRICTIONAL.md structure comes from the template Claude made on 2026-10-24.
