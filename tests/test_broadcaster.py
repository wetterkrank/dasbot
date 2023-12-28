import logging

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import aiounittest
import mongomock
from aiogram.exceptions import TelegramAPIError
from aiogram.methods import SendMessage

from dasbot.db.chats_repo import ChatsRepo
from dasbot.models.chat import Chat, ChatSchema
from dasbot.models.dictionary import Dictionary
from dasbot.broadcaster import Broadcaster


class TestBroadcaster(aiounittest.AsyncTestCase):
    ts = datetime.now(tz=timezone.utc)
    tomorrow = datetime.now(tz=timezone.utc) + timedelta(days=1)

    @staticmethod
    async def success(chat):
        pass

    @staticmethod
    async def failGeneric(chat):
        raise TelegramAPIError(method=SendMessage, message="foobar")

    def setUp(self):
        self.chats_collection = mongomock.MongoClient(tz_aware=True).db.collection
        self.scores_collection = mongomock.MongoClient(tz_aware=True).db.collection
        chats_repo = ChatsRepo(self.chats_collection, self.scores_collection)
        self.ui_mock = MagicMock()
        self.dictionary = Dictionary({w: {'articles': 'foo', 'translation': {'en': 'bar'}, 'level': 1} for w in ['Tag', 'Monat', 'Jahr']})
        self.broadcaster = Broadcaster(self.ui_mock, chats_repo, self.dictionary)

    async def test_send_quiz(self):
        tomorrow = datetime.now(tz=timezone.utc).date() + timedelta(days=1)
        current_quiz_time = datetime.fromisoformat('2011-11-04 12:05:23+00:00')
        expected_next_quiz_time = current_quiz_time.replace(
            year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
        self.ui_mock.daily_hello = TestBroadcaster.success
        self.ui_mock.ask_question = TestBroadcaster.success

        chat = Chat(chat_id=1001, quiz_scheduled_time=current_quiz_time)
        result = await self.broadcaster.send_quiz(chat)

        saved_chat = ChatSchema().load(self.chats_collection.find_one({"chat_id": 1001}))
        self.assertEqual(1, saved_chat.quiz.pos)
        self.assertEqual(expected_next_quiz_time, saved_chat.quiz_scheduled_time)
        self.assertTrue(result)

    async def test_send_quiz_fail_daily_hello(self):
        logging.disable(logging.ERROR)
        self.ui_mock.daily_hello = TestBroadcaster.failGeneric
        self.ui_mock.ask_question = TestBroadcaster.success

        ts = datetime.now(tz=timezone.utc)
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts)
        result = await self.broadcaster.send_quiz(chat)
        self.assertFalse(result)

    async def test_send_quiz_fail_ask_question(self):
        logging.disable(logging.ERROR)
        self.ui_mock.daily_hello = TestBroadcaster.success
        self.ui_mock.ask_question = TestBroadcaster.failGeneric

        ts = datetime.now(tz=timezone.utc)
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts)
        result = await self.broadcaster.send_quiz(chat)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
