import logging

from datetime import datetime
from pytz import timezone

from marshmallow import Schema, fields, EXCLUDE, post_load
from dynaconf import settings

from .quiz import QuizSchema
from dasbot import util

log = logging.getLogger(__name__)


class Chat(object):
    def __init__(self, chat_id, subscribed=True, last_seen=None, quiz=None,
                 quiz_scheduled_time=None, quiz_length=None, now=None):
        self.id = chat_id
        self.subscribed = subscribed
        self.last_seen = last_seen
        self.quiz = quiz
        self.quiz_scheduled_time = quiz_scheduled_time
        self.quiz_length = quiz_length or settings.QUIZ_LEN
        if self.quiz_scheduled_time is None:
            self.set_quiz_time("12:00", now)  # Default: nearest noon

    def stamp_time(self):
        self.last_seen = datetime.now(tz=timezone('UTC'))

    def unsubscribe(self):
        self.subscribed = False

    def set_quiz_time(self, hhmm, now=None):
        """
        :param hhmm: string "HH:MM"
        :param now: datetime, if None then current datetime in Berlin TZ will be used
        :return: nothing, changes the Chat instance
        """
        berlin = timezone('Europe/Berlin')
        now = now or datetime.now().astimezone(berlin)
        self.quiz_scheduled_time = util.next_hhmm(hhmm, now)


class ChatSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization

    chat_id = fields.Integer()
    subscribed = fields.Boolean(missing=True)
    last_seen = fields.Raw(missing=None)  # Keep the raw datetime for Mongo
    quiz = fields.Nested(QuizSchema, missing=None)
    quiz_scheduled_time = fields.Raw(missing=None)  # Keep the raw datetime for Mongo
    quiz_length = fields.Integer(missing=None)

    @post_load
    def get_chat(self, data, **kwargs):
        return Chat(**data)


if __name__ == "__main__":
    pass
