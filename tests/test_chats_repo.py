import unittest

import mongomock

from dasbot.chats_repo import ChatsRepo
from dasbot.models.chat import Chat


class TestChatsRepo(unittest.TestCase):
    def setUp(self):
        self.chats_collection = mongomock.MongoClient().db.collection
        self.chats_repo = ChatsRepo(self.chats_collection)

    def test_save_chat(self):
        chat = Chat(chat_id=1001)
        self.chats_repo.save_chat(chat)
        saved_chats = list(self.chats_collection.find())
        self.assertEqual(1, len(saved_chats))
        self.assertEqual(1001, saved_chats[0]['chat_id'])

    def test_load_saved_chat(self):
        chat = Chat(chat_id=1001, subscribed=False)
        self.chats_repo.save_chat(chat)
        result = self.chats_repo.load_chat(1001)
        self.assertEqual(False, result.subscribed)

    def test_load_chat(self):
        result = self.chats_repo.load_chat(1001)
        self.assertEqual(result.id, 1001)
        self.assertEqual(True, result.subscribed)

    def test_get_subscriptions(self):
        chat = Chat(chat_id=1001)
        self.chats_repo.save_chat(chat)

        result = self.chats_repo.get_subscriptions("12:00")
        self.assertGreater(len(result), 0)
        self.assertEqual(1001, result[0])
        result = self.chats_repo.get_subscriptions("06:00")
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
