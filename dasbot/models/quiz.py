import logging
import random
from datetime import datetime
from pytz import timezone

from marshmallow import Schema, fields, EXCLUDE, post_load

from dynaconf import settings
from dasbot.dictionary import Dictionary

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

dictionary = Dictionary(settings.DICT_FILE)


class Quiz(object):
    def __init__(self, length=None, cards=[], position=0, correctly=0, active=False, scores={}):
        self.length = length
        self.cards = cards
        self.position = position
        self.correctly = correctly
        self.active = active
        self.scores = scores

    @classmethod
    def new(cls, history):
        cards = []
        length = settings.QUIZ_LEN
        n_known = min(length // 2, len(history))
        n_new = length - n_known

        scores = dict(random.sample(history.items(), n_known))
        log.debug('scores planned to repeat: %s', scores)
        for word in scores.keys():
            card = {'word': word, 'articles': dictionary.articles(word)}
            cards.append(card)
        new = random.sample(dictionary.contents.items(), n_new)
        for word, attrs in new:
            card = {'word': word, 'articles': attrs[0]}  # TODO: Store scores in cards
            cards.append(card)
        return cls(length=length, cards=cards, position=0, correctly=0, active=True, scores=scores)

    @property
    def pos(self):
        return self.position + 1

    @property
    def has_questions(self):
        # log.debug("HAS Qs: position %s, self.len %s, self.cards %s", self.position, self.length, len(self.cards))
        return self.position < self.length and self.position < len(self.cards)

    @property
    def question(self):
        return self.cards[self.position]['word']

    @property
    def answer(self):
        return self.cards[self.position]['articles']

    @property
    def score(self):
        values = self.scores.get(self.question)
        return values or (0, datetime.now(tz=timezone('UTC')))
        # return {self.question: values} if values else {self.question: (0, 'someday')}

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
    active = fields.Boolean(missing=False)
    cards = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))
    scores = fields.Dict(keys=fields.Str(), values=fields.Tuple((fields.Integer(), fields.Raw())))

    @post_load
    def get_quiz(self, data, **kwargs):
        return Quiz(**data)


if __name__ == "__main__":
    pass
