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

SCHEDULE = {
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
        """ Returns a new fully setup Quiz
        :param history: dictionary {word: (score, due_date)}
        :return: new Quiz instance
        """
        length = settings.QUIZ_LEN
        review_length = min(length // 2, len(history))
        scores = Quiz.prepare_review(history, review_length)
        cards = Quiz.prepare_cards(length, scores, dictionary.allwords)
        return Quiz(
            length=length,
            cards=cards,
            position=0,
            correctly=0,
            active=True,
            scores=scores
        )

    @staticmethod
    def prepare_review(history, rev_length, now=None):
        """ Selects overdue words to practice from the history dict
        :param history: dictionary {word: (score, due_date)}
        :param rev_length: integer; function returns rev_length (or fewer) entries
        :param now: datetime for testing
        :return: scores, in the same format as input dictionary
        """
        now = now or datetime.now(tz=timezone('UTC')).replace(tzinfo=None)  # Strip TZ here or add to DB-stored dates
        # NOTE: Could add a randomizer right here:
        overdue = filter(
            lambda rec: rec[1][1] and now > rec[1][1], history.items())
        scores = {k: v for _, (k, v) in zip(range(rev_length), overdue)}
        return scores

    @staticmethod
    def prepare_cards(length, scores, allwords):
        cards = []
        new_length = length - len(scores)
        # TODO: Consecutive instead of random?
        new_words = random.sample(set(allwords) - set(scores), new_length)
        for word in scores.keys():
            cards.append({'word': word, 'articles': dictionary.articles(word)})
        for word in new_words:
            # TODO: Store scores in cards?
            cards.append({'word': word, 'articles': dictionary.articles(word)})
        return cards

    # NOTE: Split into 2 parts?
    def verify_and_update_score(self, answer):
        accepted_answers = self.answer.split("/")  # TODO: set in dictionary
        if answer in accepted_answers:
            result = True
            self.correctly += 1
            new_score_num = min(self.score[0] + 1, max(SCHEDULE.keys()))
        else:
            result = False
            new_score_num = max(self.score[0] - 1, min(SCHEDULE.keys()))
        self.score = (new_score_num, self.next_review(new_score_num))
        return result

    @staticmethod
    def next_review(score_num, now=None):
        """
        :param score_num: current score (after the answer check), Integer
        :param now: current datetime, for testing
        :return: next review datetime for this score
        """
        now = now or datetime.now(tz=timezone('UTC')).replace(tzinfo=None)
        next_review_date = now + SCHEDULE[score_num]
        return next_review_date

    def advance(self):
        self.position += 1

    def stop(self):
        self.active = False

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
        """ Returns a tuple (Integer score, Datetime due date) """
        return self.scores.get(self.question) or (0, datetime.now(tz=timezone('UTC')))

    @score.setter
    def score(self, new_val):
        self.scores[self.question] = new_val


class QuizSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skips unknown fields on deserialization

    length = fields.Integer()
    position = fields.Integer()
    correctly = fields.Integer()
    active = fields.Boolean(missing=False)
    cards = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))
    scores = fields.Dict(keys=fields.Str(),
                         values=fields.Tuple((fields.Integer(), fields.Raw())))

    @post_load
    def get_quiz(self, data, **kwargs):
        return Quiz(**data)


if __name__ == "__main__":
    pass
