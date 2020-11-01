import logging
from aiogram import types
from . import config

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Interface(object):
    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz.')

    async def welcome(self, chat):
        text = ("Hi! Dasbot will help you memorize German articles.\n"
                "It will send you a short quiz every day. "
                "You can also practice any time by sending the /start command.")
        await self.bot.send_message(chat.id, text)

    async def daily_hello(self, chat):
        text = "Hi, it's Dasbot! Here's your daily German articles quiz:"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.position}/{config.QUIZ_LEN}. "
        text += f"What's the article for {chat.quiz.question}?"
        result = await self.bot.send_message(chat.id, text, reply_markup=self.quiz_kb())
        log.debug("message sent, result: %s", result)

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "Incorrect, "
        text += f"{chat.quiz.answer} {chat.quiz.question}"
        await message.answer(text)  # Reply balloon, no quoting?

    async def say_score(self, chat):
        text = f"{chat.quiz.correctly} out of {config.QUIZ_LEN}"
        text += self.rate(chat.quiz.correctly) + "\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=types.ReplyKeyboardRemove())

    def rate(self, correctly):
        ratio = round(correctly/config.QUIZ_LEN * 10)
        if ratio in range(0, 4):
            msg = ", keep trying!"
        elif ratio in range(4, 7):
            msg = ", good job!"
        elif ratio in range(7, 10):
            msg = ", excellent!"
        elif ratio == 10:
            msg = ", perfeKt!"
        else: msg = "."
        return msg

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
