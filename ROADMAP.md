# Roadmap

Direction and intent for the English Article Helper. This is the layer above
[`TASKS.md`](TASKS.md): the *why* and the ordering, not the task list. When a
decision is unclear, it should be settled by the north star and principles
below.

## North star

A deterministic, inspectable, offline tool that helps English learners choose
`a/an` / `the` / no article — faithful to Seonaid Beckwith's guide, engaged
through several modes (ask, explore, drill), and shareable as a single file with
no server or account.

**Where it's going:** the Article Helper is the first module of a larger
grammar-activity platform — a coolenglish-style suite of Learn / Play / watch
activities across the A1–C2 curriculum. Articles is one topic among many, but an
unusually deep one (a full decision engine, not a simple drill). The platform is
**next**, not someday, so we shape for it now.

That gives every decision a test: *does this move us toward a portable,
embeddable module — or does it deepen a standalone monolith we'll have to unpick?*

## Principles

**Load-bearing today (do not erode):**

- **Rules live in data, never in code.** `rules_data.json` is the single source
  of truth; no front-end decides an article in code. The map view and path trail
  are generated from it so they can't drift.
- **The learner never sees a rule number or the book.** Citations are for us.
- **It answers, it doesn't guess.** Context-sensitive nouns defer with "it
  depends" rather than picking a likely reading.
- **Works from `file://`.** No server, no network, no account. Rules are inlined
  into the page.
- **Learner-facing prose is American English.**

**Platform-shaping (adopt now, so the module is ready to lift out):**

- **Separate the engine from the chrome.** The durable asset is the rules engine
  + all prose + the modes. The standalone page's outer styling is disposable and
  will be re-presented inside the platform shell. Invest in a design *system*,
  not one-off page CSS.
- **Speak the platform's vocabulary: Learn / Play / (Watch).** Reconcile the
  modes we have with that pattern (see below) rather than inventing a parallel
  one.
- **Articles is the prototype for "a topic."** Each future topic = its own data +
  a set of modes. Decisions here set the pattern the rest of the curriculum will
  copy, so keep the data contract and the module boundary clean.
- **The engine is the oracle; AI generates and perceives, never adjudicates.**
  The canonical rules always decide the article. Anything AI produces is verified
  — by the engine and/or by a human — before a learner sees it, kept in its own
  file and tagged with provenance. This is the same generate-then-verify
  discipline Play already uses: mine an item, hand it back to the engine, keep it
  only if the engine agrees.

## The modes we have, mapped to the platform pattern

| Platform slot | What exists today | Gap |
|---|---|---|
| **Play** | The drill ("Play" view) — mines items from the data, checks them back through Gate 0. | Solid. |
| **Learn** | Raw material only: the "why" on every card, the map view, and "Look a word up." | No mode that *teaches the principle first*, then practices. This is the main content gap. |
| **Explore / reference** | Lookup + walkable tree, the whole-map view, readings mode. | Rich. May present differently once inside a shell. |
| **Watch** (video / listening) | Nothing. | Needs *sourcing*, not just building — find or make clips. |

## Now — polish the standalone tool (it's live, in front of students)

- Land a real design identity (the "Gloss" direction) as a **design system**,
  not page-glued CSS — this doubles as the seed of the platform's look. Tracked
  in [`docs/design-direction.md`](docs/design-direction.md).
- Make the four views cohere: consistent navigation and interaction across
  lookup, map, readings, and Play.
- Retire the Tkinter desktop app and update the README/docs that still present it
  as a first-class citizen.
- Tune Q4's eight-cue list — watch whether learners still work down it.

## Next — shape the module for the platform

- Draw the **module boundary**: make the rules engine mountable independent of
  the standalone chrome, so it can be dropped into the platform shell.
- Build a genuine **Learn mode** — teach the principle, then hand off to Play —
  from the explanatory material that already exists.
- **Correctness depth:** the noun-vs-verb problem (`bank holiday` vs `sun
  rises`) needs real part-of-speech knowledge; broaden condition coverage. This
  is the first candidate for **AI as perception** (Role B, below).

## The AI layer

An AI layer sits *on top* of the deterministic core, governed by the "engine is
the oracle" principle above. Two roles, kept apart because they differ in risk,
latency, and where they run:

- **Role A — content generator (build time; started).** AI drafts example
  sentences; each draft is run back through the engine and kept only if it
  classifies as the intended rule; survivors are staged for human approval and
  baked into `examples_data.json`, partitioned from canon and tagged with
  provenance. Runtime never calls an API — the vetted corpus ships inside the
  page like the rules do. Powers "see all examples of a word," and enriches Play
  and the readings mode. Built by [`tools/generate_examples.py`](tools/generate_examples.py).
- **Role B — perception / parser (runtime, optional; later).** AI supplies the
  linguistic features the regex layer lacks (POS, head-noun, countable-in-this-
  use); the **canonical rules run on those features**. An optional online call
  with a deterministic offline fallback; on AI/regex disagreement, surface "it
  depends." Tradeoffs to settle before building: API cost, and sending learner
  text (possibly minors) to an external service.

The same generate → engine-verify → human-approve pipeline becomes the
content-authoring pipeline for the wider platform: Learn copy and Play items per
topic, each vetted against that topic's canonical engine.

## Later — the platform itself

- Additional grammar topics on the articles pattern, across A1–C2.
- Cross-topic learner progress (today's state is per-view `localStorage`).
- Source and integrate video / listening ("Watch").

## Non-goals

- **Not a general grammar checker.** It answers one question well.
- **No LLM as the authority in the runtime answer path.** The canonical rules
  always decide the article. AI may *generate* content (verified before it
  ships) and may *optionally* extract features the rules then act on — always
  with a deterministic offline fallback. What it must never do is decide, or
  override, a rule. See "The AI layer" above.
- **No server or account requirement**, even inside the platform, unless a
  feature genuinely can't exist without it.
- **Newspaper headlines stay out** (6.4) — dropping articles there is a stylistic
  choice, not a rule a learner needs.
