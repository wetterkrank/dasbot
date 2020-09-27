import logging

import csv
from config import DICT_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Dictionary(object):
    def __init__(self, dict_path):
        # not the encoding parameter for Excel-produced UTF-8 with BOM
        with open(dict_path, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, quoting=csv.QUOTE_MINIMAL)
            self.details = {}
            for row in csv_reader:
                self.details.update({row["word"]: 
                    [row["articles"], row["translation"], row["context"], int(row["level"])]
                })
            self.allwords = list(self.details.keys())
            logger.debug("Imported dictionary, %s words, last row: %s", len(self.allwords), row)

    def articles(self, word):
        articles = self.details[word][0]
        return articles

    def context(self, word):
        context = self.details[word][2]
        return context

if __name__ == '__main__':
    testdict = Dictionary(DICT_FILE)
