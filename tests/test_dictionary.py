import unittest

from dasbot.models.dictionary import Dictionary


class TestDictionary(unittest.TestCase):
    def setUp(self):
        dict_data = {
            "foo": {"articles": "bar", "note": {"en": "baz"}, "frequency": 2.0},
            "bar": {"articles": "foo", "note": {"en": "woo"}, "frequency": 0.5},
        }
        self.dict = Dictionary(dict_data)

    def test_new(self):
        self.assertEqual(2, len(self.dict.words()))
        self.assertEqual(2, self.dict.wordcount())

    def test_articles(self):
        self.assertEqual("bar", self.dict.articles("foo"))
        self.assertEqual(None, self.dict.articles("fzz"))

    def test_note(self):
        self.assertEqual("woo", self.dict.note("bar", "en"))
        self.assertEqual(None, self.dict.note("bar", "zz"))
        self.assertEqual(None, self.dict.note("bzz", "en"))

    def test_frequency(self):
        self.assertEqual(2.0, self.dict.frequency("foo"))
        self.assertEqual(None, self.dict.frequency("fzz"))


if __name__ == '__main__':
    unittest.main()
