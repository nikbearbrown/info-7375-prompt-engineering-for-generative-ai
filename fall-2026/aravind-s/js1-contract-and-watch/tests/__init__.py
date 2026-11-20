import os

# No test may reach the real Claude Code: any lookup lands on a path that does not exist, so a test that
# forgot its stand-in fails with "could not be run" instead of making a live call on the author's seat.
os.environ["JOB_AGENT_CLAUDE"] = "/nonexistent/job-agent-tests-never-call-claude"
