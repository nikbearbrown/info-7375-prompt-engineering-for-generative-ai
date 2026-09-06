# Lesson authoring template

Create lessons/NN-slug/docs/en.md, code/main.py, code/tests/test_main.py, quiz.json, and outputs/artifact-brief.md.

The lesson document must include title; Type: Build; Languages: Python; prerequisites; time; week; reading alignment; Learning Objectives; The Problem; The Concept; Predict Before Running; Build It; Use It; Interactive Lab; Practice Lab; Ship It; Verify It; Assessments; Capstone Connection; and Knowledge Check.

Use an original, small standard-library implementation that runs offline and exits. Write at least five tests of substantive behavior and failure boundaries. Include six quiz questions with stages pre, check, check, check, post, post; four options; zero-based correct index; and meaningful explanations. Balance correct-option positions.

The Claude exercise should use the same mechanism in a practical workflow. Label fixtures. State model, protocol, and verification limitations. No production claims from a toy implementation.

Where directly relevant, append a closing section titled "Anthropics" after Knowledge Check. Link to Anthropic's own repository example, course, documentation, or engineering guidance. Annotate why it fits and ask students to compare it with their Python build. Record the verification date, distinguish course adaptations from upstream implementations, and preserve explicit optional API execution. Omit this section if there is no substantive match. An instructor film adapting the source may be linked alongside it only when its title and URL are verified.

Only where a specific companion-book passage adds a useful diagnostic, add a closing "Computational Skepticism" note. Read the chapter passage, name the section, explain its relevance, and pose one concrete check on the existing lesson artifact. Link through docs/computational-skepticism.md so the note remains readable without the companion checkout. When both sections apply, place this note after Anthropics. Omit it when the match is generic or merely repeats another lesson's note.

Only where a read chapter adds a distinct supervisory practice, append a "Conducting AI" note. Name the source chapter and section through docs/conducting-ai.md, explain the connection, and apply one focused practice to the existing artifact. Keep the note useful without a companion checkout. Do not import companion assessment weights or word counts, require invented critique findings, or turn an observed model miss into a universal impossibility claim. Closing order, omitting irrelevant sections: Anthropics, Computational Skepticism, Conducting AI, Irreducibly Human.

Only where a read chapter offers a distinct division-of-labor lesson, end with "Irreducibly Human". Link the chapter and section through docs/irreducibly-human.md. Include explicit "AI should" and "Human should" paragraphs with concrete actions, plus a "Record the split" check inside the current artifact. Explain what assistance is useful and what the learner must practice, judge, authorize, or do with actual people. Do not use “humans supervise” as a substitute for specifying the work, claim human judgment is infallible, or fabricate consent, reflection, or approvals. Preserve the Claude/Python stack and first-attempt learning sequence. Omit the note if it only repeats another closing section.

Label the exercises and knowledge checks as ungraded Assessments. Do not attach weekly grades or video requirements; NEU graded Assignments bundle specified Assessments on the separate ten-day schedule.
