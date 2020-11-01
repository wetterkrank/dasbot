import unittest
from datetime import datetime

from dasbot import util


class TestUtil(unittest.TestCase):
    def test_next_noon_current_day(self):
        ts_before_noon = datetime.fromisoformat('2011-11-04 11:05:23.283+00:00')
        self.assertEqual(datetime.fromisoformat('2011-11-04 12:00:00.000+00:00'), util.next_noon(ts_before_noon))

    def test_next_noon_next_day(self):
        ts_before_noon = datetime.fromisoformat('2011-11-04 12:05:23.283+00:00')
        self.assertEqual(datetime.fromisoformat('2011-11-05 12:00:00.000+00:00'), util.next_noon(ts_before_noon))


if __name__ == '__main__':
    unittest.main()
