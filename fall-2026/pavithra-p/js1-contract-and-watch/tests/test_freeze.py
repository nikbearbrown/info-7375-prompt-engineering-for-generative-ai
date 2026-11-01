"""The experiment's selection and split. Every job here is a CONSTRUCTED fixture."""
import unittest

from agent import freeze


def job(job_id, title, location="Remote, US"):
    return {"id": job_id, "title": title, "location": {"name": location}, "content": ""}


class FreezeTests(unittest.TestCase):
    def test_keeps_only_non_senior_us_engineering_roles(self):
        jobs = [job(1, "Software Engineer II"), job(2, "Staff Software Engineer"), job(3, "Software Engineer", "Toronto, ON, CA"),
                job(4, "Account Executive"), job(5, "Software Engineer Intern 2027")]
        self.assertEqual([j["id"] for j, _ in freeze.select([jobs])], [1])

    def test_watched_board_first_then_others_by_id_and_split_alternates(self):
        pinterest = [job(30, "Software Engineer"), job(10, "Backend Engineer")]
        others = [[job(5, "AI Engineer"), job(50, "Cloud Engineer")], [job(1, "Software Engineer")]]
        picked = freeze.select([pinterest] + others, n=4)
        self.assertEqual([j["id"] for j, _ in picked], [10, 30, 1, 5])
        self.assertEqual([s for _, s in picked], ["dev", "held-out", "dev", "held-out"])

    def test_set_2_drops_set_1_and_repeats_and_takes_up_to_4_per_board_biggest_first(self):
        small = [job(i, f"Software Engineer {i}") for i in (3, 1, 2)] + [job(4, "Software Engineer 1")]
        big = [job(i, f"Backend Engineer {i}") for i in range(10, 16)]
        picked = freeze.select_set2([small, big], exclude={10}, per_board=4, n=6)
        self.assertEqual([j["id"] for j, _ in picked], [11, 12, 13, 14, 1, 2], "same title kept once (4 dropped)")
        self.assertEqual([s for _, s in picked], ["dev", "held-out"] * 3)

    def test_twenty_split_ten_ten(self):
        jobs = [job(i, "Software Engineer") for i in range(1, 30)]
        picked = freeze.select([jobs])
        self.assertEqual(len(picked), 20)
        self.assertEqual(sum(s == "dev" for _, s in picked), 10)


if __name__ == "__main__":
    unittest.main()
