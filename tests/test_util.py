import unittest
from datetime import datetime

from dasbot import util


class TestUtil(unittest.TestCase):
    def test_next_quiz_time(self):
        last_quiz_time = datetime.fromisoformat('2011-11-04 11:05:17+00:00')
        now = datetime.fromisoformat('2011-12-01 01:00:00+00:00')
        self.assertEqual(util.next_quiz_time(last_quiz_time, now),
            datetime.fromisoformat('2011-12-02 11:05:17+00:00'))

    def test_next_hhmm_today(self):
        now_early = datetime.fromisoformat('2011-11-01 11:05:23+01:00')
        actual = util.next_hhmm("12:00", now_early)
        expected = datetime.fromisoformat('2011-11-01 12:00:00+01:00')
        self.assertEqual(expected, actual)

    def test_next_hhmm_tomorrow(self):
        now_late = datetime.fromisoformat('2011-11-01 15:05:23+01:00')
        actual = util.next_hhmm("15:00", now_late)
        expected = datetime.fromisoformat('2011-11-02 15:00:00+01:00')
        self.assertEqual(expected, actual)

    def test_month_ago(self):
        now = datetime.fromisoformat('2011-12-01 01:02:03+00:00')
        self.assertEqual(util.month_ago(now),
            datetime.fromisoformat('2011-11-01 01:02:03+00:00'))

    def test_equalizer(self):
        # Even total
        self.assertEqual(util.equalizer(5, 5, 10), (5, 5))
        self.assertEqual(util.equalizer(6, 6, 10), (5, 5))
        self.assertEqual(util.equalizer(1, 1, 10), (1, 1))
        self.assertEqual(util.equalizer(1, 20, 10), (1, 9))
        self.assertEqual(util.equalizer(1, 5, 10), (1, 5))
        self.assertEqual(util.equalizer(20, 1, 10), (9, 1))
        self.assertEqual(util.equalizer(5, 1, 10), (5, 1))
        # Odd total
        self.assertEqual(util.equalizer(4, 5, 9), (4, 5))
        self.assertEqual(util.equalizer(10, 10, 9), (4, 5))
        self.assertEqual(util.equalizer(1, 1, 9), (1, 1))
        self.assertEqual(util.equalizer(20, 1, 9), (8, 1))
        self.assertEqual(util.equalizer(5, 1, 9), (5, 1))
        self.assertEqual(util.equalizer(1, 20, 9), (1, 8))
        self.assertEqual(util.equalizer(1, 5, 9), (1, 5))


if __name__ == '__main__':
    unittest.main()
