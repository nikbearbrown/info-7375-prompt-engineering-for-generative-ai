"""Load the frozen JS3 corpus listed in CORPUS.sha256.

Every file is checked against its SHA-256 before it is parsed; a mismatch
raises CorpusHashMismatch. A listed file that is missing is reported as
"not evaluated", never as a board with zero postings.

Each posting becomes
    {"board", "id", "title", "location", "url", "body_text"}
where body_text is the posting body as plain text.
"""

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from agent.adapters import PARSERS

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "CORPUS.sha256"
BOARDS_CONFIG = Path("config") / "boards.json"
NOT_EVALUATED = "not evaluated"

# out/raw/<run-id>_<board>_a<attempt>.json
_RAW_NAME = re.compile(
    r"^(?P<run>[^_]+)_(?P<board>.+)_a(?P<attempt>\d+)\.json$")


class CorpusError(Exception):
    """The corpus manifest or a corpus file cannot be used."""


class CorpusHashMismatch(CorpusError):
    """A corpus file's SHA-256 differs from CORPUS.sha256."""


class _TextExtractor(HTMLParser):
    """Collect text content; every tag boundary becomes a space."""

    _SKIP = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1
        self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1
        self.parts.append(" ")

    def handle_startendtag(self, tag, attrs):
        self.parts.append(" ")

    def handle_data(self, data):
        if not self._skip_depth:
            self.parts.append(data)


def html_to_text(content):
    """HTML-unescape, strip tags, collapse whitespace.

    Greenhouse escapes its HTML (``&lt;p&gt;``), so one unescape turns it
    into HTML. The HTML parser then strips the tags and decodes the entities
    that were inside the HTML itself (``&nbsp;``, ``&amp;``).
    """
    if not content:
        return ""
    extractor = _TextExtractor()
    extractor.feed(html.unescape(content))
    extractor.close()
    return re.sub(r"\s+", " ", "".join(extractor.parts)).strip()


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(root=ROOT):
    """Return [(relative_path, expected_sha256)] from CORPUS.sha256."""
    path = Path(root) / MANIFEST
    entries = []
    for number, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise CorpusError(f"{MANIFEST} line {number} is not "
                              f"'<sha256>  <path>': {line!r}")
        entries.append((parts[1].strip().lstrip("*"), parts[0]))
    if not entries:
        raise CorpusError(f"{MANIFEST} lists no files")
    return entries


def board_from_filename(rel_path):
    match = _RAW_NAME.match(Path(rel_path).name)
    if not match:
        raise CorpusError(f"cannot read a board name from {rel_path!r}")
    return match.group("board")


def load_ats_map(root=ROOT):
    data = json.loads((Path(root) / BOARDS_CONFIG).read_text("utf-8"))
    return {b["name"]: b["ats"] for b in data["boards"]}


def load(root=ROOT):
    """Load the corpus.

    Returns {"postings": [...], "boards": {board: info}} where info is
    {"status": "evaluated" | "not evaluated", "file", "sha256",
     "postings" (evaluated only), "reason" (not evaluated only)}.
    Raises CorpusHashMismatch if a present file has the wrong hash.
    """
    root = Path(root)
    ats_map = load_ats_map(root)
    postings = []
    boards = {}
    for rel_path, expected in read_manifest(root):
        board = board_from_filename(rel_path)
        if board in boards:
            raise CorpusError(f"board {board!r} listed twice in {MANIFEST}")
        info = {"file": rel_path, "sha256": expected}
        boards[board] = info
        path = root / rel_path
        if not path.is_file():
            info.update(status=NOT_EVALUATED, reason="file missing")
            continue
        actual = sha256_of(path)
        if actual != expected:
            raise CorpusHashMismatch(
                f"{rel_path}: expected sha256 {expected}, got {actual}")
        if board not in ats_map:
            raise CorpusError(f"board {board!r} not in {BOARDS_CONFIG}")
        parsed = PARSERS[ats_map[board]](path.read_bytes())
        for raw in parsed:
            postings.append({
                "board": board,
                "id": raw["id"],
                "title": raw["title"],
                "location": raw["location"],
                "url": raw["url"],
                "body_text": html_to_text(raw["content"]),
            })
        info.update(status="evaluated", postings=len(parsed))
    # Boards in config/boards.json without a frozen file (e.g. the 404
    # board) are listed too, so they are never read as "0 postings".
    for board in ats_map:
        if board not in boards:
            boards[board] = {"status": NOT_EVALUATED, "file": None,
                             "sha256": None,
                             "reason": f"not in {MANIFEST}"}
    return {"postings": postings, "boards": boards}
