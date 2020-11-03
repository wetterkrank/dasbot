import unittest
from datetime import datetime

from dasbot import util


class TestUtil(unittest.TestCase):
    def test_next_noon_current_day(self):
        time_am = datetime.fromisoformat('2011-11-04 11:05:23+00:00')
        self.assertEqual(datetime.fromisoformat('2011-11-04 12:00:00+00:00'), util.next_noon(time_am))

    def test_next_noon_next_day(self):
        time_pm = datetime.fromisoformat('2011-11-04 12:05:23+00:00')
        self.assertEqual(datetime.fromisoformat('2011-11-05 12:00:00+00:00'), util.next_noon(time_pm))

    def test_next_quiz_time(self):
        last_quiz_time = datetime.fromisoformat('2011-11-04 11:05:17+00:00')
        now = datetime.fromisoformat('2011-12-01 01:00:00+00:00')
        self.assertEqual(
            datetime.fromisoformat('2011-12-02 11:05:17+00:00'),
            util.next_quiz_time(last_quiz_time, now))


if __name__ == '__main__':
    unittest.main()
