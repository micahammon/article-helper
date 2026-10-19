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
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from logic import ArticleLogic, _normalize_noun, _tokenize_words

ROOT = Path(__file__).resolve().parents[1]
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
                analysis = self.logic.analyze_input(e["text"], focus=word)
                self.assertEqual(analysis["mode"], "lookup",
                                 f"{e['text']!r}: engine no longer commits")
                self.assertEqual(analysis["result"]["article"], e["verified_article"],
                                 f"{e['text']!r}: article drifted from the corpus")

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


if __name__ == "__main__":
    unittest.main()
