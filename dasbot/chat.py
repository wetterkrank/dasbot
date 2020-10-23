import logging
from datetime import datetime, timezone

from marshmallow import Schema, fields, EXCLUDE, post_load

from .quiz import Quiz, QuizSchema

log = logging.getLogger(__name__)


class Chat(object):
    def __init__(self, chat_id, subscribed=False, last_seen=None, quiz=Quiz()):
        self.id = chat_id
        self.subscribed = subscribed
        self.last_seen = last_seen
        self.quiz = quiz

    def seen_now(self):
        self.last_seen = datetime.now(timezone.utc)


class ChatSchema(Schema):
    class Meta:
        unknown = EXCLUDE   # Skip unknown fields on deserialization
    chat_id = fields.Integer()
    subscribed = fields.Boolean()
    last_seen = fields.DateTime()
    quiz = fields.Nested(QuizSchema)

    @post_load
    def get_chat(self, data, **kwargs):
        return Chat(**data)


if __name__ == "__main__":
    pass
