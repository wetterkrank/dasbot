import csv
import logging

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

    def articles(self, word):
        articles = self.contents[word][0]
        return articles

    def context(self, word):
        context = self.contents[word][2]
        return context


if __name__ == '__main__':
    pass
