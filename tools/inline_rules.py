"""Copy each rules file into the page that reads it, so the pages work from disk.

Both pages used to fetch their rules, which a browser refuses to do for a
`file://` document -- so a learner who was sent the .html and opened it saw an
instruction to run a Python web server. The rules now travel inside the pages.

The JSON files stay the source of truth: the Python side reads
`rules_data.json`, the tests read both, and edits are made there. Run this
after changing either:

    python tools/inline_rules.py

`tests/test_gate_zero.py` fails if a copy in a page has drifted, so a forgotten
run cannot ship.
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("rules_data.json", "index.html"),
    ("rules_data.classic.json", "classic.html"),
]

OPEN = '<script id="rules-data" type="application/json">'
CLOSE = "</script>"
BLOCK = re.compile(re.escape(OPEN) + r".*?" + re.escape(CLOSE), re.DOTALL)


def payload(data):
    """The data as JSON that is safe between script tags.

    Escaping `<` means the string can never contain `</script`, whatever ends
    up in the rules; JSON.parse reads \\u003c back as `<`.
    """
    return json.dumps(data, ensure_ascii=False,
                      separators=(",", ":")).replace("<", "\\u003c")


def inline(data_name, page_name):
    data = json.loads((ROOT / data_name).read_text(encoding="utf-8"))
    page_path = ROOT / page_name
    page = page_path.read_text(encoding="utf-8")

    if not BLOCK.search(page):
        print("no rules-data block in %s" % page_name, file=sys.stderr)
        return False

    body = payload(data)
    updated = BLOCK.sub(lambda _: OPEN + "\n" + body + "\n" + CLOSE, page, count=1)
    if updated == page:
        print("%-12s already up to date" % page_name)
        return True

    io.open(page_path, "w", encoding="utf-8", newline="").write(updated)
    print("%-12s <- %s (%d bytes)" % (page_name, data_name, len(body)))
    return True


def main():
    return 0 if all(inline(*pair) for pair in PAIRS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
