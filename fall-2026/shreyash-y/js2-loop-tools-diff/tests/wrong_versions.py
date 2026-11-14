"""GATE.md section 7: the wrong versions, written as small plausible implementations so the tests
can show their checks catch them. Nothing in jsagent/ imports this file."""
import pathlib


def wv1_empty_is_ok(postings):
    """Wrong 1: an empty board is a board with zero new jobs."""
    return {"status": "ok", "fetched": len(postings), "new": 0}


def wv2_exit_ignoring_failures(board_statuses):
    """Wrong 2: failed boards are dropped and the run is called finished."""
    return "finished"


def wv3_prefix_inside(path, runs):
    """Wrong 3: 'inside runs/' tested with a string prefix."""
    return str(pathlib.Path(path)).startswith(str(pathlib.Path(runs)))


def wv4_retry_until_ok(transport, url, max_tries=5):
    """Wrong 4: retries any non-200, a 404 included."""
    for _ in range(max_tries):
        status, body = transport.get(url)
        if status == 200:
            return status, body
    return status, body


def wv5_count_after_failure(status, body):
    """Wrong 5: counts whatever came back, even from a failed response."""
    try:
        import json
        data = json.loads(body)
        return len(data.get("jobs", data) if isinstance(data, dict) else data)
    except Exception:
        return 0
