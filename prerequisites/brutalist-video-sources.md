# Brutalist prerequisite: sources and migration notes

The [NEU-only prerequisite](brutalist-video.md) was prepared on 2026-09-06 by searching the instructor's `books/` tree for beat-sheet JSON containing “Brutalist” (case-insensitive), then reading the relevant narration and current toolkit files. A matching brand/component name alone was not treated as a tutorial.

## Instructor tutorials used

These source beat sheets are under `../humanitarians-youtube/claude-for-design/`, relative to the course root. They are not bundled; use the named tutorial in the instructor-supplied materials. Public video URLs were not present in the inspected tutorial Markdown, so none is invented.

| Tutorial title | Beat-sheet path under that folder | What the prerequisite retains |
|---|---|---|
| Install & Set Up | `hai-brutalist-install/beat_sheet.json` | Install, check readiness, list available builders |
| Your Week in a Folder | `hai-brutalist-week-folder/beat_sheet.json` | Gather notes, real code, outputs, and source material |
| The Prompt: Generic to Specific | `hai-brutalist-the-prompt/beat_sheet.json` | Name the project, result, visual evidence, and takeaway |
| What's a Beat Sheet? | `hai-brutalist-beat-sheet/beat_sheet.json` | Read the plan; measured narration drives timing |
| Make It Move | `hai-brutalist-make-it-move/beat_sheet.json` | Use motion to explain a mechanism and preserve evidence |
| Watch & Revise | `hai-brutalist-watch-revise/beat_sheet.json` | Watch, timestamp the issue, request a correction, watch again |

Also inspected: `installs/beat_sheet.json` (**Installs, .env & Credentials**) and `../humanitarians-youtube/claude/claude-code/hai-brutalist-run-claude-code/beat_sheet.json` (**Run Claude Code**). These are useful historical context but not the setup authority for this prerequisite.

## Current download and command authority

Use the public [brutalist.art repository](https://github.com/nikbearbrown/brutalist.art), not the older hyphenated sandbox. The local source revision inspected was `7ee2da69b599348cc38e0d2c39642b7c4171ef7e`; record your own checkout revision because the toolkit changes.

- [README](https://github.com/nikbearbrown/brutalist.art/blob/main/README.md): free default path and download/setup entry points.
- [Setup script](https://github.com/nikbearbrown/brutalist.art/blob/main/setup): package installation, fonts, voice-model download, and live feature checks.
- [HOW-TO](https://github.com/nikbearbrown/brutalist.art/blob/main/HOW-TO.md): beat-sheet workflow and worked examples; see corrections below.
- [Agent instructions](https://github.com/nikbearbrown/brutalist.art/blob/main/CLAUDE.md): beginner/advanced boundary, permissions, and library-first workflow.
- [ai-explainer instructions](https://github.com/nikbearbrown/brutalist.art/blob/main/skills/make/ai-explainer/SKILL.md): the agent-driven beginner builder.
- [Render targets](https://github.com/nikbearbrown/brutalist.art/blob/main/RENDER-TARGETS.md): local master destination, explicit output folder, and resolution.
- [Worked examples](https://github.com/nikbearbrown/brutalist.art/tree/main/examples): inspect plans and paperwork, not finished outputs as your own work.

## Corrections applied

The older install narration calls for email access, environment keys, and optional paid voices; the public checkout can be cloned directly and uses local Kokoro. The current README/setup fetch the model once; the older HOW-TO statement that it ships inside Git is stale. Setup also installs user fonts and does not supply every system dependency, so the lesson avoids a “five minutes to ready” guarantee and uses a dedicated virtual environment.

Some tutorial narration specifies `af_kore`; the public audio path documents `am_onyx` and `af_bella`. The prerequisite uses those supported voices with explicit synthetic-narration disclosure. Historical channel/persona credits do not authorize a student to impersonate the instructor or claim endorsement.

The Run Claude Code tutorial disables permission prompts. The course keeps normal permissions and bounded folders. The old installation video discusses YouTube OAuth, voice cloning, and direct rendering commands; none is part of this beginner path. Current wrapper commands govern, and the prerequisite never uploads.

Some toolkit prose gives different output filenames or says the master always stays beside the reel. The prerequisite supplies `--out` and asks for the actual produced filename; it explicitly chooses `--height 1080` rather than silently inheriting the 4K default.

This change adds instruction, not a toolkit installation or a rendered film. Course validation checks the lesson links and offline Python programs; it does not prove a new student's media environment is ready. Verify that environment and inspect the finished video during the prerequisite.
