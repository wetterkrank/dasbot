import logging

from .chat import Chat
from .quiz import Quiz
from .interface import Interface

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        self.ui = Interface(bot)

    # if /help received
    async def help(self, message):
        await self.ui.reply_with_help(message)

    # if /start received
    async def start(self, message):
        chat = self.db.load_chat(message.chat.id)
        if not chat.last_seen:
            await self.ui.welcome(chat)
        chat.quiz = Quiz()  # Resets the quiz
        chat.quiz.next_question_ready()
        await self.ui.ask_question(chat)
        self.db.save_chat(chat)

    # if smth else received
    async def generic(self, message):
        chat = self.db.load_chat(message.chat.id)
        answer = message.text.strip().lower()
        if not (chat.quiz.active and self.ui.recognized(answer)):
            return await self.ui.reply_with_help(message)
        result = chat.quiz.prove(answer)
        await self.ui.give_feedback(chat, message, result)
        if chat.quiz.next_question_ready():
            await self.ui.ask_question(chat)
        else:
            await self.ui.say_score(chat)
        self.db.save_chat(chat)


if __name__ == "__main__":
    pass
