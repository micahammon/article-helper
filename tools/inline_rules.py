"""Copy rules_data.json into index.html, so the page works from disk.

`index.html` used to fetch its rules, which a browser refuses to do for a
`file://` document -- so a learner who was sent the .html and opened it saw an
instruction to run a Python web server. The rules now travel inside the page.

`rules_data.json` stays the source of truth: the Python side reads it, the
tests read it, and edits are made there. Run this after changing it:

    python tools/inline_rules.py

`tests/test_gate_zero.py` fails if the copy in the page has drifted, so a
forgotten run cannot ship.
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "rules_data.json"
PAGE = ROOT / "index.html"

OPEN = '<script id="rules-data" type="application/json">'
CLOSE = "</script>"
BLOCK = re.compile(
    re.escape(OPEN) + r".*?" + re.escape(CLOSE), re.DOTALL)


def payload(data):
    """The data as JSON that is safe between script tags.

    Escaping `<` means the string can never contain `</script`, whatever ends
    up in the rules; JSON.parse reads \\u003c back as `<`.
    """
    return json.dumps(data, ensure_ascii=False,
                      separators=(",", ":")).replace("<", "\\u003c")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")

    if not BLOCK.search(page):
        print("no rules-data block in index.html", file=sys.stderr)
        return 1

    updated = BLOCK.sub(
        lambda _: OPEN + "\n" + payload(data) + "\n" + CLOSE, page, count=1)
    if updated == page:
        print("index.html already up to date")
        return 0

    io.open(PAGE, "w", encoding="utf-8", newline="").write(updated)
    print("inlined %d bytes of rules into index.html" % len(payload(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
