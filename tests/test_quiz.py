import unittest

from datetime import datetime, timedelta
from pytz import timezone

from dasbot.models.quiz import Quiz, SCHEDULE
from dasbot.models.dictionary import Dictionary


class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(tz=timezone('UTC')).replace(tzinfo=None)  # NOTE: We're using TZ-naive dt here
        # 13 words in the dictionary
        words = ['Tag', 'Monat', 'Jahr', 'Mal', 'Zeit', 'Beispiel', 'Deutsch', 'Frau', 'Kind', 'Aspekt', 'Mensch', 'Mann', 'Haus']
        self.dictionary = Dictionary({w: {'articles': 'foo', 'translation': {'en': 'bar'}, 'level': 1} for w in words})
        # of them, 3 overdue words to review
        self.scores = {
            'Tag': (1, self.now - timedelta(days=1)),
            'Monat': (1, self.now - timedelta(days=1)),
            'Jahr': (1, self.now - timedelta(days=1)),
        }

    def test_get_review(self):
        self.scores['Tag'] = (1, self.now + timedelta(days=1))
        to_review = Quiz.get_review(self.scores, 5, self.now)
        self.assertEqual(len(to_review), 2, f'review must be of correct length')
        self.assertEqual(to_review.get('Tag'), None, f'review must not include non-overdue words')

    def test_get_new_words(self):
        new_words = Quiz.get_new_words(self.scores, 5, self.dictionary)
        self.assertEqual(5, len(new_words))
        new_words = Quiz.get_new_words(self.scores, 15, self.dictionary)
        self.assertEqual(10, len(new_words))

    def test_new(self):
        quiz = Quiz.new(10, self.scores, self.dictionary)
        self.assertEqual(len(quiz.cards), 10)
        self.assertEqual(len(quiz.scores), 3, f'unexpected scores length')
        self.assertEqual(quiz.position, 0)
        self.assertEqual(quiz.pos, 1)
        self.assertEqual(quiz.correctly, 0)
        self.assertTrue(quiz.active)

    # all dictionary words are already "touched" -> cards are built using review words only
    def test_new_with_no_newwords(self):
        scores = {word: (1, self.now - timedelta(days=1)) for word in self.dictionary.allwords()}
        quiz = Quiz.new(10, scores, self.dictionary)
        self.assertEqual(len(quiz.cards), 10)
        self.assertTrue(not any([card['word'] in ['Haus', 'Mann', 'Mensch'] for card in quiz.cards]))

    def test_schedule_review(self):
        review_date = Quiz.next_review(0, self.now)
        self.assertEqual(self.now, review_date)
        review_date = Quiz.next_review(3, self.now)
        self.assertEqual(self.now + timedelta(weeks=1), review_date)

    def test_verify_and_update_score(self):
        history = {
            'Jahr': (1, self.now + timedelta(days=1)),  # skip
            'Tag': (1, self.now - timedelta(days=1)),  # in
            'Monat': (10, self.now - timedelta(days=1))  # in
        }
        quiz = Quiz.new(10, history, self.dictionary)
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
