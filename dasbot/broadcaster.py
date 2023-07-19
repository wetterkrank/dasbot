import logging

import asyncio
from aiogram.utils.exceptions import Unauthorized, TelegramAPIError

from dasbot import util
from dasbot.models.quiz import Quiz
from dasbot.models.chat import Chat

log = logging.getLogger(__name__)


class Broadcaster(object):
    def __init__(self, ui, chats_repo, dictionary):
        self.ui = ui
        self.chats_repo = chats_repo
        self.dictionary = dictionary

    async def send_quiz(self, chat: Chat) -> bool:
        """
        :param chat: chat with a pending quiz
        :return: `True` if quiz is successfully sent, `False` otherwise
        """
        try:
            scores = self.chats_repo.load_scores(chat.id)
            chat.quiz = Quiz.new(chat.quiz_length, scores, self.dictionary)
            chat.quiz_scheduled_time = util.next_quiz_time(chat.quiz_scheduled_time)
            self.chats_repo.save_chat(chat)
            if chat.quiz.has_questions:
                log.debug("Broadcast: sending message to %s", chat.id)
                await self.ui.daily_hello(chat)
                await self.ui.ask_question(chat)
                self.chats_repo.save_chat(chat)
                await asyncio.sleep(1)  # FYI, TG limit: 30 messages/second
                return True
            else:
                return False
        # Kicked, blocked etc:
        except Unauthorized as err:
            log.error("Error: %s, chat id: %s", err, chat.id)
            chat.unsubscribe()
            self.chats_repo.save_chat(chat)
            return False
        # API and network errors:
        except TelegramAPIError as err:
            log.error("Error: %s, chat id: %s", err, chat.id)
            return False
        except (TimeoutError, asyncio.TimeoutError) as err:
            log.error("Error: %s", err)
            await asyncio.sleep(30)
            return False

    # Regularly called rouine that sends out the (over)due quizzes
    async def broadcast(self):
        pending_chats = self.chats_repo.get_pending_chats()
        # Consider adding +1 day to overdue chats if bot is started
        # after a downtime, so they get their quizzes on preferred time
        log.debug("Broadcast: %s pending", len(pending_chats))
        sent = 0
        for chat in pending_chats:
            result = await self.send_quiz(chat)
            if result:
                sent += 1
        log.debug("Broadcast: %s sent.", sent)

    # Runs the broadcast loop
    async def run(self):
        log.info("Broadcaster started")
        while True:
            await asyncio.sleep(60)
            await self.broadcast()
