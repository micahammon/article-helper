# Design direction — "Gloss"

The visual language for the Article Helper, and the seed of the grammar
platform's design system. This is the brief the "Gloss restyle" task in
[`../TASKS.md`](../TASKS.md) works from. It is deliberately portable: the tokens,
type roles, and accent meanings here should survive being lifted out of
`index.html` and into the platform shell, so the standalone page's chrome is the
only part that stays behind.

The problem it solves: the current page reads as *vibe-coded* — the soft cards,
the four candy accent colours, the generic SaaS gloss you see everywhere. The
fix is not "nicer" — it is **a point of view**.

---

## The concept: a glossed manuscript

The tool already behaves like a scholar reading over a student's shoulder: the
learner writes a phrase, and the tool answers in the margin — a verdict, the
reason, the rule's name, the path it took. So the design *is* that.

- The learner's text is the **primary text**, set large and central, the way the
  main body of a manuscript page is.
- The tool's reasoning — verdict, the "why," the running path — is **marginalia
  in a second hand**: smaller, set apart, annotating rather than competing.

This is what makes it original instead of templated. A generic tool would stack
the question and the answer in equal cards. Gloss makes the page *about* the
learner's words, and everything the tool says is annotation on them. The
metaphor is doing real pedagogical work, not decoration — which is the whole
test of good design here.

---

## Principles

1. **Text first.** The learner's phrase is the hero on every screen. Nothing the
   tool adds should outweigh it.
2. **Annotation, not decoration.** Every mark earns its place by meaning
   something — a verdict, the learner's own move, the current step. No ornament.
3. **Colour is a role, never a form.** We do not colour-code the four articles.
   Colour marks *what kind of thing this is* (a verdict; the learner's own hand),
   consistently, in every view.
4. **Restraint.** Two accents, a paper, an ink, and the greys between. If a
   screen needs a third colour to be legible, the layout is wrong first.
5. **The reasoning must stay readable.** The path, the "why," the rule name are
   the product. They get real typographic care, not fine print.
6. **Offline-first type.** Whatever faces we choose must work with no network
   (see Typography). This is not negotiable — it is the tool's identity.
7. **Everything must travel.** If a choice can't be lifted into the platform
   shell, it belongs to the page, not the system.

---

## Colour system

Two moves define it: **cold white paper with ink-blue text**, and a **restrained,
role-based accent set** replacing the four per-form hues.

### Roles

| Token | Role | Light (start) | Dark (start) |
|---|---|---|---|
| `--paper` | The page | `#F2F4F5` | `#10171C` |
| `--card` | A leaf laid on the page (verdict, cards) | `#FBFCFC` | `#18222A` |
| `--ink` | Text and reasoning (ink-blue, not black) | `#172A38` | `#E3EAEF` |
| `--muted` | The marginal hand — labels, the path, fine print | `#566B76` | `#94A4AD` |
| `--rule` | Hairlines, borders, running-head rule | `#C5CED3` | `#31404A` |
| `--accent` | **The verdict and the primary action** — the single blue | `#1D5B7C` | `#79BAD9` |
| `--accent-wash` | Faint field behind a verdict | `#E4EEF3` | `#12303D` |
| `--mark` | **The learner's own hand** — their marks, the path they took, chips they've run (rubric red) | `#9E3728` | `#E0917F` |
| `--mark-wash` | Faint field behind the learner's marks | `#F3E5E1` | `#2E1B16` |

Hexes are starting points, to be checked against WCAG during the restyle (body
text ≥ 4.5:1, large text and UI ≥ 3:1).

### Why these two accents

The brief is "ink-blue text, one annotating red for everything the learner did."
That resolves cleanly to two roles:

- **`--accent` (blue)** — the tool's own voice at its most definite: the verdict,
  and the one primary button per screen. This is where the four article colours
  used to shout; now they collapse into a single, calm blue. The *form* is said
  in words, not hue.
- **`--mark` (rubric red)** — the learner's hand, the way a reader's own
  annotations were rubricated in a real manuscript: the highlighted focus word,
  the path trail, the tick on a chip they've run. It answers "what did *I* do?"
  at a glance, and it never means a grammatical form.

Everything else is paper, ink, and the marginal grey between them.

### How the four forms read without per-form colour

`the` / `a·an` / `no article` / `it depends` are distinguished by, in order:

1. **The word itself**, set in the display face as the verdict — this is the
   signal.
2. **A small-caps label** (the "form pill") in ink on `--card`, bordered in
   `--rule` — not filled with a form colour.
3. **Position** — the verdict always sits in the same place, so the eye learns
   where to look, not which colour to decode.

This is the change with the most reach, so the migration is explicit below.

### Dark mode

Same token names, same roles, inverted ground: `--paper` goes to ink-dark,
`--ink` to near-white, and the two accents lift in value (blue brightens, the
rubric red warms toward clay) so both stay legible on the dark leaf. Define the
full light palette on `:root` and redefine only what changes under
`prefers-color-scheme: dark`.

### Migration from today's tokens

`index.html` `:root` (lines 8–54) currently defines `--the / --an / --zero /
--fixed`, each with `-wash` and `-edge`, plus a dark-mode block that keeps all
four "so a learner who has learned teal-means-the still reads it that way." Gloss
retires that idea:

- Collapse the four verdict colours → `--accent` everywhere a form is stated.
- Repurpose the "learner did this" signals (focus highlight, path, chip ticks) →
  `--mark`.
- Delete `--*-edge`; borders become `--rule`. Washes become `--accent-wash` /
  `--mark-wash` where a field is still wanted, otherwise nothing.
- The comment about teaching colour-as-form is removed — the tool no longer
  teaches that, and shouldn't.

---

## Typography — **open**

The faces are **not settled** (Fraunces / Newsreader / Archivo were the mock's
suggestion, not a decision). What *is* settled is the structure and the
constraint; we pick faces next, by mocking a couple of options in the page.

### The constraint (decides more than taste does)

The tool must work from a `file://` document with no network. So webfonts may
**never** be fetched from a CDN at runtime. Only two strategies are allowed:

- **Embed, subsetted** — subset the chosen faces to the characters the page uses
  and base64-embed them, via a build step alongside `tools/inline_rules.py`.
  Keeps the single-file, offline property; costs page weight.
- **System-only** — no custom faces; a strong system serif (the current
  Iowan/Palatino stack is already good) plus system-ui sans.

A face that can't be embedded-subsetted or matched by a system stack is out,
however beautiful.

### Three roles

| Role | Where | Character wanted |
|---|---|---|
| **Display** | Headword (the learner's phrase), the verdict | Distinctive, a little personality — this is the face that stops the page looking generic |
| **Reading** | Questions, examples, the "why" prose | Comfortable at length, quiet, high legibility |
| **Marginal hand** | The path/trail, form labels, fine print | A second voice: smaller, likely small-caps, letter-spaced — reads as annotation |

### Scale & rhythm (role terms now, faces later)

A modest scale on a ~1.5 body line-height: display ~2rem+ (fluid), verdict
~1.5rem, question ~1.25rem, body 1rem, marginal ~0.8rem in small caps with
~0.06em tracking. Generous measure limits on prose (~44em) so the reasoning reads
like text, not UI.

### Candidate directions (to try, not locked)

- **Display:** a warm old-style/transitional serif with real character (Fraunces
  or similar); system fallback = Iowan Old Style / Palatino.
- **Reading:** a screen-tuned reading serif (Newsreader, Source Serif) or the
  system serif stack if we go system-only.
- **Marginal hand:** a humanist grotesque in small caps (Archivo, Inter) or
  system-ui — the contrast with the serifs is what sells the "second hand."

---

## Layout & the margin

The signature move is the **margin**. On a wide screen:

- A **main column** holds the text, the question, and the verdict, at a reading
  measure (~640–680px).
- A **right margin** (~200–240px) carries the learner's path as a running gloss —
  the trail moves out of its boxed card into the actual margin, set in the
  marginal hand, in `--mark`.

Below a breakpoint the margin folds under the main column (as "Your path" does
today) — the gloss becomes a footnote rather than a side-note, but keeps its
voice. The masthead stays a running head: the title over a hairline `--rule` (the
current 2px ink border is already the right instinct; soften it to `--rule`).

---

## Component intents

- **Mode toggle** — the four views as a quiet row of tabs in the marginal hand,
  the active one in ink; no filled pills.
- **Phrase bar** — the input is where the learner writes on the page; large,
  in the reading/display face, minimally chromed.
- **Verdict card** — a leaf (`--card`) with the built phrase, the verdict word in
  the display face in `--accent`, and one small-caps form label. The "why" and
  rule name sit beneath in the marginal hand.
- **Question + options** — the question in the reading face, full width; options
  as bordered choices (`--rule`), never as coloured buttons.
- **Readings cards + "More examples"** — keep the example-led card; the "More
  examples" list stays a quiet marginal list (already close to this).
- **Chips** — worked examples as marginal entries; a run chip is ticked in
  `--mark` (the learner's hand), dimmed, never hinting at the form.
- **Map** — the reference diagram. Structure in `--rule`/`--ink`; the current
  traced route highlighted in `--mark` (the path the learner is on); leaves
  labelled by form in text and position, **not** by colour. This is the view the
  no-per-form-colour rule most changes, and the point where "one restrained
  accent set" is proven: the map earns its legibility from type and layout, with
  the two accents doing only their roles.
- **Play** — same system; the score/streak in the marginal hand, right/wrong
  feedback carried by the verdict/`--mark` roles, not new colours.

---

## Accessibility

- Contrast: body ≥ 4.5:1, large text and UI chrome ≥ 3:1, in both themes. The
  starting hexes above are provisional until checked.
- **`--mark` is never the only signal.** The learner's path is also words
  ("Whole class, or instances? — Particular instances") in a fixed place; a chip
  tick is also a dimmed state; the focus word is also underlined. Colour confirms;
  it never carries meaning alone.
- Visible focus: a `--accent` ring on every interactive element.
- Respect `prefers-reduced-motion`; motion is never required to understand state.

---

## What travels to the platform, and what doesn't

- **Travels:** the token set and its *roles*; the type roles + scale; the accent
  semantics (`--accent` = the system's voice, `--mark` = the learner's hand); the
  marginalia idea as a way to present reasoning.
- **Stays with the page:** the masthead/running-head, the mode-toggle specifics,
  the single-file inlining, exact margins.

The platform inherits the system; each topic re-uses it and only supplies its own
content.

---

## Open decisions

- **The faces** — settle next, by mocking 2–3 offline-safe options (embedded-
  subsetted vs. system-only) in the page and comparing.
- Whether a third structural accent is ever needed (default: no).
- The exact margin width and its breakpoint.
- The map's precise treatment of the traced route vs. static structure.
