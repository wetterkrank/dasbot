import sys
import aiounittest
from aioresponses import aioresponses
from unittest.mock import AsyncMock, MagicMock, patch

from dasbot.controller import Controller
from dasbot.models.dictionary import Dictionary
from dasbot.i18n import set_locale
from dasbot.models.quiz import Quiz
from posthog import Posthog


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other


# TODO: disable all network calls in tests
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
        message_mock = AsyncMock(text="🇬🇧?")

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
        message_mock = AsyncMock(text="bla")

        await controller.generic(message_mock)

        mock_ui.return_value.help.assert_called_once()

    @patch("dasbot.controller.Interface")
    async def test_generic_with_quiz_completion(self, mock_ui):
        original_modules = {}
        for module_name in ["dasbot.ads", "dasbot.analytics", "dasbot.controller"]:
            # Store original modules to restore later
            original_modules[module_name] = sys.modules.get(module_name)
            # Remove modules from cache so they can be reimported with new settings
            if module_name in sys.modules:
                del sys.modules[module_name]

        try:
            with patch("dasbot.config.settings") as mock_settings:
                mock_settings.get.side_effect = lambda key: {
                    "PUBLISHER_KEY": "test_publisher_key_123",
                    "POSTHOG_API_KEY": "test_posthog_key_456",
                }.get(key)

                import dasbot.controller

                # PostHog's batching may prevent immediate requests,
                # so we just check that real class was instantiated
                self.assertIsInstance(dasbot.analytics.tracker, Posthog)
                self.assertIsInstance(dasbot.ads.ads, dasbot.ads.Ads)

                quiz = Quiz(
                    length=1,
                    cards=[{"word": "Kartoffel", "articles": "die"}],
                    position=0,
                    correctly=0,
                    active=True,
                    scores={},
                )
                chat_mock = MagicMock(
                    id=12345, quiz=quiz, user={"last_used_locale": "de"}
                )
                self.chats_repo.load_chat = MagicMock(return_value=chat_mock)

                # Set up async interface mocks
                mock_ui.return_value.give_feedback = AsyncMock()
                mock_ui.return_value.announce_result = AsyncMock()

                # Set up HTTP interception for both ads and analytics
                with aioresponses() as m:
                    m.post("https://us.i.posthog.com/capture/", status=200)
                    ads_url = "https://dasbot-ads.yak.supplies/impressions"
                    m.post(ads_url, status=202)

                    controller = dasbot.controller.Controller(
                        self.bot, self.chats_repo, self.stats_repo, self.dictionary
                    )
                    controller.ui = mock_ui.return_value

                    message_mock = AsyncMock(text="die", chat=MagicMock(id=12345))
                    await controller.generic(message_mock)

                    # Verify HTTP calls
                    ads_requests = [
                        call for call in m.requests if str(call[1]) == ads_url
                    ]
                    self.assertEqual(
                        len(ads_requests), 1, "Expected exactly one ad request"
                    )

        finally:
            for module_name, original_module in original_modules.items():
                if original_module:
                    sys.modules[module_name] = original_module
                elif module_name in sys.modules:
                    del sys.modules[module_name]
