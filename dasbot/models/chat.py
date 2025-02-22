import logging

from datetime import datetime
from pytz import timezone

from marshmallow import Schema, fields, EXCLUDE, post_load

from dasbot import util
from dasbot.models.quiz import QuizMode, QuizSchema
from dasbot.config import settings

log = logging.getLogger(__name__)


class Chat(object):
    def __init__(self, chat_id, user={}, subscribed=True, last_seen=None, quiz=None,
                 quiz_scheduled_time=None, quiz_length=None, quiz_mode=None):
        self.id = chat_id
        self.user = user # our User is just a dictionary so far
        self.subscribed = subscribed
        self.last_seen = last_seen
        self.quiz = quiz
        self.quiz_scheduled_time = quiz_scheduled_time
        self.quiz_length = quiz_length or settings.QUIZ_LENGTH
        self.quiz_mode = quiz_mode or QuizMode.Advance
        if self.quiz_scheduled_time is None:
            self.quiz_scheduled_time = util.next_quiz_time(datetime.now(tz=timezone('UTC')))

    def stamp_time(self):
        self.last_seen = datetime.now(tz=timezone('UTC'))

    def unsubscribe(self):
        self.subscribed = False

    def subscribe(self):
        self.subscribed = True

    def set_quiz_time(self, hhmm, skip_today=False):
        """
        :param hhmm: string "HH:MM"
        :param skip_today: skip nearest HH:MM if today
        :return: nothing, changes the Chat instance
        """
        berlin = timezone('Europe/Berlin')
        now = datetime.now().astimezone(berlin)
        self.quiz_scheduled_time = util.next_hhmm(hhmm, now, skip_today=skip_today)

# TODO: Add Account object instead of current User dictionary
class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization
    username = fields.String(missing=None)
    first_name = fields.String(missing=None)
    last_name = fields.String(missing=None)
    locale = fields.String(missing=None)
    last_used_locale = fields.String(missing=None)

class ChatSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skip unknown fields on deserialization
    chat_id = fields.Integer()
    user = fields.Nested(UserSchema, missing={})
    subscribed = fields.Boolean(missing=True)
    last_seen = fields.Raw(missing=None)  # Keep the raw datetime for Mongo
    quiz = fields.Nested(QuizSchema, missing=None)
    quiz_scheduled_time = fields.Raw(missing=None)  # Keep the raw datetime for Mongo
    quiz_length = fields.Integer(missing=None)
    quiz_mode = fields.Enum(QuizMode, by_value=True, missing=None)

    @post_load
    def get_chat(self, data, **kwargs):
        return Chat(**data)


if __name__ == "__main__":
    pass
