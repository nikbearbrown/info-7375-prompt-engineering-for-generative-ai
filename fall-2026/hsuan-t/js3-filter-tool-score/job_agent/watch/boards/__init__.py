"""Board adapters: each module turns one applicant-tracking system's JSON into Postings (common/posting.py).

Every adapter module offers the same four names, so the watch never asks which system it is talking to:
  ATS          the key used in data/boards.json ("greenhouse", "ashby")
  ID_TYPE      the type of that system's job ids (int / str), checked when the state file is read
  board_url()  where one board's postings live
  parse()      the response bytes -> list[Posting], or WatchError if the shape is wrong

Supporting another system (Lever...) means adding one module and one ADAPTERS entry, plus a saved
real response and its expected places in tests/adapter_samples/ (<ats>.json, <ats>.expect.json),
which tests/test_adapter_conformance.py requires; the watch, the pipeline and the judges don't change.
"""

from . import ashby, greenhouse

# A registry instead of an if-chain in the watch: data/boards.json names the system as a string,
# and this is the one place that string becomes code.
ADAPTERS = {m.ATS: m for m in (greenhouse, ashby)}
