import logging
import sys

sys.path.insert(0, "..")

from dasbot.db.database import Database
from dasbot.config import settings


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%m.%d %H:%M:%S",
)
log = logging.getLogger(__name__)


chat_id = 0  # telegram chat_id
db = Database(settings).connect()

scores = db["scores"]
query = {"chat_id": chat_id}
log.info("Scores records count: %s" % scores.count_documents(query))
# scores.delete_many(query)

stats = db["stats"]
query = {"chat_id": chat_id}
log.info("Stats records count: %s" % stats.count_documents(query))
# stats.delete_many(query)
