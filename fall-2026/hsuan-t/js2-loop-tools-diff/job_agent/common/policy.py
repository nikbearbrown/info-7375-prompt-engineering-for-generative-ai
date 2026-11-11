"""The permission policy (GATE §5) as code: which hosts the agent may contact, which folders it may
read and write, and which overwrites need the person's yes.

Why one object instead of checks scattered per module: GATE R22 says the policy must hold without
relying on a prompt or on each caller remembering a rule. The pipeline builds one Policy per run
and every place that touches the network or a file asks it first, so the rules live in one file
and the boundary tests (tests/test_policy.py) exercise exactly what the agent uses.
"""

from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from .errors import AgentError
from .paths import Paths

# GATE §5: board requests go only to these exact hosts. api.anthropic.com is added per run, only
# with --claude-via api; the default `claude -p` line connects by itself, outside this program.
BOARD_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
CLAUDE_API_HOST = "api.anthropic.com"

Confirm = Callable[[str], bool]


class PolicyError(AgentError):
    """A request the permission policy refuses. An AgentError, so the run stops and says why."""


def refuse(question: str) -> bool:
    """The default answer when nobody can be asked (tests, scripts, no terminal): GATE §5 says a
    missing answer is a refusal."""
    return False


def ask_terminal(question: str) -> bool:
    """Ask the person running the tool. Only an explicit y counts; empty input, anything else, or
    no input at all (EOF from a pipe) is a no."""
    try:
        return input(f"{question} [y/N] ").strip().lower() == "y"
    except EOFError:
        return False


class Policy:
    """One run's permissions. Folders are stored resolved (symlinks followed), and every checked
    path is resolved the same way before comparing, so `..`, a symlink, or a look-alike sibling
    folder (runs-evil/) can't pass as an allowed folder."""

    def __init__(self, hosts, read_dirs, write_dirs, ask_dirs, confirm: Confirm = refuse):
        self.hosts = frozenset(hosts)
        self.read_dirs = tuple(Path(d).resolve() for d in read_dirs)
        self.write_dirs = tuple(Path(d).resolve() for d in write_dirs)
        self.ask_dirs = tuple(Path(d).resolve() for d in ask_dirs)
        self.confirm = confirm
        # Paths this run may write into without asking: ones it created itself, and existing ones
        # the person said y to. Each covers everything under it, so one "y" for runs/<stamp>/ does
        # not ask again for each file the report writes into that folder.
        self._approved: set[Path] = set()

    @classmethod
    def for_run(cls, paths: Paths, claude_via: str | None = None, confirm: Confirm = refuse) -> "Policy":
        """GATE §5 for one run. claude_via is None when Claude is off; prompts/ and (for "api")
        api.anthropic.com are only allowed when it is on."""
        hosts = set(BOARD_HOSTS)
        reads = [paths.repo / "data", paths.repo / "personas", paths.out / "state", paths.out / "evidence" / "raw"]
        if claude_via is not None:
            reads.append(paths.repo / "prompts")
        if claude_via == "api":
            hosts.add(CLAUDE_API_HOST)
        writes = [paths.out / "runs", paths.out / "evidence" / "raw", paths.out / "state"]
        # JS2 D15: both halves of a run's record ask before an overwrite; state/ is updated every run
        # without asking (GATE §5: "updating successful board state require[s] no prompt").
        asks = [paths.out / "runs", paths.out / "evidence" / "raw"]
        return cls(hosts, reads, writes, asks, confirm)

    # ---- network ----------------------------------------------------------------------------

    def check_url(self, url: str) -> None:
        """HTTPS to an exact allowed host on the default port. Called before every request and
        again for every redirect target (common/net.py), so a refused host never sees a byte."""
        parsed = urlparse(url)
        try:
            port = parsed.port
        except ValueError:          # "host:abc" is not a port; refuse rather than guess
            port = -1
        if parsed.scheme != "https":
            raise PolicyError(f"refused: only https is allowed, got {parsed.scheme or 'no scheme'!r} ({url})")
        # The user-name part is refused outright: "https://allowed@evil.com" is a classic trick
        # to make a URL look like it goes to the allowed host.
        if parsed.hostname not in self.hosts or parsed.username is not None or port not in (None, 443):
            raise PolicyError(f"refused: host not on allow-list: {parsed.hostname}")

    # ---- files ------------------------------------------------------------------------------

    def check_read(self, path: Path) -> Path:
        """Return the resolved path when it is inside a readable folder."""
        real = Path(path).resolve()
        if not _inside(real, self.read_dirs):
            raise PolicyError(f"refused: reading outside the allowed folders: {path}")
        return real

    def check_write(self, path: Path) -> Path:
        """Return the resolved path when it may be written. Writing over something that already
        exists in a record folder (runs/, evidence/raw/) needs an explicit yes first."""
        real = Path(path).resolve()
        if not _inside(real, self.write_dirs):
            raise PolicyError(f"refused: writing outside the allowed folders: {path}")
        if _inside(real, self.ask_dirs) and not _inside(real, self._approved):
            if not real.exists():
                # This run is about to create it, so it is this run's own record, not a historical
                # one: the next board writing into the same evidence/raw/<stamp>/ must not be asked.
                self._approved.add(real)
            elif not self.confirm(f"{path} already exists. Overwrite it?"):
                raise PolicyError(f"refused: {path} already exists and overwriting was not approved")
            else:
                self._approved.add(real)
        return real


def _inside(path: Path, folders) -> bool:
    """is_relative_to compares whole path parts, so runs-evil/ is not inside runs/ (a plain
    string prefix check would say it is)."""
    return any(path.is_relative_to(d) for d in folders)
