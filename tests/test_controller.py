import aiounittest
from unittest.mock import AsyncMock, MagicMock, ANY
import mongomock

from dasbot.db.chats_repo import ChatsRepo
from dasbot.controller import Controller
from dasbot.db.stats_repo import StatsRepo
from dasbot.models.dictionary import Dictionary

class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

class TestController(aiounittest.AsyncTestCase):
    def setUp(self):
        chats_col = mongomock.MongoClient(tz_aware=True).db.collection
        scores_col = mongomock.MongoClient(tz_aware=True).db.collection
        stats_col = mongomock.MongoClient(tz_aware=True).db.collection
        chats_repo = ChatsRepo(chats_col, scores_col)
        stats_repo = StatsRepo(scores_col, stats_col)
        bot = MagicMock()
        dict_data = {
            "foo": {"articles": "bar", "translation": {"en": "baz"}, "level": 1},
            "bar": {"articles": "foo", "translation": {"en": "woo"}, "level": 2},
        }
        dictionary = Dictionary(dict_data)
        self.controller = Controller(bot, chats_repo, stats_repo, dictionary)

    async def test_stats(self):
        message_mock = AsyncMock()
        await self.controller.stats(message_mock)
        message_mock.answer.assert_called_with(AnyStringWith('<b>Your progress: 0%</b>'))
        message_mock.answer.assert_called_with(AnyStringWith('words seen: 0 / 2'))
        message_mock.answer.assert_called_with(AnyStringWith('words to repeat: 0'))
        message_mock.answer.assert_called_with(AnyStringWith('words memorized: 0'))
