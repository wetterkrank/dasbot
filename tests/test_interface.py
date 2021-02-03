import unittest

from aiogram import types
from dasbot.interface import Interface


class TestInterface(unittest.TestCase):

    def test_quiz_kb(self):
        keyboard = Interface.quiz_kb()
        self.assertIsInstance(keyboard, types.reply_keyboard.ReplyKeyboardMarkup)
        # TODO: check buttons


if __name__ == '__main__':
    unittest.main()
