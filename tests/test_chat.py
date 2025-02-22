import unittest
from datetime import datetime

from unittest.mock import patch, MagicMock

from dasbot.models.chat import Chat

FAKE_NOW = datetime.fromisoformat('2020-11-01 11:05:00+00:00')


class TestChat(unittest.TestCase):
    @patch('dasbot.models.chat.datetime')
    @patch('dasbot.util.datetime')
    def test_init(self, mock_chat_dt, mock_util_dt):
        mock_chat_dt.now = MagicMock(return_value=FAKE_NOW)
        mock_util_dt.now = MagicMock(return_value=FAKE_NOW)
        chat = Chat(chat_id=1001)
        self.assertEqual(1001, chat.id)
        # For new chats, next scheduled quiz will run on the same time tomorrow
        self.assertEqual(chat.quiz_scheduled_time, datetime.fromisoformat('2020-11-02 11:05:00+00:00'))
        self.assertEqual(None, chat.last_seen)

    @patch('dasbot.models.chat.datetime')
    def test_set_quiz_time(self, mock_dt):
        mock_dt.now().astimezone = MagicMock(return_value=FAKE_NOW)
        chat = Chat(chat_id=1001)
        chat.set_quiz_time("15:00")
        # For existing chats, quiz at scheduled to nearest requested HH:MM
        self.assertEqual(chat.quiz_scheduled_time, datetime.fromisoformat('2020-11-01 15:00:00+00:00'))


if __name__ == '__main__':
    unittest.main()
