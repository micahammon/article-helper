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


def verify(engine, text, word):
    """Does the engine give `word` a definite reading inside `text`?

    Returns the corpus fields on success, or None when the engine declines to
    commit -- a question, or an "it depends". An ambiguous sentence teaches the
    wrong thing, so it is dropped rather than guessed at.
    """
    word = _normalize_noun(word)
    if word not in _tokenize_words(text):
        return None
    analysis = engine.analyze_input(text, focus=word)
    if analysis.get("mode") != "lookup":
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
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        sys.exit("draft: model did not return a JSON array:\n" + text)
    return [str(s) for s in json.loads(match.group(0))]


def draft(word, sense, n, model):
    engine = ArticleLogic()
    candidates = _draft_from_llm(word, sense, n, model)

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
    print("draft: %d/%d survived verification -> %s (review, then `promote`)"
          % (kept, len(candidates), STAGING.name))


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
    sub.add_parser("promote", help="move reviewed staged entries into the corpus")

    args = parser.parse_args(argv)
    if args.cmd == "harvest":
        harvest()
    elif args.cmd == "draft":
        draft(args.word, args.sense, args.n, args.model)
    elif args.cmd == "promote":
        promote()


if __name__ == "__main__":
    main()
