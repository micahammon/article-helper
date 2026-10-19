/*
 * Parity guard: run every corpus example through the *browser* engine.
 *
 * examples_data.json is verified at build time against the Python engine
 * (logic.py). Learners, though, get their answers from the JavaScript engine
 * inlined in index.html. The two are meant to agree, and the suite already
 * guards that in general -- but a vetted example is a promise to a learner, so
 * this checks the promise directly: it loads the real engine out of index.html
 * and asserts the JS gives each example the same form the corpus recorded.
 *
 * No browser and no dependencies: the engine's functions are pure, so they run
 * under Node's `vm` with a thin DOM stub standing in for the page wiring that
 * runs at load time. Prints JSON; exits 0 on parity, 1 on drift, 2 if the
 * engine could not be loaded at all.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const corpus = JSON.parse(
  fs.readFileSync(path.join(ROOT, "examples_data.json"), "utf8"));

/* Pull a named JSON block out of the page. */
function jsonBlock(id) {
  const open = '<script id="' + id + '" type="application/json">';
  const start = html.indexOf(open);
  if (start === -1) throw new Error("no " + id + " block in index.html");
  const from = start + open.length;
  return html.slice(from, html.indexOf("</script>", from)).trim();
}

/* The engine is the plain <script> block (no attributes) after the data. */
function engineCode() {
  const marker = html.indexOf('"use strict"');
  const open = html.lastIndexOf("<script>", marker);
  const close = html.indexOf("</script>", marker);
  if (open === -1 || close === -1) throw new Error("could not find engine script");
  return html.slice(open + "<script>".length, close);
}

/* A DOM element that never throws, whatever the page does to it. Unknown
   properties resolve to a no-op that returns another stub, so chained calls and
   event wiring at load time run harmlessly. */
function makeEl() {
  const base = {
    style: {}, dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    textContent: "", innerHTML: "", value: "", checked: false, hidden: false,
  };
  return new Proxy(base, {
    get(t, p) { return p in t ? t[p] : function () { return makeEl(); }; },
    set(t, p, v) { t[p] = v; return true; },
  });
}

function buildSandbox() {
  const cache = {};
  const document = {
    getElementById(id) {
      if (id === "rules-data") return { textContent: jsonBlock("rules-data") };
      // the corpus is not needed to answer; an empty block keeps boot happy
      if (id === "examples-data") return { textContent: '{"examples":[]}' };
      return cache[id] || (cache[id] = makeEl());
    },
    createElement() { return makeEl(); },
    createTextNode() { return makeEl(); },
    addEventListener() {}, removeEventListener() {},
    querySelector() { return makeEl(); }, querySelectorAll() { return []; },
    body: makeEl(), documentElement: makeEl(),
  };
  const sandbox = {
    document, console,
    localStorage: {
      _s: {}, getItem(k) { return k in this._s ? this._s[k] : null; },
      setItem(k, v) { this._s[k] = String(v); }, removeItem(k) { delete this._s[k]; },
    },
    matchMedia() { return { matches: false, addEventListener() {}, addListener() {} }; },
    setTimeout() { return 0; }, clearTimeout() {},
    requestAnimationFrame() { return 0; },
    location: { href: "", reload() {} },
    JSON, Math, Date, RegExp, Object, Array, String, Number, Boolean, parseInt, parseFloat,
  };
  sandbox.window = sandbox;
  return sandbox;
}

function main() {
  const sandbox = buildSandbox();
  vm.createContext(sandbox);
  try {
    vm.runInContext(engineCode(), sandbox, { filename: "index.html:engine" });
  } catch (err) {
    console.log(JSON.stringify({ ok: false, loaded: false, error: String(err) }));
    process.exit(2);
  }

  const { D, formOf, gate0Pinned } = sandbox;
  if (!D || typeof gate0Pinned !== "function" || typeof formOf !== "function") {
    console.log(JSON.stringify({ ok: false, loaded: false,
      error: "engine loaded but D/gate0Pinned/formOf missing (boot did not run)" }));
    process.exit(2);
  }

  const failures = [];
  for (const e of corpus.examples) {
    const expected = formOf(e.verified_article);
    const hit = gate0Pinned(e.text, e.word);
    const actual = hit ? hit.form : null;
    if (actual !== expected) {
      failures.push({ text: e.text, word: e.word,
        article: e.verified_article, expected, actual });
    }
  }

  console.log(JSON.stringify({
    ok: failures.length === 0, loaded: true,
    checked: corpus.examples.length, failures,
  }, null, 2));
  process.exit(failures.length === 0 ? 0 : 1);
}

main();
