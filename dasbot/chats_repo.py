import logging
from datetime import datetime
from datetime import timezone

from dasbot.models.chat import Chat, ChatSchema
from dasbot import util

from pymongo.errors import DuplicateKeyError, OperationFailure

log = logging.getLogger(__name__)


class ChatsRepo(object):
    def __init__(self, chats_col, scores_col, stats_col):
        self._chats = chats_col
        self._scores = scores_col
        self._stats = stats_col
        self.__status()

    def __status(self):
        log.info("%s chat(s) in DB" % self._chats.count_documents({}))

    def load_chat(self, chat_id):
        """
        :param chat_id: Telegram chat id
        :return: Chat instance, loaded from DB, or new if not found
        """
        chat_data = self._chats.find_one({"chat_id": chat_id}, {"_id": 0})
        log.debug("requested chat %s, result: %s", chat_id, chat_data)
        if chat_data:
            chat = ChatSchema().load(chat_data)
        else:
            chat = Chat(chat_id)
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
        results_cursor = self._chats.find(query, {"_id": 0})
        chats = [ChatSchema().load(chat_data) for chat_data in results_cursor]
        return chats

    # TODO: make Score a separate model?
    def load_scores(self, chat):
        """
        :param chat: chat instance
        :return: dict of scores {word: (score, due_date)}
        """
        query = {"chat_id": chat.id}
        results_cursor = self._scores.find(query, {"_id": 0})
        scores = {item["word"]: (item["score"], item["revisit"])
                  for item in results_cursor}
        # log.debug("loaded scores for chat %s, result: %s", chat.id, scores)
        return scores

    # TODO: check if saved successfully?
    def save_score(self, chat, word, score):
        """
        :param chat: chat instance
        :param word: word to save the score for
        :param score: a tuple (score, due_date)
        :return: pymongo UpdateResult instance
        """
        query = {"chat_id": chat.id, "word": word}
        update = {"$set": {"score": score[0], "revisit": score[1]}}
        result = self._scores.update_one(query, update, upsert=True)
        # log.debug("saved score for chat %s, result: %s", chat.id, result.raw_result)
        return result

    def save_stats(self, chat, word, result: bool):
        """
        :param chat: chat instance
        :param word: word to save the result for
        :param result: last answer correct?
        """
        update = {"chat_id": chat.id, "word": word,
                  "correct": result, "date": datetime.now(tz=timezone.utc)}
        result = self._stats.insert_one(update)
        return result

    # TODO: generate the stats periodically in the background and save them in a separate collection
    # NOTE: we could use $facet in the aggregation as an alternative (no indexes though)
    def get_stats(self, chat_id, month_ago=None):
        """
        :param chat_id: chat id
        :param month_ago: time when the function is called, minus 30 days
        :return: dictionary
        """
        stats = {}
        if month_ago is None:
            month_ago = util.month_ago()
        pipe_30days = [
            {
                '$match': {
                    'chat_id': chat_id,
                    'correct': False,
                    'date': {
                        '$gt': month_ago
                    }
                }
            },
            {'$group': { '_id': '$word', 'count': { '$sum': 1 } }},
            {'$sort': { 'count': -1 }},
            {'$limit': 5},
            {'$project': {'word': '$_id', 'count': 1, '_id': 0}}
        ]
        pipe_alltime = [
            {
                '$match': {
                    'chat_id': chat_id,
                    'correct': False
                }
            },
            {'$group': { '_id': '$word', 'count': { '$sum': 1 } }},
            {'$sort': { 'count': -1 }},
            {'$limit': 10},
            {'$project': {'word': '$_id', 'count': 1, '_id': 0}}
        ]
        query_progress = {'chat_id': chat_id, 'score': {'$gt': 0}}
        count = self._scores.count_documents(query_progress)
        stats['touched'] = count
        results = self._stats.aggregate(pipe_30days)
        stats['mistakes_30days'] = [item for item in results]
        results = self._stats.aggregate(pipe_alltime)
        stats['mistakes_alltime'] = [item for item in results]
        return stats


if __name__ == "__main__":
    pass
