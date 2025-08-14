import unittest
from unittest.mock import patch
import aiounittest
import sys

from dasbot.ads import Ads, NoOpAds


class TestNoOpAds(aiounittest.AsyncTestCase):
    def setUp(self):
        self.noop_ads = NoOpAds()

    async def test_send_does_nothing(self):
        """Test that NoOpAds.send() does nothing and doesn't raise exceptions"""
        await self.noop_ads.send(12345, "de")


class TestAds(aiounittest.AsyncTestCase):
    def setUp(self):
        self.ads = Ads()

    def test_payload_construction(self):
        """Test that Ads.send builds the correct request payload and URL"""
        with patch('dasbot.ads.settings') as mock_settings:
            mock_settings.get.side_effect = lambda key: {
                "PUBLISHER_KEY": "test_key"
            }.get(key)

            ads_instance = Ads()

            # Collector to capture what ClientSession.post receives
            collected = {}

            # Dummy classes to simulate aiohttp's async context managers
            class DummyResponse:
                def __init__(self, status):
                    self.status = status

            class DummyPostCtx:
                def __init__(self, response):
                    self._response = response
                async def __aenter__(self):
                    return self._response
                async def __aexit__(self, exc_type, exc, tb):
                    return False

            class DummySession:
                def post(self, url, json):
                    collected["url"] = url
                    collected["json"] = json
                    return DummyPostCtx(DummyResponse(202))
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc, tb):
                    return False

            # Patch ClientSession to our dummy
            with patch('dasbot.ads.aiohttp.ClientSession', return_value=DummySession()):
                # Run the send to trigger payload construction
                import asyncio
                asyncio.run(ads_instance.send("12345", "en"))

            expected_payload = {
                "impression": {
                    "key": "test_key",
                    "chat_id": "12345",
                    "locale": "en",
                }
            }

            self.assertEqual(collected["url"], ads_instance.endpoint)
            self.assertEqual(collected["json"], expected_payload)

    @patch('dasbot.ads.log')
    async def test_send_network_exception(self, mock_log):
        """Test ad impression sending with network exception"""

        with patch('dasbot.ads.settings') as mock_settings:
            mock_settings.get.side_effect = lambda key: {
                "PUBLISHER_KEY": "test_key"
            }.get(key)

            ads_instance = Ads()

            # Mock the entire aiohttp.ClientSession to raise an exception
            with patch('dasbot.ads.aiohttp.ClientSession') as mock_session_class:
                mock_session_class.side_effect = Exception("Network error")

                await ads_instance.send("12345", "en")

                mock_log.error.assert_called_once_with("Failed to send ad impression: Network error")


class TestAdsInitialization(unittest.TestCase):
    """Test the conditional initialization of the ads module"""

    def setUp(self):
        # Store the original module to restore it after tests
        self.original_ads_module = sys.modules.get('dasbot.ads')
        if 'dasbot.ads' in sys.modules:
            del sys.modules['dasbot.ads']

    def tearDown(self):
        # Restore the original module
        if self.original_ads_module:
            sys.modules['dasbot.ads'] = self.original_ads_module
        elif 'dasbot.ads' in sys.modules:
            del sys.modules['dasbot.ads']

    def test_ads_initialization_without_publisher_key(self):
        """Test that NoOpAds is initialized when PUBLISHER_KEY is missing"""
        with patch('dasbot.config.settings') as mock_settings:
            mock_settings.get.side_effect = lambda key: {
                "PUBLISHER_KEY": None
            }.get(key)

            # Import the module fresh
            import dasbot.ads

            # Verify the correct class was instantiated
            self.assertIsInstance(dasbot.ads.ads, dasbot.ads.NoOpAds)

if __name__ == '__main__':
    unittest.main()
