import logging

import asyncio
from aiogram.utils.exceptions import BotBlocked

from dasbot import util
from dasbot.models.quiz import Quiz

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Scheduler(object):
    def __init__(self, ui, chats_repo):
        self.ui = ui
        self.chats_repo = chats_repo

    async def send_quiz(self, chat):
        """
        :param chat: chat with a pending quiz
        :return: `true` if quiz is successfully sent, `false` otherwise
        """
        try:
            await self.ui.daily_hello(chat)
            chat.quiz = Quiz()  # Resets the quiz
            chat.quiz.next_question_ready()
            chat.quiz_scheduled_time = util.next_quiz_time(chat.quiz_scheduled_time)
            await self.ui.ask_question(chat)
            self.chats_repo.save_chat(chat)
            await asyncio.sleep(.5)  # FYI, TG limit: 30 messages/second
            return True
        except BotBlocked:
            log.info("Bot blocked, chat id: %s", chat.id)
            chat.unsubscribe()
            self.chats_repo.save_chat(chat)
            return False

    # Regularly called rouine that sends out the (over)due quizzes
    async def broadcast(self):
        pending_chats = self.chats_repo.get_pending_chats()
        log.debug("Broadcast: %s pending", len(pending_chats))
        sent = 0
        for chat in pending_chats:
            result = await self.send_quiz(chat)
            if result:
                sent += 1
        log.debug("Broadcast: %s sent.", sent)

    # Sets the schedule and runs the scheduler loop
    async def run(self):
        log.info("Broadcaster started")
        while True:
            await asyncio.sleep(60)
            await self.broadcast()
