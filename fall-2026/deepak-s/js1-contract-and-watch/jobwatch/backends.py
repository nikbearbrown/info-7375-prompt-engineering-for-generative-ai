"""Judge backends: `--judge sdk` (default) or `--judge claude-cli` (Amendment A14)."""
from jobwatch.judge import SdkJudge
from jobwatch.judge_cli import CliJudge

BACKENDS = ("sdk", "claude-cli")


def make_judge(name, client=None):
    return CliJudge() if name == "claude-cli" else SdkJudge(client)
