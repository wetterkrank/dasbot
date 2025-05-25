import aiounittest
from unittest.mock import AsyncMock, MagicMock, patch

from dasbot.controller import Controller
from dasbot.models.dictionary import Dictionary
from dasbot.i18n import set_locale
from dasbot.models.quiz import Quiz


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other


class TestController(aiounittest.AsyncTestCase):
    def setUp(self):
        self.chats_repo = MagicMock()
        self.stats_repo = MagicMock()
        self.bot = MagicMock()
        self.dictionary = Dictionary(
            {
                "foo": {"articles": "bar", "note": {"en": "baz"}, "frequency": 1},
                "bar": {"articles": "foo", "note": {"en": "woo"}, "frequency": 2},
            }
        )
        set_locale("en")

    async def test_stats(self):
        self.stats_repo.get_stats = MagicMock(
            return_value={
                "touched": 0,
                "mistakes_30days": [],
            }
        )
        self.chats_repo.load_scores = MagicMock(return_value={})
        controller = Controller(
            self.bot, self.chats_repo, self.stats_repo, self.dictionary
        )
        message_mock = AsyncMock()

        await controller.stats(message_mock)

        message_mock.answer.assert_called_with(
            AnyStringWith("<b>Your progress: 0%</b>")
        )
        message_mock.answer.assert_called_with(AnyStringWith("words seen: 0 / 2"))
        message_mock.answer.assert_called_with(AnyStringWith("words to repeat: 0"))
        message_mock.answer.assert_called_with(AnyStringWith("words memorized: 0"))

    async def test_generic_no_text(self):
        message_mock = AsyncMock()
        message_mock.text = None
        controller = Controller(
            self.bot, self.chats_repo, self.stats_repo, self.dictionary
        )

        await controller.generic(message_mock)

    @patch("dasbot.controller.Interface")
    async def test_generic_with_hint(self, mock_ui):
        self.chats_repo.load_chat = MagicMock(
            return_value=MagicMock(quiz=MagicMock()),
        )
        mock_ui.return_value.give_hint = AsyncMock()
        mock_ui.return_value.hint_commands = MagicMock(return_value=["🇬🇧?"])
        controller = Controller(
            self.bot, self.chats_repo, self.stats_repo, self.dictionary
        )
        message_mock = AsyncMock(text = "🇬🇧?")

        await controller.generic(message_mock)

        mock_ui.return_value.give_hint.assert_called_once()

    @patch("dasbot.controller.Interface")
    async def test_generic_with_help(self, mock_ui):
        self.chats_repo.load_chat = MagicMock(
            return_value=MagicMock(quiz=Quiz()),
        )
        mock_ui.return_value.help = AsyncMock()
        controller = Controller(
            self.bot, self.chats_repo, self.stats_repo, self.dictionary
        )
        message_mock = AsyncMock(text = "bla")

        await controller.generic(message_mock)

        mock_ui.return_value.help.assert_called_once()
