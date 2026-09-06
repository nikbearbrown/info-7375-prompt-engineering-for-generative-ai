# Validation record

2026-09-06: all 15 offline demos and 90 lesson unit tests passed, along with 13 integration tests for transport, tool history, request limits, argument rejection, and the MCP fixture lifecycle. The course validator also checked the Python-only implementation surface, quiz structure, minimum test count, and local Markdown links.

Course navigation listed all 15 weeks, and the default Claude client printed an offline preview. The live CLI rejected absent model configuration before making a request. No live Claude API response or API billing outcome was tested. No Claude Code/Cowork student session, full MCP conformance run, or academic grading outcome is claimed by these checks.

Run python3 scripts/validate_course.py to reproduce the automated checks. Offline fixtures remain distinct from actual Claude responses. Instructor decisions about grading, dates, and missing bibliography are documented separately.
