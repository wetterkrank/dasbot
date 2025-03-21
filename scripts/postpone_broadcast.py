# Postpones overdue quizzes by 24 hours
# May need to run several times if broadcast was out for more than a day

import logging
import sys
from datetime import datetime, timedelta, timezone


sys.path.insert(0, "..")

from dasbot.config import settings
from dasbot.db.database import Database
from dasbot.db.chats_repo import ChatsRepo


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%m.%d %H:%M:%S",
)
log = logging.getLogger(__name__)


db = Database(settings).connect()
chats = db["chats"]
now = datetime.now(tz=timezone.utc)

query = {"subscribed": True, "quiz_scheduled_time": {"$lte": now}}
log.info(f"Pending: {chats.count_documents(query)}")

update = [
    {"$set": {"quiz_scheduled_time": {"$add": ["$quiz_scheduled_time", 24 * 60 * 60 * 1000]}}}
]
# result = chats.update_many(query, update)
# log.info(f"Updated {result.modified_count} records")
