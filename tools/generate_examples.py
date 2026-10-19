"""Build a vetted corpus of example sentences, verified against the engine.

The rule the whole AI layer turns on: the engine is the oracle. Nothing here
decides an article. A sentence is kept only if `ArticleLogic.analyze_input`
already classifies it as the reading it was meant to show -- the same
generate-then-verify discipline the Play view uses when it mines items and hands
them back to gate0(). `rules_data.json` is never written to.

Two sources of candidates:

  harvest  -- phrases the data already carries (the chip traces, and the <em>
              phrases inside lookup explanations). Deterministic, no network.
              Verified survivors go straight into examples_data.json, tagged
              source="harvested".

  draft    -- an LLM drafts fresh sentences for one word, through OpenRouter.
              Verified survivors go to examples_staging.json, tagged source="ai",
              for a human to read before `promote` moves them into
              examples_data.json. Needs ARTICLE_HELPER_OPENROUTER_API_KEY in the
              environment; the rest of the tool runs without it.

Usage:
    python tools/generate_examples.py harvest
    python tools/generate_examples.py draft --word radio --sense "listen to it" --n 6
    python tools/generate_examples.py draft-all --dry-run
    python tools/generate_examples.py draft-all --limit 5
    python tools/generate_examples.py promote
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# The verifier is the same engine the tests trust (see tests/test_gate_zero.py).
from logic import ArticleLogic, _normalize_noun, _tokenize_words  # noqa: E402

DATA = ROOT / "rules_data.json"
CORPUS = ROOT / "examples_data.json"
STAGING = ROOT / "examples_staging.json"

# The draft step talks to OpenRouter's OpenAI-compatible endpoint. Key lives in
# the environment, never in the repo; no SDK, just stdlib urllib.
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY_ENV = "ARTICLE_HELPER_OPENROUTER_API_KEY"

_EM = re.compile(r"<em>(.*?)</em>", re.IGNORECASE | re.DOTALL)
_TODAY = datetime.date.today().isoformat()


def _load(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _save(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def target_words(data):
    """Every word the data holds a definite reading for -- the words a learner
    might look up, and so the words worth carrying examples for."""
    words = set()
    words.update(data["lookup_table"].keys())
    for cat in data["categories"].values():
        words.update(cat.get("words", []))
    for group in data["time_words"]["groups"].values():
        words.update(group.get("words", []))
    for key in data["fixed_expressions"]:
        if not re.search(r"\d", key):
            words.update(key.split(" "))
    words.update(data["nationality_the"].get("examples", []))
    words.update(w.lower() for w in data["proper_noun_the"].get("named", []))
    return {w for w in words if len(w) > 1}


# Looking back from the noun, how far an article may sit: room for a couple of
# adjectives, and a hyphenated one ("black-and-white") tokenizes as three.
_ARTICLE_WINDOW = 5
_DETERMINERS = {
    "my", "your", "his", "her", "its", "our", "their", "this", "that", "these",
    "those", "some", "any", "no", "every", "each", "another",
}
# What each engine answer allows to stand before the noun in the sentence.
_SHOWS = {
    "the": {"the"},
    "a / an": {"a", "an"},
    "no article": {None},
    "no article needed": {None},
    "either the or no article": {"the", None},
}


def article_in_sentence(text, word):
    """The article the sentence itself puts before `word`: "the", "a", "an", or
    None when there is none (a bare noun, or a determiner like "my" in its slot).

    The engine's lookup answers for the word, not the sentence, so this is the
    surface check that the sentence actually shows that answer. Tokens carry no
    parts of speech; it walks back a short window and stops at the first article
    or determiner.
    """
    word = _normalize_noun(word)
    if word in ("the", "a", "an"):
        # Harvested proper-noun entries ("the Alps") key on the article itself.
        return word
    tokens = _tokenize_words(text)
    i = tokens.index(word)
    for tok in reversed(tokens[max(0, i - _ARTICLE_WINDOW):i]):
        if tok in ("the", "a", "an"):
            return tok
        if tok in _DETERMINERS:
            return None
    return None


def sentence_shows(article, text, word):
    """Does the sentence use the article the engine gave? An answer this table
    does not know is let through: the engine has the final word on labels."""
    allowed = _SHOWS.get(article)
    return allowed is None or article_in_sentence(text, word) in allowed


_FIXED_KEYS = None


def _fixed_keys():
    """The data's fixed expressions, longest first ("all of a sudden" before
    "a sudden"), skipping the numeric patterns."""
    global _FIXED_KEYS
    if _FIXED_KEYS is None:
        keys = _load(DATA, {}).get("fixed_expressions", {})
        _FIXED_KEYS = sorted((k for k in keys if not re.search(r"\d", k)),
                             key=len, reverse=True)
    return _FIXED_KEYS


def _contains_phrase(tokens, phrase):
    p = phrase.split()
    return any(tokens[i:i + len(p)] == p for i in range(len(tokens) - len(p) + 1))


def _fixed_expression_read(engine, text, tokens, word):
    """If the sentence holds a fixed expression containing `word`, the engine's
    answer for that expression, else None.

    The whole-sentence read is tried first; if it settles on some other phrase
    ("most of the..."), the expression is asked about on its own. Either way the
    engine answers. The expression carries its own article, so no surface check
    is needed.
    """
    hit = next((k for k in _fixed_keys()
                if word in k.split() and _contains_phrase(tokens, k)), None)
    if hit is None:
        return None
    analysis = engine.analyze_input(text)
    if not (analysis.get("source") == "fixed_expression"
            and word in (analysis.get("focus_noun") or "").split()):
        analysis = engine.analyze_input(hit)
    if analysis.get("mode") != "lookup" or analysis.get("source") != "fixed_expression":
        return None
    return analysis


# How close a construction's cue must end before the word to govern it:
# "what a beautiful day", "there's a post office".
_CUE_REACH = 3


def _answers_for(analysis, tokens, word):
    """Is the engine's answer about `word`? Either the phrase it settled on
    contains the word, or it is a construction whose cue sits just before the
    word -- not "the most" four words back, nor "most of the" after it."""
    cue = (analysis.get("focus_noun") or "").lower().split()
    if word in cue:
        return True
    if not (analysis.get("source") or "").startswith("construction") or not cue:
        return False
    i = tokens.index(word)
    for start in range(max(0, i - _CUE_REACH - len(cue)), i):
        if tokens[start:start + len(cue)] == cue and i - (start + len(cue) - 1) <= _CUE_REACH:
            return True
    return False


def verify(engine, text, word):
    """Does the engine give `word` a definite reading inside `text`?

    Returns the corpus fields on success, or None when the engine declines to
    commit -- a question, or an "it depends". An ambiguous sentence teaches the
    wrong thing, so it is dropped rather than guessed at.
    """
    word = _normalize_noun(word)
    tokens = _tokenize_words(text)
    if word not in tokens:
        return None
    analysis = _fixed_expression_read(engine, text, tokens, word)
    if analysis is None:
        # No fixed expression for this word here: the focused read, but only
        # when its answer is about this word and the sentence shows it.
        analysis = engine.analyze_input(text, focus=word)
        if (analysis.get("mode") != "lookup"
                or not _answers_for(analysis, tokens, word)):
            return None
        article = (analysis.get("result") or {}).get("article")
        if not sentence_shows(article, text, word):
            return None
    result = analysis.get("result") or {}
    article = result.get("article")
    if not article or article == "it depends":
        return None
    return {
        "text": text.strip(),
        "word": word,
        "verified_article": article,
        "verified_rule_ref": result.get("rule_ref"),
        "verified_source": analysis.get("source"),
    }


def _candidates_for(data, word):
    """Phrases the data already carries that use `word`: chip traces first, then
    the <em> examples inside its own lookup explanation."""
    seen, out = set(), []

    def offer(text):
        text = (text or "").strip()
        key = _normalize_noun(text)
        if text and key and key != word and key not in seen:
            seen.add(key)
            out.append(text)

    for trace in data.get("traces", []):
        phrase = trace.get("p", "")
        if word in _tokenize_words(phrase):
            offer(phrase)

    entry = data["lookup_table"].get(word)
    if entry:
        for m in _EM.findall(entry.get("explanation", "")):
            offer(re.sub(r"<[^>]*>", "", m))
    return out


def harvest():
    data = _load(DATA, {})
    engine = ArticleLogic()
    corpus = _load(CORPUS, {"meta": {}, "examples": []})

    # harvested entries are regenerated wholesale; anything a human staged and
    # promoted (source != "harvested") is left untouched.
    kept = [e for e in corpus["examples"] if e.get("source") != "harvested"]
    have = {(e["word"], _normalize_noun(e["text"])) for e in kept}

    added = 0
    for word in sorted(target_words(data)):
        for text in _candidates_for(data, word):
            fields = verify(engine, text, word)
            if not fields:
                continue
            if (fields["word"], _normalize_noun(fields["text"])) in have:
                continue
            have.add((fields["word"], _normalize_noun(fields["text"])))
            fields.update(source="harvested", date=_TODAY)
            kept.append(fields)
            added += 1

    corpus["meta"] = {
        "note": "Example sentences verified against the engine. Not canonical "
                "rules -- regenerate with tools/generate_examples.py. AI-drafted "
                "entries are human-approved before they land here.",
        "generated": _TODAY,
        "count": len(kept),
    }
    corpus["examples"] = sorted(kept, key=lambda e: (e["word"], e["text"]))
    _save(CORPUS, corpus)
    print("harvest: +%d verified, %d total -> %s" % (added, len(kept), CORPUS.name))


def _draft_from_llm(word, sense, n, model):
    """Ask a model (via OpenRouter) for candidate sentences. Isolated so the rest
    of the tool runs with no key and no network."""
    key = os.environ.get(OPENROUTER_KEY_ENV)
    if not key:
        sys.exit("draft needs %s in the environment. If you just added it, "
                 "restart the session so the shell inherits it." % OPENROUTER_KEY_ENV)

    sense_line = (" The sense to illustrate: %s." % sense) if sense else ""
    prompt = (
        "You write example sentences for an English-article learning tool.\n"
        "Give %d short, natural sentences (8-14 words) that each use the word "
        "\"%s\" as a noun, with its article chosen correctly.%s\n"
        "Vary the sentences. Return ONLY a JSON array of strings, nothing else."
        % (n, word, sense_line))

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        # writing sentences is not deep reasoning: keep thinking (and cost) low
        "reasoning": {"effort": "low"},
        # ask OpenRouter to report what the call cost, so a batch can total it
        "usage": {"include": True},
    }
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            # optional OpenRouter attribution, harmless if ignored
            "HTTP-Referer": "https://github.com/micahammon/article-helper",
            "X-Title": "Article Helper example generator",
        },
        method="POST",
    )
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        sys.exit("draft: OpenRouter returned %s: %s"
                 % (e.code, e.read().decode("utf-8", "replace")))

    text = resp["choices"][0]["message"]["content"]
    cost = float((resp.get("usage") or {}).get("cost") or 0)
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError("model did not return a JSON array:\n" + text)
    return [str(s) for s in json.loads(match.group(0))], cost


def draft(word, sense, n, model):
    """Draft one word into staging. Returns what the call cost in USD."""
    engine = ArticleLogic()
    try:
        candidates, cost = _draft_from_llm(word, sense, n, model)
    except ValueError as e:
        sys.exit("draft: %s" % e)

    staging = _load(STAGING, {"examples": []})
    have = {(e["word"], _normalize_noun(e["text"])) for e in staging["examples"]}

    kept = 0
    for text in candidates:
        fields = verify(engine, text, word)
        if not fields:
            print("  dropped (engine would not commit): %s" % text)
            continue
        if (fields["word"], _normalize_noun(fields["text"])) in have:
            continue
        have.add((fields["word"], _normalize_noun(fields["text"])))
        fields.update(source="ai", model=model, date=_TODAY)
        staging["examples"].append(fields)
        kept += 1
        print("  kept [%s]: %s" % (fields["verified_article"], text))

    _save(STAGING, staging)
    print("draft: %d/%d survived verification -> %s (review, then `promote`), $%.4f"
          % (kept, len(candidates), STAGING.name, cost))
    return cost


# Plain text for a prompt: the data's explanations carry <em> and <br>.
_TAGS = re.compile(r"<[^>]+>")


def _plain(html):
    return re.sub(r"\s+", " ", _TAGS.sub(" ", html or "")).strip()


# Words an expression can end on that are not its noun ("in charge of").
_FUNCTION_WORDS = {"a", "an", "the", "of", "to", "in", "on", "at", "by", "for",
                   "with", "from"}


def build_plan(data):
    """One entry per single-word target, with the sense the data gives it.

    Each word is drafted for the reading the rules hold for it, so the plan
    says which reading that is: the lookup entry's sense (or explanation), the
    category or time group's explanation, or the fixed expression it ends.
    Multi-word names ("united kingdom") are left out: verify() matches a single
    token, so nothing drafted for them could be kept. So are the prepositions
    and verbs inside fixed expressions; only the noun an expression ends on
    is a target.
    """
    plan = {}

    def add(word, article, sense, source):
        word = word.lower()
        if " " in word or len(word) < 2 or word in plan:
            return
        plan[word] = {"word": word, "article": article,
                      "sense": _plain(sense), "source": source}

    for word, entry in data["lookup_table"].items():
        cond = entry.get("conditions") or {}
        add(word, entry["article"], cond.get("sense") or entry.get("explanation"),
            "lookup")
    for name, cat in data["categories"].items():
        for word in cat.get("words", []):
            add(word, cat["article"], "%s: %s" % (name, cat.get("explanation", "")),
                "category")
    for name, group in data["time_words"]["groups"].items():
        for word in group.get("words", []):
            add(word, group["article"], "%s: %s" % (name, group.get("explanation", "")),
                "time")
    for key, expr in data["fixed_expressions"].items():
        if re.search(r"\d", key):
            continue
        nouns = [w for w in key.split(" ") if w not in _FUNCTION_WORDS]
        if not nouns:
            continue
        add(nouns[-1], expr["article"],
            "as in the fixed expression \"%s\". Use that exact phrase word for "
            "word in every sentence: do not change its verb form or swap its "
            "words" % key, "fixed")
    nat = data["nationality_the"]
    for word in nat.get("examples", []):
        add(word, nat["article"], "the people as a group: %s" % nat.get("explanation", ""),
            "nationality")
    pn = data["proper_noun_the"]
    for word in pn.get("named", []):
        add(word, pn["article"], "the proper name: %s" % pn.get("explanation", ""),
            "proper")
    return [plan[w] for w in sorted(plan)]


def draft_all(model, n, limit, dry_run, words=None):
    """Draft every planned word that has no example yet, in the corpus or staging.

    --dry-run lists what would be drafted and makes no call. A word whose
    response cannot be parsed is reported and skipped; the run goes on.
    """
    data = _load(DATA, None)
    covered = {e["word"] for e in _load(CORPUS, {"examples": []})["examples"]}
    covered |= {e["word"] for e in _load(STAGING, {"examples": []})["examples"]}
    if words:
        # an explicit list redrafts those words even if they have some examples
        todo = [p for p in build_plan(data) if p["word"] in words]
    else:
        todo = [p for p in build_plan(data) if p["word"] not in covered]
    if limit:
        todo = todo[:limit]
    if dry_run:
        for p in todo:
            print("  %-16s [%s] %s" % (p["word"], p["article"], p["sense"][:70]))
        print("draft-all --dry-run: %d words would be drafted, no calls made" % len(todo))
        return
    spent, failed = 0.0, []
    for i, p in enumerate(todo, 1):
        print("[%d/%d] %s" % (i, len(todo), p["word"]))
        sense = "%s (in this reading the word takes: %s)" % (p["sense"], p["article"])
        try:
            spent += draft(p["word"], sense, n, model)
        except SystemExit as e:
            print("  skipped: %s" % e)
            failed.append(p["word"])
    print("draft-all: %d words, $%.4f spent, %d skipped%s"
          % (len(todo), spent, len(failed), (": " + ", ".join(failed)) if failed else ""))


def promote():
    """Move human-reviewed staged entries into the shipped corpus. Re-verify on
    the way in, so a rules edit since drafting cannot smuggle a stale example."""
    staging = _load(STAGING, {"examples": []})
    if not staging["examples"]:
        sys.exit("nothing staged in %s" % STAGING.name)

    engine = ArticleLogic()
    corpus = _load(CORPUS, {"meta": {}, "examples": []})
    have = {(e["word"], _normalize_noun(e["text"])) for e in corpus["examples"]}

    moved, dropped = 0, 0
    for entry in staging["examples"]:
        fields = verify(engine, entry["text"], entry["word"])
        if not fields:
            print("  stale, dropped: %s" % entry["text"])
            dropped += 1
            continue
        if (fields["word"], _normalize_noun(fields["text"])) in have:
            continue
        have.add((fields["word"], _normalize_noun(fields["text"])))
        fields.update(source=entry.get("source", "ai"), date=entry.get("date", _TODAY))
        if entry.get("model"):
            fields["model"] = entry["model"]
        corpus["examples"].append(fields)
        moved += 1

    corpus["meta"]["count"] = len(corpus["examples"])
    corpus["examples"] = sorted(corpus["examples"], key=lambda e: (e["word"], e["text"]))
    _save(CORPUS, corpus)
    _save(STAGING, {"examples": []})
    print("promote: %d moved, %d dropped, %d total -> %s"
          % (moved, dropped, len(corpus["examples"]), CORPUS.name))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("harvest", help="verify phrases the data already carries")
    d = sub.add_parser("draft", help="draft fresh sentences for one word (needs API key)")
    d.add_argument("--word", required=True)
    d.add_argument("--sense", default="", help="the reading to illustrate")
    d.add_argument("--n", type=int, default=6)
    d.add_argument("--model", default="anthropic/claude-sonnet-5.5",
                   help="OpenRouter model slug, e.g. anthropic/claude-haiku-5.5")
    a = sub.add_parser("draft-all",
                       help="draft every planned word with no example yet (needs API key)")
    a.add_argument("--n", type=int, default=8)
    a.add_argument("--model", default="anthropic/claude-sonnet-5.5")
    a.add_argument("--limit", type=int, default=0, help="draft only the first N words")
    a.add_argument("--dry-run", action="store_true", help="list the words, make no calls")
    a.add_argument("--words", nargs="+", help="draft only these words (redrafts thin ones)")
    sub.add_parser("promote", help="move reviewed staged entries into the corpus")

    args = parser.parse_args(argv)
    if args.cmd == "draft-all":
        draft_all(args.model, args.n, args.limit, args.dry_run, args.words)
    if args.cmd == "harvest":
        harvest()
    elif args.cmd == "draft":
        draft(args.word, args.sense, args.n, args.model)
    elif args.cmd == "promote":
        promote()


if __name__ == "__main__":
    main()
