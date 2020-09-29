import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO: Add username & password
class Database(object):
    def __init__(self, db_conn, db_name):
        client = MongoClient(db_conn) # DB connection details
        db = client[db_name] # Database name here
        self._chats = db['chats'] # Collection name here
        self.__status()

    def __status(self):
        logger.info("%s chat(s) stored" % self._chats.count_documents({}))

    def get_chat(self, chat_id):
        chat_id = str(chat_id)
        chat_state = self._chats.find_one({"chat_id": chat_id})
        logger.debug("Mongo retrieving chat %s, result: %s", chat_id, chat_state)
        if chat_state:
            chat_state.pop('_id')
            return chat_state
        return None

    def save_chat(self, chat_id, chat_state):
        chat_id = str(chat_id)
        query = {"chat_id": chat_id}
        update = {"$set": chat_state}
        result = self._chats.update_one(query, update, upsert=True)
        logger.debug("Mongo updating chat %s, result: %s", chat_id, result.raw_result)
        return result
