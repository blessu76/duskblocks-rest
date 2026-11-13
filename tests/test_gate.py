import importlib.util
import os
import random
import tempfile
import unittest
from datetime import datetime

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


if __name__ == "__main__":
    unittest.main()
