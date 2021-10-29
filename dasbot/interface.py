import logging

from aiogram import types

log = logging.getLogger(__name__)


class Interface(object):
    def __init__(self, bot):
        self.bot = bot
        self.settings_text = {
            'main-hint': 'Please select option',
            'main-btn1': 'Quiz length',
            'main-btn2': 'Daily quiz time',
            'quiz-len-hint': 'Please select the number of questions',
            'quiz-time-hint': 'Please select quiz time (time zone Berlin/CET)',
            'quiz-time-btn': 'Daily quiz OFF'
        }

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz, /settings to change the quiz time.')

    async def welcome(self, chat):
        text = ("Hi! I'm Dasbot. My mission is to help you memorize German articles.\n"
                "I know about 2000 most frequently used German words, and I'll be sending you a short quiz every day.\n"
                "To change the preferred quiz time (or turn it off), use /settings command.\n"
                "You can also practice any time by sending /start.")
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
        if correct: text += " ✅"
        await message.answer(text)

    async def announce_result(self, chat):
        text = f"{chat.quiz.correctly} out of {chat.quiz.length}"
        text += self.rate(chat.quiz.correctly, chat.quiz.length) + "\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=types.ReplyKeyboardRemove())

    def rate(self, correctly, total):
        ratio = round(correctly / total * 10)
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


    async def send_stats(self, message, stats, dict_length):
        def bullet(item):
            return f"• {item['word']}: {item['count']}  "
        def wordlist(key):
            return "\n".join([bullet(item) for item in stats[key]]) + "\n\n"
        text = f"*Your progress* 📈\n{stats['touched']} words touched out of {dict_length}\n\n"
        text += "*I recommend working on these words*:\n\n"
        if len(stats['mistakes_30days']) > 0:
            text += "Last 30 days' top 💔\n"
            text += wordlist('mistakes_30days')
        if len(stats['mistakes_alltime']) > 0:
            text += "All-time top 💔\n"
            text += wordlist('mistakes_alltime')
        await message.answer(text, parse_mode='Markdown')

    @staticmethod
    def quiz_kb():
        """ Returns object of ReplyKeyboardMarkup type """
        labels = ('der', 'die', 'das')
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_btns = (types.KeyboardButton(text) for text in labels)
        keyboard_markup.row(*row_btns)
        return keyboard_markup

    def quiz_time_set(self, pref):
        return (f'Daily quiz time is set to {pref} (Berlin time)', 'Daily quiz is off')[pref == "UNSUBSCRIBE"]

    def quiz_length_set(self, pref):
        return f'Quiz length is set to {pref} questions'


if __name__ == "__main__":
    pass
