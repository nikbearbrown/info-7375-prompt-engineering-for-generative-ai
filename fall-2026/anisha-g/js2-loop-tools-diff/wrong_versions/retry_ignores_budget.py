"""WRONG VERSION 2 (GATE 6.2): the retry does not check the budget, so it can make one request past the limit."""
from wrong_versions._mutate import mutant
_m = mutant("retry_ignores_budget", "if attempt == 2 and not can_request():", "if False:")
run, Budget = _m.run, _m.Budget
