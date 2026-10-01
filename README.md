# portfolio-projects

The shared library behind Ethan's formula pages: themes, CSS/JS, plotting, Manim helpers, the page builder and the static API (`pp.js` + manifest), all in [`general/`](general/). Read [general/README.md](general/README.md) first.

The topics themselves live in one repo per domain, each published to its own GitHub Pages site (`https://ethan-gueck.github.io/<domain>/`) and each with its own 1 GB Pages budget. Each domain repo installs this package from git:

| Domain repo | Flashcard decks |
| --- | --- |
| [algebra](https://github.com/ethan-gueck/algebra) | Algebra I, Algebra II |
| [geometry](https://github.com/ethan-gueck/geometry) | Geometry |
| [trigonometry](https://github.com/ethan-gueck/trigonometry) | Trigonometry |
| [calculus](https://github.com/ethan-gueck/calculus) | Calculus I, Calculus II |
| [vector-calculus](https://github.com/ethan-gueck/vector-calculus) | Multivariable & Vector Calculus |
| [linear-algebra](https://github.com/ethan-gueck/linear-algebra) | Linear Algebra |
| [statistics](https://github.com/ethan-gueck/statistics) | Statistics & Probability |
| [functions-distributions](https://github.com/ethan-gueck/functions-distributions) | Probability Distributions |
| [machine-learning](https://github.com/ethan-gueck/machine-learning) | Machine Learning |
| [algorithms](https://github.com/ethan-gueck/algorithms) | Algorithms |
| [optimization](https://github.com/ethan-gueck/optimization) | Optimization & Simulation |
| [finance](https://github.com/ethan-gueck/finance) | Finance, Finance Terms |
| [physics](https://github.com/ethan-gueck/physics) | Physics & Natural Phenomena |
| [electrical-engineering](https://github.com/ethan-gueck/electrical-engineering) | Electrical Engineering, EE Symbols, EE Terms |
| [key-terms](https://github.com/ethan-gueck/key-terms) | Key Terms |
| [acronyms](https://github.com/ethan-gueck/acronyms) | Acronyms |
| [greek-alphabet](https://github.com/ethan-gueck/greek-alphabet) | Greek Alphabet |

A domain repo's `pyproject.toml` declares the dependency and names its site:

```toml
dependencies = ["portfolio-projects"]

[tool.uv.sources]
portfolio-projects = { git = "https://github.com/ethan-gueck/portfolio-projects", branch = "main" }

[tool.portfolio-site]
title = "Algebra"
url = "https://ethan-gueck.github.io/algebra/"
```

After changing `general/` here and pushing to `main`, update a domain repo with `uv lock --upgrade-package portfolio-projects`.

```bash
uv sync                              # install everything into .venv (see general/README.md for Manim's system deps)
uv run pytest                        # general/'s tests (against general/tests/fixtures/demo_site)
```

Pushing to `main` runs `.github/workflows/tests.yml`. This repo has no Pages site of its own.
