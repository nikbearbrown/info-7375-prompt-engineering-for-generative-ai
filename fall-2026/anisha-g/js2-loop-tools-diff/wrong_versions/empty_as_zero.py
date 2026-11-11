"""WRONG VERSION 1 (GATE 6.1): a board that fails (404, timeout, blank body) is reported as 'ok, 0 jobs'.
The run then ends 'finished' - cleanly, and wrong."""
from wrong_versions._mutate import mutant
_m = mutant("empty_as_zero",
    '    ok = [r for r in results if r["status"] == "ok"]\n',
    '    for r in results:\n'
    '        if r["status"] == "failed": r.update(status="ok", jobs=0, new=[], baseline=False, error="")\n'
    '    ok = [r for r in results if r["status"] == "ok"]\n')
run, Budget = _m.run, _m.Budget
