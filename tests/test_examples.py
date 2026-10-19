"""The example corpus must never teach what the tool denies.

examples_data.json holds sentences drafted or harvested for the readings view.
Each one was kept only because the engine classified it as a definite reading;
this suite re-checks that against the engine as it stands now, so a later rules
edit that changes an answer fails here instead of shipping a page whose examples
contradict its own tree. It also holds the provenance contract: nothing ships
untagged.

Run with the rest of the suite:

    python -m unittest discover -s tests -v
"""
import importlib.util
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from logic import ArticleLogic, _normalize_noun, _tokenize_words

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "generate_examples", ROOT / "tools" / "generate_examples.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)
PARITY = ROOT / "tools" / "check_parity.js"
CORPUS = json.loads((ROOT / "examples_data.json").read_text(encoding="utf-8"))
EXAMPLES = CORPUS.get("examples", [])

_ALLOWED_SOURCES = {"harvested", "ai"}
_REQUIRED = {"text", "word", "verified_article", "source", "date"}


class ExampleCorpusTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def test_corpus_is_not_empty(self):
        """A harvest has run; the readings view has something to show."""
        self.assertTrue(EXAMPLES, "examples_data.json is empty: run "
                                  "`python tools/generate_examples.py harvest`")

    def test_every_example_still_verifies(self):
        """The engine still gives each sentence the article the corpus claims.

        This is the whole point of the layer: AI (or a harvest) proposes, the
        canonical engine disposes. If a rules change moves an answer, the stale
        example is caught here.
        """
        for e in EXAMPLES:
            with self.subTest(text=e.get("text")):
                word = _normalize_noun(e["word"])
                self.assertIn(word, _tokenize_words(e["text"]),
                              "the focus word must appear in the sentence")
                fields = gen.verify(self.logic, e["text"], word)
                self.assertIsNotNone(fields, f"{e['text']!r}: engine no longer commits")
                self.assertEqual(fields["verified_article"], e["verified_article"],
                                 f"{e['text']!r}: article drifted from the corpus")

    def test_every_example_shows_its_article(self):
        """The engine answers for the word, not the sentence, so the sentence
        must actually put that article before the word."""
        for e in EXAMPLES:
            with self.subTest(text=e.get("text")):
                self.assertTrue(
                    gen.sentence_shows(e["verified_article"], e["text"], e["word"]),
                    f"{e['text']!r} does not show {e['verified_article']!r}")

    def test_no_example_is_an_it_depends(self):
        """An ambiguous sentence teaches the wrong thing, so none may survive."""
        for e in EXAMPLES:
            self.assertNotEqual(e["verified_article"], "it depends", e.get("text"))

    def test_every_example_carries_provenance(self):
        """Nothing ships untagged: source, word, article and date are required,
        and an AI-drafted entry names the model it came from."""
        for e in EXAMPLES:
            with self.subTest(text=e.get("text")):
                self.assertTrue(_REQUIRED.issubset(e),
                                f"missing fields: {_REQUIRED - set(e)}")
                self.assertIn(e["source"], _ALLOWED_SOURCES)
                if e["source"] == "ai":
                    self.assertTrue(e.get("model"), "an AI entry must name its model")

    def test_no_duplicate_examples(self):
        """The same sentence for the same word should not appear twice."""
        keys = [(e["word"], _normalize_noun(e["text"])) for e in EXAMPLES]
        self.assertEqual(len(keys), len(set(keys)), "duplicate example(s) in corpus")

    @unittest.skipUnless(shutil.which("node"), "node not on PATH; JS-parity check skipped")
    def test_examples_read_the_same_in_the_browser_engine(self):
        """Belt and suspenders: the corpus is verified against the Python engine,
        but learners read it through the JavaScript engine in index.html. This
        loads that engine and asserts every example gives the same form there, so
        the two can never silently disagree over a sentence a learner is shown.
        `tools/check_parity.js` does the loading; here we just gate on its result.
        """
        proc = subprocess.run(["node", str(PARITY)], capture_output=True, text=True)
        try:
            report = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            self.fail("parity harness produced no JSON:\n" + (proc.stderr or proc.stdout))
        self.assertTrue(report.get("loaded"),
                        "parity harness could not load the JS engine: "
                        + (report.get("error") or proc.stderr))
        self.assertEqual(proc.returncode, 0,
                         "JS reads these examples differently from the corpus:\n"
                         + json.dumps(report.get("failures", []), indent=2))


class SentenceArticleTests(unittest.TestCase):
    """verify() keeps a sentence only if its surface matches the engine's answer.
    These are the Haiku cinema drafts that once slipped through as "the"."""

    def test_reads_the_article_before_the_word(self):
        cases = {
            "We often go to the cinema on rainy Sunday afternoons.": "the",
            "The old black-and-white cinema closed.": "the",
            "She works at a cinema downtown.": "a",
            "Cinema has changed how people share stories.": None,
            "Studying cinema taught him to notice light.": None,
            "The cinema near my house is small.": "the",
            "We went to my cinema.": None,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(gen.article_in_sentence(text, "cinema"), expected)

    def test_bare_noun_is_not_a_the_example(self):
        self.assertFalse(gen.sentence_shows(
            "the", "Cinema has changed how people share stories.", "cinema"))
        self.assertFalse(gen.sentence_shows(
            "the", "Studying cinema taught him to notice light.", "cinema"))
        self.assertTrue(gen.sentence_shows(
            "the", "Nothing beats the cinema with friends.", "cinema"))

    def test_verify_drops_a_sentence_that_contradicts_the_engine(self):
        logic = ArticleLogic()
        self.assertIsNone(gen.verify(
            logic, "Studying cinema taught him to notice light.", "cinema"))
        kept = gen.verify(logic, "We often go to the cinema on Sundays.", "cinema")
        self.assertIsNotNone(kept)
        self.assertEqual(kept["verified_article"], "the")

    def test_verify_reads_fixed_expressions_in_a_sentence(self):
        logic = ArticleLogic()
        kept = gen.verify(logic, "We met in the afternoon.", "afternoon")
        self.assertEqual(kept["verified_article"], "the")
        kept = gen.verify(logic, "She went to school by bus.", "school")
        self.assertEqual(kept["verified_article"], "no article")
        # the expression matched must contain the target word
        self.assertIsNone(gen.verify(logic, "We met in the afternoon.", "met"))

    def test_either_answer_allows_both_forms(self):
        self.assertTrue(gen.sentence_shows("either the or no article", "in summer", "summer"))
        self.assertTrue(gen.sentence_shows(
            "either the or no article", "in the summer", "summer"))
        self.assertFalse(gen.sentence_shows(
            "either the or no article", "a summer to remember", "summer"))


class DraftPlanTests(unittest.TestCase):
    """The batch plan is built from rules_data.json alone; no network."""

    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / "rules_data.json").read_text(encoding="utf-8"))
        cls.plan = {p["word"]: p for p in gen.build_plan(data)}

    def test_only_single_word_targets(self):
        for word in self.plan:
            self.assertNotIn(" ", word)

    def test_fixed_expressions_contribute_their_noun_not_their_preposition(self):
        self.assertIn("school", self.plan)
        for word in ("at", "by", "to", "after"):
            self.assertNotIn(word, self.plan)

    def test_lookup_sense_is_carried(self):
        self.assertEqual(self.plan["phone"]["article"], "the")
        self.assertEqual(self.plan["phone"]["sense"], "the medium")

    def test_senses_are_plain_text(self):
        for p in self.plan.values():
            self.assertNotIn("<", p["sense"], p["word"])


if __name__ == "__main__":
    unittest.main()
