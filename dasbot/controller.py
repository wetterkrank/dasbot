import logging

from aiogram import types

from dasbot.models.quiz import Quiz
from .interface import Interface

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, bot, chats_repo):
        self.bot = bot
        self.chats_repo = chats_repo
        self.ui = Interface(bot)

    # /help
    async def help(self, message: types.Message):
        await self.ui.reply_with_help(message)

    # /start
    async def start(self, message: types.Message):
        chat = self.chats_repo.load_chat(message.chat)
        if not chat.last_seen:
            await self.ui.welcome(chat)
        scores = self.chats_repo.load_scores(chat.id)
        chat.quiz = Quiz.new(chat.quiz_length, scores)
        await self.ui.ask_question(chat)
        chat.stamp_time()
        self.chats_repo.save_chat(chat)

    # /stats
    async def stats(self, message: types.Message, dictionary):
        stats = self.chats_repo.get_stats(message.chat.id)
        await self.ui.send_stats(message, stats, dictionary.wordcount())

    # not-a-command
    async def generic(self, message: types.Message):
        chat = self.chats_repo.load_chat(message.chat)
        answer = message.text.strip().lower()
        if not (chat.quiz and chat.quiz.active and chat.quiz.valid(answer)):
            return await self.ui.reply_with_help(message)
        result = chat.quiz.verify_and_update_score(answer)
        await self.ui.give_feedback(chat, message, result)
        self.chats_repo.save_score(chat, chat.quiz.question, chat.quiz.score)
        self.chats_repo.save_stats(chat, chat.quiz.question, result)
        chat.quiz.advance()
        if chat.quiz.has_questions:
            await self.ui.ask_question(chat)
        else:
            await self.ui.announce_result(chat)
            chat.quiz.stop()
        chat.stamp_time()
        self.chats_repo.save_chat(chat)


if __name__ == "__main__":
    pass
