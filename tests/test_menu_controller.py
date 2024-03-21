import aiounittest
from unittest.mock import AsyncMock, MagicMock, ANY
import mongomock

from aiogram.types import InlineKeyboardMarkup
from dasbot.db.chats_repo import ChatsRepo
from dasbot.menu_controller import MenuController


class TestMenuController(aiounittest.AsyncTestCase):
    def setUp(self):
        chats_col = mongomock.MongoClient(tz_aware=True).db.collection
        scores_col = mongomock.MongoClient(tz_aware=True).db.collection
        chats_repo = ChatsRepo(chats_col, scores_col)
        ui = MagicMock()
        settings_dict = MagicMock()
        settings_dict.__getitem__.side_effect = lambda name: name
        ui.settings_text = settings_dict
        self.menucon = MenuController(ui, chats_repo)

    async def test_main(self):
        message_mock = AsyncMock()
        await self.menucon.main(message=message_mock)
        message_mock.answer.assert_called_with(text='main-hint', reply_markup=ANY)

    def test_settings_kb(self):
        level = 1
        menu_id = 'quiz-time'
        keyboard = self.menucon.settings_kb(level, menu_id)
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        self.assertEqual(len(keyboard.inline_keyboard), 3)
        self.assertEqual(keyboard.inline_keyboard[-1][0].callback_data, 'menu:2:quiz-time:UNSUBSCRIBE')
