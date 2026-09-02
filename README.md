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

0. **Is the slot already taken?** A possessive, demonstrative or quantifier
   leaves no room for an article: `my book`, `this book`, `each student`,
   `some water`, `Sarah's car`. The answer is **not** "no article" — the
   question does not arise, so these report `no article needed` and stop.
1. **Fixed expressions** — `at night`, `by car`, `in the end`, `twice a week`.
   Set phrases override every rule below them, so they are caught first. Each
   one resolves to a **specific form**, never to "it's memorized, good luck."
2. **Noun + classifying number** — `Page 42`, `Platform 9`, `Question B`.
3. **The lookup table** — nouns with fixed or idiosyncratic rules: proper nouns
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
4. **Time words** (Part 6.2) — months, days (`Mondays` = every), holidays,
   seasons (either `the` or none), historical periods, plus patterns for years
   (`1991`), decades (`the 1960s`, `the eighties`), centuries, dates in both
   orders (`the 22nd of September` vs `November 16th`), and a part of the day
   named with its day (`Wednesday night`).
5. **Nationality adjectives** — `the French`, `the British`. This is the
   *the + adjective* construction, so it needs the article in front: bare
   `French` is a language, not a people.
6. **Languages, meals and sports** (Part 6.1) — productive rules, not word
   lists, so `Arabic`, `brunch` and `rugby` are covered without being
   enumerated.
7. **Names in the *the*-taking class** — plural names, `of`-constructions,
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
- **Q4** — can your listener identify **which one**? Broken into seven concrete
  cues (**4a–4g**), ordered most-mechanical-first: a relative clause or
  `of`-phrase, a superlative or ordinal, second mention, inference from
  something already mentioned, uniqueness in the world, uniqueness in the
  shared community, and role nouns like `the government`. A sub-gate under 4f
  separates a **place** (`the mall`) from an **institutional activity**
  (`at school`) — the classic collision.
- **Q5** — countable or not **in this use**, not as a property of the noun, so
  `coffee` / `a coffee` and `paper` / `a paper` route correctly.

Categories and time words carry the book's **unusual use** contrast (6.1.4,
6.2.8) alongside the answer: used in a different way the word stops being an
exception, and the ordinary rules apply again — *the football they play in the
USA*, *the Monday we met*.

Every outcome — from Gate 0 or from the tree — names a form and cites the
section of the source guide it comes from.

`Walk the tree` steps through it one question at a time; `See the whole map`
renders the entire thing at once, generated from the same data, so the map can
never drift from the logic.

### How to Use

1. **Enter text** — a noun, a phrase, or a full sentence.
2. **Click Check.** If Gate 0 matches, you get the answer immediately.
3. **Otherwise, answer the questions** until you reach a form.
4. **Read the result** — the recommended article, why it applies, the phrase
   built for you, and the rule reference.

Every step you take is recorded in **Your path**, naming both the question and
your answer — `Question 3 · whole class, or instances? — Particular instances` —
so the route to an answer stays readable after the fact. `Go back a step` walks
it backwards.

Or click any of the chips at the bottom to watch a worked example route itself.
Some are answered instantly by Gate 0, others walk the tree, which is the
quickest way to see the two halves working.

### Running Locally

The page reads its rules from `rules_data.json`, so it must be served over HTTP —
opening the `.html` from disk will not work (the page says so if you try).

1. Clone the repository.
2. From the project directory: `python -m http.server`
3. Open `http://localhost:8000/`.

### Project Layout

| File | What it is |
|---|---|
| `index.html` | The tool. Gate 0 + the walkable tree + the map view. |
| `rules_data.json` | All rules and all prose. Shared with the desktop app. |
| `classic.html` | The previous web version, kept for reference. |
| `rules_data.classic.json` | Frozen data for `classic.html`. |
| `app.py`, `logic.py`, `rules.py` | Tkinter desktop app, reading the same JSON. |
| `tests/` | Suite guarding the tree and Gate 0. |

The desktop app and the browser read the same `rules_data.json`, so they stay in
sync. `rules.py` adapts the browser-shaped nodes into the plain-text shape the
Tkinter GUI expects.

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
| When a noun is only fixed in context | that entry's `conditions` |
| A caveat shown alongside an answer | that entry's `note` |
| An a/an pronunciation exception | `phonetics` |

**Citations are validated, not trusted.** `source_sections` holds the book's
real contents, and the build refuses to write a `rule_ref` that is not in it.
This is not hypothetical: an earlier version stamped all 94 fixed expressions
with `7.5`, which is the *Illnesses* section, and pointed the proper-noun rule
at `9.2.1`, which is the *'No article'* subsection — the opposite of what it
was claiming. Both passed the tests of the day, because those only checked that
a reference was **present**. Five inherited lookup entries had the same `9.2.1`
misfiling; the fixes are recorded in `lookup_ref_corrections` so a deliberate
correction stays distinguishable from drift.

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
- context-sensitive nouns defer rather than answer — `I bought a piano`,
  `a lovely dinner`, `the history of art` — while the fixed senses still
  answer, and every condition block actually has a trigger.

### Known Gaps

Section 6 is now covered: languages, meals and sports as productive rules
(6.1), and time words (6.2).

Still missing, though the book has them: existential *there is/are* (2.7),
exclamations (5.3), newspaper headlines (6.4), unique roles after *elect* /
*appoint* / *become* (6.5), *next/last* with time expressions (7.11), ordinals
(7.12), *most* vs *the most* (7.8), *few/a few* and *little/a little* (7.7),
*a/an* vs *one* (7.9), comparatives (7.13), people's names (*the Smiths*,
*a Mr Jones*, *a Picasso* — 9.4), and body-part constructions (4.7).

The lookup table is now conditioned (26 of 49 entries), so context-sensitive
nouns defer instead of guessing. What remains is coverage rather than
correctness: the conditions are word lists, not grammar, so an unusual phrasing
can still slip past one. Adding vocabulary to the table means adding its
conditions at the same time.

### Deploying

The site is served by GitHub Pages from `main` at `/`, so pushing to `main`
publishes it. Two things to know:

- `index.html` and `rules_data.json` are cached separately for ten minutes. The
  page fetches its rules with `cache: "no-cache"` so the data can never be older
  than the code reading it, but a returning visitor may still see the previous
  version of the page itself until that expires. First-time visitors are
  unaffected, and a hard reload gets the latest immediately. GitHub Pages does
  not allow custom cache headers, so this is a floor rather than a bug.
- Mismatches degrade quietly rather than erroring, so verify a deploy by
  exercising the live page — not just by checking that the build went green.
