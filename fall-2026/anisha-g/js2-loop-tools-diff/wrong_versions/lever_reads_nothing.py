"""WRONG VERSION 3 (for the finished-wrong demo, the assignment's own example): the Lever parser returns no jobs, so a
board that has postings is reported as 'ok, 0 jobs, no new jobs', and a run over working boards ends 'finished'."""
from wrong_versions._mutate import mutant
_m = mutant("lever_reads_nothing",
    'return [(str(j["id"]), j.get("text", "")) for j in data]', 'return []')
run, Budget, parse_jobs = _m.run, _m.Budget, _m.parse_jobs
