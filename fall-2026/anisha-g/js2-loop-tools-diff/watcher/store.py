"""All file writes go through the policy (GATE 5): new files only, inside reports/job-watch/, never a delete."""
import json, re, datetime
from pathlib import Path
from watcher.policy import Policy, REPORT_DIR

class Store:
    def __init__(self, base_dir=".", label="live"):
        self.policy = Policy(base_dir); self.base = Path(base_dir)
        self.run_id = datetime.datetime.now().strftime("%Y%m%dT%H%M%S") + "-" + label
        self.run_dir = self.base / REPORT_DIR / "runs" / self.run_id
        self.state_dir = self.base / REPORT_DIR / "state"

    def write(self, path, data, approved=False):
        real = self.policy.check_write(path, approved=approved)        # raises Blocked / NeedsApproval
        real.parent.mkdir(parents=True, exist_ok=True)
        real.write_bytes(data if isinstance(data, bytes) else data.encode())
        return real

    def save_raw(self, board, attempt, response):
        name = re.sub(r"[^a-z0-9-]", "_", board.lower()) + f"-a{attempt}.body"
        self.write(self.run_dir / "raw" / name, response.body)
        self.write(self.run_dir / "raw" / (name + ".status"), str(response.status))
        return "raw/" + name

    def load_seen(self):
        files = sorted(self.state_dir.glob("seen-*.json")) if self.state_dir.exists() else []
        if not files: return {}, None
        latest = self.policy.check_read(files[-1])
        return {k: set(v) for k, v in json.loads(latest.read_text()).items()}, latest.name

    def save_seen(self, seen):        # a NEW snapshot each run, so nothing is ever overwritten
        return self.write(self.state_dir / f"seen-{self.run_id}.json", json.dumps({k: sorted(v) for k, v in seen.items()}, indent=1))
