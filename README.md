# English Article Helper 📖

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=github)](https://micahammon.github.io/article-helper/)

An interactive, rule-based tool to help English learners choose the correct article (`a/an`, `the`, or no article). Pure HTML, CSS and JavaScript, translating the logic from Seonaid Beckwith's guide, "'A' and 'The' Explained".

---

### Live Demonstration

**[Visit the live demo site](https://micahammon.github.io/article-helper/)** — no install, works in any modern browser.

---

### How It Works

The tool is **lookup first, tree second**. That order matters: the questions a
learner genuinely cannot answer are the ones the tool answers for them.

**Gate 0 — matched automatically, before any question is asked.**
Type a noun or phrase and the tool normalizes it (trims spaces, drops a leading
`a/an/the`, strips punctuation) and checks it against the data in
[`rules_data.json`](rules_data.json), in strict precedence order:

0. **Is this a construction?** Some rules turn on the shape of the phrase
   rather than the noun in it: `next week` vs `the next bus`, `second prize`,
   `a second cup of coffee`, `The more you do, the better`, `most people` vs
   `the most intelligent`, `few problems`, `one of the students`,
   `half an hour`, `she touched him on the arm`, `the Smiths`,
   `a Mr Thompson`, `There's a post office`, `What a beautiful day`,
   `She was elected president`.

   These run in two passes. A match covering the whole input goes first, ahead
   of everything. A match buried in a longer sentence goes **last**, so
   `They moved to the United Kingdom last year` stays a question about the
   country rather than about `last year`.

   The exception is a **sentence frame** — `there is/are` (2.7), exclamations
   (5.3) and unique roles (6.5). These describe the shape of the whole clause
   rather than an adjunct inside it, so they join the first pass even when the
   match is partial: `There's a post office in my town` is Part 2.7, not a
   question about the noun `post`.
1. **Is the slot already taken?** A possessive, demonstrative or quantifier
   leaves no room for an article: `my book`, `this book`, `each student`,
   `some water`, `Sarah's car`. The answer is **not** "no article" — the
   question does not arise, so these report `no article needed` and stop.
2. **Fixed expressions** — `at night`, `by car`, `in the end`, `twice a week`.
   Set phrases override every rule below them, so they are caught first. Each
   one resolves to a **specific form**, never to "it's memorized, good luck."
3. **Noun + classifying number** — `Page 42`, `Platform 9`, `Question B`.
4. **The lookup table** — nouns with fixed or idiosyncratic rules: proper nouns
   (`the USA`), abstractions (`music`), systems (`the internet`). Matched on the
   longest phrase found anywhere in your input, so `I listened to the radio`
   finds `radio`.

   Most of these nouns are only fixed **inside a particular construction**, so
   the entries carry conditions and the tool refuses to answer outside them.
   Two guards run before any lookup answer:

   - **A determiner already in front of the noun that disagrees with the entry.**
     `piano` is fixed as *play the piano*, so `I bought a piano` is the other
     sense and the fixed rule does not apply. The check looks past adjectives,
     so `a lovely dinner` still sees the `a`.
   - **The entry's own conditions** — a required construction (`play` for
     instruments), a required preceding word (`the` for `the elderly`), or a
     following word that voids the fixed sense (`of` in `the history of art`).

   When a guard fires, the answer is **`it depends`**: the card shows the fixed
   sense, the reading that applies otherwise, and a button into the questions.
   It does not guess.
5. **Time words** (Part 6.2) — months, days (`Mondays` = every), holidays,
   seasons (either `the` or none), historical periods, plus patterns for years
   (`1991`), decades (`the 1960s`, `the eighties`), centuries, dates in both
   orders (`the 22nd of September` vs `November 16th`), and a part of the day
   named with its day (`Wednesday night`).
6. **Nationality adjectives** — `the French`, `the British`. This is the
   *the + adjective* construction, so it needs the article in front: bare
   `French` is a language, not a people.
7. **Languages, meals and sports** (Part 6.1) — productive rules, not word
   lists, so `Arabic`, `brunch` and `rugby` are covered without being
   enumerated.
8. **Names in the *the*-taking class** — plural names, `of`-constructions,
   rivers, seas, deserts, ranges, regions, hotels, museums, newspapers. Matched
   conservatively: a keyword only counts inside a capitalised name
   (`the Nile River`, not `a storm crossed the desert`), and an
   `of`-construction needs a capital on each side (`the Republic of Ireland`,
   not `a cup of coffee`).

When the answer is `a/an`, the form is chosen by **sound, not spelling** —
`a university`, `an hour`, `an MBA`, `a UFO`, `an X-ray`. The exception lists
and the letter-name rule for initialisms live in `phonetics` in the JSON.

A **noun-noun pair** (`bus station`) is handled here too: the first noun works
like an adjective, so the tool re-runs itself on the second noun and says so.

**The decision tree — only on a Gate 0 miss.**
Five ordered questions, first match wins, each one about *your own intent*
rather than about facts you would have to already know:

- **Q2** — is it a proper noun?
- **Q3** — the whole class, or particular instances? *(Test: can you insert
  "in general" without changing the meaning?)* This is the highest-error node
  for Romance-language speakers — `La vida es dura` is `Life is hard`, not
  `the life` — so it carries an explicit warning and a safe default.
- **Q4** — can your listener identify **which one**? Broken into eight concrete
  cues (**4a–4h**), ordered most-mechanical-first: a relative clause or
  `of`-phrase, a superlative or ordinal, second mention, inference from
  something already mentioned, uniqueness in the world, the situation the two of
  you are in (2.2), the everyday place taken as an idea (4.1/4.2), and role
  nouns like `the government`. A sub-gate under 4g separates a **place**
  (`the mall`) from an **institutional activity** (`at school`) — the classic
  collision.

  **4f and 4g are different rules**, and were one option until they were split.
  4f is Part 2.2: the room, building or town you are both in does the
  identifying — *pass me the glass*, or *the market* meaning the market in our
  town. 4g is Part 4.1/4.2: `the` + a singular noun for a whole category, the
  place as an idea rather than a particular building — *go to the cinema*,
  *the gym*, *the doctor's*. The single option had 2.2's citation, 4.1/4.2's
  examples and prose that fitted neither, so a learner pointing at a bike
  matched nothing and fell out to `a bike`.
- **Q5** — countable or not **in this use**, not as a property of the noun, so
  `coffee` / `a coffee` and `paper` / `a paper` route correctly.

Categories and time words carry an **unusual use** contrast alongside the
answer: used in a different way the word stops being an
exception, and the ordinary rules apply again — *the football they play in the
USA*, *the Monday we met*.

Every outcome — from Gate 0 or from the tree — names a form and names the
rule it comes from. Learners never see a rule *number*: `rule_ref` stays in the
data for us, and `rule_names` holds the wording that reaches the screen. Where a
tree outcome is reached by more than its cited section covers — the
ordinary-name leaf answers for people and companies, not only places — the node
carries its own `rule_name`, which wins over the one the ref implies. Nothing
a student reads cites a section, a gate, or the book — they have none of those
to hand.

`Walk the tree` steps through it one question at a time; `See the whole map`
renders the entire thing at once, generated from the same data, so the map can
never drift from the logic.

### How to Use

1. **Enter text** — a noun, a phrase, or a full sentence.
2. **Click Check.** If Gate 0 matches, you get the answer immediately.

**Which word is it answering about?** A sentence usually holds more than one
noun, and the tool used to pick one silently — in `I have a doubt about the
homework` either is a fair guess, and nothing on the page said which had been
chosen. The sentence is now shown back with the targeted word highlighted and
the other candidates underlined; tapping one re-answers for that word instead.

**Go back a step** unwinds whatever the last step actually was: a question if
you are walking the tree, otherwise the word you chose — after a Gate 0 match
there is no walk to undo, so the button reads *Undo word choice* and returns to
the word the tool picked itself. When there is nothing to undo it is disabled
rather than inert.

Pinning a word narrows only the *matching*. The sentence still supplies
context, so `I bought a piano last week` pinned to `piano` still sees the `a`
in front of it — and `last week` no longer answers a question about the piano.

3. **Otherwise, answer the questions** until you reach a form.
4. **Read the result** — the recommended article, why it applies, the phrase
   built for you, and the name of the rule behind it.

Every step you take is recorded in **Your path**, naming both the question and
your answer — `Whole class, or instances? — Particular instances` —
so the route to an answer stays readable after the fact. `Go back a step` walks
it backwards.

Or click any of the chips at the bottom to set a worked example going. Most
finish on their own — some answered instantly by Gate 0, some walking the tree
to a form — which is the quickest way to see the two halves working. `bus
station` is the one that stops and asks: a noun-noun pair defers to its second
noun, so the chip hands the reader Question 1 about `station`. The heading says
*set going* rather than *route itself* for that reason.

There are far more examples than fit on screen, so the row is a random draw of
twenty-four out of the full set, reshuffled on every load and by the `Shuffle`
button. A chip says nothing about where it lands until you click it. Once run,
it is ticked and dimmed — a memory aid, kept across reloads, that never hints at
the form. Marked phrases stay in the pool and can come round again; `Clear
marks` wipes the ticks.

### Running Locally

Open `index.html`. That is the whole procedure — it carries its rules inside it,
so it works from a `file://` document, from a USB stick, or out of an email
attachment, with no server and no network. `classic.html` works the same way.

No server is needed for anything, but if you want one — to test the deployed
paths, say — `python -m http.server` from the project directory still serves
both at `http://localhost:8000/`.

### Project Layout

| File | What it is |
|---|---|
| `index.html` | The tool. Gate 0 + the walkable tree + the map view, rules included. |
| `rules_data.json` | All rules and all prose. Shared with the desktop app. |
| `tools/inline_rules.py` | Copies each rules file into the page that reads it. |
| `classic.html` | The previous web version, kept for reference. Rules included. |
| `rules_data.classic.json` | Frozen data for `classic.html`. |
| `app.py`, `logic.py`, `rules.py` | Tkinter desktop app, reading the same JSON. |
| `tests/` | Suite guarding the tree and Gate 0. |

The desktop app and the browser read the same `rules_data.json`, so they stay in
sync. `rules.py` adapts the browser-shaped nodes into the plain-text shape the
Tkinter GUI expects.

**The JSON files are where rules are written; the pages carry a copy.**
Both pages used to fetch their data, which a browser refuses to do for a
`file://` document — so a learner who was sent the `.html` and opened it got an
instruction to install a web server instead of an answer. After editing either
`rules_data.json` or `rules_data.classic.json`, run:

```
python tools/inline_rules.py
```

`tests/test_gate_zero.py` compares each page's copy against its file and fails
if they differ, so a forgotten run cannot ship a page that answers from stale
rules.

### Changing the Rules

**Every article rule lives in `rules_data.json`** — the tree, all question and
answer text, the fixed-expression lists, the lookup table, the proper-noun and
nationality lists, and every rule reference. Neither front-end decides an
article in code, so editing that file changes the web page and the desktop app
together, and no code change is needed to correct a rule or add a phrase.

| To change | Edit |
|---|---|
| A memorized phrase | `fixed_expressions` — each entry names its own `article` |
| A noun with a fixed rule | `lookup_table` |
| A name that takes *the* | `proper_noun_the.named` or `.keywords` |
| A question's wording | `decision_tree.<node>.q`, `.note`, `.opts[].label` |
| Its label in the path trail | `decision_tree.<node>.short` |
| An explanation or citation | the leaf's `why` and `rule_ref` |
| A determiner that blocks articles | `determiners.groups` |
| A language, meal or sport | `categories.<name>.words` |
| A month, day, holiday, season, period | `time_words.groups.<name>.words` |
| A date / year / decade pattern | `time_words.patterns` |
| A phrase-shape rule | `constructions` (ordered; first match wins) |
| Which words can be tapped as the focus | `_NOT_A_FOCUS` in `logic.py` |
| Whether it outranks the lexical gates | that rule's `frame` flag |
| When a noun is only fixed in context | that entry's `conditions` |
| A caveat shown alongside an answer | that entry's `note` |
| An a/an pronunciation exception | `phonetics` |

**Learner-facing prose is American English.** Spelling in every string a
learner reads — questions, options, examples, explanations, notes — is
normalized to American: *favorite*, *theater*, *neighbor*, *generalize*, *on
vacation*. Two places keep British spellings on purpose:

- `source_sections` is the book's own contents page, checked against every
  `rule_ref`, so it stays verbatim. Nothing renders it to a learner.
- `phonetics` and the lookup keys are **matching data, not writing**. `honour`
  sits beside `honor` so a learner who types the British spelling still gets
  the silent-h rule, and `theatre` stays a key alongside `theater`. Add both
  spellings when a new word has one.

Where the two dialects differ in the article itself, that is content and both
belong on the card: `in hospital` / `in the hospital`, `the cinema` / `the
movies`, `the chemist's` / `the drugstore`.

`classic.html` and `rules_data.classic.json` had their prose swept the same
way. The classic pair is not developed further, but `/classic.html` is still
served, so a learner can still read it — which means an error there is an error
in front of a student, and gets fixed. **Do not add lookup entries to
`rules_data.classic.json`.** It is not only classic.html's data:
`test_all_49_original_lookup_entries_survive` reads its 49-entry lookup table as
the baseline proving the live table never drops an inherited entry, changes its
article, or drifts on a reference. A new key there breaks that count. So
`theater` joins `theatre` in `rules_data.json` but not in the classic file, and
classic.html answers only the British spelling.

**Citations are validated, not trusted.** `source_sections` holds the book's
real contents, and the build refuses to write a `rule_ref` that is not in it.
This is not hypothetical: an earlier version stamped all 94 fixed expressions
with `7.5`, which is the *Illnesses* section, and pointed the proper-noun rule
at `9.2.1`, which is the *'No article'* subsection — the opposite of what it
was claiming. Both passed the tests of the day, because those only checked that
a reference was **present**. Five inherited lookup entries had the same `9.2.1`
misfiling — *the USA*, *the United Kingdom*, *the Netherlands*, *the
Philippines*, *The Hague*, all of which take *the* and so belong to `9.2.2`.
They are corrected in both files, and `lookup_ref_corrections` records what
changed and why. That record is what keeps the two tables comparable: the test
asserts their references now agree and that the `was` value never returns.

The misfiling survived as long as it did because nothing rendered it in a form
anyone could check. Naming the rules is what exposed it — `9.2.1` reads as
nothing, but *Place names without an article* under a **the** answer is
obviously wrong.

The map view and the path trail are both generated from this file, so neither
can drift from the logic it documents. `tests/test_gate_zero.py` enforces the
no-hardcoding property directly: it flips a value in memory and asserts the
answer follows.

### Tests

```
python -m unittest discover -s tests -v
```

`tests/test_gate_zero.py` covers the parts most likely to rot:

- every fixed expression resolves to a real form;
- all 49 original lookup entries survive, with their articles and references;
- every tree edge points at a real node, every node is reachable, and **no leaf
  is a dead end**;
- the worked examples land on the leaves they claim;
- chips meant to demonstrate Gate 0 actually hit it, and chips meant to walk the
  tree are not shadowed by Gate 0;
- every Gate 0 rule carries its own `article` and `rule_ref`, and the answer
  follows the data when that value is changed — so a hardcoded form fails the
  suite instead of going unnoticed;
- every citation names a real section of the book, and the fixed expressions are
  not all filed under one;
- determiners block rather than returning zero, and `blocked` stays distinct
  from `no article`;
- proper-noun keywords do not fire outside a capitalised name, while the real
  names still match;
- `a/an` is chosen by sound: `a university`, `an hour`, `an MBA`, `a UFO`;
- languages, meals and sports resolve productively, and `the French` (a people)
  stays distinct from `French` (a language);
- time words resolve, including both date orders and the decade/century split;
- every construction cites a real section and carries examples, `next week`
  stays distinct from `the next bus`, and an incidental match inside a longer
  sentence does not hijack the answer;
- a sentence frame outranks the lexical gates but does not swallow them, and a
  contraction (`There's`) is not mistaken for a possessive (`Sarah's`);
- context-sensitive nouns defer rather than answer — `I bought a piano`,
  `a lovely dinner`, `the history of art` — while the fixed senses still
  answer, and every condition block actually has a trigger.

### Known Gaps

Now covered: Section 6 (languages, meals, sports and time words), and the
phrase-shape rules — *next/last* (7.11), ordinals (7.12), *most* (7.8),
*few/little* (7.7), *a/an* vs *one* and *half* (7.9), comparatives (7.13),
body parts (4.7) and people's names (9.4).

Only **newspaper headlines** (6.4) are left out, deliberately: dropping
articles there is a journalist's stylistic choice, not a rule a learner needs.

Two rules answer with a split, because nothing in the input settles them: a
season takes either `the` or none (6.2.6), and an exclamation takes `a/an`
before a singular countable noun and nothing before a plural or uncountable
one (5.3).

The constructions are regexes over the input, which is a real limit: they read
word order, not grammar. An unusual phrasing can miss one, and a loose match
inside a long sentence is only ever a fallback.

The lookup table is now conditioned (22 of 68 entries), so context-sensitive
nouns defer instead of guessing. What remains is coverage rather than
correctness: the conditions are word lists, not grammar, so an unusual phrasing
can still slip past one. Adding vocabulary means deciding, for each word,
whether it is genuinely two-way.

Only some words are. `piano` is: *I bought a piano* is the other sense, so it
carries conditions and defers. The everyday places of 4.1/4.2 are not — `the
gym` is `the` under either reading — so they answer outright, and the caveat
about meaning one particular building rides alongside as a `note`. Having that
backwards made `the cinema` refuse to answer while `the gym` answered, under the
same rule.

### Deploying

The site is served by GitHub Pages from `main` at `/`, so pushing to `main`
publishes it. Two things to know:

- `index.html` is cached for ten minutes, and it now carries its own rules, so
  code and data can no longer disagree: a returning visitor sees the previous
  version of both, or the new version of both, never a mix. First-time visitors
  are unaffected, and a hard reload gets the latest immediately. GitHub Pages
  does not allow custom cache headers, so the delay is a floor rather than a bug.
- Mismatches degrade quietly rather than erroring, so verify a deploy by
  exercising the live page — not just by checking that the build went green.
