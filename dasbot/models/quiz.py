import logging
import random

from marshmallow import Schema, fields, EXCLUDE, post_load

from dynaconf import settings
from dasbot.dictionary import Dictionary

logger = logging.getLogger(__name__)

dictionary = Dictionary(settings.DICT_FILE)


class Quiz(object):
    def __init__(self, length=None, cards=[], position=0, correctly=0, active=False):
        self.length = length
        self.cards = cards
        self.position = position
        self.correctly = correctly
        self.active = active

    @classmethod
    def new(cls):
        length = settings.QUIZ_LEN
        cards = []
        items = random.sample(dictionary.contents.items(), length)
        for word, attrs in items:
            card = {'word': word, 'articles': attrs[0]}
            cards.append(card)
        position = 0
        correctly = 0
        active = True
        return cls(length=length, cards=cards, position=position, correctly=correctly, active=active)

    @property
    def pos(self):
        return self.position + 1

    @property
    def has_questions(self):
        return self.position + 1 < settings.QUIZ_LEN and self.position + 1 < len(self.cards)

    @property
    def question(self):
        return self.cards[self.position]['word']

    @property
    def answer(self):
        return self.cards[self.position]['articles']

    def verify(self, answer):
        # self.position += 1
        accepted_answers = self.answer.split("/")  # TODO: set in dictionary
        if answer in accepted_answers:
            self.correctly += 1
            return True
        return False

    def advance(self):
        self.position += 1

    def stop(self):
        self.active = False


class QuizSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skips unknown fields on deserialization

    length = fields.Integer()
    position = fields.Integer()
    correctly = fields.Integer()
    cards = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))
    active = fields.Boolean(missing=False)

    @post_load
    def get_quiz(self, data, **kwargs):
        return Quiz(**data)


if __name__ == "__main__":
    pass
