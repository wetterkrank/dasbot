import logging

from datetime import datetime
from pytz import timezone

from marshmallow import Schema, fields, EXCLUDE, post_load
from dynaconf import Dynaconf

from .quiz import QuizSchema
from dasbot import util

# TODO: receive settings from __main__? we'll have to pass them through several levels
settings = Dynaconf(
    environments=['default', 'production', 'development'],
    settings_file='settings.toml',
    load_dotenv=True
)

log = logging.getLogger(__name__)


class Chat(object):
    def __init__(self, chat_id, user=None, subscribed=True, last_seen=None, quiz=None,
                 quiz_scheduled_time=None, quiz_length=None, now=None):
        self.id = chat_id
        self.user = user
        self.subscribed = subscribed
        self.last_seen = last_seen
        self.quiz = quiz
        self.quiz_scheduled_time = quiz_scheduled_time
        self.quiz_length = quiz_length or settings.QUIZ_LENGTH
        if self.quiz_scheduled_time is None:
            random_hhmm = util.random_time(9, 20)
            self.set_quiz_time(random_hhmm, now)  # Default: random btw 09:00 and 20:59

    def stamp_time(self):
        self.last_seen = datetime.now(tz=timezone('UTC'))

    def unsubscribe(self):
        self.subscribed = False

    def subscribe(self):
        self.subscribed = True

    def set_quiz_time(self, hhmm, now=None):
        """
        :param hhmm: string "HH:MM"
        :param now: datetime, if None then current datetime in Berlin TZ will be used
        :return: nothing, changes the Chat instance
        """
        berlin = timezone('Europe/Berlin')
        now = now or datetime.now().astimezone(berlin)
        self.quiz_scheduled_time = util.next_hhmm(hhmm, now)

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization
    username = fields.String(missing=None)
    first_name = fields.String(missing=None)
    last_name = fields.String(missing=None)

class ChatSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization
    chat_id = fields.Integer()
    user = fields.Nested(UserSchema, missing=None)
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
