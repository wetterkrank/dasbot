import unittest

from datetime import datetime, timedelta

from dasbot.models.quiz import Quiz
from dynaconf import settings


# TODO: Split tests into separate cases
# TODO: Inject settings to Quiz and mock them instead of using real settings?
class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()  # NOTE: We're using TZ-naive dt here

    def test_new(self):
        # TODO: Mock the dictionary as well
        quiz = Quiz.new(history={
            'Tag': (1, None),
            'Monat': (1, self.now - timedelta(days=1)),
            'Jahr': (1, self.now)
        })
        self.assertEqual(settings.QUIZ_LEN, quiz.length)
        self.assertEqual(settings.QUIZ_LEN, len(quiz.cards))
        self.assertEqual(1, len(quiz.scores))
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
            'Tag': (1, self.now - timedelta(days=1)),
            'Monat': (1, self.now - timedelta(days=1)),
            'Jahr': (1, self.now + timedelta(days=1)),
        }
        quiz = Quiz.new(history)
        quiz.cards = [
            {'word': 'Jahr', 'articles': 'das'},
            {'word': 'Tag', 'articles': 'der'},
            {'word': 'Monat', 'articles': 'der'}
        ]
        result = quiz.verify_and_update_score('der')
        self.assertEqual(False, result)
        self.assertEqual(0, quiz.score[0])
        quiz.advance()
        result = quiz.verify_and_update_score('der')
        self.assertEqual(True, result)
        self.assertEqual(2, quiz.score[0])


if __name__ == '__main__':
    unittest.main()
