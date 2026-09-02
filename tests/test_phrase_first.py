import unittest

from logic import ArticleLogic


class PhraseFirstTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def test_direct_lookup_from_noun_input(self):
        analysis = self.logic.analyze_input("the USA")
        self.assertEqual(analysis["mode"], "lookup")
        self.assertEqual(analysis["focus_noun"], "usa")
        self.assertEqual(analysis["result"]["article"], "the")

    def test_lookup_phrase_found_inside_sentence(self):
        analysis = self.logic.analyze_input("I listened to the radio this morning.")
        self.assertEqual(analysis["mode"], "lookup")
        self.assertEqual(analysis["focus_noun"], "radio")
        self.assertEqual(analysis["result"]["article"], "the")

    def test_longest_lookup_phrase_wins(self):
        analysis = self.logic.analyze_input("They moved to the United Kingdom last year.")
        self.assertEqual(analysis["mode"], "lookup")
        self.assertEqual(analysis["focus_noun"], "united kingdom")
        self.assertEqual(analysis["result"]["article"], "the")

    def test_fallback_infers_focus_noun(self):
        analysis = self.logic.analyze_input("I bought book yesterday")
        self.assertEqual(analysis["mode"], "question")
        self.assertEqual(analysis["focus_noun"], "book")
        self.assertIsNone(analysis["result"])

    def test_empty_input_fallback(self):
        analysis = self.logic.analyze_input("")
        self.assertEqual(analysis["mode"], "question")
        self.assertEqual(analysis["focus_noun"], "")
        self.assertIsNone(analysis["result"])


if __name__ == "__main__":
    unittest.main()
