import unittest
from datetime import datetime

from dasbot import util


class TestUtil(unittest.TestCase):
    def test_next_quiz_time(self):
        last_quiz_time = datetime.fromisoformat('2011-11-04 11:05:17+00:00')
        now = datetime.fromisoformat('2011-12-01 01:00:00+00:00')
        self.assertEqual(
            datetime.fromisoformat('2011-12-02 11:05:17+00:00'),
            util.next_quiz_time(last_quiz_time, now))

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


if __name__ == '__main__':
    unittest.main()
