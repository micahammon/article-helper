"""Verification suite for the Gate 0 / tree split.

Gate 0 must resolve every fixed expression and listed name to a *specific*
article form. The old failure mode on both sides of this project was a
highest-precedence gate that returned "memorized" or "go and restart" instead of
an answer, so these tests assert that a form always comes back.
"""

import json
import unittest
from pathlib import Path

from logic import ArticleLogic, choose_a_or_an
from rules import DECISION_TREE, ENTRY_NODE

DATA = json.loads((Path(__file__).resolve().parents[1] / "rules_data.json").read_text(encoding="utf-8"))
RAW_TREE = DATA["decision_tree"]
FORMS = {"the", "a / an", "no article"}


class GateZeroTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def assertGate(self, text, article, source=None):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} should match at Gate 0")
        self.assertEqual(analysis["result"]["article"], article, f"wrong form for {text!r}")
        self.assertTrue(analysis["result"]["rule_ref"], f"{text!r} must cite a rule")
        if source:
            self.assertEqual(analysis["source"], source)

    def test_fixed_expressions_resolve_to_a_form(self):
        self.assertGate("at night", "no article", "fixed_expression")
        self.assertGate("in the end", "the", "fixed_expression")
        self.assertGate("twice a week", "a / an", "fixed_expression")
        self.assertGate("go to school", "no article", "fixed_expression")
        self.assertGate("during the week", "the", "fixed_expression")

    def test_no_fixed_expression_returns_a_group_list(self):
        """The old outFixed leaf printed all three groups and named no form."""
        for phrase in DATA["fixed_expressions"]:
            entry = DATA["fixed_expressions"][phrase]
            self.assertIn(entry["article"], FORMS, f"{phrase!r} resolves to no form")

    def test_proper_nouns(self):
        self.assertGate("the Netherlands", "the")
        analysis = self.logic.analyze_input("Madrid")
        self.assertEqual(analysis["mode"], "question", "Madrid should fall through to the tree")

    def test_noun_with_classifying_number(self):
        self.assertGate("Page 42", "no article", "noun_number")
        self.assertGate("Platform 9", "no article", "noun_number")

    def test_nationality_adjective(self):
        self.assertGate("the French", "the", "nationality")

    def test_noun_adjunct_defers_to_second_noun(self):
        analysis = self.logic.analyze_input("bus station")
        self.assertIsNotNone(analysis["note"], "a noun-noun pair should explain itself")
        self.assertIn("second", analysis["note"].lower())

    def test_place_activity_collision(self):
        """the mall walks the tree; at school is caught by Gate 0."""
        self.assertGate("at school", "no article", "fixed_expression")
        self.assertEqual(self.logic.analyze_input("the mall")["mode"], "question")

    def test_every_gate_zero_rule_carries_its_own_article(self):
        """No Gate 0 branch may hardcode a form: editing the JSON must be enough."""
        for section in ("proper_noun_the", "nationality_the"):
            self.assertIn("article", DATA[section], f"{section} does not name its article")
            self.assertIn(DATA[section]["article"], FORMS)
            self.assertTrue(DATA[section]["rule_ref"])

    def test_proper_noun_article_is_read_from_the_data(self):
        """Flip the value in memory; the answer must follow it."""
        import rules

        original = rules.PROPER_NOUN_THE["article"]
        try:
            rules.PROPER_NOUN_THE["article"] = "no article"
            flipped = ArticleLogic().analyze_input("the Nile")
            self.assertEqual(flipped["result"]["article"], "no article")
        finally:
            rules.PROPER_NOUN_THE["article"] = original
        self.assertEqual(ArticleLogic().analyze_input("the Nile")["result"]["article"], original)

    def test_all_49_original_lookup_entries_survive(self):
        original = json.loads(
            (Path(__file__).resolve().parents[1] / "rules_data.classic.json").read_text(encoding="utf-8")
        )["lookup_table"]
        self.assertEqual(len(original), 49)
        corrections = DATA["lookup_ref_corrections"]
        for key, entry in original.items():
            self.assertIn(key, DATA["lookup_table"], f"lost lookup entry {key!r}")
            kept = DATA["lookup_table"][key]
            self.assertEqual(kept["article"], entry["article"], f"{key!r} changed article")
            if key in corrections:
                # A deliberate, recorded fix - not drift.
                self.assertEqual(corrections[key]["was"], entry["rule_ref"])
                self.assertEqual(corrections[key]["now"], kept["rule_ref"])
            else:
                self.assertEqual(kept["rule_ref"], entry["rule_ref"], f"{key!r} ref drifted")

    def test_corrected_lookup_refs_are_all_the_same_misfiling(self):
        """Only the 9.2.1 -> 9.2.2 fix is allowed to change an inherited ref."""
        for key, fix in DATA["lookup_ref_corrections"].items():
            self.assertEqual((fix["was"], fix["now"]), ("9.2.1", "9.2.2"), key)
            self.assertEqual(DATA["lookup_table"][key]["article"], "the", key)


class CitationTests(unittest.TestCase):
    """Every rule_ref must name a real section of the source book.

    The previous build stamped all 94 fixed expressions with 7.5, which is the
    Illnesses section, and pointed the proper-noun rule at 9.2.1, which is the
    'No article' subsection. Both passed the old test, because it only checked
    that a reference was present.
    """

    def refs(self):
        found = []
        for phrase, entry in DATA["fixed_expressions"].items():
            found.append(("fixed:" + phrase, entry["rule_ref"]))
        for node_id, node in RAW_TREE.items():
            if node.get("rule_ref"):
                found.append(("tree:" + node_id, node["rule_ref"]))
        for key in ("proper_noun_the", "nationality_the"):
            found.append((key, DATA[key]["rule_ref"]))
        for key, pattern in DATA["patterns"].items():
            found.append(("pattern:" + key, pattern["rule_ref"]))
        found.append(("determiners.some_any", DATA["determiners"]["some_any_rule_ref"]))
        found.append(("phonetics", DATA["phonetics"]["rule_ref"]))
        return found

    def test_every_reference_names_a_real_section(self):
        sections = DATA["source_sections"]
        for where, ref in self.refs():
            self.assertIn(ref, sections, f"{where} cites {ref!r}, which is not a section")

    def test_fixed_expressions_are_not_all_one_section(self):
        refs = {e["rule_ref"] for e in DATA["fixed_expressions"].values()}
        self.assertGreater(len(refs), 5, "idioms from many families share one reference")
        self.assertNotIn("7.5", refs, "7.5 is Illnesses, not fixed expressions")

    def test_proper_nouns_cite_the_the_subsection(self):
        self.assertEqual(DATA["proper_noun_the"]["rule_ref"], "9.2.2")
        self.assertIn("The", DATA["source_sections"]["9.2.2"])
        self.assertIn("No article", DATA["source_sections"]["9.2.1"])


class DeterminerGateTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def test_determiners_block_rather_than_return_zero(self):
        for phrase in ["my book", "this book", "those cars", "each student",
                       "every student", "either answer", "some water",
                       "any questions", "no reason", "Sarah's car"]:
            analysis = self.logic.analyze_input(phrase)
            self.assertEqual(analysis["mode"], "lookup", f"{phrase!r} reached the tree")
            self.assertEqual(analysis["result"]["article"], "no article needed",
                             f"{phrase!r} did not report a blocked slot")
            self.assertTrue(analysis["source"].startswith("determiner:"))

    def test_blocked_is_distinct_from_zero(self):
        blocked = self.logic.analyze_input("my book")["result"]["article"]
        zero = self.logic.analyze_input("at school")["result"]["article"]
        self.assertNotEqual(blocked, zero)

    def test_an_ordinary_article_phrase_is_not_blocked(self):
        self.assertEqual(self.logic.analyze_input("a book")["mode"], "question")


class ProperNounPrecisionTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def test_keywords_do_not_fire_outside_a_name(self):
        for phrase in ["We booked a hotel room", "A storm crossed the desert",
                       "I drank a cup of coffee", "a hotel", "the desert",
                       "I read the post", "we swam in the sea"]:
            analysis = self.logic.analyze_input(phrase)
            self.assertNotEqual(analysis.get("source"), "proper_noun",
                                f"{phrase!r} was treated as a proper name")

    def test_real_names_still_match(self):
        for phrase in ["the Netherlands", "the Nile", "the Nile River", "the Alps",
                       "the Sahara", "the Guardian", "the Republic of Ireland",
                       "the Mediterranean", "the United Kingdom"]:
            analysis = self.logic.analyze_input(phrase)
            self.assertEqual(analysis["mode"], "lookup", f"{phrase!r} stopped matching")
            self.assertEqual(analysis["result"]["article"], "the")


class PhoneticArticleTests(unittest.TestCase):
    def test_vowel_letter_consonant_sound(self):
        for word in ["university", "European", "unit", "useful", "one", "unicorn"]:
            self.assertEqual(choose_a_or_an(word), "a", f"expected 'a {word}'")

    def test_consonant_letter_vowel_sound(self):
        for word in ["hour", "honest", "heir", "honour"]:
            self.assertEqual(choose_a_or_an(word), "an", f"expected 'an {word}'")

    def test_initialisms_use_the_letter_name(self):
        self.assertEqual(choose_a_or_an("MBA"), "an")
        self.assertEqual(choose_a_or_an("FBI"), "an")
        self.assertEqual(choose_a_or_an("X-ray"), "an")
        self.assertEqual(choose_a_or_an("UFO"), "a")
        self.assertEqual(choose_a_or_an("BBC"), "a")

    def test_word_acronyms_follow_the_word(self):
        self.assertEqual(choose_a_or_an("NASA"), "a")

    def test_ordinary_words_still_work(self):
        self.assertEqual(choose_a_or_an("apple"), "an")
        self.assertEqual(choose_a_or_an("dog"), "a")
        self.assertEqual(choose_a_or_an("umbrella"), "an")


class TreeIntegrityTests(unittest.TestCase):
    def test_every_edge_points_at_a_real_node(self):
        for node_id, node in RAW_TREE.items():
            for opt in node.get("opts", []):
                self.assertIn(opt["go"], RAW_TREE, f"{node_id} -> {opt['go']} is dangling")

    def test_every_leaf_names_a_form_and_cites_a_rule(self):
        for node_id, node in RAW_TREE.items():
            if "out" in node:
                self.assertIn(node["out"], {"the", "an", "zero"}, f"{node_id} has no form")
                self.assertTrue(node.get("rule_ref"), f"{node_id} cites no rule")

    def test_every_node_is_reachable_from_the_entry(self):
        seen, stack = set(), [ENTRY_NODE]
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            for opt in RAW_TREE[node_id].get("opts", []):
                stack.append(opt["go"])
        self.assertEqual(set(RAW_TREE) - seen, set(), "unreachable nodes")

    def test_no_leaf_is_a_dead_end(self):
        """Every terminal must be an answer, not an instruction to start over."""
        for node_id, node in RAW_TREE.items():
            if "opts" not in node:
                self.assertIn("out", node, f"{node_id} terminates without a form")

    def test_scripted_traces_land_where_they_claim(self):
        expected = {
            "Madrid": "outPropZero",
            "Dogs are loyal": "outGenZeroPl",
            "Life is hard": "outGenZeroNc",
            "the book I lent you": "out4a",
            "the mall": "out4f",
            "the government": "out4g",
            "I need a pen": "out5a",
            "We need water": "out5zNc",
        }
        for trace in DATA["traces"]:
            path = trace.get("path")
            if not path:
                continue
            node_id = ENTRY_NODE
            for index in path:
                node_id = RAW_TREE[node_id]["opts"][index]["go"]
            self.assertIn("out", RAW_TREE[node_id], f"{trace['p']} did not reach a form")
            if trace["p"] in expected:
                self.assertEqual(node_id, expected[trace["p"]], f"{trace['p']} landed on {node_id}")

    def test_gate_zero_traces_actually_hit_gate_zero(self):
        """Chips without a path must be resolved by Gate 0, or they render nothing."""
        logic = ArticleLogic()
        for trace in DATA["traces"]:
            if trace.get("path"):
                continue
            analysis = logic.analyze_input(trace["p"])
            if trace["p"] == "bus station":
                continue  # noun adjunct: explains itself, then walks the tree
            self.assertEqual(analysis["mode"], "lookup", f"{trace['p']!r} missed Gate 0")

    def test_traces_with_a_path_must_miss_gate_zero(self):
        """Otherwise Gate 0 answers first and the scripted walk never runs."""
        logic = ArticleLogic()
        for trace in DATA["traces"]:
            if not trace.get("path"):
                continue
            analysis = logic.analyze_input(trace["p"])
            self.assertEqual(analysis["mode"], "question", f"{trace['p']!r} is shadowed by Gate 0")


if __name__ == "__main__":
    unittest.main()
