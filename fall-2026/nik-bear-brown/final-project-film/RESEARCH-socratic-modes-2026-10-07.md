# Research: ChatGPT's Socratic feature and NotebookLM's, as of 2026-10-07

## Executive summary

**Correction, same day.** NotebookLM has been renamed **Gemini Notebook**. Google's blog dated 2026-07-16 says so, and notebooklm.google now redirects to notebook.google. This note was written under the old name. Google's rename post does not mention the Learning Guide, so whether it still exists under the new name is unchecked.

**What this is.** A check of two claims: that ChatGPT has a Socratic mode, and that NotebookLM is Google's main educational tool. Both are true in substance, with different names than the ones used in conversation.

**What I found.**
- **ChatGPT.** The feature is called **Study mode**, not "Socratic mode." It launched on 2025-07-29. It answers a question by asking questions back, giving hints and checking understanding, rather than handing over the answer. OpenAI's help page says it is available across ChatGPT plans on web, iOS and Android. On the web you turn it on by typing `@study` in the message box, or by choosing Study from the **+** menu.
- **NotebookLM.** Its Socratic feature is **Learning Guide**, launched 2025-09-23. It responds with "probing, open-ended questions" instead of answers. For education accounts, an administrator controls whether NotebookLM is on. Whether NotebookLM is Google's *main* educational tool I did not establish; it is clearly one of the main ones, and it has classroom integration, quizzes and flashcards.

**What I could not verify.** OpenAI's own pages (the announcement, the help article, the release notes) refused my fetch tool (HTTP 403). The how-to steps above come from a search engine's reading of OpenAI's help page, and the launch date is from several news and blog reports. Several secondary sources claim Study mode vanished from the menu in April 2026 and came back with upgrades, and that the trigger changed from `/study` to `@study`. I did not confirm that against OpenAI. The only way to settle these is to open ChatGPT and try it, which is also the film's test.

## 1. ChatGPT Study mode

| Claim | Status | Source |
|---|---|---|
| It is called Study mode | Confirmed, several sources | OpenAI's title "Introducing study mode"; news coverage |
| Launched 2025-07-29 | Reported by several sources, not seen on OpenAI's page | secondary |
| Uses Socratic questioning, hints, self-reflection prompts, knowledge checks | Reported consistently | secondary |
| Turn on: type `@study`, or **+** then Study; also chatgpt.com/studymode | From search engine's reading of OpenAI's help page | help page, not fetched directly |
| Available on all plans, web, iOS, Android, all models | Same | same |
| Extended to Edu (2025-08-06) and Enterprise (2025-08-14) | One secondary summary only | unverified |
| Vanished April 2026, returned with upgrades | Blog claims only | unverified |
| Part of ChatGPT for Teens, launched 2026-08-18 | One secondary source | unverified |

My own recollection of the July 2025 announcement is that the behaviour comes from custom instructions written with teachers and learning scientists, not from a different model. I have not re-checked that today, so treat it as a lead.

## 2. NotebookLM Learning Guide

Read directly from Google's Workspace Updates blog post of 2025-09-23:
- The Learning Guide "encourages participation with probing, open-ended questions" and helps users "break down problems step-by-step."
- For Education accounts, teachers and students need to be "in a group or OU with NotebookLM set to On." Admins control it in the console.
- Rollout was gradual, up to 15 days.

From secondary sources (not read in full): NotebookLM also makes quizzes, flashcards, audio and video overviews, has a Google Classroom integration, and in 2026 added personal class notebooks for higher-education students aged 18 and over.

## 3. What this means for the film

Both tools claim the same teaching behaviour, questions before answers. That is a claim about a prompt-level behaviour, and it is cheap to test honestly. The trial, to be filmed:

1. **One real task.** The same assignment given to a student, once with ChatGPT Study mode and once with NotebookLM's Learning Guide.
2. **The push test.** Does either tool hold the line when the student says "just give me the answer"? Record exactly what happens.
3. **The teacher's seat.** What does a teacher actually see afterwards? Can they tell the student learned something rather than only that a transcript exists? This is the gap the project cares about.
4. **Show failures in the same film.** Whatever goes wrong goes in.

Open questions for the trial: whether Study mode is currently in the menu, what the real trigger is today, and whether a teacher can see or control a student's use of either mode.

## 4. What I did not do

- I did not read OpenAI's announcement, help article or release notes directly.
- I did not open ChatGPT or NotebookLM to confirm any behaviour.
- I did not read the comparison articles of AI study modes across ChatGPT, Gemini and Claude that turned up in the search; they would be a good next read.
