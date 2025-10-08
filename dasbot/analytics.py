from posthog import Posthog
from dasbot.config import settings

class NoOpTracker:
    def capture(self, *args, **kwargs):
        pass

# TODO: support test environment
if settings.get("POSTHOG_API_KEY"):
    tracker = Posthog(
        project_api_key=settings.get("POSTHOG_API_KEY"),
        host="https://us.i.posthog.com"
    )
else:
    tracker = NoOpTracker()
