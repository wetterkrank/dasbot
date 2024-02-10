import unittest
from unittest.mock import MagicMock

from dasbot.db.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        mock_settings = MagicMock(
            DB_ADDRESS="mongodb://test:27017/",
            DB_USERNAME="username",
            DB_PASSWORD="password",
        )
        mock_settings.get.side_effect = lambda name: getattr(mock_settings, name)
        self.db = Database(mock_settings)

    def test_url(self):
        self.assertEqual("mongodb://username:password@test:27017/", self.db.url())


if __name__ == "__main__":
    unittest.main()
