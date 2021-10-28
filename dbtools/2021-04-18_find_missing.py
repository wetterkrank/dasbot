# Checks the scores collection for entries where word is not present in the dictionary.

import logging

import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import pymongo
from dynaconf import settings

from dasbot.dictionary import Dictionary

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m.%d %H:%M:%S')
log = logging.getLogger(__name__)


if __name__ == '__main__':
    print('HELLO')
    client = pymongo.MongoClient(settings.DB_ADDRESS)
    db = client[settings.DB_NAME]
    scores_col = db['scores']

    dictionary = Dictionary(settings.DICT_FILE)

    unique_score_words = scores_col.distinct('word')
    for word in unique_score_words:
        if not dictionary.articles(word):
            print(word)
