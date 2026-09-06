# INFO 7375 contributor guide

This repository teaches Prompt Engineering for Generative AI through Claude
and Python only. The course adaptation supersedes the inherited multilingual
curriculum, website, certification routes, and their automation contracts.

All exercises assume Claude Code access. Enrolled students receive it through
NEU; public readers need their own Claude Code account. Mention the university
portal early. Do not make Claude Code optional or equate that account with API
credits. Offline Python references precede explicit optional direct API calls.

Preserve the teaching spine: predict, explain, Build It, Use It, Ship It,
verify, reflect. Implement mechanisms in Python's standard library before
introducing abstractions. Claude is the only external model provider. Do not
add other model SDKs, orchestration frameworks, or non-Python implementations.
JSON, Markdown, YAML configuration, and shell invocation examples are allowed.
NEU-only course logistics belong in prerequisites/, not numbered lessons.
Brutalist video preparation is a separate media-tool exception: use an external
brutalist.art checkout for its Node/Remotion and Python packages, never vendor
that stack into the course. Store course films and their source records under
youtube/; keep assignment implementations in learning-artifacts/. Do not add
video prerequisites for independent readers or infer permission to publish.

Each weekly lesson has docs/en.md, code/main.py, code/tests/test_main.py,
quiz.json (six questions: pre, check, check, check, post, post), and outputs/.
Provide five or more deterministic tests with meaningful boundary cases.
Code runs offline by default and terminates without keys. Live API work must
be explicitly requested and labeled; never portray fixtures as Claude output.
Use actual tool_use/tool_result messages in provider integration examples.
Use Mermaid or SVG diagrams and language tags on code fences.

Students build their own version before consulting reference code. Ask for a
prediction, then an explanation of the observed result. Never fabricate test
results, provenance, human approvals, citations, or student understanding.
Learner work belongs in learning-artifacts/, not in reference solutions.

Run python3 scripts/validate_course.py before handing off changes. Preserve
LICENSE and ATTRIBUTION.md. Product details need dated primary sources.
When committing, use one commit per lesson directory and conventional subjects.
Do not publish or push without user authorization. Keep course policy conflicts
visible in docs/instructor-decisions.md; do not silently choose grading rules.

Where a lesson has a direct match in Anthropic's own repositories or official
guidance, append a closing section titled exactly "Anthropics". Use a small set
of verified, specific primary-source links, explain their connection to the
Python build, and include a short comparison or adaptation task. Omit the
section when the connection would be generic or forced. Record the link-check
date. Do not imply our teaching mechanisms are Anthropic's implementations.
Instructor films may adapt these materials: add film titles/URLs only when
verified, alongside the original source; never invent a film mapping. Keep
Claude Code access assumed and direct API examples explicit and optional.

Add a closing "Computational Skepticism" note only when a passage in the companion
book adds a specific diagnostic question to that lesson. Read the passage;
cite its chapter and section through docs/computational-skepticism.md, explain
the connection, and apply it to the existing artifact. Do not append a generic
warning to every lesson. When closing sections apply, use this order: Anthropics,
Computational Skepticism, Conducting AI, then Irreducibly Human; omit
inapplicable sections. Keep the course Claude/Python
scope even where the source book discusses other tools. Do not silently resolve
the companion manuscript's duplicate versions or conflict markers.

Add a closing section titled exactly "Conducting AI" only when a chapter in
that companion book contributes a distinct supervisory practice to the lesson.
Read the passage, cite its chapter and section through docs/conducting-ai.md,
and apply the practice to the existing artifact. Keep notes self-contained
without the companion checkout. Do not repeat a generic warning, import the
book's grading rules, or treat philosophical claims of AI impossibility as
established empirical limits. Preserve unresolved editorial choices in the
source manuscript; do not invent findings, human judgments, or approvals.

Add an "Irreducibly Human" closing note only for a specific, relevant connection
to a chapter you have read. Cite the passage through docs/irreducibly-human.md.
Each note must explicitly state "AI should" and "Human should", naming concrete
responsibilities for this lesson, then ask for evidence of the split in the
existing artifact. AI can draft, compute, retrieve, test, and challenge; humans
practice the foundational mechanism, justify assumptions, maintain relationships,
and own authorized decisions. Assign by task, not a blanket claim of superior
human accuracy or machine incapacity. Preserve build-before-reference learning,
real consent and approvals, and human reflection. Omit generic or repetitive
notes; do not add a new assessment or mistake simulated stakeholders for people.

Call lesson exercises and quizzes Assessments: they are ungraded practice. NEU graded Assignments occur every 10 days and total 100 points: implementation 60, Frictional 10, proper GitHub version posting 10, Relative Quartile 20. Explainer videos and Brutalist are optional; no separate video points or required Progress Reels. Keep exact term deadlines and cycle-to-Assessment mapping in instructor-published briefs. Preserve the distinction between effort, posting, and resulting quality.

Include the instructor-provided policy video link in every graded Assignment brief: [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz). Keep it with the assignment instructions and shared grading rubrics, not as a graded-video production requirement.
