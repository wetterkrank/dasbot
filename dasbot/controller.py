import logging

from aiogram import types

from dasbot.models.quiz import Quiz
from .interface import Interface

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, bot, chats_repo, stats_repo, dictionary):
        self.bot = bot
        self.chats_repo = chats_repo
        self.stats_repo = stats_repo
        self.ui = Interface(bot)
        self.dictionary = dictionary

    # /help
    async def help(self, message: types.Message):
        await self.ui.reply_with_help(message)

    # /start
    async def start(self, message: types.Message):
        chat = self.chats_repo.load_chat(message.chat)
        if not chat.last_seen:
            await self.ui.welcome(chat)
        scores = self.chats_repo.load_scores(chat.id)
        chat.quiz = Quiz.new(chat.quiz_length, scores, self.dictionary)
        if chat.quiz.has_questions:
            await self.ui.ask_question(chat)
        else:
            await self.ui.quiz_empty(message)
        self.chats_repo.save_chat(chat, update_last_seen=True)

    # /stats
    async def stats(self, message: types.Message, dictionary):
        stats = self.stats_repo.get_stats(message.chat.id)
        await self.ui.send_stats(message, stats, dictionary.wordcount())

    # not-a-command
    async def generic(self, message: types.Message):
        answer = message.text.strip().lower()
        chat = self.chats_repo.load_chat(message.chat)
        quiz = chat.quiz

        if not (quiz and quiz.expected(answer)):
            return await self.ui.reply_with_help(message)
        if answer == '?': return await self.ui.give_hint(quiz, message, self.dictionary)

        result = chat.quiz.verify_and_update_score(answer)
        await self.ui.give_feedback(chat, message, result)
        self.chats_repo.save_score(chat, quiz.question, quiz.score)
        self.stats_repo.save_stats(chat, quiz.question, result)
        quiz.advance()
        if quiz.has_questions:
            await self.ui.ask_question(chat)
        else:
            await self.ui.announce_result(chat)
            quiz.stop()
        self.chats_repo.save_chat(chat, update_last_seen=True)


if __name__ == "__main__":
    pass
