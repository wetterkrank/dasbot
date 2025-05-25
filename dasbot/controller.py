import logging

from aiogram import Bot
from aiogram.types import Message

from dasbot.db.chats_repo import ChatsRepo
from dasbot.db.stats_repo import StatsRepo
from dasbot.models.dictionary import Dictionary
from dasbot.models.quiz import Quiz
from dasbot.interface import Interface
from dasbot.analytics import tracker

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(
        self,
        bot: Bot,
        chats_repo: ChatsRepo,
        stats_repo: StatsRepo,
        dictionary: Dictionary,
    ):
        self.bot = bot
        self.chats_repo = chats_repo
        self.stats_repo = stats_repo
        self.ui = Interface(bot)
        self.dictionary = dictionary

    # /help
    async def help(self, message: Message):
        await self.ui.help(message)

    # /start
    async def start(self, message: Message):
        chat = self.chats_repo.load_chat(message)
        tracker.capture(
            chat.id,
            "quiz started",
            {"locale": chat.user["last_used_locale"]},
        )
        if not chat.last_seen:
            await self.ui.welcome(chat)
        scores = self.chats_repo.load_scores(chat.id)
        chat.quiz = Quiz.new(chat.quiz_length, scores, self.dictionary, chat.quiz_mode)
        if chat.quiz.has_questions:
            await self.ui.ask_question(chat, self.dictionary)
        else:
            await self.ui.quiz_empty(message)
        self.chats_repo.save_chat(chat, update_last_seen=True)

    # /stats
    async def stats(self, message: Message):
        scores = self.chats_repo.load_scores(message.chat.id)
        review_count = len(Quiz.get_review(scores, len(scores), self.dictionary))
        stats = self.stats_repo.get_stats(message.chat.id)
        dict_length = self.dictionary.wordcount()
        stats["touched"] = min(stats.get("touched"), dict_length)
        await self.ui.send_stats(message, stats, review_count, dict_length)

    # not-a-command
    async def generic(self, message: Message):
        if not message.text:
            return

        answer = message.text.strip().lower()
        chat = self.chats_repo.load_chat(message)
        quiz = chat.quiz

        if quiz and answer in self.ui.hint_commands():
            return await self.ui.give_hint(quiz, message, answer, self.dictionary)
        if not (quiz and quiz.expected(answer)):
            return await self.ui.help(message)

        result = chat.quiz.verify_and_update_score(answer)
        await self.ui.give_feedback(chat, message, result)
        self.chats_repo.save_score(chat, quiz.question, quiz.score)
        self.stats_repo.save_stats(chat, quiz.question, result)
        quiz.advance()
        if quiz.has_questions:
            await self.ui.ask_question(chat, self.dictionary)
        else:
            await self.ui.announce_result(chat)
            quiz.stop()
            tracker.capture(
                chat.id,
                "quiz completed",
                {
                    "locale": chat.user["last_used_locale"],
                },
            )

        self.chats_repo.save_chat(chat, update_last_seen=True)


if __name__ == "__main__":
    pass
