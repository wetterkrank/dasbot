import logging
import random
from datetime import datetime, timedelta
from pytz import timezone

from marshmallow import Schema, fields, EXCLUDE, post_load

from dynaconf import settings
from dasbot.dictionary import Dictionary

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

dictionary = Dictionary(settings.DICT_FILE)

REVIEW = {
    0: timedelta(0),
    1: timedelta(hours=1),
    2: timedelta(hours=12),
    3: timedelta(days=1),
    4: timedelta(days=3),
    5: timedelta(weeks=1),
    6: timedelta(weeks=2),
    7: timedelta(weeks=4),
    8: timedelta(weeks=8),
    9: timedelta(weeks=16),
    10:	timedelta(weeks=24)
}


class Quiz(object):
    def __init__(self, length=None, cards=[], position=0, correctly=0, active=False, scores={}):
        self.length = length
        self.cards = cards
        self.position = position
        self.correctly = correctly
        self.active = active
        self.scores = scores

    @staticmethod
    def new(history):
        """
        :param history: dictionary {word: (score, due_date)}
        :return: new Quiz instance
        """
        length = settings.QUIZ_LEN
        review_length = min(length // 2, len(history))
        scores = Quiz.prepare_review(history, review_length)
        cards = Quiz.prepare_cards(length, scores, dictionary.allwords)
        return Quiz(length=length, cards=cards, position=0, correctly=0, active=True, scores=scores)

    @staticmethod
    def prepare_review(history, rev_length, now=None):
        """
        :param history: dictionary {word: (score, due_date)}
        :param rev_length: integer
        :return: scores, a selection from this dictionary -- of rev_length or shorter
        """
        now = now or datetime.now(tz=timezone('UTC')).replace(tzinfo=None)
        # NOTE: Could add a randomizer right here:
        overdue = filter(lambda rec: rec[1][1] and now > rec[1][1], history.items())
        scores = {k: v for _, (k, v) in zip(range(rev_length), overdue)}
        # scores = dict(random.sample(overdue, min(rev_length, len(overdue))))  # There's no len() for iterator though
        log.debug('planned review scores: %s', scores)
        return scores

    @staticmethod
    def prepare_cards(length, scores, allwords):
        cards = []
        new_length = length - len(scores)
        new_words = random.sample(set(allwords) - set(scores), new_length)  # TODO: Consecutive instead of random?
        for word in scores.keys():
            cards.append({'word': word, 'articles': dictionary.articles(word)})
        for word in new_words:
            cards.append({'word': word, 'articles': dictionary.articles(word)})  # TODO: Store scores in cards?
        return cards

    @property
    def pos(self):
        return self.position + 1

    @property
    def has_questions(self):
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
