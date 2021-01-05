import unittest
from datetime import datetime, timezone
from datetime import timedelta

import mongomock

from dasbot.chats_repo import ChatsRepo
from dasbot.models.chat import Chat


class TestChatsRepo(unittest.TestCase):
    def setUp(self):
        self.chats_collection = mongomock.MongoClient().db.collection
        self.scores_collection = mongomock.MongoClient().db.collection
        self.chats_repo = ChatsRepo(self.chats_collection, self.scores_collection)

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

    def test_load_new_chat(self):
        result = self.chats_repo.load_chat(1001)
        self.assertEqual(result.id, 1001)
        self.assertEqual(True, result.subscribed)
        self.assertEqual(None, result.last_seen)

    def test_get_pending_chats_empty(self):
        ts = datetime.now(tz=timezone.utc)
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts + timedelta(seconds=1))
        self.chats_repo.save_chat(chat)

        result = self.chats_repo.get_pending_chats(ts)
        self.assertEqual(0, len(result))

    def test_get_pending_chats_non_empty(self):
        ts = datetime.now(tz=timezone.utc)
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts - timedelta(seconds=1))
        self.chats_repo.save_chat(chat)

        result = self.chats_repo.get_pending_chats(ts)
        self.assertEqual(1, len(result))

    def test_get_pending_chats_empty_ts(self):
        ts = datetime.now(tz=timezone.utc)
        chat = Chat(chat_id=1001, quiz_scheduled_time=None)
        self.chats_repo.save_chat(chat)

        result = self.chats_repo.get_pending_chats(ts)
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
