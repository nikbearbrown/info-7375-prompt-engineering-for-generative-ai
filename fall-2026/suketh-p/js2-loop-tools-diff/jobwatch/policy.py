"""The permission policy, enforced in code (GATE.md 'Permission policy').

Requests: HTTPS GET only, only to the exact configured board endpoints, on two hosts.
Files: read only the persona, the state and saved run evidence; write only inside the
current run's folder. Creating or replacing state/state.json (and the temporary file
that makes the update atomic) needs an approval that names this run and that file,
given before the run starts. A path with `..`, or with a symlink anywhere below the
project folder, is refused, even when it would land inside. Every refusal names the
rule that fired, so a denial can be explained."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from jobwatch.errors import PolicyDenied

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
PERSONA_FILE = "persona/alex_morgan.json"
STATE_FILE = "state/state.json"
OPERATIONS = ("read", "write")


@dataclass(frozen=True)
class Approval:
    """The student's approval to create or replace one file in one run. On the command
    line: --approve-state RUN_ID:state/state.json. In tests it is a simulated fixture."""

    run_id: str
    path: str

    @classmethod
    def parse(cls, text):
        run_id, separator, path = text.partition(":")
        if not separator or not run_id.strip() or not path.strip():
            raise ValueError("an approval must look like RUN_ID:state/state.json")
        return cls(run_id, path)

    def __str__(self):
        return f"{self.run_id}:{self.path}"


def _inside(path, folder):
    """A path relation, not a string prefix: runs/R2-evil is not inside runs/R2."""
    return path == folder or folder in path.parents


def _has_parent_part(path):
    return ".." in Path(path).parts


def _symlink_in_path(root, full):
    """The first existing component between the project folder and the target that is
    a symlink, or None. Components that do not exist yet cannot be links."""
    current = root
    for part in full.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return current
        if not current.exists():
            return None
    return None


def _is_state_temp(rel):
    path = PurePosixPath(rel)
    return str(path.parent) == "state" and path.name.startswith(".state.json.") and path.name.endswith(".tmp")


class Policy:
    def __init__(self, root, run_id, approved_urls, approval=None):
        self.root = Path(root).resolve()
        self.run_id = run_id
        self.approved_urls = frozenset(approved_urls)
        self.approval = approval

    # Requests -------------------------------------------------------------------

    def check_request(self, method, url):
        if method != "GET":
            raise PolicyDenied("method", f"{method} {url}: only GET is allowed")
        parts = urlsplit(url)
        if parts.scheme != "https":
            raise PolicyDenied("scheme", f"{url}: only https is allowed")
        host = parts.hostname or ""
        if parts.username is not None or parts.password is not None or parts.port is not None \
                or host not in ALLOWED_HOSTS:
            raise PolicyDenied("host", f"{url}: host {host!r} is not on the allow-list")
        if url not in self.approved_urls:
            raise PolicyDenied("endpoint", f"{url} is not a configured board endpoint")

    # Files ----------------------------------------------------------------------

    def approval_problem(self):
        """None when the approval names this run and the state file; otherwise why not."""
        approval = self.approval
        if approval is None:
            return "no approval was given for this run"
        if not isinstance(approval, Approval):
            return "an approval must name the run and the file (RUN_ID:state/state.json)"
        if approval.run_id != self.run_id:
            return f"the approval names run {approval.run_id!r}, not this run ({self.run_id!r})"
        if approval.path != STATE_FILE:
            return f"the approval names {approval.path!r}, not {STATE_FILE!r}"
        return None

    def check_file(self, operation, path):
        """Return the resolved path if the policy allows the operation; raise otherwise."""
        if operation not in OPERATIONS:
            raise PolicyDenied("operation", f"{operation!r} is not an allowed operation")
        given = Path(path)
        if _has_parent_part(given):
            raise PolicyDenied("parent-traversal", f"{path}: paths containing '..' are refused")
        full = given if given.is_absolute() else self.root / given
        if not _inside(full, self.root):
            raise PolicyDenied("outside-project", f"{path} is outside the project folder")
        link = _symlink_in_path(self.root, full)
        if link is not None:
            raise PolicyDenied("symlink", f"{path}: {link.relative_to(self.root)} is a symlink")
        resolved = full.resolve()
        if not _inside(resolved, self.root):
            raise PolicyDenied("outside-project", f"{path} resolves outside the project folder")
        rel = resolved.relative_to(self.root).as_posix()
        runs = self.root / "runs"
        if operation == "read":
            if rel in (PERSONA_FILE, STATE_FILE) or _inside(resolved, runs):
                return resolved
            raise PolicyDenied("not-readable", f"{path} is not the persona, the state, or saved run evidence")
        if self.run_id and (resolved == runs or _inside(resolved, runs / self.run_id)):
            return resolved
        if rel in (STATE_FILE, "state") or _is_state_temp(rel):
            problem = self.approval_problem()
            if problem:
                raise PolicyDenied("approval", f"{path}: {problem}")
            return resolved
        raise PolicyDenied("not-writable", f"{path} is not inside this run's folder (runs/{self.run_id})")
