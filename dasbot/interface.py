import logging

from aiogram import html
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

log = logging.getLogger(__name__)


class Interface(object):
    def __init__(self, bot):
        self.bot = bot
        self.settings_text = {
            'main-hint': 'Please select option',
            'main-btn1': 'Quiz length',
            'main-btn2': 'Quiz mode',
            'main-btn3': 'Daily quiz time',
            'quiz-len-hint': 'Please select the number of questions',
            'quiz-time-hint': 'Please select quiz time (time zone Berlin/CET)',
            'quiz-time-btn': 'Daily quiz OFF',
            'quiz-mode-hint': 'Please select quiz mode',
            'quiz-mode-advance': 'Review + new words',
            'quiz-mode-review': 'Maximize review',
        }

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz, /settings to change the quiz time or length. Any issues -- please message @wetterkrank.')

    async def welcome(self, chat):
        text = ("Hi! I'm Dasbot. \nMy mission is to help you memorize German articles.\n"
                "I'll be sending you a short quiz every day.\n\n"
                "My dictionary has about 2000 most frequently used German nouns, and we'll start from the most common ones like Frau, Kind, Mann, and move on to less frequent words as you progress. \n\n"
                "To change the preferred quiz time/length (or turn it off), use /settings command. Practice any time by sending /start.\n\n"
                "Let's go!")
        await self.bot.send_message(chat.id, text)

    async def daily_hello(self, chat):
        text = "Hi, it's Dasbot! Here's your daily German articles quiz:"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.pos}/{chat.quiz.length}. "
        text += f"What's the article for <b>{html.quote(chat.quiz.question)}</b>?"
        result = await self.bot.send_message(chat.id, text,
                                             reply_markup=Interface.quiz_kb(),
                                             disable_notification=True)
        log.debug("message sent, result: %s", result)

    async def give_hint(self, quiz, message, dictionary):
        translation = dictionary.translation(quiz.question, 'en') or '?'
        text = f"{quiz.question}: {translation}"
        await message.answer(text, disable_notification=True)

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "❌ Incorrect, "
        text += f"<b>{html.quote(chat.quiz.answer)} {html.quote(chat.quiz.question)}</b>"
        if correct: text += " ✅"
        await message.answer(text, disable_notification=True)

    async def announce_result(self, chat):
        text = f"{chat.quiz.correctly} out of {chat.quiz.length}"
        text += self.rate(chat.quiz.correctly, chat.quiz.length) + "\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=ReplyKeyboardRemove())

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


    async def quiz_empty(self, message):
        await message.reply("Hmm, I couldn't find any new words or words to review. Well done! Come back later!")

    async def send_stats(self, message, stats, review_count, dict_length):
        def bullet(item):
            return f"• {html.quote(item['articles'])} {html.quote(item['word'])}: {item['count']}  "
        def wordlist(key):
            return "\n".join([bullet(item) for item in stats[key]]) + "\n\n"
        memorized = stats.get('touched') - review_count
        progress = round(memorized / dict_length * 100)
        text = f"📈 <b>Your progress</b>: {progress}%\n"
        text += f"• words seen: {stats['touched']} / {dict_length}\n"
        text += f"• words memorized: {memorized}\n"
        text += f"• words to repeat: {review_count}\n\n"
        text += "<b>I recommend working on these words</b>:\n"
        if len(stats['mistakes_30days']) > 0:
            text += "Last 30 days' top mistakes\n"
            text += wordlist('mistakes_30days')
        await message.answer(text)

    @staticmethod
    def quiz_kb() -> ReplyKeyboardMarkup:
        labels = ('der', 'die', 'das', '?')
        buttons = [(KeyboardButton(text=text) for text in labels)]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        return keyboard

    def quiz_time_set(self, pref):
        return (f'Daily quiz time is set to {pref} (Berlin time)', 'Daily quiz is off')[pref == "UNSUBSCRIBE"]

    def quiz_length_set(self, pref):
        return f'Quiz length is set to {pref} questions'

    def quiz_mode_set(self, pref):
        return ('Quiz mode is set to 50% review. Dasbot will add new words to each quiz.', 'Quiz mode is set to max review. Dasbot will prioritise repetition.')[pref == 'review']


if __name__ == "__main__":
    pass
