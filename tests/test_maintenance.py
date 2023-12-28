import unittest
import aiounittest

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from dasbot.maintenance import Maintenance


class TestMaintenance(aiounittest.AsyncTestCase):
    async def test_delete_old_stats(self):
        stats_repo = MagicMock()
        ts = datetime.now(tz=timezone.utc)
        cutoff_time = ts - timedelta(days=30)

        maintenance = Maintenance(stats_repo)
        await maintenance.delete_old_stats(ts)

        stats_repo.delete_old_stats.assert_called_with(cutoff_time)


if __name__ == '__main__':
    unittest.main()
