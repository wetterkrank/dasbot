import logging
from datetime import datetime
from datetime import timezone

from aiogram.types import Message

from dasbot.models.chat import Chat, ChatSchema

log = logging.getLogger(__name__)


class ChatsRepo(object):

    def __init__(self, chats_col, scores_col):
        self._chats = chats_col
        self._scores = scores_col
        self.__status()

    def __status(self):
        log.info("%s chat(s) in DB" % self._chats.count_documents({}))
        log.info("%s scores(s) in DB" % self._scores.count_documents({}))

    # NOTE: Could make this more explicit by separating load_chat and create_chat methods
    def load_chat(self, message: Message):
        """
        :param message: Telegram message
        :return: Chat instance, loaded from DB, or new if not found
        """
        tg_chat = message.chat  # NOTE: Chat may be a group etc and have many users
        locale = message.from_user.language_code if message.from_user else None
        chat_data = self._chats.find_one({"chat_id": tg_chat.id}, {"_id": 0})
        log.debug("requested chat %s, result: %s", tg_chat.id, chat_data)
        if chat_data:
            chat: Chat = ChatSchema().load(chat_data)
            chat.user['last_used_locale'] = locale # locale may change over time and depend on device
        else:
            user = {
                'username': tg_chat.username,
                'first_name': tg_chat.first_name,
                'last_name': tg_chat.last_name,
                'locale': locale,
                'last_used_locale': locale,
            }
            chat = Chat(tg_chat.id, user)
        return chat

    def save_chat(self, chat: Chat, update_last_seen=False):
        """ Returns pymongo UpdateResult instance """
        if update_last_seen:
            chat.stamp_time()
        query = {"chat_id": chat.id}
        data = ChatSchema().dump(chat)
        update = {"$set": data}
        result = self._chats.update_one(query, update, upsert=True)
        log.debug("saved chat %s, result: %s", chat.id, result.raw_result)
        return result

    # TODO: return ids instead of full objects, or do it in batches
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
    def load_scores(self, chat_id):
        """
        :param chat_id: chat id
        :return: dict of scores {word: (score, due_date)}
        """
        query = {"chat_id": chat_id}
        results_cursor = self._scores.find(query, {"_id": 0})
        scores = {
            item["word"]: (item["score"], item["revisit"])
            for item in results_cursor
        }
        log.debug("loaded all scores for chat %s, count: %s", chat_id,
                  len(scores))
        return scores

    # TODO: check if saved successfully?
    def save_score(self, chat: Chat, word, score):
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

if __name__ == "__main__":
    pass
