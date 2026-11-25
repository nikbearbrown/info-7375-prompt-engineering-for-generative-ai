"""The watch: board adapters, the state file, and the step that finds new postings.

Everything about "which postings are new" lives here; nothing here judges a posting. Fetching
with retries and budgets is the loop's job (job_agent/loop/).
"""

from .watcher import WatchResult

__all__ = ["WatchResult"]
