"""Utilities for loading article helper rules from a shared JSON file.

``rules_data.json`` is written for the browser first: its decision-tree nodes use
``q`` / ``opts`` for questions and ``out`` / ``why`` for leaves, and the prose
carries light HTML for the web page.

The Tkinter app predates that shape and expects ``question`` / ``options`` /
``article`` / ``explanation`` with plain text. Rather than rewrite the GUI, this
module adapts the new nodes into the old shape, so both front-ends read the same
file and stay in sync.
"""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from pathlib import Path

GUIDANCE_NODE_TYPE = "guidance"

_TAG_RE = re.compile(r"<[^>]+>")
_ARTICLE_FOR_FORM = {"the": "the", "an": "a / an", "zero": "no article"}


def _strip_tags(text):
    """Turn the page's light HTML into plain text for the desktop app."""
    if not text:
        return ""
    cleaned = _TAG_RE.sub("", str(text))
    cleaned = cleaned.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", cleaned).strip()


def _adapt_node(node):
    """Return one decision-tree node in the shape the Tkinter app expects."""
    adapted = dict(node)

    if "opts" in node:
        options = OrderedDict()
        for opt in node["opts"]:
            label = _strip_tags(opt.get("label"))
            example = _strip_tags(opt.get("ex"))
            if example:
                label = "{0}  ({1})".format(label, example)
            options[label] = opt["go"]

        adapted["question"] = _strip_tags(node.get("q"))
        adapted["details"] = _strip_tags(node.get("note"))
        adapted["options"] = options
        if node.get("warn"):
            adapted["warning"] = _strip_tags(node["warn"])

    elif "out" in node:
        adapted["article"] = _ARTICLE_FOR_FORM.get(node["out"], node["out"])
        adapted["explanation"] = _strip_tags(node.get("why"))
        adapted["category"] = _strip_tags(node.get("cat"))

    return adapted


def _adapt_tree(decision_tree):
    return OrderedDict((key, _adapt_node(node)) for key, node in decision_tree.items())


_DATA_PATH = Path(__file__).resolve().with_name("rules_data.json")

with _DATA_PATH.open(encoding="utf-8") as data_file:
    _rules_data = json.load(data_file)

LOOKUP_TABLE = _rules_data["lookup_table"]
FIXED_EXPRESSIONS = _rules_data["fixed_expressions"]
PROPER_NOUN_THE = _rules_data["proper_noun_the"]
NATIONALITY_THE = _rules_data["nationality_the"]
DETERMINERS = _rules_data["determiners"]
DETERMINER_CONFLICT = _rules_data["determiner_conflict"]
PHONETICS = _rules_data["phonetics"]
CATEGORIES = _rules_data["categories"]
CONSTRUCTIONS = _rules_data["constructions"]
TIME_WORDS = _rules_data["time_words"]
SOURCE_SECTIONS = _rules_data["source_sections"]
# What a rule is called when a learner sees it. SOURCE_SECTIONS keeps the
# numbering for us; RULE_NAMES is the half that reaches the screen.
RULE_NAMES = _rules_data["rule_names"]
PATTERNS = _rules_data["patterns"]
FORM_LABELS = _rules_data["form_labels"]
ENTRY_NODE = _rules_data.get("meta", {}).get("entry_node", "q2")
DECISION_TREE = _adapt_tree(_rules_data["decision_tree"])

__all__ = [
    "LOOKUP_TABLE",
    "FIXED_EXPRESSIONS",
    "PROPER_NOUN_THE",
    "NATIONALITY_THE",
    "DETERMINERS",
    "DETERMINER_CONFLICT",
    "PHONETICS",
    "CATEGORIES",
    "CONSTRUCTIONS",
    "TIME_WORDS",
    "SOURCE_SECTIONS",
    "RULE_NAMES",
    "PATTERNS",
    "FORM_LABELS",
    "ENTRY_NODE",
    "DECISION_TREE",
    "GUIDANCE_NODE_TYPE",
]
