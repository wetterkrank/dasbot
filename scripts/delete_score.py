import logging

from dynaconf import Dynaconf

import sys
sys.path.insert(0, '..')
from dasbot.db.database import Database


settings = Dynaconf(environments=['default', 'production', 'development'],
                    settings_file='settings.toml',
                    load_dotenv=True)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


db = Database(settings).connect()
scores = db['scores']

query = {"word": "Pro"}

log.info("Scores in the DB: %s" % scores.count_documents(query))

# result = scores.delete_many(query)
# log.info("Deletion result: %s" % result)
