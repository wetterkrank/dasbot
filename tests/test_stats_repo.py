import unittest

import mongomock

from dasbot.db.stats_repo import StatsRepo


class TestStatsRepo(unittest.TestCase):
    def setUp(self):
        scores_col = mongomock.MongoClient().db.collection
        stats_col = mongomock.MongoClient().db.collection
        self.stats_repo = StatsRepo(scores_col, stats_col)

    def test_get_stats_no_data(self):
        stats = self.stats_repo.get_stats(1)
        self.assertDictEqual(
            {'touched': 0, 'mistakes_30days': []}, stats)


if __name__ == '__main__':
    unittest.main()
