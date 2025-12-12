import logging

from collections import defaultdict

from dasbot.models.dictionary import Dictionary, DictionaryEntrySchema, Level

log = logging.getLogger(__name__)


class DictRepo(object):
    def __init__(self, dict_col):
        self._dict_col = dict_col

    # Loads the dictionary from the database and splits by level
    def load(self):
        """
        :return: defaultdict of Level -> Dictionary, with full dictionary as default
        """
        data_cursor = self._dict_col.find()
        dict_data = {}
        for item in data_cursor:
            dict_data.update(DictionaryEntrySchema().load(item))

        log.info("%s dictionary word(s) in DB", len(dict_data))
        if len(dict_data) == 0:
            log.warning("Dictionary is empty")

        dictionaries = defaultdict(lambda: Dictionary(dict_data))
        dictionaries[Level.Default] = Dictionary(dict_data)
        dictionaries[Level.A1] = Dictionary(self.filter_by_level(dict_data, Level.A1))
        return dictionaries

    def filter_by_level(self, data, level):
        return {
            word: data
            for word, data in data.items()
            if (data.get("level") or "").lower() == level.value.lower()
        }


if __name__ == "__main__":
    pass
