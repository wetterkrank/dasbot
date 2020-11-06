import logging
from datetime import datetime
from datetime import timezone

from dasbot import util
from dasbot.models.chat import Chat, ChatSchema

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ChatsRepo(object):
    def __init__(self, chats_table):
        self._chats = chats_table
        self.__status()

    def __status(self):
        log.info("%s chat(s) in DB" % self._chats.count_documents({}))

    def load_chat(self, chat_id, now=None):
        """
        :param chat_id: Telegram chat id
        :param now: timestamp when the function is called
        :return: Chat instance, loaded from DB, or new if not found
        """
        if now is None:
            now = datetime.now(tz=timezone.utc)
        chat_data = self._chats.find_one({"chat_id": chat_id}, {"_id": 0})
        log.debug("requested chat %s, result: %s", chat_id, chat_data)
        if chat_data:
            chat = ChatSchema().load(chat_data)
        else:
            chat = Chat(chat_id, quiz_scheduled_time=util.next_noon(now))
        return chat

    def save_chat(self, chat):
        """ Returns pymongo UpdateResult instance """
        query = {"chat_id": chat.id}
        data = ChatSchema().dump(chat)
        update = {"$set": data}
        result = self._chats.update_one(query, update, upsert=True)
        log.debug("saved chat %s, result: %s", chat.id, result.raw_result)
        return result

    def get_pending_chats(self, now=None):
        """
        :param now: timestamp when the function is called
        :return: list of chats that have pending quizzes
        """
        if now is None:
            now = datetime.now(tz=timezone.utc)
        query = {"subscribed": True, "quiz_scheduled_time": {"$lte": now}}
        log.debug('DB query: %s', query)
        results_from_db = self._chats.find(query, {"_id": 0})
        chats = [ChatSchema().load(chat_data) for chat_data in results_from_db]
        return chats


if __name__ == "__main__":
    pass
