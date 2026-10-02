# general/

This folder holds the shared building blocks for every project: themes, CSS and JS, plotting, Manim helpers, the page builder, and the static API. Topics live in the domain repos (such as [algebra/a1](https://github.com/ethan-gueck/algebra/tree/main/a1)) and contain only their own math, scene, page and `api.py`; each domain repo installs this package from git (see the [repo README](../README.md)).

```
general/
├── themes/            Theme dataclass; "portfolio" (default, from ethan-gueck.github.io) and "manim" (dark)
├── styles/            Bundle loader (Python) + shared assets
│   ├── css/           base.css, layout.css, components/{masthead,controls,stage,results,steps,catalog}.css
│   └── js/            manim_canvas.js (Manim-style canvas engine), params.js (URL hash), frame.js (embed resize)
├── plotting/          viewport.py: plot window and tick spacing
├── animations/        render_scene(), manim_base.ThemedScene (theme-aware Manim helpers)
├── web/               render_page(): template + themed bundle + JSON config → one HTML file; site index template
├── api/               topic registry, manifest/site build, pp.js browser client
├── jsrun.py           run browser JS from Python (Node or macOS JavaScriptCore) for parity tests
└── tests/
```

## Themes

A theme has three parts:

- **Page tokens**: CSS variables. Shared CSS only uses the semantic names (`--bg`, `--surface`, `--text`, `--primary`, `--accent`, `--gradient-primary`, and so on), so any complete theme works with every component.
- **Stage palette**: literal colours for drawing on the animation stage. Both `manim_canvas.js` and Manim scenes use it. The roles are generic (`primary`, `highlight`, `point`, `secondary`, `guide`, `warning`, and more), and each topic maps its own elements onto them (see `a1/style.py` in the algebra repo).
- **Fonts**: the portfolio theme loads Newsreader and IBM Plex Sans from Google Fonts, the same as your site.

```python
from general.themes import get_theme, register_theme

theme = get_theme()                  # "portfolio"
dark = get_theme("manim")
gold = theme.variant("portfolio-gold", stage={"primary": "#F2C14E"})   # dict fields merge
register_theme(gold)                 # now usable by name everywhere (pages, CLI, build)
theme.css()                          # :root { --green-800: #0B3D2E; ... }
```

## Styles

```python
from general.styles import BASE, WIDGET

bundle = WIDGET.extend(css=[HERE / "topic.css"], js=[HERE / "topic_math.js", HERE / "topic.js"])
```

A shared asset is named by a string (`"components/stage.css"`) and a topic file by a `Path`. `bundle.css_text(theme)` always puts the theme variables first.

## Pages

```python
from general.web import render_page, write_page

html = render_page(TEMPLATE, title="...", config={...}, theme="portfolio", bundle=bundle)
```

Template placeholders are `{{title}} {{head}} {{styles}} {{scripts}} {{config}} {{theme_name}}`, plus any `extra` values you pass. The config is embedded as `<script id="pp-config">` and includes `theme` (the stage palette and fonts).

## Static API (GitHub Pages)

GitHub Pages only serves static files, so it can't run Python. The API therefore runs in the browser:

1. Each topic's Python `core/` is mirrored by a small JS module, and parity tests keep the two identical.
2. The topic declares its modules and pages in `api.py`.
3. `python -m general build`, run inside a domain repo, publishes its topics to `_site/`, including `api/v1/manifest.json` and the `api/v1/pp.js` client. `[tool.portfolio-site]` in that repo's `pyproject.toml` gives the site's title and URL.
4. The domain repo's `.github/workflows/pages.yml` runs its tests and deploys `_site/` on every push to `main`.

**One-time setup per domain repo:** Settings → Pages → Source: **GitHub Actions**. The site is then live at `https://ethan-gueck.github.io/<domain>/`.

Each topic's manifest entry also lists `cards`, the flashcard ids its pages cover; the portfolio's "Ethan's NN" tab reads every domain's manifest and fills those neurons.

### Using it from any page (e.g. ethan-gueck.github.io)

```html
<script src="https://ethan-gueck.github.io/algebra/api/v1/pp.js"></script>
<div id="quadratic"></div>
<script>
  // 1. Compute: load the module and call it
  PP.call("a1/quadratic", "solve", 1, -3, 2).then((s) => console.log(s.roots, s.vertex));
  const q = await PP.use("a1/quadratic");        // or keep the module: q.discriminant(1, -3, 2)

  // 2. Embed the interactive page (auto-sized iframe, banner hidden)
  const widget = await PP.embed("#quadratic", "a1/quadratic", { a: 1, b: 2, c: 5 });
  widget.set({ c: -4 });                                 // update it live

  // 3. Style your own markup with the shared theme + components
  PP.useTheme("portfolio");
  // PP.list() → every module, function signature and page in the manifest
</script>
```

`ethan-gueck.github.io` and every `ethan-gueck.github.io/<domain>/` site share an origin, so these calls need no CORS setup.

### Local preview

```bash
# inside a domain repo:
uv run python -m general serve   # build _site/ and serve it at http://localhost:8000
uv run python -m general manifest # print the manifest
```

## Adding a topic

1. The mathematics goes in the neuron's section of the domain repo's `core/formula.py`, written the way it reads (no input checks, rounding cleanup or formatting); this is the only code the page's "View the code" popup shows (`CodeFile(..., only=(...))`).
2. In the domain repo, add a topic folder (e.g. `unit_circle/` in trigonometry; the folder path becomes the API id) with a `solver.py` built on `core.formula`, whose `solve()` result has `to_dict()`. The algebra repo has worked examples.
3. Write a JS mirror in `html/static/<topic>_math.js`, plus a parity test built on `general.jsrun`.
4. Page: a template, plus `WIDGET.extend(...)` with the topic's CSS/JS. The animation's show toggles go in the gear menu in the stage's corner: pass `show=(("grid", "Grid"), ...)` to `render_page` and put `{{stage_settings}}` inside `.stage`. Scene: subclass `ThemedScene`.
5. Declare `TOPIC` in `api.py`, with `cards=("T.3",)` for the flashcards it covers. The build and tests pick it up automatically.

## Manim setup

The environment is managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`, `.venv/`). Manim is only needed for videos. On macOS:

```bash
brew install pkgconf cairo pango      # system libraries pycairo/manimpango build against
uv sync                               # dev + animations groups into .venv (general/ installed editable)
uv sync --only-group dev              # lighter: tests and site build only (what CI uses)
# optional LaTeX for MathTex formulas: brew install --cask mactex-no-gui
```

Without LaTeX, scenes fall back to plain `Text`.
