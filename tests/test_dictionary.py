import unittest

from dasbot.models.dictionary import Dictionary


class TestDictionary(unittest.TestCase):
    def setUp(self):
        dict_data = {
            "foo": {"articles": "bar", "translation": {"en": "baz"}, "level": 1},
            "bar": {"articles": "foo", "translation": {"en": "woo"}, "level": 2},
        }
        self.dict = Dictionary(dict_data)

    def test_new(self):
        self.assertEqual(2, len(self.dict.allwords()))
        self.assertEqual(2, self.dict.wordcount())

    def test_articles(self):
        self.assertEqual("bar", self.dict.articles("foo"))
        self.assertEqual(None, self.dict.articles("fzz"))

    def test_translation(self):
        self.assertEqual("woo", self.dict.translation("bar", "en"))
        self.assertEqual(None, self.dict.translation("bar", "zz"))
        self.assertEqual(None, self.dict.translation("bzz", "en"))

    def test_level(self):
        self.assertEqual(1, self.dict.level("foo"))
        self.assertEqual(None, self.dict.level("fzz"))


if __name__ == '__main__':
    unittest.main()
