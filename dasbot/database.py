# TODO: Add username & password

import logging
from pymongo import MongoClient

from .chat import Chat, ChatSchema

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Database(object):
    def __init__(self, db_conn, db_name):
        client = MongoClient(db_conn)  # DB connection details
        db = client[db_name]  # Database name here
        self._chats = db['chats']  # Collection name here
        self.__status()

    def __status(self):
        log.info("%s chat(s) in DB" % self._chats.count_documents({}))

    def load_chat(self, chat_id):
        ''' Returns a Chat instance '''
        chat_data = self._chats.find_one({"chat_id": chat_id}, {"_id": 0})
        log.debug("loaded chat %s, result: %s", chat_id, chat_data)
        chat = ChatSchema().load(chat_data) if chat_data else Chat(chat_id)
        return chat

    def save_chat(self, chat):
        ''' Returns pymongo UpdateResult instance '''
        chat.seen_now()
        query = {"chat_id": chat.id}
        data = ChatSchema().dump(chat)
        update = {"$set": data}
        result = self._chats.update_one(query, update, upsert=True)
        log.debug("saved chat %s, result: %s", chat.id, result.raw_result)
        return result

    def get_subscriptions(self):
        ''' Returns the list of chat_ids '''
        found = self._chats.find({"subscribed": True}, {"chat_id": 1, "_id": 0})
        subscriptions = [item['chat_id'] for item in found]
        return subscriptions


if __name__ == "__main__":
    pass
