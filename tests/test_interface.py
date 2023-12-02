import unittest

from aiogram.types import ReplyKeyboardMarkup
from dasbot.interface import Interface


class TestInterface(unittest.TestCase):

    def test_quiz_kb(self):
        keyboard = Interface.quiz_kb()
        self.assertIsInstance(keyboard, ReplyKeyboardMarkup)


if __name__ == '__main__':
    unittest.main()
