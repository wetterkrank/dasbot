import logging

from dasbot.models.quiz import Quiz
from .interface import Interface

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Controller(object):
    def __init__(self, bot, chats_repo):
        self.bot = bot
        self.chats_repo = chats_repo
        self.ui = Interface(bot)

    # /help
    async def help(self, message):
        await self.ui.reply_with_help(message)

    # /start
    async def start(self, message):
        chat = self.chats_repo.load_chat(message.chat.id)
        if not chat.last_seen:
            await self.ui.welcome(chat)
        chat.quiz = Quiz.new()  # Resets the quiz
        await self.ui.ask_question(chat)
        chat.stamp_time()
        self.chats_repo.save_chat(chat)

    # not-a-command
    async def generic(self, message):
        chat = self.chats_repo.load_chat(message.chat.id)
        answer = message.text.strip().lower()
        if not (chat.quiz.active and self.ui.recognized(answer)):
            return await self.ui.reply_with_help(message)
        result = chat.quiz.verify(answer)
        await self.ui.give_feedback(chat, message, result)
        chat.quiz.advance()
        if chat.quiz.has_questions:
            await self.ui.ask_question(chat)
        else:
            await self.ui.say_score(chat)
            chat.quiz.stop()
        chat.stamp_time()
        self.chats_repo.save_chat(chat)

    # /settings
    async def settings(self, message):
        await self.ui.settings_root(message)

    # /settings UNSUBSCRIBE
    async def settings_unsubscribe(self, query):
        await query.answer()  # To confirm reception
        chat = self.chats_repo.load_chat(query.message.chat.id)
        chat.unsubscribe()
        chat.stamp_time()
        self.chats_repo.save_chat(chat)
        await self.ui.settings_quiztime_set(query, "UNSUBSCRIBE")

    # /settings HH:MM
    async def settings_timepref(self, query):
        await query.answer()
        chat = self.chats_repo.load_chat(query.message.chat.id)
        preferred_time = query.data
        chat.set_quiz_time(preferred_time)
        chat.stamp_time()
        self.chats_repo.save_chat(chat)
        await self.ui.settings_quiztime_set(query, preferred_time)


if __name__ == "__main__":
    pass
