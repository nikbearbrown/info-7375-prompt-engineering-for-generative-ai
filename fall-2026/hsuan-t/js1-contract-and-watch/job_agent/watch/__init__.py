"""The watch: board adapters, the state file, and the step that finds new postings.

Everything about "which postings are new" lives here; nothing here judges a posting.
"""

from .watcher import WatchResult, watch

__all__ = ["WatchResult", "watch"]
