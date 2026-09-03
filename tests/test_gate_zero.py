"""Verification suite for the Gate 0 / tree split.

Gate 0 must resolve every fixed expression and listed name to a *specific*
article form. The old failure mode on both sides of this project was a
highest-precedence gate that returned "memorized" or "go and restart" instead of
an answer, so these tests assert that a form always comes back.
"""

import json
import re
import unittest
from pathlib import Path

from logic import ArticleLogic, choose_a_or_an, focus_candidates
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


class ConditionalLookupTests(unittest.TestCase):
    """The lookup table used to answer unconditionally on a word match.

    `I bought a piano` came back as *the*, `They bought a bed` as *no article*,
    and `She studies the history of art` as *no article* - all confidently
    wrong, because the entry's fixed sense did not apply.
    """

    def setUp(self):
        self.logic = ArticleLogic()

    def assertDefers(self, text, reason=None):
        result = self.logic.analyze_input(text)["result"]
        self.assertIsNotNone(result, f"{text!r} produced no result")
        self.assertEqual(result.get("result"), "context_required",
                         f"{text!r} answered {result.get('article')!r} instead of deferring")
        self.assertIn("fixed_sense", result)
        if reason:
            self.assertEqual(result["reason"], reason)
        return result

    def assertAnswers(self, text, article):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} did not answer")
        self.assertEqual(analysis["result"]["article"], article, f"wrong form for {text!r}")

    def test_the_three_reported_failures(self):
        self.assertDefers("I bought a piano", "determiner_conflict")
        self.assertDefers("They bought a bed", "determiner_conflict")
        self.assertDefers("She studies the history of art", "determiner_conflict")

    def test_a_conflicting_article_defers(self):
        for text in ["an opera", "I saw an opera", "a radio", "a cinema near my house"]:
            self.assertDefers(text, "determiner_conflict")

    def test_an_adjective_does_not_hide_the_determiner(self):
        """`a lovely dinner` must still see the `a`."""
        self.assertDefers("We had a lovely dinner", "determiner_conflict")
        self.assertDefers("a beautiful piano", "determiner_conflict")
        self.assertDefers("The lunch they served was cold", "determiner_conflict")

    def test_missing_construction_defers(self):
        self.assertDefers("piano", "missing_required_word")
        self.assertDefers("radio", "missing_required_word")
        self.assertDefers("poor people", "missing_required_word")

    def test_following_word_can_void_the_fixed_sense(self):
        self.assertDefers("music of Bach", "blocked_by_following_word")

    def test_the_fixed_sense_still_answers(self):
        self.assertAnswers("I play piano", "the")
        self.assertAnswers("go to the cinema", "the")
        self.assertAnswers("listen to the radio", "the")
        self.assertAnswers("the elderly", "the")
        self.assertAnswers("tennis", "no article")
        self.assertAnswers("music", "no article")

    def test_unconditional_entries_are_untouched(self):
        for text, article in [("the USA", "the"), ("the sun", "the"),
                              ("the Netherlands", "the"), ("the police", "the"),
                              ("the internet", "the"), ("mount fuji", "no article")]:
            self.assertAnswers(text, article)

    def test_deferred_results_carry_both_readings(self):
        result = self.assertDefers("I bought a piano")
        self.assertEqual(result["fixed_sense"]["article"], "the")
        self.assertTrue(result["fixed_sense"]["explanation"])
        self.assertTrue(result["examples"], "a deferred result should show a contrast")
        self.assertIn(result["rule_ref"], DATA["source_sections"])

    def test_deferred_article_is_a_string(self):
        """app.py calls .startswith on it, so None would crash the desktop app."""
        result = self.assertDefers("I bought a piano")
        self.assertIsInstance(result["article"], str)

    def test_every_condition_is_well_formed(self):
        known = {"sense", "contrast", "examples", "contrast_rule_ref",
                 "requires_any", "requires_prev", "blocked_by_next"}
        conditioned = 0
        for word, entry in DATA["lookup_table"].items():
            cond = entry.get("conditions")
            if not cond:
                continue
            conditioned += 1
            self.assertTrue(set(cond) <= known, f"{word} has unknown keys: {set(cond) - known}")
            self.assertTrue(cond["sense"], word)
            self.assertTrue(cond["contrast"], word)
            self.assertIn(cond["contrast_rule_ref"], DATA["source_sections"], word)
            self.assertTrue(
                any(k in cond for k in ("requires_any", "requires_prev", "blocked_by_next")),
                f"{word} has a condition block that never fires")
        self.assertGreater(conditioned, 15, "most context-sensitive nouns should be conditioned")


class ProductiveCategoryTests(unittest.TestCase):
    """Languages, meals and sports are categories, not word lists.

    Only French, lunch and tennis were listed before, so rugby, Arabic and
    brunch fell through to the questions.
    """

    def setUp(self):
        self.logic = ArticleLogic()

    def assertCategory(self, text, source):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} fell through")
        self.assertEqual(analysis["result"]["article"], "no article", text)
        self.assertEqual(analysis["source"], source, text)

    def test_languages(self):
        for text in ["Arabic", "Swahili", "She speaks Japanese", "They're studying Spanish"]:
            self.assertCategory(text, "category:languages")

    def test_meals(self):
        for text in ["brunch", "supper", "tea"]:
            self.assertCategory(text, "category:meals")

    def test_sports(self):
        for text in ["rugby", "judo", "He plays cricket", "baseball"]:
            self.assertCategory(text, "category:sports")

    def test_nationality_needs_the_in_front(self):
        """`the French` is a people; bare `French` is a language."""
        self.assertEqual(self.logic.analyze_input("the French")["source"], "nationality")
        self.assertEqual(self.logic.analyze_input("the British")["source"], "nationality")
        self.assertEqual(self.logic.analyze_input("French")["source"], "category:languages")
        self.assertEqual(self.logic.analyze_input("She speaks French")["source"],
                         "category:languages")

    def test_categories_carry_the_unusual_use_contrast(self):
        analysis = self.logic.analyze_input("rugby")
        self.assertIn("unusual", analysis)
        self.assertIn("6.1.4", analysis["unusual"])


class TimeWordTests(unittest.TestCase):
    def setUp(self):
        self.logic = ArticleLogic()

    def assertTime(self, text, article, source=None):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} fell through")
        self.assertEqual(analysis["result"]["article"], article, text)
        self.assertIn(analysis["result"]["rule_ref"], DATA["source_sections"])
        if source:
            self.assertEqual(analysis["source"], source, text)

    def test_months_days_holidays(self):
        self.assertTime("in June", "no article", "time_words:months")
        self.assertTime("Mondays", "no article", "time_words:days")
        self.assertTime("Christmas Day", "no article", "time_words:holidays")
        self.assertTime("Ramadan", "no article", "time_words:holidays")

    def test_seasons_allow_either(self):
        self.assertTime("in summer", "either the or no article", "time_words:seasons")

    def test_years_decades_centuries(self):
        self.assertTime("1991", "no article", "time_words:year")
        self.assertTime("the 1960s", "the", "time_words:decade")
        self.assertTime("the eighties", "the", "time_words:decade")
        self.assertTime("the sixteenth century", "the", "time_words:century")

    def test_historical_periods(self):
        self.assertTime("the Renaissance", "the", "time_words:periods")
        self.assertTime("the Middle Ages", "the", "time_words:periods")

    def test_dates_depend_on_the_order(self):
        """Number first takes `the`; number second takes none."""
        self.assertTime("22nd of September", "the", "time_words:date_number_first")
        self.assertTime("November 16th", "no article", "time_words:date_number_second")

    def test_part_of_day_with_a_named_day(self):
        self.assertTime("Wednesday night", "no article", "time_words:day_part")
        # on its own it is the other way round, and stays a fixed expression
        self.assertEqual(self.logic.analyze_input("in the morning")["result"]["article"], "the")

    def test_time_words_carry_the_unusual_use_contrast(self):
        analysis = self.logic.analyze_input("Mondays")
        self.assertIn("unusual", analysis)
        self.assertIn("6.2.8", analysis["unusual"])


class ConstructionTests(unittest.TestCase):
    """Rules where the shape of the phrase decides the article, not the noun."""

    def setUp(self):
        self.logic = ArticleLogic()

    def assertRule(self, text, article, rule_ref, name=None):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} fell through")
        self.assertEqual(analysis["result"]["article"], article, text)
        self.assertEqual(analysis["result"]["rule_ref"], rule_ref, text)
        if name:
            self.assertEqual(analysis["source"], "construction:" + name, text)

    def test_next_last_with_time_expressions(self):
        self.assertRule("next week", "no article", "7.11", "next_last_time_word")
        self.assertRule("last summer", "no article", "7.11", "next_last_time_word")
        self.assertRule("next Tuesday", "no article", "7.11", "next_last_time_word")

    def test_next_last_as_ordinary_adjectives(self):
        """`the next bus` is 2.4.4, not the 7.11 time rule."""
        self.assertRule("the next bus", "the", "2.4.4", "next_last_adjective")
        self.assertRule("the last chocolate", "the", "2.4.4", "next_last_adjective")

    def test_in_the_next_changes_the_meaning(self):
        self.assertRule("in the next year", "the", "7.11", "in_the_next_last")

    def test_next_time_allows_either(self):
        self.assertRule("next time", "either the or no article", "7.11")

    def test_ordinals(self):
        self.assertRule("second prize", "no article", "7.12", "ordinal_prize")
        self.assertRule("first place", "no article", "7.12", "ordinal_prize")
        self.assertRule("the first dress", "the", "7.12", "ordinal_noun")
        self.assertRule("a second cup of coffee", "a / an", "7.12", "a_ordinal_one_more")

    def test_comparative_pairs(self):
        self.assertRule("The sunnier it is, the happier I am", "the", "7.13")
        self.assertRule("The more work you do, the better your result", "the", "7.13")

    def test_most_and_the_most(self):
        self.assertRule("Most people like chocolate", "no article", "7.8", "most_noun")
        self.assertRule("Most of the people in the class", "no article", "7.8", "most_of_the")
        self.assertRule("the most intelligent student", "the", "7.8", "the_most")

    def test_most_is_not_a_blocked_slot(self):
        """7.8 gives `most` its own rule, so it must not be a determiner."""
        self.assertNotIn("most", DATA["determiners"]["groups"]["quantifier"])

    def test_bare_few_and_little(self):
        self.assertRule("few problems", "no article", "7.7", "bare_few_little")
        self.assertRule("little money", "no article", "7.7", "bare_few_little")
        # `a few` keeps its own entry and its own meaning
        self.assertEqual(self.logic.analyze_input("a few")["result"]["article"], "a / an")

    def test_a_an_or_one(self):
        self.assertRule("one of the students", "one", "7.9.1", "one_of_the")
        self.assertRule("a hundred years old", "a / an", "7.9.1", "a_with_large_numbers")

    def test_half(self):
        self.assertRule("half an hour", "no article", "7.9.2", "half_zero")
        self.assertRule("half past four", "no article", "7.9.2", "half_zero")
        self.assertRule("two and a half hours", "a / an", "7.9.2", "and_a_half")

    def test_body_parts_after_certain_verbs(self):
        self.assertRule("She touched him on the arm", "the", "4.7")
        self.assertRule("The criminal shot the policeman in the leg", "the", "4.7")

    def test_peoples_names(self):
        self.assertRule("the Smiths", "the", "9.4.2", "family_surname")
        self.assertRule("A Mr Thompson called for you", "a / an", "9.4.3", "unknown_person")
        self.assertRule("Mr Brown", "no article", "9.4.1", "titled_name")

    def test_an_incidental_construction_does_not_hijack_the_answer(self):
        """`last year` inside a sentence about a country must not win.

        Constructions run in two passes: whole-input matches first, loose
        matches only after the lexical gates.
        """
        analysis = self.logic.analyze_input("They moved to the United Kingdom last year")
        self.assertEqual(analysis["focus_noun"], "united kingdom")
        self.assertEqual(analysis["source"], "lookup")

        analysis = self.logic.analyze_input("I listened to the radio last week")
        self.assertEqual(analysis["source"], "lookup")

    def test_every_construction_is_well_formed(self):
        seen = set()
        for rule in DATA["constructions"]:
            self.assertNotIn(rule["name"], seen, "duplicate construction name")
            seen.add(rule["name"])
            self.assertIn(rule["rule_ref"], DATA["source_sections"], rule["name"])
            self.assertTrue(rule["explanation"], rule["name"])
            self.assertTrue(rule["examples"], rule["name"])
            re.compile(rule["regex"])  # must be a valid pattern


class SentenceFrameTests(unittest.TestCase):
    """2.7, 5.3 and 6.5 describe the shape of a clause, not a noun.

    They are marked `frame`, which puts them in the first pass even when the
    match is partial - otherwise the lexical gates answer first, and
    `There's a post office in my town` comes back as a question about `post`.
    """

    def setUp(self):
        self.logic = ArticleLogic()

    def assertRule(self, text, article, rule_ref, name=None):
        analysis = self.logic.analyze_input(text)
        self.assertEqual(analysis["mode"], "lookup", f"{text!r} fell through")
        self.assertEqual(analysis["result"]["article"], article, text)
        self.assertEqual(analysis["result"]["rule_ref"], rule_ref, text)
        if name:
            self.assertEqual(analysis["source"], "construction:" + name, text)

    def test_there_is_takes_a_singular(self):
        self.assertRule("There's a post office in my town", "a / an", "2.7",
                        "there_is_singular")
        self.assertRule("Is there a bank nearby", "a / an", "2.7", "there_is_singular")

    def test_there_are_takes_a_plural(self):
        """The verb settles it, so this does not have to guess."""
        self.assertRule("There are two train stations in Glasgow", "no article", "2.7",
                        "there_are_plural")
        self.assertRule("There are butterflies in my garden", "no article", "2.7",
                        "there_are_plural")

    def test_there_is_carries_the_uncountable_contrast(self):
        result = self.logic.analyze_input("There's a post office in my town")["result"]
        self.assertIn("uncountable", result["contrast"])

    def test_a_contraction_is_not_a_possessive(self):
        """`There's` is `there is`; only `Sarah's` blocks the slot."""
        self.assertNotEqual(
            self.logic.analyze_input("There's a post office in my town")["source"],
            "determiner:possessive")
        self.assertEqual(self.logic.analyze_input("Sarah's car")["source"],
                         "determiner:possessive")

    def test_exclamations(self):
        self.assertRule("What a beautiful day", "a / an", "5.3", "exclamation_what_a")
        analysis = self.logic.analyze_input("What terrible weather")
        self.assertEqual(analysis["result"]["rule_ref"], "5.3")
        self.assertIn("otherwise no article", analysis["result"]["article"])

    def test_unique_roles(self):
        self.assertRule("Julie was appointed headteacher of our school", "no article",
                        "6.5", "unique_role")
        self.assertRule("She was elected president", "no article", "6.5", "unique_role")
        self.assertRule("He became king in 1781", "no article", "6.5", "unique_role")

    def test_unique_role_allows_a_name_between_verb_and_role(self):
        self.assertRule("We elected Amy director of the committee", "no article", "6.5")

    def test_a_frame_outranks_an_adjunct(self):
        """`as CEO last week` is about the role, not about `last week`."""
        analysis = self.logic.analyze_input("Luke started working as CEO last week")
        self.assertEqual(analysis["source"], "construction:unique_role")

    def test_an_ordinary_job_still_reaches_the_questions(self):
        """`Julie is a headteacher` is 5.2, which the tree handles."""
        self.assertEqual(self.logic.analyze_input("Julie is a headteacher")["mode"],
                         "question")

    def test_frames_do_not_swallow_the_lexical_gates(self):
        for text in ["They moved to the United Kingdom last year",
                     "I listened to the radio last week", "next week", "the Smiths"]:
            analysis = self.logic.analyze_input(text)
            self.assertNotIn(analysis.get("source"),
                             {"construction:there_is_singular",
                              "construction:there_are_plural",
                              "construction:unique_role"}, text)

    def test_frame_rules_are_declared_in_the_data(self):
        frames = {r["name"] for r in DATA["constructions"] if r.get("frame")}
        self.assertEqual(frames, {"there_is_singular", "there_are_plural",
                                  "exclamation_what_a", "exclamation_what",
                                  "unique_role",
                                  # `most` governs its noun phrase, so it
                                  # outranks the lexical gates too
                                  "the_most", "most_of_the", "most_noun"})


class LearnerSentenceTests(unittest.TestCase):
    """Regressions found by tracing real learner sentences (see trace.py).

    All three came from the same blind spot: a gate that works on a bare noun
    phrase behaving badly once the input is a whole sentence.
    """

    def setUp(self):
        self.logic = ArticleLogic()

    def test_a_leading_determiner_does_not_answer_for_a_whole_sentence(self):
        """`My mother is a teacher` is a question about `a teacher`.

        The determiner gate only reads the first word, so on a sentence it was
        reporting a blocked slot for the subject.
        """
        analysis = self.logic.analyze_input("My mother is a teacher.")
        self.assertNotEqual(analysis.get("source"), "determiner:possessive")
        self.assertEqual(analysis["mode"], "question")

        analysis = self.logic.analyze_input("I read my book every night")
        self.assertNotEqual(analysis.get("source"), "determiner:possessive")

    def test_a_bare_noun_phrase_still_blocks(self):
        for phrase, group in [("my book", "possessive"), ("my new book", "possessive"),
                              ("each student", "quantifier"), ("those cars", "demonstrative"),
                              ("some water", "some_any"), ("Sarah's car", "possessive")]:
            analysis = self.logic.analyze_input(phrase)
            self.assertEqual(analysis["source"], "determiner:" + group, phrase)

    def test_most_outranks_the_lexical_gates(self):
        """`The most people think that English is hard` was answered as a language."""
        analysis = self.logic.analyze_input("The most people think that English is hard.")
        self.assertEqual(analysis["source"], "construction:the_most")
        self.assertEqual(analysis["result"]["rule_ref"], "7.8")

    def test_bare_few_matches_mid_sentence(self):
        """The rule was anchored, so it only fired when `few` started the input."""
        analysis = self.logic.analyze_input("I have few friends here.")
        self.assertEqual(analysis["source"], "construction:bare_few_little")
        self.assertEqual(analysis["result"]["article"], "no article")

    def test_a_known_name_beats_the_family_surname_shape(self):
        """`the Netherlands` fits "the + capitalised word + s" as neatly as
        `the Smiths`, and was being answered as a family."""
        for place in ["the Netherlands", "the Alps", "the Philippines", "the Andes"]:
            analysis = self.logic.analyze_input(place)
            self.assertNotEqual(analysis["source"], "construction:family_surname", place)
            self.assertEqual(analysis["result"]["rule_ref"], "9.2.2", place)

        for family in ["the Smiths", "the Blacks"]:
            analysis = self.logic.analyze_input(family)
            self.assertEqual(analysis["source"], "construction:family_surname", family)

    def test_a_few_is_still_the_other_meaning(self):
        """`a few` must not be swallowed by the unanchored bare-few rule."""
        for phrase in ["I have a few friends here.", "I have a little money"]:
            analysis = self.logic.analyze_input(phrase)
            self.assertEqual(analysis["source"], "fixed_expression", phrase)
            self.assertEqual(analysis["result"]["article"], "a / an", phrase)


class FocusTests(unittest.TestCase):
    """The tool has always picked a noun silently.

    In `I have a doubt about the homework` either noun is a fair guess, and
    nothing on the page said which one had been chosen.
    """

    def setUp(self):
        self.logic = ArticleLogic()

    def test_candidates_are_the_plausible_nouns(self):
        analysis = self.logic.analyze_input("I have a doubt about the homework.")
        self.assertEqual([c["word"] for c in analysis["candidates"]],
                         ["doubt", "homework"])

    def test_candidates_skip_function_words_and_verbs(self):
        words = [c["word"] for c in focus_candidates("I bought a piano last week.")]
        self.assertEqual(words, ["piano", "week"])
        self.assertNotIn("bought", words)
        self.assertNotIn("last", words)

    def test_every_answer_reports_its_candidates(self):
        for text in ["at school", "the Netherlands", "my book",
                     "I have a doubt about the homework.", "rugby"]:
            self.assertIn("candidates", self.logic.analyze_input(text), text)

    def test_pinning_changes_the_answer(self):
        text = "We went to the Netherlands in July."
        self.assertEqual(self.logic.analyze_input(text, focus="netherlands")["source"],
                         "lookup")
        self.assertEqual(self.logic.analyze_input(text, focus="july")["source"],
                         "time_words:months")

    def test_pinning_uses_sentence_context_not_just_the_word(self):
        """`piano` alone would defer for a missing verb; here the `a` decides."""
        analysis = self.logic.analyze_input("I bought a piano last week.", focus="piano")
        self.assertEqual(analysis["result"]["result"], "context_required")
        self.assertEqual(analysis["result"]["reason"], "determiner_conflict")

    def test_an_unrelated_construction_does_not_answer_for_a_pinned_noun(self):
        """`last week` must not answer when the learner asked about `piano`."""
        analysis = self.logic.analyze_input("I bought a piano last week.", focus="piano")
        self.assertNotEqual(analysis.get("source"), "construction:next_last_time_word")

    def test_a_frame_still_answers_for_a_noun_inside_it(self):
        """2.7 is a rule about the noun after `there is`."""
        analysis = self.logic.analyze_input("There is a problem with my computer.",
                                            focus="problem")
        self.assertEqual(analysis["source"], "construction:there_is_singular")

    def test_a_construction_reports_what_it_matched(self):
        """Not the whole sentence - the page highlights this."""
        analysis = self.logic.analyze_input("There is a problem with my computer.")
        self.assertEqual(analysis["focus_noun"], "there is")

    def test_pinned_results_are_marked(self):
        analysis = self.logic.analyze_input("I have a doubt about the homework.",
                                            focus="homework")
        self.assertTrue(analysis["pinned"])
        self.assertEqual(analysis["focus_noun"], "homework")
        self.assertFalse(self.logic.analyze_input("rugby")["pinned"])


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
