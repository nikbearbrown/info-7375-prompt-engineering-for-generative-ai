"""DELIBERATELY WRONG — FILTER.md §4 W7 (newest first). NEVER USED BY THE AGENT.

Breaks score ties by posting date, newest first, instead of by board key and
posting id, so it breaks F8. To do that its judge keeps the posting's date in
the record, which agent.filter never reads; the verdicts are agent.filter's.

Interface: judge(posting, persona) -> record and rank(records) -> list, as
agent.filter.
"""

from agent import filter as correct

# Greenhouse's and Ashby's date fields, as a careless version would read them.
DATE_FIELDS = ("updated_at", "publishedAt")


def judge(posting, persona):
    record = correct.judge(posting, persona)
    record["posted"] = next((posting[name] for name in DATE_FIELDS if isinstance(posting.get(name), str)), "")
    return record


def rank(records):
    relevant = [record for record in records if record["verdict"] == correct.RELEVANT]
    newest_first = sorted(relevant, key=lambda record: record.get("posted", ""), reverse=True)  # WRONG: dates
    return sorted(newest_first, key=lambda record: -record["score"])  # stable: ties stay newest first
