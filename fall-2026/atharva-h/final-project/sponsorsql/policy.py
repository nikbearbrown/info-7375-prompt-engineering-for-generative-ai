"""The permission policy, enforced in code.

Two independent layers:
1. check_text(): a text check before anything runs. Exactly one SELECT/WITH
   statement, no comments, no write or schema keywords outside string literals.
2. authorizer(): SQLite calls this while preparing every statement. Only reading
   the `lca` table and calling allow-listed functions is permitted. Everything
   else (writes, ATTACH, PRAGMA, other tables, recursion) is denied.

The connection itself is opened read-only (mode=ro) with query_only on, so a
write would fail even if both layers were removed.
"""

import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from . import udf

ALLOWED_TABLES = frozenset({"lca"})
ALLOWED_FUNCTIONS = frozenset({
    "count", "sum", "avg", "min", "max", "total", "group_concat",
    "lower", "upper", "trim", "ltrim", "rtrim", "substr", "substring", "length",
    "replace", "instr", "coalesce", "ifnull", "nullif", "iif", "round", "abs",
    "date", "strftime", "like", "glob", "typeof",
    "row_number", "rank", "dense_rank", "lag", "lead",
    "median", "norm", "title_has",
})
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|pragma|vacuum|"
    r"reindex|analyze|begin|commit|rollback|savepoint|release|load_extension|"
    r"writefile|readfile)\b",
    re.IGNORECASE,
)
MAX_SQL_CHARS = 8000
MAX_VALUE_BYTES = 10_000_000   # SQLite string/blob size limit, where Python supports setlimit (3.11+)
QUOTED = re.compile(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|`[^`]*`|\[[^\]]*\]")


class PolicyDenied(Exception):
    """The SQL was refused by the text check or the authorizer."""


class BudgetExceeded(Exception):
    """A statement ran past its time budget and was interrupted."""


@dataclass
class PolicyResult:
    allowed: bool
    reason: str


@dataclass
class ExecResult:
    columns: List[str]
    rows: List[Tuple]
    total_rows: int
    truncated: bool
    seconds: float
    kept_rows: int = 0
    notes: List[str] = field(default_factory=list)


def _without_literals(sql):
    """Blank out quoted text before scanning for keywords.

    One left-to-right pass over single-quoted strings, double-quoted identifiers,
    backtick and [bracket] identifiers, so a quote character inside one kind
    cannot make the scanner swallow the rest of the statement (independent
    review, finding 4).
    """
    return QUOTED.sub("''", sql)


def check_text(sql) -> PolicyResult:
    if not isinstance(sql, str) or not sql.strip():
        return PolicyResult(False, "empty SQL")
    if len(sql) > MAX_SQL_CHARS:
        return PolicyResult(False, f"SQL longer than {MAX_SQL_CHARS} characters")
    bare = _without_literals(sql).strip()
    if bare.endswith(";"):
        bare = bare[:-1].rstrip()
    if ";" in bare:
        return PolicyResult(False, "more than one statement")
    if "--" in bare or "/*" in bare:
        return PolicyResult(False, "SQL comments are not allowed")
    first = re.match(r"\s*(\w+)", bare)
    if not first or first.group(1).lower() not in ("select", "with"):
        return PolicyResult(False, "only SELECT or WITH ... SELECT is allowed")
    hit = FORBIDDEN.search(bare)
    if hit:
        return PolicyResult(False, f"forbidden keyword: {hit.group(1).upper()}")
    return PolicyResult(True, "ok")


def authorizer(action, arg1, arg2, dbname, trigger):
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK if arg1 in ALLOWED_TABLES else sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        name = (arg2 or "").lower()
        return sqlite3.SQLITE_OK if name in ALLOWED_FUNCTIONS else sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY


def open_readonly(db_path) -> sqlite3.Connection:
    """The connection the model's SQL runs on: read-only file, query_only, authorizer."""
    path = Path(db_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"database not found: {path}")
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    con.execute("PRAGMA query_only = ON")
    if hasattr(con, "setlimit"):  # Python 3.11+: cap any single string or blob
        con.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_VALUE_BYTES)
    udf.register(con)
    con.set_authorizer(authorizer)
    return con


def read_metadata(db_path) -> dict:
    """System-side read of the source checksum. The model never sees this connection."""
    path = Path(db_path).resolve()
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        return dict(con.execute("SELECT key, value FROM metadata"))
    finally:
        con.close()


def strip_trailing_semicolon(sql):
    sql = sql.strip()
    return sql[:-1].rstrip() if sql.endswith(";") else sql


def execute(con, sql, seconds, keep_rows) -> ExecResult:
    """Run one checked statement under a wall-clock budget."""
    verdict = check_text(sql)
    if not verdict.allowed:
        raise PolicyDenied(verdict.reason)
    sql = strip_trailing_semicolon(sql)
    start = time.monotonic()
    deadline = start + seconds
    con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
    try:
        try:
            cur = con.execute(sql)
        except sqlite3.DatabaseError as exc:
            _reraise(exc)
        columns = [d[0] for d in (cur.description or [])]
        rows, total = [], 0
        try:
            for row in cur:
                total += 1
                if len(rows) < keep_rows:
                    rows.append(tuple(row))
        except sqlite3.DatabaseError as exc:
            _reraise(exc)
    finally:
        con.set_progress_handler(None, 0)
    return ExecResult(columns, rows, total, total > len(rows),
                      round(time.monotonic() - start, 3), kept_rows=len(rows))


def _reraise(exc):
    text = str(exc).lower()
    if "not authorized" in text or "prohibited" in text or "one statement at a time" in text:
        raise PolicyDenied(f"authorizer denied: {exc}") from exc
    if "interrupt" in text:
        raise BudgetExceeded("statement exceeded its time budget") from exc
    raise exc


def count_rows(con, rows_sql, seconds) -> Optional[int]:
    """COUNT(*) over the evidence query, used to cross-check count answers."""
    inner = strip_trailing_semicolon(rows_sql)
    result = execute(con, f"SELECT COUNT(*) FROM ({inner})", seconds, 1)
    return int(result.rows[0][0]) if result.rows else None
