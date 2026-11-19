import importlib.util
import os
import random
import tempfile
import unittest
from datetime import datetime
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("journal_gate", os.path.join(HERE, "..", "ops", "journal_gate.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def kst(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=g.KST)


class PickTime(unittest.TestCase):
    def test_excludes_yesterday_hour_and_stays_in_afternoon(self):
        for prev in ("12:05", "15:59", "17:00", None):
            for seed in range(300):
                t = g.pick_time(prev, random.Random(seed))
                h = int(t[:2])
                self.assertTrue(12 <= h <= 17, t)
                if prev:
                    self.assertNotEqual(h, int(prev[:2]))


class Roll(unittest.TestCase):
    def test_same_day_keeps_slot(self):
        s = {"date": "2026-11-14", "time": "14:10", "prev_date": None, "prev_time": None, "published": False}
        self.assertIs(g.roll(s, "2026-11-14"), s)

    def test_rollover_moves_old_to_prev_and_resets(self):
        s = {"date": "2026-11-13", "time": "16:20", "prev_date": None, "prev_time": None, "published": True}
        n = g.roll(s, "2026-11-14", random.Random(1))
        self.assertEqual((n["date"], n["prev_date"], n["prev_time"], n["published"]), ("2026-11-14", "2026-11-13", "16:20", False))
        self.assertNotEqual(n["time"][:2], "16")

    def test_first_run_without_state(self):
        n = g.roll(None, "2026-11-14", random.Random(2))
        self.assertIsNone(n["prev_time"])
        self.assertFalse(n["published"])


class Run(unittest.TestCase):
    def setUp(self):
        self.q = tempfile.mkdtemp()
        self.calls = []

    def pub(self, ok=True):
        def f(date, hhmm, queue):
            self.calls.append((date, hhmm))
            return ok
        return f

    def seed(self, **kw):
        s = {"date": "2026-11-14", "time": "14:00", "prev_date": "2026-11-13", "prev_time": "22:40", "published": False}
        s.update(kw)
        g.save(os.path.join(self.q, "slot.json"), s)

    def test_waits_before_time(self):
        self.seed()
        self.assertEqual(g.run(kst("2026-11-14 13:45"), self.q, publish=self.pub()), "wait")
        self.assertEqual(self.calls, [])

    def test_publishes_after_time_once(self):
        self.seed()
        self.assertEqual(g.run(kst("2026-11-14 14:15"), self.q, publish=self.pub()), "published")
        self.assertTrue(g.load(os.path.join(self.q, "slot.json"))["published"])
        self.assertEqual(g.run(kst("2026-11-14 14:30"), self.q, publish=self.pub()), "skip")
        self.assertEqual(len(self.calls), 1)

    def test_failure_keeps_unpublished_for_retry(self):
        self.seed()
        self.assertEqual(g.run(kst("2026-11-14 14:15"), self.q, publish=self.pub(False)), "failed")
        self.assertFalse(g.load(os.path.join(self.q, "slot.json"))["published"])

    def test_already_published_is_ignored(self):
        self.seed(published=True)
        self.assertEqual(g.run(kst("2026-11-14 17:45"), self.q, publish=self.pub()), "skip")
        self.assertEqual(self.calls, [])

    def test_new_day_rolls_then_gate_excludes_hour(self):
        self.seed(date="2026-11-13", time="15:30", published=True)
        g.run(kst("2026-11-14 12:00"), self.q, rng=random.Random(5), publish=self.pub())
        s = g.load(os.path.join(self.q, "slot.json"))
        self.assertEqual((s["date"], s["prev_time"], s["published"]), ("2026-11-14", "15:30", False))
        self.assertNotEqual(s["time"][:2], "15")

    def test_publish_prearms_next_slot_and_next_day_uses_it(self):
        self.seed()
        g.run(kst("2026-11-14 14:15"), self.q, rng=random.Random(7), publish=self.pub())
        s = g.load(os.path.join(self.q, "slot.json"))
        self.assertEqual(s["next_date"], "2026-11-15")
        self.assertTrue(12 <= int(s["next_time"][:2]) <= 17)
        self.assertNotEqual(s["next_time"][:2], "14")
        g.run(kst("2026-11-15 12:00"), self.q, rng=random.Random(99), publish=self.pub())
        n = g.load(os.path.join(self.q, "slot.json"))
        self.assertEqual((n["date"], n["time"]), ("2026-11-15", s["next_time"]))

    def test_plan_next_failure_keeps_published_true_on_disk(self):
        self.seed()
        path = os.path.join(self.q, "slot.json")
        with mock.patch.object(g, "plan_next", side_effect=RuntimeError("boom")):
            self.assertEqual(g.run(kst("2026-11-14 14:15"), self.q, publish=self.pub()), "published")
        self.assertTrue(g.load(path)["published"])
        # 다음 틱에 같은 날 재발행되지 않는다
        self.assertEqual(g.run(kst("2026-11-14 14:30"), self.q, publish=self.pub()), "skip")
        self.assertEqual(len(self.calls), 1)

    def test_publish_failure_writes_no_next_fields(self):
        self.seed()
        self.assertEqual(g.run(kst("2026-11-14 14:15"), self.q, publish=self.pub(False)), "failed")
        s = g.load(os.path.join(self.q, "slot.json"))
        self.assertNotIn("next_date", s)
        self.assertNotIn("next_time", s)


class Corrupt(unittest.TestCase):
    def roll_with_next(self, next_time, next_date="2026-11-15", seed=11):
        old = {"date": "2026-11-14", "time": "14:00", "published": True,
               "next_date": next_date, "next_time": next_time}
        return g.roll(old, "2026-11-15", random.Random(seed))

    def test_corrupt_next_time_falls_back_to_pick_time(self):
        for bad in ("99:99", "9:5", "20:00", "11:30", "17:60", "1430", None, 1430):
            n = self.roll_with_next(bad)
            self.assertEqual(n["time"], g.pick_time("14:00", random.Random(11)), bad)
            self.assertTrue(g.valid_time(n["time"]), bad)
            self.assertTrue(12 <= int(n["time"][:2]) <= 17, bad)

    def test_next_date_not_today_falls_back_to_pick_time(self):
        n = self.roll_with_next("15:20", next_date="2026-11-16")  # 하루 건너뜀
        self.assertEqual(n["time"], g.pick_time("14:00", random.Random(11)))

    def test_valid_next_time_is_used(self):
        n = self.roll_with_next("15:20")
        self.assertEqual(n["time"], "15:20")


class MonthEnd(unittest.TestCase):
    def test_plan_next_month_and_year_rollover(self):
        for today, expect in (("2026-11-30", "2026-12-01"), ("2026-12-31", "2027-01-01")):
            s = g.plan_next({"time": "14:00"}, today, random.Random(4))
            self.assertEqual(s["next_date"], expect)
            self.assertTrue(g.valid_time(s["next_time"]))
            self.assertNotEqual(s["next_time"][:2], "14")


if __name__ == "__main__":
    unittest.main()
