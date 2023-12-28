import logging

from datetime import datetime, timezone, timedelta

import asyncio

log = logging.getLogger(__name__)


class Maintenance(object):
    def __init__(self, stats_repo):
        self.stats_repo = stats_repo

    async def delete_old_stats(self, now=None):
        """
        :param now: timestamp when the function is called
        """
        if now is None:
            now = datetime.now(tz=timezone.utc)
        cutoff_time = now - timedelta(days=30)
        log.info("DB maintenance: deleting stats prior to %s" % cutoff_time)
        result = self.stats_repo.delete_old_stats(cutoff_time)
        log.info("%s documents deleted" % result.deleted_count)

    # Runs the daily db cleanup
    async def run(self):
        log.info("DB maintenance on, first run in 24h")
        while True:
            await asyncio.sleep(60 * 60 * 24)
            await self.delete_old_stats()


if __name__ == "__main__":
    pass
