import logging
from datetime import datetime
from datetime import timezone

from dasbot.models.chat import Chat, ChatSchema

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ChatsRepo(object):
    def __init__(self, chats_col, scores_col):
        self._chats = chats_col
        self._scores = scores_col
        self.__status()

    def __status(self):
        log.info("%s chat(s) in DB" % self._chats.count_documents({}))

    def load_chat(self, chat_id):
        """
        :param chat_id: Telegram chat id
        :param now: datetime when the function is called
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
        results_from_db = self._chats.find(query, {"_id": 0})
        chats = [ChatSchema().load(chat_data) for chat_data in results_from_db]
        return chats

    # TODO: make Score into a separate model?
    def load_scores(self, chat):
        """
        :param chat: chat instance
        :return: dict of scores {word: (score, due_date)}
        """
        query = {"chat_id": chat.id}
        results_from_db = self._scores.find(query, {"_id": 0})
        scores = {item["word"]: (item["score"], item["revisit"]) for item in results_from_db}
        log.debug("loaded scores for chat %s, result: %s", chat.id, scores)
        return scores

    def save_score(self, chat, word, score):
        """
        :param chat: chat instance
        :param word: word to save the score for
        :param score: a tuple (score, due_date)
        :return: pymongo UpdateResult instance
        """
        query = {"chat_id": chat.id, "word": word}
        update = {"$set": {"chat_id": chat.id, "word": word, "score": score[0], "revisit": score[1]}}
        result = self._scores.update_one(query, update, upsert=True)
        log.debug("saved score for chat %s, result: %s", chat.id, result.raw_result)
        return result


if __name__ == "__main__":
    pass
