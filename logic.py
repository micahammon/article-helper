# logic.py
# This file contains the "engine" that interacts with the rules.
# It manages the state of the decision-making process.

# Import standard library helpers
import re
import string

# Import the data structures from our rules file
from rules import (
    CATEGORIES,
    DECISION_TREE,
    DETERMINER_CONFLICT,
    DETERMINERS,
    ENTRY_NODE,
    FIXED_EXPRESSIONS,
    LOOKUP_TABLE,
    NATIONALITY_THE,
    PATTERNS,
    PHONETICS,
    PROPER_NOUN_THE,
    TIME_WORDS,
)

WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")

_NOUN_NUMBER_RE = re.compile(PATTERNS["noun_number"]["regex"], re.IGNORECASE)


def _normalize_noun(noun):
    """Return a canonical form of ``noun`` for lookup-table comparisons."""
    if noun is None:
        return ""

    normalized = str(noun).strip()
    normalized = re.sub(r"^(?:the|an|a)\s+", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.translate(str.maketrans("", "", string.punctuation))
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized.lower()


def _tokenize_words(text):
    """Return lowercase word tokens from free-form user text."""
    if text is None:
        return []
    return [token.lower() for token in WORD_PATTERN.findall(str(text))]


def _find_phrase(tokens, table):
    """
    Find the longest phrase in ``tokens`` that exists as a key of ``table``.
    Returns:
        tuple[str, int, int] | None: (matched_key, start_index, end_index_exclusive)
    """
    if not tokens:
        return None

    max_window = min(5, len(tokens))
    for window_size in range(max_window, 0, -1):
        for start_index in range(0, len(tokens) - window_size + 1):
            end_index = start_index + window_size
            candidate = " ".join(tokens[start_index:end_index])
            if candidate in table:
                return candidate, start_index, end_index
    return None


def _find_lookup_phrase(tokens):
    """Backwards-compatible helper: longest phrase present in the lookup table."""
    return _find_phrase(tokens, LOOKUP_TABLE)


def _infer_focus_noun(tokens):
    """Infer a focus noun from free-form text when no lookup phrase matches."""
    if not tokens:
        return ""

    determiners = {"a", "an", "the"}
    for index, token in enumerate(tokens[:-1]):
        if token in determiners:
            candidate = tokens[index + 1]
            if candidate not in determiners:
                return candidate

    stop_words = {
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
        "my", "your", "his", "our", "their", "am", "is", "are", "was", "were", "be",
        "been", "being", "do", "does", "did", "have", "has", "had", "go", "goes", "went",
        "come", "came", "arrive", "arrived", "buy", "bought", "see", "saw", "like", "use",
        "at", "in", "on", "to", "for", "from", "with", "by", "of", "and", "or", "but",
        "this", "that", "these", "those", "today", "tomorrow", "yesterday", "now", "then",
    }

    filtered = [token for token in tokens if token not in determiners and token not in stop_words]
    if filtered:
        return filtered[-1]

    return ""


#: words that end the search for a determiner sitting in front of a noun
_LOOKBACK_BOUNDARY = {
    "on", "in", "at", "to", "by", "for", "of", "with", "from", "into", "onto",
    "about", "over", "under", "and", "or", "but", "that", "who", "which", "than",
}
_LOOKBACK_LIMIT = 4


def _determiner_before(tokens, start, determiner_words):
    """
    The determiner governing a noun, looking past any adjectives in between.

    Checking only the immediately preceding token misses `a lovely dinner`,
    where an adjective hides the article that decides the reading.
    """
    index = start - 1
    steps = 0
    while index >= 0 and steps < _LOOKBACK_LIMIT:
        token = tokens[index]
        if token in determiner_words:
            return token
        if token in _LOOKBACK_BOUNDARY:
            return None
        index -= 1
        steps += 1
    return None


def _find_in(tokens, words):
    """The longest listed phrase present in the tokens, if any."""
    for size in range(min(3, len(tokens)), 0, -1):
        for start in range(0, len(tokens) - size + 1):
            candidate = " ".join(tokens[start:start + size])
            if candidate in words:
                return candidate
    return None


def _span_of(tokens, phrase):
    """Where a normalized phrase sits in the token list, if it does."""
    parts = phrase.split()
    for start in range(0, len(tokens) - len(parts) + 1):
        if tokens[start:start + len(parts)] == parts:
            return start, start + len(parts)
    return 0, None


def _result(article, explanation, rule_ref):
    return {"article": article, "explanation": explanation, "rule_ref": rule_ref}


def _cased_tokens(text):
    """Word tokens with their original capitalisation preserved."""
    if text is None:
        return []
    return WORD_PATTERN.findall(str(text))


def _is_capitalised(token):
    return bool(token) and token[0].isupper()


def choose_a_or_an(word):
    """
    Pick ``a`` or ``an`` by the sound the word starts with, not the letter.

    Spelling alone gives "an university" and "a hour"; the rules and exception
    lists live in PHONETICS so they can be corrected without touching code.
    """
    if not word:
        return "a"

    raw = str(word).strip()
    bare = raw.strip(string.punctuation)
    if not bare:
        return "a"
    low = bare.lower()

    # An acronym pronounced as a word follows the word, not its letters.
    if low in PHONETICS["word_acronyms"]["words"]:
        return "an" if low[0] in "aeiou" else "a"

    # Read as letters when it opens with a run of capitals ("MBA", "FBI"), or
    # with a single capital that is not the start of an ordinary word ("X-ray").
    leading_caps = re.match(r"^[A-Z]+", bare)
    if leading_caps:
        run = leading_caps.group(0)
        rest = bare[len(run):]
        if len(run) > 1 or not rest[:1].islower():
            vowel_letters = PHONETICS["initialisms"]["vowel_sounding_letters"]
            return "an" if run[0] in vowel_letters else "a"

    consonant_sound = PHONETICS["vowel_letter_consonant_sound"]
    if low in consonant_sound["words"]:
        return consonant_sound["article"]
    for prefix in consonant_sound["prefixes"]:
        if low.startswith(prefix):
            return consonant_sound["article"]

    vowel_sound = PHONETICS["consonant_letter_vowel_sound"]
    if low in vowel_sound["words"]:
        return vowel_sound["article"]
    for prefix in vowel_sound["prefixes"]:
        if low.startswith(prefix):
            return vowel_sound["article"]

    return "an" if low[0] in "aeiou" else "a"


class ArticleLogic:
    """
    Manages the logic flow for determining the correct English article.
    It holds the current state of the user's path through the decision tree.
    """

    def __init__(self):
        """Initializes the logic controller."""
        self.current_node_id = ENTRY_NODE

    def reset(self):
        """Resets the logic to the beginning of the decision tree."""
        self.current_node_id = ENTRY_NODE

    def check_lookup_table(self, noun):
        """
        See if the noun is a special case in our LOOKUP_TABLE.
        Args:
            noun (str): The raw user-provided noun or phrase.
        Returns:
            dict: The result dictionary if found, otherwise None.
        """
        normalized = _normalize_noun(noun)
        if not normalized:
            return None

        return LOOKUP_TABLE.get(normalized)

    def _lookup_result(self, key, tokens, span):
        """
        Answer from the lookup table, but only where the entry's fixed sense
        actually holds. Two guards, in order:

        1. A determiner already in front of the noun that disagrees with the
           entry's article means the writer is using the other sense
           (`I bought a piano`, `the history of art`).
        2. The entry's own `conditions` - a required construction, a required
           preceding word, or a following word that voids the fixed sense.

        Neither guard guesses: both hand back `context_required`, which shows
        the fixed sense and its contrast and then defers to the questions.
        """
        entry = dict(LOOKUP_TABLE[key])
        conditions = entry.get("conditions")
        start, end = span
        previous = tokens[start - 1] if start > 0 else None
        following = tokens[end] if end is not None and end < len(tokens) else None

        def deferred(reason, why):
            result = {
                # a string, not None: app.py calls .startswith on this
                "article": "it depends",
                "result": "context_required",
                "reason": reason,
                "fixed_sense": {"article": entry["article"],
                                "explanation": entry["explanation"],
                                "rule_ref": entry["rule_ref"]},
                "explanation": why,
                "rule_ref": (conditions or {}).get("contrast_rule_ref") or entry["rule_ref"],
            }
            if conditions:
                result["sense"] = conditions.get("sense")
                result["contrast"] = conditions.get("contrast")
                result["examples"] = conditions.get("examples", [])
            return {"focus_noun": key, "result": result, "source": "context_required"}

        # 1. A determiner in front of the noun, looking past any adjectives.
        forms = DETERMINER_CONFLICT["determiner_forms"]
        governing_words = set(forms)
        for _words in DETERMINERS["groups"].values():
            governing_words.update(_words)
        governing = _determiner_before(tokens, start, governing_words)

        if governing:
            for group, words in DETERMINERS["groups"].items():
                if governing in words:
                    return {
                        "focus_noun": key,
                        "result": _result(DETERMINERS["article"],
                                          DETERMINERS["explanation"],
                                          DETERMINERS["some_any_rule_ref"]
                                          if group == "some_any" else DETERMINERS["rule_ref"]),
                        "source": "determiner:" + group,
                    }
            if governing in forms and forms[governing] != entry["article"]:
                return deferred("determiner_conflict",
                                DETERMINER_CONFLICT["explanation"])

        # 2. The entry's own conditions.
        if conditions:
            if "requires_prev" in conditions and previous not in conditions["requires_prev"]:
                return deferred("missing_required_word", conditions["contrast"])
            if "blocked_by_next" in conditions and following in conditions["blocked_by_next"]:
                return deferred("blocked_by_following_word", conditions["contrast"])
            if "requires_any" in conditions and not set(tokens) & set(conditions["requires_any"]):
                return deferred("missing_required_word", conditions["contrast"])

        entry.pop("conditions", None)
        # `note` is informational: it rides along with a successful answer
        # rather than changing it (see the sports entries).
        return {"focus_noun": key, "result": entry, "source": "lookup"}

    def check_time_words(self, normalized, tokens):
        """Months, days, holidays, seasons, historical periods, and the
        date / year / decade / century patterns of Part 6.2."""
        for name, pattern in TIME_WORDS["patterns"].items():
            if re.search(pattern["regex"], normalized, re.IGNORECASE):
                return {
                    "focus_noun": normalized,
                    "result": _result(pattern["article"], pattern["explanation"],
                                      pattern["rule_ref"]),
                    "source": "time_words:" + name,
                }

        for name, group in TIME_WORDS["groups"].items():
            key = normalized if normalized in group["words"] else _find_in(tokens, group["words"])
            if key:
                return {
                    "focus_noun": key,
                    "result": _result(group["article"], group["explanation"],
                                      group["rule_ref"]),
                    "source": "time_words:" + name,
                    "unusual": TIME_WORDS["unusual"],
                }
        return None

    def check_categories(self, normalized, tokens):
        """Languages, meals and sports - productive rules, not word lists."""
        for name, category in CATEGORIES.items():
            key = normalized if normalized in category["words"] else _find_in(tokens, category["words"])
            if key:
                return {
                    "focus_noun": key,
                    "result": _result(category["article"], category["explanation"],
                                      category["rule_ref"]),
                    "source": "category:" + name,
                    "unusual": category["unusual"],
                }
        return None

    def check_determiner(self, text):
        """
        Is the article slot already filled? ``my book``, ``this book``,
        ``each student`` and ``some water`` admit no article at all, which is a
        different answer from "no article" - and the tree has no way to say so.
        """
        tokens = _tokenize_words(text)
        if not tokens:
            return None

        first = tokens[0]
        for group, words in DETERMINERS["groups"].items():
            if first in words:
                ref = (DETERMINERS["some_any_rule_ref"]
                       if group == "some_any" else DETERMINERS["rule_ref"])
                return {
                    "focus_noun": " ".join(tokens[1:]) or first,
                    "result": _result(DETERMINERS["article"],
                                      DETERMINERS["explanation"], ref),
                    "source": "determiner:" + group,
                }

        # A possessive 's fills the same slot: "Sarah's car".
        if re.match(r"^\s*\S+['’]s\s+\S+", str(text or "")):
            return {
                "focus_noun": " ".join(tokens[1:]) or tokens[0],
                "result": _result(DETERMINERS["article"],
                                  DETERMINERS["explanation"], DETERMINERS["rule_ref"]),
                "source": "determiner:possessive",
            }

        return None

    def _is_the_taking_name(self, text, normalized, tokens):
        """
        A the-taking name, checked conservatively.

        The previous version matched a bare keyword anywhere in the input, so
        "We booked a hotel room" and "A storm crossed the desert" both came back
        as proper names, and any capitalised sentence containing "of" matched
        too ("I drank a cup of coffee"). A keyword now only counts inside a
        capitalised name, and an of-construction needs a capital on each side.
        """
        named = PROPER_NOUN_THE["named"]
        if normalized in named:
            return True

        cased = _cased_tokens(text)
        lowered = [t.lower() for t in cased]

        # A listed name, but only where it is actually capitalised.
        for index, token in enumerate(lowered):
            if token in named and _is_capitalised(cased[index]):
                return True

        # A keyword only counts as part of a capitalised name: "the Nile River",
        # "the Red Sea" - not "a storm crossed the desert".
        for index, token in enumerate(lowered):
            if token not in PROPER_NOUN_THE["keywords"]:
                continue
            if not _is_capitalised(cased[index]):
                continue
            neighbours = []
            if index > 0:
                neighbours.append(cased[index - 1])
            if index + 1 < len(cased):
                neighbours.append(cased[index + 1])
            if any(_is_capitalised(n) for n in neighbours):
                return True

        # An of-construction needs a capitalised word on each side:
        # "the Republic of Ireland", not "a cup of coffee".
        if PROPER_NOUN_THE.get("contains_of"):
            for index, token in enumerate(lowered):
                if token != "of" or index == 0 or index + 1 >= len(cased):
                    continue
                if _is_capitalised(cased[index - 1]) and _is_capitalised(cased[index + 1]):
                    return True

        return False

    def check_gate_zero(self, text):
        """
        Gate 0: everything that can be decided from the noun alone, before any
        question is asked. Checked in precedence order, first match wins.

        Returns:
            dict | None: {"focus_noun", "result", "source"} when something matched.
        """
        normalized = _normalize_noun(text)
        tokens = _tokenize_words(text)
        if not normalized and not tokens:
            return None

        # 0. The article slot may already be taken. A possessive, demonstrative
        #    or quantifier leaves no room for an article, so this is not a
        #    zero-article answer - the question does not arise.
        blocked = self.check_determiner(text)
        if blocked:
            return blocked

        # 1. Fixed expressions outrank every rule below them.
        match = _find_phrase(tokens, FIXED_EXPRESSIONS)
        key = match[0] if match else (normalized if normalized in FIXED_EXPRESSIONS else None)
        if key:
            entry = FIXED_EXPRESSIONS[key]
            return {
                "focus_noun": key,
                "result": _result(entry["article"], entry["explanation"], entry["rule_ref"]),
                "source": "fixed_expression",
            }

        # 2. A noun followed by a classifying number or letter.
        if _NOUN_NUMBER_RE.match(normalized):
            pattern = PATTERNS["noun_number"]
            return {
                "focus_noun": normalized,
                "result": _result(pattern["article"], pattern["explanation"], pattern["rule_ref"]),
                "source": "noun_number",
            }

        # 3. The lookup table: exact normalized form, then longest phrase.
        #    Both go through the same conditions, so a noun that is only fixed
        #    inside a particular construction cannot answer outside it.
        if normalized in LOOKUP_TABLE:
            span = _span_of(tokens, normalized)
            return self._lookup_result(normalized, tokens, span)
        phrase_match = _find_lookup_phrase(tokens)
        if phrase_match:
            matched, start, end = phrase_match
            return self._lookup_result(matched, tokens, (start, end))

        # 3.5 Time words: months, days, holidays, seasons, periods, and the
        #     date / year / decade / century patterns.
        time_hit = self.check_time_words(normalized, tokens)
        if time_hit:
            return time_hit

        # 4. Nationality adjective standing for a whole people. This is the
        #    "the + adjective" construction, so it needs the article in front:
        #    without it, `Spanish` is a language, not a people.
        requires_prev = NATIONALITY_THE.get("requires_prev")
        span = _span_of(tokens, normalized)
        preceded_by_the = (span[1] is not None and span[0] > 0
                           and tokens[span[0] - 1] in (requires_prev or []))
        if normalized in NATIONALITY_THE["examples"] and (not requires_prev or preceded_by_the):
            return {
                "focus_noun": normalized,
                "result": _result(
                    NATIONALITY_THE["article"],
                    NATIONALITY_THE["explanation"],
                    NATIONALITY_THE["rule_ref"],
                ),
                "source": "nationality",
            }

        # 4.5 Productive categories: languages, meals, sports. These are rules
        #     about a category, not a closed vocabulary, so `rugby`, `Arabic`
        #     and `brunch` are covered without being listed individually.
        category_hit = self.check_categories(normalized, tokens)
        if category_hit:
            return category_hit

        # 5. Names in the the-taking class.
        if self._is_the_taking_name(text, normalized, tokens):
            return {
                "focus_noun": normalized,
                "result": _result(
                    PROPER_NOUN_THE["article"],
                    PROPER_NOUN_THE["explanation"],
                    PROPER_NOUN_THE["rule_ref"],
                ),
                "source": "proper_noun",
            }

        return None

    def analyze_input(self, text):
        """
        Analyze free-form user input and prepare the next step.
        Returns:
            dict: {
                "mode": "lookup" | "question",
                "focus_noun": str,
                "result": dict | None,
                "source": str | None,
                "note": str | None
            }
        """
        self.reset()

        gate_zero = self.check_gate_zero(text)
        if gate_zero:
            answer = {
                "mode": "lookup",
                "focus_noun": gate_zero["focus_noun"],
                "result": gate_zero["result"],
                "source": gate_zero["source"],
                "note": None,
            }
            # the "unusual use" contrast (6.1.4 / 6.2.8) rides along with the
            # answer rather than replacing it
            if "unusual" in gate_zero:
                answer["unusual"] = gate_zero["unusual"]
            return answer

        tokens = _tokenize_words(_normalize_noun(text))
        note = None

        # A two-noun pair: the first noun acts like an adjective, so the second
        # one decides. Re-run Gate 0 on it before falling through to the tree.
        if len(tokens) == 2:
            second = tokens[1]
            second_hit = self.check_gate_zero(second)
            if second_hit:
                return {
                    "mode": "lookup",
                    "focus_noun": second_hit["focus_noun"],
                    "result": second_hit["result"],
                    "source": "noun_adjunct",
                    "note": PATTERNS["noun_adjunct"]["explanation"],
                }
            note = PATTERNS["noun_adjunct"]["explanation"]

        return {
            "mode": "question",
            "focus_noun": _infer_focus_noun(_tokenize_words(text)),
            "result": None,
            "source": None,
            "note": note,
        }

    def get_current_node(self):
        """
        Retrieves the data for the current node in the decision tree.
        Returns:
            dict: The dictionary of the current node.
        """
        return DECISION_TREE[self.current_node_id]

    def process_answer(self, selected_option_text):
        """
        Processes the user's answer and moves to the next node in the tree.
        Args:
            selected_option_text (str): The text from the button the user clicked.
        Returns:
            dict: The data for the *next* node in the decision tree.
        """
        # Find the current node
        current_node = self.get_current_node()

        # Look up the next node's ID based on the user's choice
        next_node_id = current_node["options"][selected_option_text]

        # Update the state to the new node
        self.current_node_id = next_node_id

        # Return the data for the new node
        return self.get_current_node()


# --- This section is for testing our logic directly ---
def test_logic():
    """A simple text-based simulation to ensure our logic works."""
    print("--- Testing ArticleLogic ---")

    print("\n[Test 1: Gate 0]")
    logic_engine = ArticleLogic()
    samples = ["USA", "the USA", "an opera", "at school", "during the week", "Page 42", "the French"]
    for sample in samples:
        analysis = logic_engine.analyze_input(sample)
        if analysis["mode"] == "lookup":
            print(f"'{sample}': {analysis['result']['article']}  [{analysis['source']}]")
        else:
            print(f"'{sample}': no Gate 0 match, starting tree...")

    print("\n[Test 2: Decision Tree Walkthrough]")
    logic_engine.reset()

    current_node = logic_engine.get_current_node()
    print(f"Q: {current_node['question']}")
    options = list(current_node["options"].keys())
    print(f"Options: {options}")

    user_choice = options[0]
    print(f"\nUser chooses: '{user_choice}'")
    current_node = logic_engine.process_answer(user_choice)

    if "question" in current_node:
        print(f"Q: {current_node['question']}")
        print(f"Options: {list(current_node['options'].keys())}")
    elif "article" in current_node:
        print("\nFinal Result Reached!")
        print(f"  -> Article: {current_node['article']}")
        print(f"  -> Explanation: {current_node['explanation']}")


if __name__ == "__main__":
    # This block runs ONLY when you execute `python logic.py` directly.
    # It allows us to test our logic before building the GUI.
    test_logic()
