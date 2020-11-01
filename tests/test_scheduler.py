import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import aiounittest
import mongomock
from aiogram.utils.exceptions import BotBlocked

from dasbot.chats_repo import ChatsRepo
from dasbot.models.chat import Chat, ChatSchema
from dasbot.scheduler import Scheduler


class TestScheduler(aiounittest.AsyncTestCase):
    ts = datetime.utcnow()
    tomorrow = datetime.utcnow() + timedelta(days=1)

    @staticmethod
    async def success(chat):
        pass

    @staticmethod
    async def fail(chat):
        raise BotBlocked("foobar")

    def setUp(self):
        self.chats_collection = mongomock.MongoClient().db.collection
        self.chats_repo = ChatsRepo(self.chats_collection)

    async def test_send_quiz(self):
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        current_quiz_time = datetime.fromisoformat('2011-11-04 12:05:23')
        expected_next_quiz_time = current_quiz_time.replace(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)

        self.ui_mock = MagicMock()
        self.ui_mock.daily_hello = TestScheduler.success
        self.ui_mock.ask_question = TestScheduler.success
        self.scheduler = Scheduler(self.ui_mock, self.chats_repo)

        chat = Chat(chat_id=1001, quiz_scheduled_time=current_quiz_time)
        result = await self.scheduler.send_quiz(chat)

        saved_chat = ChatSchema().load(self.chats_collection.find_one({"chat_id": 1001}))

        self.assertEqual(1, saved_chat.quiz.position)
        self.assertEqual(expected_next_quiz_time, saved_chat.quiz_scheduled_time)

        self.assertTrue(result)

    async def test_send_quiz_fail_daily_hello(self):
        self.ui_mock = MagicMock()
        self.ui_mock.daily_hello = TestScheduler.fail
        self.ui_mock.ask_question = TestScheduler.success
        self.scheduler = Scheduler(self.ui_mock, self.chats_repo)

        ts = datetime.utcnow()
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts)
        result = await self.scheduler.send_quiz(chat)
        self.assertFalse(result)

    async def test_send_quiz_fail_ask_question(self):
        self.ui_mock = MagicMock()
        self.ui_mock.daily_hello = TestScheduler.success
        self.ui_mock.ask_question = TestScheduler.fail
        self.scheduler = Scheduler(self.ui_mock, self.chats_repo)

        ts = datetime.utcnow()
        chat = Chat(chat_id=1001, quiz_scheduled_time=ts)
        result = await self.scheduler.send_quiz(chat)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
