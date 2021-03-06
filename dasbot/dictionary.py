import logging

import csv

log = logging.getLogger(__name__)


class Dictionary(object):
    """
    Attributes
    ----------
    allwords : list
        a list of all words
    contents : dictionary of arrays
        "word: [articles, translation, context, level]"

    Methods
    -------
    articles(word)
        Returns article(s) for the word (separated by / if more than one)
    context(word)
        Returns a sentence with the word
    """

    # note the encoding parameter for Excel-produced UTF-8 with BOM
    def __init__(self, dict_path):
        """ dict_path : path to the dictionary file """
        with open(dict_path, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file, quoting=csv.QUOTE_MINIMAL)
            self.contents = {}
            for row in csv_reader:
                self.contents.update(
                    {
                        row["word"]: [row["articles"], row["translation"], row["context"], int(row["level"])]
                    }
                )
            self.allwords = list(self.contents.keys())
            log.debug("Imported dictionary, %s words, last row: %s", len(self.allwords), row)

    # BUG: Need error handling in case word is not found (dictionary edited but the word is present in the history)
    def articles(self, word):
        record = self.contents.get(word)
        if not record:
            return None
        return self.contents[word][0]

    def context(self, word):
        return self.contents[word][2]

    def level(self, word):
        return self.contents[word][3]


if __name__ == '__main__':
    pass
