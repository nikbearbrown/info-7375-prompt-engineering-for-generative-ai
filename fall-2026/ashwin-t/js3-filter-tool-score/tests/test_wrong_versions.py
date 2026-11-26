"""Each FILTER.md wrong version must fail at least one of the cases written to catch it."""
import unittest

from jobfilter.filter import load_config
from jobfilter.wrong_versions import WRONG_FILTERS
from tests.cases import CASES

CFG = load_config("v1.0")


def failures(filter_cls):
    f = filter_cls(CFG)
    out = []
    for name, p, decision, score, _ in CASES:
        d = f.classify(p)
        if d["decision"] != decision or (score is not None and d["score"] != score):
            out.append(name)
    return out


class WrongVersionsAreCaught(unittest.TestCase):
    def test_each_wrong_version_fails_its_own_case(self):
        for wid, cls in WRONG_FILTERS.items():
            with self.subTest(wid):
                own = {name for name, _, _, _, catches in CASES if wid in catches}
                self.assertTrue(own, f"{wid} has no case meant to catch it")
                self.assertTrue(own & set(failures(cls)), f"{wid} passed every case meant to catch it")

    def test_matrix(self):
        """Printed for the README: which cases each wrong version fails."""
        for wid, cls in WRONG_FILTERS.items():
            self.assertGreater(len(failures(cls)), 0, wid)


if __name__ == "__main__":
    for wid, cls in WRONG_FILTERS.items():
        print(wid, cls.__doc__.strip().splitlines()[0], "->", failures(cls))
