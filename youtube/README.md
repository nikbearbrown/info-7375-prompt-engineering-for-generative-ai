# INFO 7375 course films

This folder holds films related to **Prompt Engineering for Generative AI**: instructor tutorials, assignment explanations, and course Progress Reels. The name `youtube/` is an organizational convention, not a claim that a film is public or permission to upload it.

NEU students start with the [video prerequisite](../prerequisites/brutalist-video.md). Independent readers may browse course films without installing the video toolchain.

## One film, one folder

Use a descriptive, unique kebab-case slug, such as `assignment-02-your-name/`, `week-08-progress-reel-your-name/`, or `prompt-contracts-tutorial/`. Do not overwrite another student's or the instructor's project.

A film project should retain:

- `README.md`: title, author, lesson/topic, intended audience, status, and actual final-file path.
- `beat_sheet.json`: the reviewed narration/visual plan.
- `BUILD-PROMPT.md`: the Claude prompt and reproducible build instructions.
- `SOURCES.md`: assignment evidence paths, external credits/rights, and Claude/synthetic-narration disclosure.
- `REVIEW.md`: timestamped problems, requested changes, re-checks, and the real human review decision.
- `final/`: rendered MP4 and any caption files used for submission.

The renderer may also create its own build logs, check reports, audio, and media folders. Preserve the meaningful source and review records; generated media and caches are ignored by Git. Keep Python assignment code under `learning-artifacts/` and link or refer to its sanitized evidence. Do not commit restricted inputs, credentials, or private student information.

## Build outside the toolkit

Keep the `brutalist.art` checkout and its Node/Remotion dependencies outside this repository. Use the existing scene library for the beginner path. The film project lives here; the media engine lives there. Do not vendor dependencies or the renderer into this folder.

## Status and sharing

Mark each film as draft, review cut, reviewed local final, or published. A rendered file is not automatically a reviewed final. Add a public URL only after actual publication is authorized and verified; never invent a video link.

Large media is not committed by default. Submit the actual MP4 through the assigned course channel, or use an explicitly approved media-storage workflow. A source-only Git checkout does not include the finished film. Public sharing of student work is a separate consent and publication decision.

No films have been generated or published merely by creating this folder.
