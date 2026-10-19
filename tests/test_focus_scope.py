"""A pinned focus must be answered about that noun, not another phrase.

Verifying AI example sentences showed the focused read often answering about
something else in the sentence: a determiner heading a different noun, a
construction elsewhere in the clause, or a fixed expression the matcher did not
look for. Each case here runs through both engines, logic.py and the JS twin in
index.html, so they cannot drift apart on it.
"""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from logic import ArticleLogic

ROOT = Path(__file__).resolve().parents[1]
PARITY = ROOT / "tools" / "check_parity.js"

# (sentence, focus or None, expected source or a prefix of it, expected form)
# The form is the page's key: "the", "an", "zero", "blocked", "context".
CASES = [
    # 1. a determiner counts only when it heads the focus noun's phrase
    ("My grandmother always cooks dinner", "dinner", "not:determiner", None),
    ("Many children learn football", "football", "not:determiner", "zero"),
    ("Students in this course study history", "history", "not:determiner", None),
    ("We had a lovely dinner", "dinner", "context_required", "context"),
    ("my new book", None, "determiner:possessive", "blocked"),
    # 2. a construction applies only when the focus is part of it
    ("Some of the most dramatic moments in history", "history",
     "not:construction", None),
    ("Some of the most dramatic moments in history", "moments",
     "construction:the_most", "the"),
    ("There is a cat in the garden", "cat", "construction:there_is_singular", "an"),
    ("There are many students in the history class", "history",
     "not:construction", None),
    # 3. a fixed expression around the focus is still found
    ("We met in the afternoon.", "afternoon", "fixed_expression", "the"),
    ("a few", "few", "fixed_expression", "an"),
    # 4. a fixed expression that opens the input is read whole
    ("all of a sudden", None, "fixed_expression", "an"),
    ("all of a sudden", "sudden", "fixed_expression", "an"),
    # 5. inflected variants of fixed expressions
    ("The meeting took place on Monday", "place", "fixed_expression", "zero"),
    ("The concert takes place in May", None, "fixed_expression", "zero"),
    ("She made progress", None, "fixed_expression", "zero"),
    ("We are making progress", "progress", "fixed_expression", "zero"),
    ("I visit them once a month", None, "fixed_expression", "an"),
]

_FORM = {"the": "the", "a / an": "an", "no article": "zero",
         "no article needed": "blocked", "it depends": "context"}


def _check_source(test, source, expected, label):
    if expected.startswith("not:"):
        test.assertFalse((source or "").startswith(expected[4:]),
                         f"{label}: answered by {source}")
    else:
        test.assertTrue((source or "").startswith(expected),
                        f"{label}: expected {expected}, got {source}")


class FocusScopePythonTests(unittest.TestCase):
    def test_cases(self):
        logic = ArticleLogic()
        for text, focus, source, form in CASES:
            with self.subTest(text=text, focus=focus):
                answer = logic.analyze_input(text, focus=focus)
                _check_source(self, answer.get("source"), source, f"{text!r}/{focus}")
                if form:
                    article = (answer.get("result") or {}).get("article")
                    self.assertEqual(_FORM.get(article), form, f"{text!r}/{focus}: {article}")


_JS = """
const {loadEngine} = require(process.argv[1]);
const s = loadEngine();
const cases = JSON.parse(process.argv[2]);
console.log(JSON.stringify(cases.map(([text, focus]) => {
  const hit = focus ? s.gate0Pinned(text, focus) : s.gate0(text);
  return hit ? {form: hit.form, fixed: !!hit.fixed, construction: !!hit.construction,
                blocked: !!hit.blocked, cat: hit.cat || ""} : null;
})));
"""


@unittest.skipUnless(shutil.which("node"), "node not on PATH; JS check skipped")
class FocusScopeJsTests(unittest.TestCase):
    def test_cases(self):
        pairs = [[text, focus] for text, focus, _, _ in CASES]
        proc = subprocess.run(["node", "-e", _JS, str(PARITY), json.dumps(pairs)],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        hits = json.loads(proc.stdout)
        for (text, focus, source, form), hit in zip(CASES, hits):
            with self.subTest(text=text, focus=focus):
                hit = hit or {}
                kind = ("fixed_expression" if hit.get("fixed")
                        else "construction" if hit.get("construction")
                        else "determiner" if hit.get("blocked") else "other")
                if source.startswith("not:"):
                    self.assertNotEqual(kind, source[4:], f"{text!r}/{focus}: {hit}")
                elif source in ("fixed_expression",) or source.startswith(("construction", "determiner")):
                    self.assertEqual(kind, source.split(":")[0], f"{text!r}/{focus}: {hit}")
                if form:
                    self.assertEqual(hit.get("form"), form, f"{text!r}/{focus}: {hit}")


if __name__ == "__main__":
    unittest.main()
