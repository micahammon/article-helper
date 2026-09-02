"""Trace how a sentence is decided, gate by gate.

Written for reviewing the *wording* the learner sees, so every trace shows
three things: which gates were tried and why each missed, which rule finally
answered, and the exact text rendered on the page.

    python trace.py "I have a doubt about the homework."
    python trace.py --file sentences.txt
    python trace.py --file sentences.txt --out docs/wording-review.md

With no arguments it runs the built-in sample of learner sentences.
"""

from __future__ import annotations

import argparse
import re
import sys

from logic import ArticleLogic, _normalize_noun, _tokenize_words, choose_a_or_an
from rules import (
    CATEGORIES,
    CONSTRUCTIONS,
    DECISION_TREE,
    DETERMINERS,
    ENTRY_NODE,
    FIXED_EXPRESSIONS,
    FORM_LABELS,
    LOOKUP_TABLE,
    NATIONALITY_THE,
    SOURCE_SECTIONS,
    TIME_WORDS,
)

# Typical learner sentences. Several are deliberately wrong in the way the
# tool is meant to catch; others are correct and should be confirmed.
SAMPLE = [
    "I have a doubt about the homework.",
    "The life is difficult.",
    "I go to the school every day.",
    "She plays the football on Saturdays.",
    "I bought a piano last week.",
    "We had a lunch at two o'clock.",
    "My mother is a teacher.",
    "I don't like the coffee.",
    "There is a problem with my computer.",
    "What a nice day!",
    "He was elected president last year.",
    "I studied the English for three years.",
    "In the summer I go to the beach.",
    "I saw Mr Smith at the supermarket.",
    "It takes half an hour by bus.",
    "The most people think that English is hard.",
    "I have few friends here.",
    "She is the best student in the class.",
    "I need an information.",
    "We went to the Netherlands in July.",
]

_TAG = re.compile(r"<[^>]+>")


def plain(text):
    """Render the page's light HTML the way a reader sees it."""
    if not text:
        return ""
    out = str(text)
    out = re.sub(r"<br\s*/?>", "\n", out)
    out = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", out, flags=re.S)
    out = re.sub(r"<(b|strong)>(.*?)</\1>", r"**\2**", out, flags=re.S)
    out = _TAG.sub("", out)
    out = out.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"[ \t]+", " ", out).strip()


def wrap(text, indent, width=76):
    """Wrap for reading, keeping deliberate line breaks."""
    lines = []
    for para in str(text).split("\n"):
        words, current = para.split(), ""
        if not words:
            continue
        for word in words:
            if len(current) + len(word) + 1 > width:
                lines.append(indent + current)
                current = word
            else:
                current = (current + " " + word).strip()
        lines.append(indent + current)
    return "\n".join(lines)


def gate_probe(logic, text):
    """Try each Gate 0 stage in order and record what happened.

    The winner is taken from `analyze_input`'s own `source`, so this can never
    disagree with the engine about who answered - it only explains the path.
    """
    normalized = _normalize_noun(text)
    tokens = _tokenize_words(text)
    steps = []

    def note(stage, hit, detail=""):
        steps.append((stage, hit, detail))

    frame = logic.check_constructions(text, tokens, whole_only=True)
    note("constructions (whole input + frames)", bool(frame),
         frame["source"].split(":", 1)[1] if frame else "")

    determiner = logic.check_determiner(text)
    note("determiners (slot already taken)", bool(determiner),
         determiner["source"].split(":", 1)[1] if determiner else "")

    fixed = [p for p in FIXED_EXPRESSIONS if p in " ".join(tokens)]
    note("fixed expressions", bool(fixed), ", ".join(fixed[:3]))

    from logic import _NOUN_NUMBER_RE
    number = bool(_NOUN_NUMBER_RE.match(normalized))
    note("noun + classifying number", number, normalized if number else "")

    time_hit = logic.check_time_words(normalized, tokens)
    note("time words", bool(time_hit),
         time_hit["source"].split(":", 1)[1] if time_hit else "")

    in_lookup = normalized in LOOKUP_TABLE or any(
        t in LOOKUP_TABLE for t in tokens)
    matched = normalized if normalized in LOOKUP_TABLE else next(
        (t for t in tokens if t in LOOKUP_TABLE), "")
    detail = matched
    if matched and LOOKUP_TABLE[matched].get("conditions"):
        cond = LOOKUP_TABLE[matched]["conditions"]
        keys = [k for k in ("requires_any", "requires_prev", "blocked_by_next") if k in cond]
        detail = "%s (conditional: %s)" % (matched, ", ".join(keys))
    note("lookup table", in_lookup, detail)

    nat = normalized in NATIONALITY_THE["examples"]
    note("nationality adjective", nat, normalized if nat else "")

    category = logic.check_categories(normalized, tokens)
    note("categories (language / meal / sport)", bool(category),
         category["source"].split(":", 1)[1] if category else "")

    name = logic._is_the_taking_name(text, normalized, tokens)
    note("name in the the-taking class", name, normalized if name else "")

    loose = logic.check_constructions(text, tokens, whole_only=False)
    note("constructions (inside a sentence)", bool(loose),
         loose["source"].split(":", 1)[1] if loose else "")

    return steps


def describe_construction(name):
    for rule in CONSTRUCTIONS:
        if rule["name"] == name:
            return rule
    return None


def trace(text, logic=None):
    logic = logic or ArticleLogic()
    analysis = logic.analyze_input(text)
    result = analysis["result"]
    source = analysis.get("source") or ""
    out = []

    out.append("=" * 78)
    out.append('INPUT   "%s"' % text)
    out.append("focus   %s" % (analysis["focus_noun"] or "(none inferred)"))
    out.append("")
    out.append("GATE 0")

    winner_stage = {
        "construction": "constructions",
        "determiner": "determiners",
        "fixed_expression": "fixed expressions",
        "noun_number": "noun + classifying number",
        "time_words": "time words",
        "lookup": "lookup table",
        "context_required": "lookup table",
        "nationality": "nationality adjective",
        "category": "categories",
        "proper_noun": "name in the the-taking class",
        "noun_adjunct": "lookup table",
    }.get(source.split(":", 1)[0], "")

    answered = False
    for stage, hit, detail in gate_probe(logic, text):
        is_winner = hit and winner_stage and winner_stage in stage and not answered
        mark = "HIT " if hit else "miss"
        if is_winner:
            note, answered = "  <-- ANSWERED HERE", True
        elif hit and answered:
            note = "  (would match, but a gate above answered first)"
        elif hit:
            note = "  (matched, but did not answer)"
        else:
            note = ""
        out.append("  %-4s %-38s %s%s" % (mark, stage, detail, note))

    out.append("")
    if analysis["mode"] == "question":
        node = DECISION_TREE[ENTRY_NODE]
        out.append("OUTCOME  no Gate 0 match - the learner is asked the questions")
        out.append("")
        out.append("FIRST QUESTION (%s)" % ENTRY_NODE)
        out.append(wrap(plain(node["question"]), "  "))
        if node.get("details"):
            out.append(wrap(plain(node["details"]), "    "))
        for label in node["options"]:
            out.append("    [ ] %s" % plain(label))
        if node.get("warning"):
            out.append(wrap("WARNING: " + plain(node["warning"]), "    "))
        return "\n".join(out)

    article = result.get("article")
    form_key = next((k for k, v in FORM_LABELS.items()
                     if v["word"].strip("— ").lower() == str(article).lower()), None)
    shown = FORM_LABELS.get(form_key, {}).get("word") or article

    out.append("OUTCOME  %s" % shown)
    out.append("source   %s" % source)
    ref = result.get("rule_ref")
    if ref:
        out.append("rule     %s  %s" % (ref, SOURCE_SECTIONS.get(ref, "?")))
    if result.get("result") == "context_required":
        out.append("reason   %s" % result.get("reason"))

    out.append("")
    out.append("TEXT SHOWN TO THE STUDENT")
    out.append('  headline: %s' % shown)
    body = wrap(plain(result.get("explanation")), "            ")
    out.append("  body:   " + body.lstrip())

    if result.get("result") == "context_required":
        fixed_sense = result["fixed_sense"]
        out.append("  fixed sense (%s): %s" % (fixed_sense["article"], result.get("sense") or ""))
        out.append(wrap(plain(fixed_sense["explanation"]), "      "))
        if result.get("examples"):
            out.append("  otherwise: " + " / ".join(plain(e) for e in result["examples"]))
        out.append("  button:   Work it out with the questions")

    if source.startswith("construction:"):
        rule = describe_construction(source.split(":", 1)[1])
        if rule:
            if rule.get("examples"):
                out.append("  examples: " + " / ".join(plain(e) for e in rule["examples"]))
            if rule.get("contrast"):
                out.append(wrap(plain(rule["contrast"]), "  but:      "))

    if analysis.get("unusual"):
        out.append(wrap(plain(analysis["unusual"]), "  unusual:  "))
    if analysis.get("note"):
        out.append(wrap(plain(analysis["note"]), "  note:     "))

    word = analysis["focus_noun"]
    if word and article in ("the", "a / an", "no article"):
        built = ("the " + word if article == "the"
                 else (choose_a_or_an(word) + " " + word) if article == "a / an"
                 else word)
        out.append("  built:    %s" % built)
    return "\n".join(out)


def node_inventory():
    """Every question and every leaf, as the learner reads them.

    The traces only show the first question, because the walk is interactive.
    Wording work needs the whole set in one place.
    """
    out = ["", "=" * 78, "ALL TREE WORDING", "=" * 78]
    for node_id, node in DECISION_TREE.items():
        out.append("")
        if "question" in node:
            out.append("[%s]  %s" % (node_id, node.get("gate", "")))
            out.append(wrap(plain(node["question"]), "  Q: "))
            if node.get("short"):
                out.append("  trail label: %s" % plain(node["short"]))
            if node.get("details"):
                out.append(wrap(plain(node["details"]), "     "))
            for label, goes in node["options"].items():
                out.append("     -> %-14s %s" % (goes, plain(label)))
            if node.get("warning"):
                out.append(wrap("WARNING: " + plain(node["warning"]), "     "))
        else:
            out.append("[%s]  LEAF -> %s   (rule %s)"
                       % (node_id, node.get("article"), node.get("rule_ref")))
            out.append("  %s" % plain(node.get("category")))
            out.append(wrap(plain(node.get("explanation")), "     "))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sentences", nargs="*")
    parser.add_argument("--file", help="one sentence per line")
    parser.add_argument("--out", help="write the report here as well")
    parser.add_argument("--no-nodes", action="store_true",
                        help="skip the full tree-wording inventory")
    args = parser.parse_args()

    sentences = list(args.sentences)
    if args.file:
        with open(args.file, encoding="utf-8") as handle:
            sentences += [line.strip() for line in handle if line.strip()]
    if not sentences:
        sentences = SAMPLE

    logic = ArticleLogic()
    report = "\n\n".join(trace(s, logic) for s in sentences)
    if not args.no_nodes:
        report += "\n" + node_inventory()

    # Write before printing: a Windows console is cp1252, and an em dash in the
    # rule text used to kill the run before the file was saved.
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(report + "\n")

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    print(report)
    if args.out:
        print("\nwritten to %s" % args.out, file=sys.stderr)


if __name__ == "__main__":
    main()
