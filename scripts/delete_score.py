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


db = Database(settings).connect()

scores = db["scores"]
query = {"word": "Pro"}

log.info("Scores records: %s" % scores.count_documents(query))
# scores.delete_many(query)
