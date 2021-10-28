# The migration will reset all quizzes and save them in the new format, with empty history.
# Was:
#   position = fields.Integer()
#   question = fields.String()
#   answer = fields.String()
#   correctly = fields.Integer()
# Now:
#   length = fields.Integer()
#   position = fields.Integer()
#   correctly = fields.Integer()
#   active = fields.Boolean()
#   cards = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))
#   scores = fields.Dict(keys=fields.Str(), values=fields.Tuple((fields.Integer(), fields.Raw())))

import logging

import pymongo
from dynaconf import settings

import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from dasbot.models.chat import ChatSchema
from dasbot.models.quiz import Quiz

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


def get_all_chats(chats_col):
    query = {}
    try:
        results_from_db = chats_col.find(query, {"_id": 0})
        chats = [ChatSchema().load(chat_data) for chat_data in results_from_db]
        return chats
    except pymongo.errors.PyMongoError as e:
        log.debug(e)
        return False


def save_chat(chat):
    query = {"chat_id": chat.id}
    data = ChatSchema().dump(chat)
    update = {"$set": data}
    try:
        result = chats_col.update_one(query, update, upsert=False)
        return result.matched_count > 0
    except pymongo.errors.PyMongoError as e:
        log.debug(e)
        return False


if __name__ == '__main__':
    # settings.QUIZ_LEN = 10

    client = pymongo.MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    chats_col = db['chats']

    chats = get_all_chats(chats_col)

    for chat in chats:
        chat.quiz = Quiz.new(history={})
        chat.quiz.active = False
        updated = save_chat(chat)
        print(chat.id, end=': ')
        print('ok') if updated else print('not ok')
