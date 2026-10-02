"""Generic page builder: template + themed CSS/JS bundle + JSON config -> one HTML file.

CSS and JS are inlined so the page is one self-contained file that works
opened locally, on GitHub Pages, or inside a PP.embed() iframe. Only web
fonts load from the network, with system fallbacks. Templates use ``{{name}}``
placeholders; an unknown placeholder raises so typos surface early.

Placeholders: title, head (font links), styles, scripts, config, footer,
code_button, plus any ``extra`` values passed in. Pages that pass ``code``
(web/code.py) put ``{{code_button}}`` where the "View the code" button goes. Every page gets the portfolio's call to action
and footer (web/footer.py): at ``{{footer}}`` if the template has it,
otherwise just before ``</body>``.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from ..styles import WIDGET, Bundle
from ..themes import DARK_MODES, Theme, get_theme
from .code import CodeFile, code_viewer
from .footer import site_footer

# Dark mode before first paint, from the choice saved on ethan-gueck.github.io (same origin).
_DARK_SNIPPET = (
    "\n  <script>try { if (localStorage.getItem('pp-theme') === 'dark') "
    "document.documentElement.dataset.mode = 'dark'; } catch (e) {}</script>"
)

_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def json_for_script(data: dict) -> str:
    """JSON that is safe inside a <script> tag."""
    return json.dumps(data, indent=2).replace("</", "<\\/")


def fill_template(template: str | Path, values: dict[str, str]) -> str:
    text = Path(template).read_text() if isinstance(template, Path) else template

    def substitute(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"Unknown placeholder {{{{{key}}}}} in {template if isinstance(template, Path) else 'template'}")
        return values[key]

    return _PLACEHOLDER.sub(substitute, text)


def render_page(
    template: str | Path,
    *,
    title: str,
    config: dict | None = None,
    theme: str | Theme | None = None,
    bundle: Bundle = WIDGET,
    extra: dict[str, str] | None = None,
    footer: bool = True,
    code: list[CodeFile] | tuple[CodeFile, ...] = (),
) -> str:
    """Fill a template and return the full HTML document.

    ``config`` is embedded as JSON (``<script id="pp-config">``) with the
    theme's stage palette added under ``"theme"``. ``footer=False`` leaves out
    the call to action and footer. ``code`` lists the files shown in the
    "View the code" popup.
    """
    text = Path(template).read_text() if isinstance(template, Path) else template
    if code and "{{code_button}}" not in text:
        raise ValueError("Pages that pass `code` need a {{code_button}} placeholder in their template.")
    button, dialog = code_viewer(code, title) if code else ("", "")
    theme = get_theme(theme)
    dark = DARK_MODES.get(theme.name)
    config = {**(config or {}), "theme": theme.to_dict()}
    if dark:
        config["theme_dark"] = dark.to_dict()
    values = {
        "title": html.escape(title),
        "head": theme.head_links() + (_DARK_SNIPPET if dark else ""),
        "styles": bundle.css_text(theme) + ("\n" + dark.css(':root[data-mode="dark"]') if dark else ""),
        "scripts": bundle.js_text(),
        "config": json_for_script(config),
        "theme_name": theme.name,
        "footer": dialog + (site_footer(title) if footer else ""),
        "code_button": button,
        **(extra or {}),
    }
    document = fill_template(template, values)
    if (footer or dialog) and "{{footer}}" not in text and "</body>" in document:
        head, _, tail = document.rpartition("</body>")
        document = head + values["footer"] + "</body>" + tail
    return document


def write_page(document: str, output_path: str | Path) -> Path:
    """Write the document, creating parent folders; returns the resolved path."""
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")
    return path
