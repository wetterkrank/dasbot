import unittest

from dasbot.database import Database
from dasbot.chat import Chat

DB_ADDRESS = 'mongodb://localhost:27017/'
DB_NAME = 'dasbot_test'


class TestDB(unittest.TestCase):
    def setUp(self):
        self.db = Database(DB_ADDRESS, DB_NAME)

    def test_save_chat(self):
        chat = Chat(chat_id = 1001)
        chat.subscribed = True
        result = self.db.save_chat(chat)
        success = result.matched_count == 1 or result.modified_count == 1
        self.assertEqual(success, True)

    def test_load_chat(self):
        result = self.db.load_chat(1001)
        self.assertEqual(result.id, 1001)

    def test_get_subscriptions(self):
        result = self.db.get_subscriptions("12:00")
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0], 1001)
        result = self.db.get_subscriptions("06:00")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
