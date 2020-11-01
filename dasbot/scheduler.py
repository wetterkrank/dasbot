import logging
import asyncio
import aioschedule
from aiogram.utils.exceptions import BotBlocked
from datetime import datetime
import time

from .quiz import Quiz
from .interface import Interface

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TIMES_UTC = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]


class Scheduler(object):
    def __init__(self, bot, chats_repo):
        self.bot = bot
        self.chats_repo = chats_repo
        self.ui = Interface(bot)

    # Callback that sends out the quizes to subscribed chats
    async def broadcast(self, timepoint):
        subscriptions = self.chats_repo.get_subscriptions(timepoint)
        sent_count = 0
        try:
            for chat_id in subscriptions:
                chat = self.chats_repo.load_chat(chat_id)
                await self.ui.daily_hello(chat)
                chat.quiz = Quiz()  # Resets the quiz
                chat.quiz.next_question_ready()
                await self.ui.ask_question(chat)
                self.chats_repo.save_chat(chat)
                sent_count += 1
                await asyncio.sleep(.5)  # FYI, TG limit: 30 messages/second
        except BotBlocked:
            log.info("Bot blocked, chat id: %s", chat.id)
        finally:
            log.info("Broadcast: %s message(s) sent.", sent_count)

    # Creates the schedule and runs it
    async def run(self):
        try:
            aioschedule.every(60).seconds.do(self.broadcast, "12:00")
            for tpoint in TIMES_UTC:
                tpoint_servertz = Scheduler.utc_to_local(tpoint)
                aioschedule.every().day.at(tpoint_servertz).do(self.broadcast, tpoint)
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
