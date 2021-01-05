import unittest

from datetime import datetime, timedelta, timezone

from dasbot.models.quiz import Quiz
# TODO: Inject settings to Quiz and mock them instead of using real settings?
from dynaconf import settings


class TestQuiz(unittest.TestCase):
    def test_new(self):
        # TODO: Mock the dictionary as well
        quiz = Quiz.new(history={
            'Tag': (1, None),
            'Monat': (1, datetime.now() - timedelta(days=1))
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
        now = datetime.now()
        history = {
            'Tag': (1, now - timedelta(days=1)),
            'Monat': (1, now - timedelta(days=1)),
            'Jahr': (1, now + timedelta(days=1)),
        }
        scores = Quiz.prepare_review(history, 3, now)
        self.assertEqual(2, len(scores))


if __name__ == '__main__':
    unittest.main()
