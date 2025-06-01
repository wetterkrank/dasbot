# Delete old chats that have not been active for over 3 years

import logging
import sys
from datetime import datetime, timedelta, timezone


sys.path.insert(0, "..")

from dasbot.config import settings
from dasbot.db.database import Database


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%m.%d %H:%M:%S",
)
log = logging.getLogger(__name__)


db = Database(settings).connect()
chats = db["chats"]
scores = db["scores"]
cutoff = datetime.now(tz=timezone.utc) - timedelta(days=365 * 3)

query = {"last_seen": {"$lte": cutoff}}
log.info(f"Active more than 3 years ago: {chats.count_documents(query)}")
results_cursor = chats.find(query, {"_id": 0})
for chat in results_cursor:
    scores_query = {"chat_id": chat["chat_id"]}
    scores_count = scores.count_documents(scores_query)
    log.info(f"Deleting {chat['chat_id']} with {scores_count} score(s), last seen at {chat['last_seen']}")

    scores.delete_many(scores_query)
    chats.delete_one({"chat_id": chat["chat_id"]})
