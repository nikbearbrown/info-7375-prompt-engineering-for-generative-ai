"""Job-Search Agent: discovery-only watcher for one public job board.

It fetches Stripe's public Greenhouse board, remembers seen posting IDs, applies the
deterministic rule of ``CONTRACT.md`` to new postings and records a separate Claude
judgment, which is an opinion, never a fact or an employer decision. It never applies,
contacts employers or logs in anywhere.
"""

__version__ = "0.1.0"
