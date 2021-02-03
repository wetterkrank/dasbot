import unittest

from aiogram import types
from dasbot.interface import Interface


class TestInterface(unittest.TestCase):
    # TODO: Refactor without injecting callback_gen
    # def test_settings_kb(self):
    #     keyboard = Interface.settings_kb()
    #     self.assertIsInstance(keyboard, types.inline_keyboard.InlineKeyboardMarkup)
    #     self.assertEqual(keyboard.row_width, 4)

    def test_quiz_kb(self):
        keyboard = Interface.quiz_kb()
        self.assertIsInstance(keyboard, types.reply_keyboard.ReplyKeyboardMarkup)
        # TODO: check buttons


if __name__ == '__main__':
    unittest.main()
