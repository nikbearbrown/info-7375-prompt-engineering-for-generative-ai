"""SEEDED demonstration of a finished wrong answer (JS2 brief, step 2).

It builds runs/seeded-finished-wrong/ from run 1's real saved responses, except that Oscar's
response is cut to its first 20 jobs; meta.total is left as the board sent it. This copies a real
failure mode (a cache or proxy serving a partial body). It also copies run 1's state, so the seeded
run is a normal second run, not a baseline. Then run the loop on it and the independent check:

  PYTHONPATH=. python3 demo/make_finished_wrong.py runs/<run1_id>
  python3 -m jsagent run --boards demo/boards-four-good.json --runs-dir runs/seeded-finished-wrong --replay runs/seeded-finished-wrong/input/map.json --run-id finished-wrong
  python3 jsagent/check.py runs/seeded-finished-wrong/finished-wrong-SEEDED
"""
import json
import pathlib
import sys

from jsagent import policy, providers

HERE = pathlib.Path(__file__).resolve().parent.parent
run1 = HERE / sys.argv[1]
out = HERE / "runs" / "seeded-finished-wrong"
files = policy.Files(HERE, HERE / "runs")
boards = json.loads((HERE / "demo" / "boards-four-good.json").read_text())["boards"]
mapping = {}
for b in boards:
    raw = run1 / "raw" / f"{b['ats']}-{b['token']}-attempt1.json"
    body = raw.read_bytes()
    if b["name"] == "oscar":
        data = json.loads(body)
        data["jobs"] = data["jobs"][:20]
        body = json.dumps(data).encode()
    name = f"{b['ats']}-{b['token']}.json"
    files.write(out / "input" / name, body)
    mapping[providers.board_url(b["ats"], b["token"])] = {"status": 200, "file": name}
files.write(out / "input" / "map.json", json.dumps(mapping, indent=1).encode())
state = sorted((HERE / "runs" / "state").glob("state-*.json"))[0]
files.write(out / "state" / state.name, state.read_bytes())
print(f"SEEDED input written to {out.relative_to(HERE)}; oscar cut to 20 jobs; state copied from {state.name}")
