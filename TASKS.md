# TASKS

The concrete backlog. Direction and the reasoning behind these live in
[`ROADMAP.md`](ROADMAP.md); this list is grouped by the roadmap's horizons —
**Now** (polish the live standalone tool), **Next** (shape it into a platform
module), **Later** (the platform itself).

The AI items all follow one rule: the engine is the oracle — AI generates and
perceives, never adjudicates, and everything it produces is verified before a
learner sees it.

## Now — polish the standalone tool (it's live, in front of students)

- [ ] Restyle index.html to the "Gloss" direction, as a **design system** rather
      than page-glued CSS (it seeds the platform's look — see
      [`docs/design-direction.md`](docs/design-direction.md)). Gloss is the
      manuscript treatment from the design mock-up, direction B: cold white
      paper, ink-blue text, one annotating red for everything the learner did,
      and the trail moved out of its card into a real right-hand margin as a
      gloss in a second hand. Fraunces for the headword and verdict, Newsreader
      for the question and examples, Archivo for the marginal hand. The four
      article colours collapse to a single blue on the verdict, so decide first
      what the map view does without per-form colour.
- [ ] Make the four views cohere — consistent navigation and interaction across
      Walk, Map, Look-a-word-up and Play. Today each grew on its own.
- [ ] Retire the Tkinter desktop app. Remove the GUI (`app.py`) and reframe
      `logic.py` / `rules.py` in the README as what they now are — the shared
      headless engine the tests and `tools/` scripts read — not "the desktop
      app." Update the README/project-layout tables that still present the GUI as
      a first-class citizen.
- [ ] Role A — run a real AI-draft batch. The pipeline, harvest, corpus, "More
      examples" surface and parity guards are in (see `done`); what remains is to
      draft fresh sentences with an LLM (`tools/generate_examples.py draft`),
      review `examples_staging.json`, `promote`, and re-inline.
- [ ] Gather user feedback on phrase-first UX and tune detection
      heuristics/wording.
- [ ] Q4's 4a-4h list is getting long. Watch whether learners still work down
      it, now that it has eight cues instead of seven.

## Next — shape the module for the platform

- [ ] Draw the **module boundary**: make the rules engine mountable independent
      of the standalone chrome, so it can be dropped into the platform shell.
      Do this alongside the Gloss restyle so presentation and engine are teased
      apart once, not twice.
- [ ] Build a genuine **Learn mode** — teach the principle first, then hand off
      to Play — assembled from the explanatory material that already exists (the
      "why" on cards, the map, the readings).
- [ ] **Role B — tell a noun from a verb**, so `bank holiday` can be told from
      `sun rises`. Both are determiner + listed word + one more word, so the
      lookup answers from the first noun and `a bank holiday` gets a card about
      banks. Handing those to the noun-adjunct rule was tried twice and reverted
      twice (bce8a71, and the gate before it): the pair test cannot see that
      `rises` is a verb, so `the sun rises` came back as a noun-noun pair.
      Neither the verb list nor position can settle it -- `rises` is not on the
      list and it sits exactly where `holiday` sits. Needs real part-of-speech
      knowledge: a small lexicon of noun and verb forms, or a tagger. This is the
      first candidate for the AI layer's **Role B** (runtime perception): AI
      extracts the features, the canonical rules act on them, with a
      deterministic offline fallback and "it depends" on disagreement. Decide API
      cost + learner-text-to-API privacy before building. Affects the same shape
      in `the piano teacher`, `a golf club`, `the art gallery`, `a history
      book`, `a bed sheet`, `the work permit`, `a home page`, `a music lesson`.

## Later — the platform itself

- [ ] Additional grammar topics on the articles pattern, across A1–C2 (each a
      topic = its own data + a set of modes).
- [ ] Cross-topic learner progress (today's state is per-view `localStorage`).
- [ ] Source and integrate video / listening ("Watch") — this needs clips found
      or made, not just code.

## done
- [x] Build the AI layer's **Role A** scaffold (generate-then-verify, at build
      time): `tools/generate_examples.py` (harvest / draft / promote),
      `examples_data.json` (74 harvested, engine-verified, provenance-tagged,
      partitioned from canon), inlined into index.html by `tools/inline_rules.py`,
      and a "More examples of …" surface in the readings view. Two guards:
      `tests/test_examples.py` re-verifies every example against the Python
      engine, and `tools/check_parity.js` (run from the suite) loads the real
      browser engine and asserts it reads each example the same — so the two
      engines can never silently disagree over a sentence a learner is shown. The
      AI-draft step is written but still needs a real batch (see Now).
- [x] Add a fourth view, "Play": a drill that asks before it answers. Early
      levels blank the article out of a phrase and ask which one goes in;
      middle levels show the phrase whole and ask which rule decides it; the
      last two ask both halves, with the wrong answers drawn from the asked
      rule's own section so they are near misses rather than obvious. Nothing
      is authored: every phrase is mined from the fixed expressions, the
      lookup table, the construction and note examples, the category words,
      the traces and the tree's own option examples, then handed back to gate
      0 -- an item survives only if the engine agrees with the entry it came
      from, so a rules edit cannot leave the drill teaching what the tool
      denies. rules_data.json is untouched. Score, streak and the rules that
      went wrong are kept in localStorage beside the chip marks.
- [x] Add a third view, "Look a word up": type a word and see every reading the
      rules hold for it -- the listed sense with the words that switch it on,
      the contrast sense, any fixed expressions it appears in, its category or
      time group -- plus the three ordinary readings, and pick the one you
      meant. Listed senses answer straight away; the ordinary ones open the
      questions pinned to the word, and the back button returns to the list.
      Browser only, assembled from rules_data.json as it already stands.
- [x] Lead each reading card with the example and keep the rule underneath in
      the small grey. The examples come out of the tree's own options, indexed
      by the node they lead to, and out of the <em> phrases the lookup
      explanations already name -- `go to the cinema`, `listen to the radio`.
      An example that only repeats the card's phrase is dropped.
- [x] Give `the` its eight readings in the readings mode instead of one. Q4's
      cues are each a leaf with its own name, rule and examples, and collapsing
      them into a single "identifying which one" card hid the reading a learner
      most often wants -- `government` is a role that belongs to something, and
      that reading could not be reached from the mode at all. Picking a cue
      answers; the one cue that opens a further question opens at that
      question, not at the top of the tree.
- [x] Split Q4's 4f into two rules: 4f is Part 2.2 (the situation we're both
      in), 4g is Part 4.1/4.2 (the everyday place as an idea), role nouns move
      to 4h. The one option cited 2.2, showed 4.1/4.2 examples and explained
      neither, so `I want the bike` matched nothing and got `a bike`.
- [x] Add the 4.1/4.2 place words to the lookup table with their American
      equivalents (the movies / the mall / the store / the drugstore / the
      doctor, alongside the cinema / the shops / the chemist's / the doctor's),
      and put the British-American split for `in hospital` on the expression
      itself.
- [x] Keep an apostrophe that sits between two letters when normalizing, so
      `the doctor's` reaches its own entry and does not display as `doctors`.
- [x] Implement phrase-first sentence input flow (MVP) in web + desktop UI
- [x] Add learner-friendly wording to key decision-tree questions
- [x] Add result examples tied to recommended article and detected focus noun
- [x] Add shared phrase analysis helper in Python logic (`analyze_input`)
- [x] Mirror phrase analysis behavior in browser logic for parity
- [x] Add tests for sentence parsing and recommendation fallback output
- [x] Update README usage + test command docs for new flow
- [x] Audit current user question flow for unclear terminology and decision points
- [x] Propose UX/content improvements with learner-friendly language and examples
- [x] Evaluate feasibility of a phrase-first helper grounded in the defining PDF
- [x] Outline an implementation plan with minimal-risk increments

## notes
- Eight lookup notes cite 6.1.4, whose learner-facing name is "A meal, sport or
  language used in an unusual way" -- right for its section, wrong over `a
  cinema`. The readings mode shows no rule name on a note, as the walk does
  not either; the citations themselves may want a look.
- Implemented phrase-first MVP without changing project architecture: both UIs still share `rules_data.json` semantics and decision-tree fallback.
- New Python API: `ArticleLogic.analyze_input(text)` returns `mode`, `focus_noun`, and optional lookup `result`.
- Validation run: `python -m py_compile logic.py app.py rules.py` and `python -m unittest discover -s tests -v` (5 tests passed).
- Default `python -m unittest -v` returned 0 tests in this repo layout; README now documents discovery command.
