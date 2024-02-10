import logging

from pymongo import MongoClient
from urllib.parse import urlparse, quote_plus, urlunparse

log = logging.getLogger(__name__)


class Database(object):
    def __init__(self, settings):
        self.settings = settings

    def url(self):
        db_address = self.settings.DB_ADDRESS
        username = self.settings.get("DB_USERNAME")
        password = self.settings.get("DB_PASSWORD")
        if not (username and password):
            return db_address

        parsed_url = urlparse(db_address)
        netloc = parsed_url.netloc
        creds = ":".join(
            [
                quote_plus(username),
                quote_plus(password),
            ]
        )
        netloc = "@".join([creds, netloc])
        return urlunparse(parsed_url._replace(netloc=netloc))

    def connect(self):
        log.info("Connecting to database: %s", self.settings.DB_ADDRESS)
        client = MongoClient(self.url())
        db = client[self.settings.DB_NAME]
        # db.command('profile', 2, filter={'op': 'query'}) # not supported on Atlas free tier

        return db


if __name__ == "__main__":
    pass
