import logging

from marshmallow import Schema, fields, EXCLUDE, post_load

log = logging.getLogger(__name__)


class Dictionary(object):
    """
    Dictionary

    Args:
        dict_data (dict): see DictionaryEntrySchema for structure }
    """

    def __init__(self, dict_data):
        self._contents = dict_data
        self._words = self._contents.keys()

    def words(self):
        """Returns (a set-like view of) all words, in insertion order"""
        # NOTE: use list() to make a copy of the set
        return self._words

    def wordcount(self):
        """Returns the dictionary length"""
        return len(self._words)

    def articles(self, word):
        """Returns the article(s) string for specified word (separated by '/' if more than one)"""
        return self._contents.get(word, {}).get("articles") or None

    def note(self, word, locale):
        """Returns the comment (for DE locale) or translation"""
        return self._contents.get(word, {}).get("note", {}).get(locale) or None

    def frequency(self, word):
        """Returns the word's frequency"""
        return self._contents.get(word, {}).get("frequency") or None

    def has(self, word):
        """Returns True if word is in dictionary"""
        return self._contents.get(word) is not None

class DictionaryEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skips unknown fields on deserialization

    word = fields.String()
    articles = fields.String()
    frequency = fields.Float()
    note = fields.Dict(keys=fields.String(), values=fields.String())

    @post_load
    def make_entry(self, data, **kwargs):
        return {
            data["word"]: {
                "articles": data["articles"],
                "frequency": data["frequency"],
                "note": data["note"],
            }
        }


if __name__ == "__main__":
    pass
