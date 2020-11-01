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

    def load_chat(self, chat_id, now=datetime.utcnow()):
        """ Returns a Chat instance """
        chat_data = self._chats.find_one({"chat_id": chat_id}, {"_id": 0})
        log.debug("loaded chat %s, result: %s", chat_id, chat_data)
        chat = ChatSchema().load(chat_data) if chat_data else Chat(chat_id, quiz_scheduled_time=util.next_noon(now))
        return chat

    def save_chat(self, chat):
        """ Returns pymongo UpdateResult instance """
        query = {"chat_id": chat.id}
        data = ChatSchema().dump(chat)
        update = {"$set": data}
        result = self._chats.update_one(query, update, upsert=True)
        log.debug("saved chat %s, result: %s", chat.id, result.raw_result)
        return result

    def get_pending_chats(self, time=datetime.now(tz=timezone.utc)):
        """
        :param time: timestamp when the function is called
        :return: list of chats that have pending quizzes
        """
        # TODO:
        #  Currently timestamps are serialized with marshmallow as strings.
        #  We should serialize them as timestamps, and query here:
        #  {"subscribed": True, "quiz_scheduled_time": {"$lte": time}}
        results_from_db = self._chats.find({"subscribed": True, "quiz_scheduled_time": {"$ne": None}}, {"_id": 0})
        chats = [ChatSchema().load(chat_data) for chat_data in results_from_db]
        return list(filter(lambda chat: chat.quiz_scheduled_time < time, chats))


if __name__ == "__main__":
    pass
