import logging
from aiogram import types
from dynaconf import settings

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Interface(object):

    time_choices = ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00", "03:00", "06:00"]

    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz, /settings to change the quiz time.')

    async def welcome(self, chat):
        text = ("Hi! Dasbot will help you memorize German articles.\n"
                "It will send you a short quiz every day -- a few words from 2000 most frequently used ones.\n"
                "To change the preferred quiz time (or turn it off), send /settings command.\n"
                "You can also practice any time by typing /start.")
        await self.bot.send_message(chat.id, text)

    async def daily_hello(self, chat):
        text = "Hi, it's Dasbot! Here's your daily German articles quiz:"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.position}/{settings.QUIZ_LEN}. "
        text += f"What's the article for {chat.quiz.question}?"
        result = await self.bot.send_message(chat.id, text, reply_markup=Interface.quiz_kb())
        log.debug("message sent, result: %s", result)

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "Incorrect, "
        text += f"{chat.quiz.answer} {chat.quiz.question}"
        await message.answer(text)

    async def say_score(self, chat):
        text = f"{chat.quiz.correctly} out of {settings.QUIZ_LEN}"
        text += self.rate(chat.quiz.correctly) + "\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=types.ReplyKeyboardRemove())

    def rate(self, correctly):
        ratio = round(correctly / settings.QUIZ_LEN * 10)
        if ratio in range(0, 4):
            msg = ", keep trying!"
        elif ratio in range(4, 7):
            msg = ", good job!"
        elif ratio in range(7, 10):
            msg = ", excellent!"
        elif ratio == 10:
            msg = ", perfeKt!"
        else:
            msg = "."
        return msg

    async def settings_root(self, message):
        await message.answer("Please select quiz time (time zone Berlin/CET)",
                             reply_markup=Interface.settings_kb())

    async def settings_quiztime_set(self, query, pref):
        text = f'Daily quiz time is set to {pref} (Berlin time)'
        if pref == "UNSUBSCRIBE":
            text = 'Daily quiz is off'
        await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         text=text)

    @staticmethod
    def quiz_kb():
        """ Returns object of ReplyKeyboardMarkup type """
        labels = ('der', 'die', 'das')
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_btns = (types.KeyboardButton(text) for text in labels)
        keyboard_markup.row(*row_btns)
        return keyboard_markup

    @staticmethod
    def settings_kb():
        """ Returns InlineKeyboardMarkup object with quiz options """
        row_width = 4
        inline_kb = types.InlineKeyboardMarkup(row_width=row_width)
        for i, option in enumerate(Interface.time_choices):
            if i % row_width == 0:
                inline_kb.row()
            inline_kb.insert(types.InlineKeyboardButton(option, callback_data=option))
        inline_kb.row()
        inline_kb.insert(types.InlineKeyboardButton("Daily quiz OFF", callback_data="UNSUBSCRIBE"))
        return inline_kb

    def recognized(self, msg_text):
        return msg_text in ['der', 'die', 'das']


if __name__ == "__main__":
    pass
