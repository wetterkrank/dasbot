import logging

from marshmallow import Schema, fields, EXCLUDE, post_load

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


class Dictionary(object):
    """
    Dictionary 

    Args:
        dict_data (dict): see DictionaryEntrySchema for structure }
    """

    def __init__(self, dict_data):
        self._contents = dict_data
        self._allwords = self._contents.keys() # NOTE: keys() returns a set-like view

    def allwords(self):
        """ Returns the list of all words """
        return self._allwords

    def wordcount(self):
        """ Returns the dictionary length """
        return len(self._allwords)

    def articles(self, word):
        """ Returns the article(s) string for specified word (separated by '/' if more than one)"""
        return self._contents.get(word, {}).get("articles") or None

    def translation(self, word, locale):
        """  Returns the word's translation """
        return self._contents.get(word, {}).get("translation", {}).get(locale) or None

    def level(self, word):
        """ Returns the word's level """
        return self._contents.get(word, {}).get("level") or None


class DictionaryEntrySchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Skips unknown fields on deserialization

    word = fields.String()
    articles = fields.String()
    translation = fields.Dict(keys=fields.String(),  values=fields.String())
    level = fields.Integer()

    @post_load
    def make_entry(self, data, **kwargs):
        return {data["word"]: {"articles": data["articles"], "translation": data["translation"], "level": data["level"]}}


if __name__ == "__main__":
    pass
