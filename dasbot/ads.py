import aiohttp
import logging
from dasbot.config import settings

log = logging.getLogger(__name__)

class NoOpAds:
    async def send(self, *args, **kwargs):
        pass

class Ads:
    def __init__(self):
        self.endpoint = "https://dasbot-ads.yak.supplies/impressions"
        self.publisher_key = settings.get("PUBLISHER_KEY")

    async def send(self, chat_id, locale):
        payload = {
            "impression": {
                "key": self.publisher_key,
                "chat_id": chat_id,
                "locale": locale
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=payload) as response:
                    if response.status != 202:
                        log.error(f"Ad impression failed with status {response.status}")
                    else:
                        log.debug("Ad impression sent successfully")
        except Exception as e:
            log.error(f"Failed to send ad impression: {e}")

if settings.get("PUBLISHER_KEY"):
    ads = Ads()
else:
    ads = NoOpAds()
