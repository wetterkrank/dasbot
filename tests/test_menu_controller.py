import aiounittest
from unittest.mock import AsyncMock, MagicMock, ANY
import mongomock

from aiogram import types
from dasbot.db.chats_repo import ChatsRepo
from dasbot.menu_controller import MenuController


class TestMenuController(aiounittest.AsyncTestCase):
    def setUp(self):
        chats_col = mongomock.MongoClient(tz_aware=True).db.collection
        scores_col = mongomock.MongoClient(tz_aware=True).db.collection
        chats_repo = ChatsRepo(chats_col, scores_col)
        ui = MagicMock()
        ui.settings_text = {
            'main-hint': 'Please select option',
            'main-btn1': '',
            'main-btn2': '',
            'quiz-len-hint': '',
            'quiz-time-hint': '',
            'quiz-time-btn': ''
        }
        self.menucon = MenuController(ui, chats_repo)

    async def test_main(self):
        message_mock = AsyncMock()
        await self.menucon.main(message=message_mock)
        message_mock.answer.assert_called_with(text='Please select option', reply_markup=ANY)

    def test_settings_kb(self):
        level = 1
        menu_id = 'quiz-time'
        keyboard = self.menucon.settings_kb(level, menu_id)
        self.assertIsInstance(keyboard, types.inline_keyboard.InlineKeyboardMarkup)
        self.assertEqual(keyboard.row_width, 4)
        self.assertEqual(keyboard['inline_keyboard'][-1][0].callback_data, 'menu:2:quiz-time:UNSUBSCRIBE')
