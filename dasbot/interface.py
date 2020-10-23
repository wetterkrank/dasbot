import logging
from aiogram import types
from . import config

logger = logging.getLogger(__name__)


class Interface(object):
    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz.')

    async def welcome(self, chat):
        text = "Welcome!"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.position}/{config.QUIZ_LEN}. "
        text += f"What's the article for {chat.quiz.question}?"
        await self.bot.send_message(chat.id, text, reply_markup=self.quiz_kb())

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "Incorrect, "
        text += f"{chat.quiz.answer} {chat.quiz.question}"
        await message.answer(text)  # Reply balloon, no quoting?

    async def say_score(self, chat):
        text = f"{chat.quiz.correctly} out of {config.QUIZ_LEN}, nice try!\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=types.ReplyKeyboardRemove())

    def quiz_kb(self):
        ''' Returns object of ReplyKeyboardMarkup type '''
        labels = ('der', 'die', 'das')
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_btns = (types.KeyboardButton(text) for text in labels)
        keyboard_markup.row(*row_btns)
        return keyboard_markup

    def settings_kb(self):
        ''' Returns object of ReplyKeyboardMarkup type '''
        pass

    def recognized(self, msg_text):
        return msg_text in ['der', 'die', 'das']


if __name__ == "__main__":
    pass
