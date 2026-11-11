"""The boards and budgets from GATE.md. Change only through a dated GATE.md entry."""
from agent2.loop import Board, Budget

BOARDS = [
    Board("greenhouse", "figma"),
    Board("lever", "spotify"),
    Board("ashby", "snowflake"),
    Board("greenhouse", "no-such-board-js2"),   # fails on purpose (HTTP 404)
]
BUDGET = Budget(max_boards=5, max_requests=10, max_seconds=60)
