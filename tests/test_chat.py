import unittest
from datetime import datetime

from unittest.mock import patch

from dasbot.models.chat import Chat


class TestChat(unittest.TestCase):
    @patch('dasbot.util.random_hhmm', return_value='12:12')
    def test_init(self, _mock):
        now = datetime.fromisoformat('2020-11-01 11:05:00+00:00')
        chat = Chat(chat_id=1001, now=now)
        self.assertEqual(1001, chat.id)
        self.assertEqual(datetime.fromisoformat('2020-11-01 12:12:00+00:00'), chat.quiz_scheduled_time)
        self.assertEqual(None, chat.last_seen)

    def test_set_quiz_time(self):
        chat = Chat(chat_id=1001)
        now = datetime.fromisoformat('2020-11-01 11:05:00+00:00')
        chat.set_quiz_time("09:00", now)
        self.assertEqual(datetime.fromisoformat('2020-11-02 09:00:00+00:00'), chat.quiz_scheduled_time)


if __name__ == '__main__':
    unittest.main()
