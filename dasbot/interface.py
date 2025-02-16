import logging

from aiogram import html
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from dasbot.i18n import t


log = logging.getLogger(__name__)


# TODO: use templates?
class Interface(object):
    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply(t("help"))

    async def welcome(self, chat):
        await self.bot.send_message(chat.id, t("welcome"))

    async def daily_hello(self, chat):
        await self.bot.send_message(chat.id, t("daily_hello"))

    async def ask_question(self, chat):
        text = t(
            "question",
            number=chat.quiz.pos,
            total=chat.quiz.length,
            word=html.quote(chat.quiz.question),
        )
        await self.bot.send_message(
            chat.id, text, reply_markup=Interface.quiz_kb(), disable_notification=True
        )

    async def give_hint(self, quiz, message, dictionary):
        translation = dictionary.translation(quiz.question, "en") or "?"
        await message.answer(
            t("hint", word=quiz.question, hint=translation),
            disable_notification=True,
        )

    async def give_feedback(self, chat, message, correct):
        answer = f"{html.quote(chat.quiz.answer)} {html.quote(chat.quiz.question)}"
        text = (
            t("feedback.correct", answer=answer)
            if correct
            else t("feedback.incorrect", answer=answer)
        )
        await message.answer(text, disable_notification=True)

    async def announce_result(self, chat):
        text = t(
            "result",
            correct=chat.quiz.correctly,
            total=chat.quiz.length,
            rate=self.rate(chat.quiz.correctly, chat.quiz.length),
        )
        await self.bot.send_message(chat.id, text, reply_markup=ReplyKeyboardRemove())

    def rate(self, correctly, total):
        grades = {
            10: "perfect",
            7: "excellent",
            4: "good",
            0: "ok",
        }
        ratio = round(correctly / total * 10)
        grade = next(grades[level] for level in grades.keys() if ratio >= level)
        return t(f"rate.{grade}")

    async def quiz_empty(self, message):
        await message.reply(t("empty"))

    async def send_stats(self, message, stats, review_count, dict_length):
        def bullet(item):
            return f"• {html.quote(item['articles'])} {html.quote(item['word'])}: {item['count']}  "

        def wordlist(key):
            return "\n".join([bullet(item) for item in stats[key]]) + "\n\n"

        memorized = stats.get("touched") - review_count
        progress = round(memorized / dict_length * 100)
        text = t(
            "stats.progress",
            progress=progress,
            touched=stats["touched"],
            total=dict_length,
            memorized=memorized,
            to_review=review_count,
        )
        if len(stats["mistakes_30days"]) > 0:
            text += "\n" + t("stats.mistakes") + wordlist("mistakes_30days")
        await message.answer(text)

    @staticmethod
    def quiz_kb() -> ReplyKeyboardMarkup:
        labels = ("der", "die", "das", "?")
        buttons = [(KeyboardButton(text=text) for text in labels)]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        return keyboard


if __name__ == "__main__":
    pass
