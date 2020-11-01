import logging
import random

from marshmallow import Schema, fields, EXCLUDE, post_load

from . import config
from .dictionary import Dictionary

logger = logging.getLogger(__name__)

dictionary = Dictionary(config.DICT_FILE)


class Quiz(object):
    def __init__(self, position=0, question='', answer='', correctly=0):
        self.position = position
        self.question = question
        self.answer = answer
        self.correctly = correctly

    def next_question_ready(self):
        ''' Generates the next question/answer pair '''
        if self.position < config.QUIZ_LEN:  # TODO: Proper config
            word = random.choice(dictionary.allwords)
            articles = dictionary.articles(word)
            self.question = word
            self.answer = articles
            self.position += 1
            return True
        return False

    def active(self):
        return self.position > 0

    def prove(self, answer):
        accepted_answers = self.answer.split("/")  # TODO: set in dictionary
        if answer in accepted_answers:
            self.correctly += 1
            return True
        return False


class QuizSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skips unknown fields on deserialization

    position = fields.Integer()
    question = fields.String()
    answer = fields.String()
    correctly = fields.Integer()

    @post_load
    def get_quiz(self, data, **kwargs):
        return Quiz(**data)


if __name__ == "__main__":
    pass
