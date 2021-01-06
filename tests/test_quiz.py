import unittest

from datetime import datetime, timedelta
from pytz import timezone

from dasbot.models.quiz import Quiz, SCHEDULE
from dynaconf import settings


# TODO: Split tests into separate cases?
# TODO: Inject settings to Quiz and mock them instead of using real settings?
class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(tz=timezone('UTC')).replace(tzinfo=None)  # NOTE: We're using TZ-naive dt here

    def test_new(self):
        # TODO: Mock the dictionary as well
        quiz = Quiz.new(history={
            'Tag': (1, None),
            'Monat': (1, self.now - timedelta(days=1)),
            'Jahr': (1, self.now + timedelta(days=1))
        })
        self.assertEqual(settings.QUIZ_LEN, quiz.length)
        self.assertEqual(settings.QUIZ_LEN, len(quiz.cards))
        self.assertEqual(1, len(quiz.scores), f'unexpected scores length; scores: {quiz.scores}; now: {self.now}')
        self.assertEqual('Monat', quiz.cards[0]['word'])
        self.assertEqual(0, quiz.position)
        self.assertEqual(1, quiz.pos)
        self.assertEqual(0, quiz.correctly)
        self.assertEqual(True, quiz.active)

    def test_prepare_review(self):
        history = {
            'Tag': (1, self.now - timedelta(days=1)),
            'Monat': (1, self.now - timedelta(days=1)),
            'Jahr': (1, self.now + timedelta(days=1)),
        }
        scores = Quiz.prepare_review(history, 3, self.now)
        self.assertEqual(2, len(scores))

    def test_schedule_review(self):
        review_date = Quiz.next_review(0, self.now)
        self.assertEqual(self.now, review_date)
        review_date = Quiz.next_review(3, self.now)
        self.assertEqual(self.now + timedelta(days=1), review_date)

    def test_verify_and_update_score(self):
        history = {
            'Jahr': (1, self.now + timedelta(days=1)),  # skip
            'Tag': (1, self.now - timedelta(days=1)),  # in
            'Monat': (10, self.now - timedelta(days=1))  # in
        }
        quiz = Quiz.new(history)
        quiz.cards = [
            {'word': 'Zeit', 'articles': 'die'},
            {'word': 'Tag', 'articles': 'der'},
            {'word': 'Monat', 'articles': 'der'}
        ]
        result = quiz.verify_and_update_score('der')  # incorrect
        self.assertEqual(False, result)
        self.assertEqual(0, quiz.score[0])
        quiz.advance()
        result = quiz.verify_and_update_score('der')  # correct
        self.assertEqual(True, result)
        self.assertEqual(2, quiz.score[0])
        quiz.advance()
        result = quiz.verify_and_update_score('der')  # correct
        self.assertEqual(True, result)
        self.assertEqual(max(SCHEDULE.keys()), quiz.score[0])


if __name__ == '__main__':
    unittest.main()
