# English Article Helper 📖

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=github)](https://micahammon.github.io/article-helper/index.html)

An interactive, rule-based tool to help English learners choose the correct article (`a/an`, `the`, or no article). This project is built with pure HTML, CSS, and JavaScript, translating the logic from Seonaid Beckwith's excellent guide, "'A' and 'The' Explained".

---

### Live Demonstration

See the tool in action below! For the full interactive experience, **[click here to visit the live demo site](https://micahammon.github.io/article-helper/)**.

![English Article Helper Demo](demo.gif)

---

### How It Works

The tool uses a two-pronged approach to determine the correct article:

1.  **Lookup Table:** A direct lookup for nouns with fixed, specific rules (e.g., proper nouns like "the USA", abstract concepts like "music", or systems like "the internet"). This provides an instant, accurate answer for common exceptions.

    The lookup step automatically normalizes what you type—trimming extra spaces, ignoring a leading "a/an/the", and removing simple punctuation—so entries such as "the USA" or "an opera" still match the right rule immediately.

2.  **Decision Tree:** For all other nouns, the tool guides the user through a series of contextual questions. By asking about specificity, listener knowledge, and the noun's function (e.g., general concept, institution, classification), it follows a logical path to deduce the correct article based on the rules of English grammar.

Both data sets live in a single machine-readable file, [`rules_data.json`](rules_data.json). The Python logic and the browser UI read from the same source so they always stay in sync.

### How to Use

1.  **Enter Text:** Type a noun, phrase, or full sentence (for example, `I bought book yesterday`).
2.  **Analyze Phrase:** Click the "Analyze Phrase" button.
3.  **Get an Instant Rule Match (when possible):** The app first tries to detect a focus noun/phrase and match it directly to known rules.
4.  **Follow Guided Questions (if needed):** If no direct match is found, the tool asks learner-friendly context questions.
5.  **Read the Result + Example:** The final output includes the recommended article, explanation, example sentence, and source section reference.

### Running Locally

Because the browser app now fetches its rules from `rules_data.json`, you should serve the files over HTTP when running locally.

1.  Clone this repository or download the project files.
2.  From the project directory, start a simple web server: `python -m http.server`
3.  Open `http://localhost:8000/index.html` in any modern web browser.

The Tkinter desktop app (`app.py`) reads the same JSON file, so no extra setup is required beyond installing its Python dependencies.


Added unit tests for phrase-first analysis behavior. New file:
`tests/test_phrase_first.py`.

You can run all tests with:

`python -m unittest discover -s tests -v`

from `C:\Users\meeky\OneDrive\Documents\#Dev\Article-Helper`.
