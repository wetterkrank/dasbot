import unittest
from unittest.mock import MagicMock

from aiogram.types import ReplyKeyboardMarkup
import aiounittest

from dasbot.interface import Interface
from dasbot.models.quiz import Quiz, QuizMode
from dasbot.models.chat import Chat
from dasbot.models.dictionary import Dictionary


class TestInterface(aiounittest.AsyncTestCase):

    def setUp(self):
        dict_data = {
            "foo": {"articles": "bar", "note": {"de": "baz"}, "frequency": 2.0},
        }
        self.dictionary = Dictionary(dict_data)

        self.bot = unittest.mock.AsyncMock()
        self.ui = Interface(self.bot)

    def test_quiz_kb(self):
        chat = Chat(chat_id=1001)
        keyboard = self.ui.quiz_kb(chat)
        self.assertIsInstance(keyboard, ReplyKeyboardMarkup)

    def test_hint_button(self):
        chat = Chat(chat_id=1001, hint_language="en")
        hint_button = self.ui.hint_button(chat)
        self.assertEqual(hint_button, "🇬🇧?")

    async def test_ask_question(self):
        quiz = Quiz.new(1, {}, self.dictionary, QuizMode.Advance)
        chat = Chat(chat_id=1001, quiz=quiz)
        await self.ui.ask_question(chat, self.dictionary)
        self.bot.send_message.assert_called_once_with(
            chat.id,
            "1/1. What's the article for <b>foo</b> (baz)?",
            reply_markup=unittest.mock.ANY,
            disable_notification=True
        )

if __name__ == '__main__':
    unittest.main()
