"""Each wrong version from GATE.md, swapped in one at a time, must make its named
tests fail; with the real code in place, the same tests must pass. A wrong version
that survives means the test list is too weak (Chapters 4-5)."""

import unittest
from unittest import mock

from tests import wrong_versions


def failures(test_names):
    suite = unittest.defaultTestLoader.loadTestsFromNames(test_names)
    result = unittest.TestResult()
    suite.run(result)
    return len(result.failures) + len(result.errors), result.testsRun


class WrongVersionsCaughtTest(unittest.TestCase):
    def test_the_named_tests_pass_on_the_real_code(self):
        names = sorted({name for names in wrong_versions.CAUGHT_BY.values() for name in names})
        broken, ran = failures(names)
        self.assertEqual((broken, ran), (0, len(names)))

    def test_every_wrong_version_fails_each_of_its_named_tests(self):
        for label, (target, replacement) in wrong_versions.ALL.items():
            for name in wrong_versions.CAUGHT_BY[label]:
                with self.subTest(wrong_version=label, test=name), mock.patch(target, replacement):
                    broken, ran = failures([name])
                    self.assertEqual(ran, 1)
                    self.assertEqual(broken, 1, f"{label} survived {name}")


if __name__ == "__main__":
    unittest.main()
