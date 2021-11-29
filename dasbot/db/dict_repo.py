import logging

from dasbot.models.dictionary import Dictionary, DictionaryEntrySchema

log = logging.getLogger(__name__)


class DictRepo(object):
    def __init__(self, dict_col):
        self._dict_col = dict_col

    def load(self):
        data_cursor = self._dict_col.find()
        dict_data = {}
        for item in data_cursor:
            dict_data.update(DictionaryEntrySchema().load(item))

        log.info("%s dictionary word(s) in DB", len(dict_data))
        if len(dict_data) == 0:
            log.warning("Dictionary is empty")
        return Dictionary(dict_data)

if __name__ == "__main__":
    pass
