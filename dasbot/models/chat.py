import logging
from datetime import datetime, timezone

from marshmallow import Schema, fields, EXCLUDE, post_load

from .quiz import Quiz, QuizSchema
from dasbot import util

log = logging.getLogger(__name__)


class Chat(object):
    def __init__(self, chat_id, subscribed=True, last_seen=None, quiz=Quiz(),
                 quiz_scheduled_time=None, now=None):
        self.id = chat_id
        self.subscribed = subscribed
        self.last_seen = last_seen
        self.quiz = quiz
        self.quiz_scheduled_time = quiz_scheduled_time
        if self.quiz_scheduled_time is None:
            self.set_quiz_time("12:00", now)  # Default: nearest noon

    def stamp_time(self):
        self.last_seen = datetime.now(tz=timezone.utc)

    def unsubscribe(self):
        self.subscribed = False

    def set_quiz_time(self, hhmm, now=None):
        now = now or datetime.now().astimezone()  # Setting quiz time in server's TZ
        self.quiz_scheduled_time = util.next_hhmm(hhmm, now)


class ChatSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization

    chat_id = fields.Integer()
    subscribed = fields.Boolean(missing=True)
    last_seen = fields.Raw(missing=None)  # Keep the raw datetime for Mongo
    quiz = fields.Nested(QuizSchema)
    quiz_scheduled_time = fields.Raw(missing=None)  # Keep the raw datetime for Mongo

    @post_load
    def get_chat(self, data, **kwargs):
        return Chat(**data)


if __name__ == "__main__":
    pass
