import asyncio
import logging
import time
from datetime import datetime
from datetime import timedelta

import aioschedule
from aiogram.utils.exceptions import BotBlocked

from dasbot import util
from dasbot.models.quiz import Quiz

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TIMES_UTC = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]


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
            return False

    # Callback that sends out the quizzes to subscribed chats
    async def broadcast(self):
        pending_chats = self.chats_repo.get_pending_chats()

        success_count = 0
        for chat in pending_chats:
            result = await self.send_quiz(chat)
            if result:
                success_count += 1

        log.info("Broadcast: %s message(s) sent.", success_count)

    # Creates the schedule and runs it
    async def run(self):
        try:
            aioschedule.every(60).seconds.do(self.broadcast)
            for tpoint in TIMES_UTC:
                tpoint_servertz = Scheduler.utc_to_local(tpoint)
                aioschedule.every().day.at(tpoint_servertz).do(self.broadcast)
            log.debug("Scheduled jobs: %s", len(aioschedule.jobs))
        except RuntimeError as e:
            log.error(e)

        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(60)

    @staticmethod
    def utc_to_local(hhmm):
        """ Returns the HH:MM time converted from UTC to server's TZ """
        utc = datetime.strptime(f"{hhmm}UTC", "%H:%M%Z")
        now = time.time()
        offset = datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)
        local = utc + offset
        return datetime.strftime(local, "%H:%M")
