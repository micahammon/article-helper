# TASKS

## current
- [ ] Restyle index.html to the "Gloss" direction, with tweaks still to
      settle. Gloss is the manuscript treatment from the design
      mock-up, direction B: cold white paper, ink-blue text, one annotating
      red for everything the learner did, and the trail moved out of its card
      into a real right-hand margin as a gloss in a second hand. Fraunces for the
      headword and verdict, Newsreader for the question and examples, Archivo
      for the marginal hand. The four article colours collapse to a single
      blue on the verdict, so decide first what the map view does without
      per-form colour.
- [ ] Gather user feedback on phrase-first UX and tune detection heuristics/wording
- [ ] Tell a noun from a verb, so `bank holiday` can be told from `sun rises`.
      Both are determiner + listed word + one more word, so the lookup answers
      from the first noun and `a bank holiday` gets a card about banks. Handing
      those to the noun-adjunct rule was tried twice and reverted twice
      (bce8a71, and the gate before it): the pair test cannot see that `rises`
      is a verb, so `the sun rises` came back as a noun-noun pair. Neither the
      verb list nor position can settle it -- `rises` is not on the list and it
      sits exactly where `holiday` sits. Needs real part-of-speech knowledge: a
      small lexicon of noun and verb forms, or a tagger. Affects the same
      shape in `the piano teacher`, `a golf club`, `the art gallery`, `a
      history book`, `a bed sheet`, `the work permit`, `a home page`, `a music
      lesson`.
- [ ] Q4's 4a-4h list is getting long. Watch whether learners still work down
      it, now that it has eight cues instead of seven.

## done
- [x] Add a third view, "Look a word up": type a word and see every reading the
      rules hold for it -- the listed sense with the words that switch it on,
      the contrast sense, any fixed expressions it appears in, its category or
      time group -- plus the three ordinary readings, and pick the one you
      meant. Listed senses answer straight away; the ordinary ones open the
      questions pinned to the word, and the back button returns to the list.
      Browser only, assembled from rules_data.json as it already stands.
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
- Implemented phrase-first MVP without changing project architecture: both UIs still share `rules_data.json` semantics and decision-tree fallback.
- New Python API: `ArticleLogic.analyze_input(text)` returns `mode`, `focus_noun`, and optional lookup `result`.
- Validation run: `python -m py_compile logic.py app.py rules.py` and `python -m unittest discover -s tests -v` (5 tests passed).
- Default `python -m unittest -v` returned 0 tests in this repo layout; README now documents discovery command.
