import logging

from datetime import datetime
from datetime import timezone

from dasbot.models.chat import Chat
from dasbot import util

log = logging.getLogger(__name__)


class StatsRepo(object):
    def __init__(self, scores_col, stats_col):
        self._scores = scores_col
        self._stats = stats_col
        self.__status()

    def __status(self):
        log.info("%s answer(s) in DB" % self._stats.count_documents({}))

    def save_stats(self, chat: Chat, word, result: bool):
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
            {'$group': {'_id': '$word', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5},
            {'$lookup': {
                'from': 'dictionary',
                'localField': '_id',
                'foreignField': 'word',
                'as': 'dictionaryEntry'
            }},
            {'$project': {'articles': {'$first': '$dictionaryEntry.articles'}, 'word': '$_id', 'count': 1, '_id': 0}}
        ]
        pipe_alltime = [
            {
                '$match': {
                    'chat_id': chat_id,
                    'correct': False
                }
            },
            {'$group': {'_id': '$word', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10},
            {'$lookup': {
                'from': 'dictionary',
                'localField': '_id',
                'foreignField': 'word',
                'as': 'dictionaryEntry'
            }},
            {'$project': {'articles': {'$first': '$dictionaryEntry.articles'}, 'word': '$_id', 'count': 1, '_id': 0}}
        ]
        query_progress = {'chat_id': chat_id}
        count = self._scores.count_documents(query_progress)
        stats['touched'] = count
        results = self._stats.aggregate(pipe_30days)
        stats['mistakes_30days'] = [item for item in results]
        results = self._stats.aggregate(pipe_alltime)
        stats['mistakes_alltime'] = [item for item in results]
        return stats


if __name__ == "__main__":
    pass
