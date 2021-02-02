import logging
from aiogram import types
from dynaconf import settings

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Interface(object):
    TIME_OPTIONS = ["0900", "1200", "1500", "1800", "2100", "0000", "0300", "0600"]
    LENGTH_OPTIONS = [5, 10, 20, 50]
    SETTINGS_MENU = {
        0: {
            'main': {'hint': 'Please select option', 'row_len': 2, 'btns': [
                {'text': 'Quiz length', 'action': 'quiz-len'},
                {'text': 'Daily quiz time', 'action': 'quiz-time'}
            ]}
        },
        1: {
            'quiz-len': {'hint': 'Please select the number of questions', 'row_len': 4, 'btns': [
                {'text': n, 'action': n} for n in LENGTH_OPTIONS
            ]},
            'quiz-time': {'hint': 'Please select quiz time (time zone Berlin/CET)', 'row_len': 4, 'btns': [
                {'text': f"{t[:2]}:{t[2:]}", 'action': t} for t in TIME_OPTIONS
            ] + [{'text': 'Daily quiz OFF', 'action': 'UNSUBSCRIBE'}]}
        }
    }

    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz, /settings to change the quiz time.')

    async def welcome(self, chat):
        text = ("Hi! I'm Dasbot. My mission is to help you memorize German articles.\n"
                "I know about 2000 most frequently used German words, and I'll be sending you a short quiz every day.\n"
                "To change the preferred quiz time (or turn it off), send /settings command.\n"
                "You can also practice any time by typing /start.")
        await self.bot.send_message(chat.id, text)

    async def daily_hello(self, chat):
        text = "Hi, it's Dasbot! Here's your daily German articles quiz:"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.pos}/{chat.quiz.length}. "
        text += f"What's the article for {chat.quiz.question}?"
        result = await self.bot.send_message(chat.id, text, reply_markup=Interface.quiz_kb())
        log.debug("message sent, result: %s", result)

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "Incorrect, "
        text += f"{chat.quiz.answer} {chat.quiz.question}"
        await message.answer(text)

    async def announce_result(self, chat):
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

    @staticmethod
    def quiz_kb():
        """ Returns object of ReplyKeyboardMarkup type """
        labels = ('der', 'die', 'das')
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_btns = (types.KeyboardButton(text) for text in labels)
        keyboard_markup.row(*row_btns)
        return keyboard_markup

    # TODO: Move the settings menu out of the UI?
    async def settings_main(self, message, callback_gen):
        await message.answer(text=Interface.SETTINGS_MENU[0]['main']['hint'],
                             reply_markup=Interface.settings_kb(callback_gen, 0, 'main'))

    async def settings_menu(self, query, callback_gen, level, menu_id):
        await query.message.edit_text(text=Interface.SETTINGS_MENU[level][menu_id]['hint'],
                                      reply_markup=self.settings_kb(callback_gen, level, menu_id))

    async def settings_confirm(self, query, text):
        await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         text=text)

    def quiz_time_set(self, pref):
        return (f'Daily quiz time is set to {pref} (Berlin time)', 'Daily quiz is off')[pref == "UNSUBSCRIBE"]

    def quiz_length_set(self, pref):
        return f'Quiz length is set to {pref} questions'

    @staticmethod
    def settings_kb(callback_gen, level, menu_id):
        menu = Interface.SETTINGS_MENU[level][menu_id]
        row_width = menu['row_len']
        buttons = menu['btns']
        markup = types.InlineKeyboardMarkup(row_width=row_width)
        for i, button in enumerate(buttons):
            callback_data = callback_gen(level=level + 1, menu_id=menu_id, selection=button['action'])
            if i % row_width == 0:
                markup.row()
            markup.insert(types.InlineKeyboardButton(text=button['text'], callback_data=callback_data))
        return markup

    def recognized(self, msg_text):
        return msg_text in ['der', 'die', 'das']


if __name__ == "__main__":
    pass
