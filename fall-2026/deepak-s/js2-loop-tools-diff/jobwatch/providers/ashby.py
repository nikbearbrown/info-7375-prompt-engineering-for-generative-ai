"""Ashby public job posting API. Shape taken from evidence/manual-capture/20261110T184001Z/06-ashby-linear.body and
07-ashby-notion.body: {"apiVersion": ..., "jobs": [{"id": str, "title": str, "location": str, "jobUrl": str, ...}]}.
"""
from jobwatch.providers import BoardError, build_postings, classify_http, wrong_shape

SYSTEM = "ashby"


def url(host, slug):
    return f"https://{host}/posting-api/job-board/{slug}"


def _fields(item):
    return item.get("id"), item.get("title"), item.get("location"), item.get("jobUrl")


def parse(result, board):
    data = classify_http(result)
    if isinstance(data, BoardError):
        return data
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return wrong_shape('expected {"jobs": [...]}')
    return build_postings(data["jobs"], board, _fields)
