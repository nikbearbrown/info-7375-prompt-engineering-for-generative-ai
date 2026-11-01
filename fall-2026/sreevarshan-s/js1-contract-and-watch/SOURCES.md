# Sources and assistance

## My words (verbatim)

**Q29.** I decided and wrote the contract myself across drafts 0–7: the target roles, skill requirements, sponsorship behavior, experience limits, clearance rules, privacy restrictions, and evaluation approach. I answered the assistant's critique questions in my own words, and Claude Code saved those answers verbatim. I'll also do the independent hand labels and personally verify the final submission.

**Q30.** Claude Code handled project file creation, Git operations, implementation work, and automated tests. I'll identify which files it generated and which changes I reviewed. I won't claim unfinished components have been implemented. [correction: Claude Code made most commits, but I made four myself: `0dd01ab`, `d7411f4`, `4a46925` and `6064e8e`.]

**Q31.** The Claude chat assistant critiqued my contract drafts, pointed out contradictions and gaps, asked the questions I answered, and gave me the exact prompts to paste into Claude Code. It declined to draft the contract for me. I'll distinguish that help from my own decisions and testing.

**Q32.** The main sources are the INFO7375 assignment instructions and course chapters, the Reallocation Engine's fictional Priya persona, the public Databricks Greenhouse job data, and the documentation for the tools actually used. I'll list the exact sources and any additional references used during implementation.

## Disclosures

**Assistance:**
- **Hand labels (ChatGPT):** ChatGPT formatted my handwritten label notes into the table in `labels/HAND_LABELS.md` (commit `f55b88d`). It chose no labels or reasons.
- **Draft 8 (chat assistant):** the Claude chat assistant worded option B, which I chose in Draft 8 (`b8a5b81`). The draft says so: "I chose option B, as worded by the chat assistant".
- **Facts table (chat assistant):** before I labeled, the Claude chat assistant made a facts-only table from the label sheets in `labels/sheets/`. It listed title, location, years asked and other facts. This table is not in the repo.
- **Sampling postings (chat assistant):** the Claude chat assistant proposed the 5 sampling postings (`experiments/sampling/`), and I accepted them.
- **Claude Code** did four things:
  - It arranged my verbatim contract sentences into the Final section of `CONTRACT.md`, with source tags.
  - It wrote all the code and tests: `js1/`, `experiments/*.py` and `tests/`.
  - It wrote the label sheets and the method paragraph in `LABEL_SET.md`.
  - It wrote the factual parts of the reports: `IMPLEMENTATION_CHOICES.md`, `experiments/SAMPLING_REPORT.md`, `experiments/ACTION_SURFACE.md`, and this file, `README.md` and `FRICTIONAL.md`.

**Data:**
- **Persona:** Priya Nair is fictional. `persona/priya-nair.resume.json` is a byte copy, and `persona/priya-nair.profile.json` is a JSON copy of `profile.yml`. Both come from the Reallocation Engine repo, `search/examples/priya-nair/`.
- **Postings:** the public Databricks Greenhouse board, `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true`. One single posting came from `https://boards-api.greenhouse.io/v1/boards/databricks/jobs/8546367002` for the action-surface comparison. The raw responses are saved under `evidence/raw/` and `experiments/action_surface/`.

**Tools:**
- Python 3.13.9 (standard library)
- the `claude` CLI v2.1.117, with model `claude-sonnet-4-6`
- the Claude app (Sonnet 4.6, incognito, web search off) for sampling
- git
