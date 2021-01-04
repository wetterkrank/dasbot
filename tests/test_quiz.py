import unittest

from dasbot.models.quiz import Quiz
from dynaconf import settings   # TODO: Inject settings to Quiz and mock them instead of using real settings?


class TestQuiz(unittest.TestCase):
    def test_new(self):
        quiz = Quiz.new()
        self.assertEqual(settings.QUIZ_LEN, quiz.length)
        self.assertEqual(settings.QUIZ_LEN, len(quiz.cards))
        self.assertEqual(0, quiz.position)
        self.assertEqual(1, quiz.pos)
        self.assertEqual(0, quiz.correctly)
        self.assertEqual(True, quiz.active)


if __name__ == '__main__':
    unittest.main()
