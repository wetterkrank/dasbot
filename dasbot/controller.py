import logging

import asyncio

from aiogram import Bot
from aiogram.types import Message

from dasbot.types import Dictionaries
from dasbot.db.chats_repo import ChatsRepo
from dasbot.db.stats_repo import StatsRepo
from dasbot.models.quiz import Quiz
from dasbot.interface import Interface
from dasbot.analytics import tracker
from dasbot.ads import ads

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(
        self,
        bot: Bot,
        chats_repo: ChatsRepo,
        stats_repo: StatsRepo,
        dictionaries: Dictionaries,
    ):
        self.bot = bot
        self.chats_repo = chats_repo
        self.stats_repo = stats_repo
        self.ui = Interface(bot)
        self.dictionaries = dictionaries

    # /help
    async def help(self, message: Message):
        await self.ui.help(message)

    # /start
    async def start(self, message: Message):
        chat = self.chats_repo.load_chat(message)
        if not chat.last_seen:
            await self.ui.welcome(chat)
        scores = self.chats_repo.load_scores(chat.id)
        dictionary = self.dictionaries[chat.dictionary_level]
        chat.quiz = Quiz.new(chat.quiz_length, scores, dictionary, chat.quiz_mode)
        self.chats_repo.save_chat(chat, update_last_seen=True)
        if chat.quiz.has_questions:
            await self.ui.ask_question(chat, dictionary)
        else:
            await self.ui.quiz_empty(message)

    # /stats
    # TODO: fix "touched" percentage calculation -- should depend on selected dictionary?
    async def stats(self, message: Message):
        chat = self.chats_repo.load_chat(message)
        scores = self.chats_repo.load_scores(chat.id)
        dictionary = self.dictionaries[chat.dictionary_level]
        review_count = len(Quiz.get_review(scores, len(scores), dictionary))
        stats = self.stats_repo.get_stats(chat.id)
        dict_length = dictionary.wordcount()
        stats["touched"] = min(stats.get("touched"), dict_length)
        await self.ui.send_stats(message, stats, review_count, dict_length)

    # not-a-command (answer or hint request)
    async def generic(self, message: Message):
        if not message.text:
            return

        answer = message.text.strip().lower()
        chat = self.chats_repo.load_chat(message)
        dictionary = self.dictionaries[chat.dictionary_level]
        quiz = chat.quiz

        if quiz and quiz.active and answer in self.ui.hint_commands():
            return await self.ui.give_hint(quiz, message, answer, dictionary)
        if not (quiz and quiz.expected(answer)):
            return await self.ui.help(message)

        result = chat.quiz.verify_and_update_score(answer)
        await self.ui.give_feedback(chat, message, result)
        self.chats_repo.save_score(chat, quiz.question, quiz.score)
        self.stats_repo.save_stats(chat, quiz.question, result)
        quiz.advance()
        if quiz.has_questions:
            await self.ui.ask_question(chat, dictionary)
        else:
            await self.ui.announce_result(chat)
            quiz.stop()
            tracker.capture(
                "quiz completed",
                distinct_id=str(chat.id),
                properties={"locale": chat.user["last_used_locale"]},
            )
            # Alternatively, we could send the ad hook inline with a short timeout
            # Can't use await since a timeout would block saving the chat
            asyncio.create_task(ads.send(chat.id, chat.user["last_used_locale"]))

        self.chats_repo.save_chat(chat, update_last_seen=True)


if __name__ == "__main__":
    pass
