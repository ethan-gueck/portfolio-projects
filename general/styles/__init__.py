"""Shared CSS/JS assets and bundles of them.

Assets live next to this file (``css/``, ``js/``) and are referenced by name
(``"components/stage.css"``, ``"manim_canvas.js"``). Topic-local files are
passed as ``Path`` objects and mixed in freely.

    from general.styles import WIDGET
    bundle = WIDGET.extend(css=[HERE / "quadratic.css"], js=[HERE / "quadratic.js"])
    bundle.css_text(theme), bundle.js_text()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Union

from ..themes import Theme, get_theme

STYLES_DIR = Path(__file__).resolve().parent
CSS_DIR = STYLES_DIR / "css"
JS_DIR = STYLES_DIR / "js"

Asset = Union[str, Path]


def resolve(asset: Asset, kind: str) -> Path:
    """A shared asset name (``str``) -> its path; a ``Path`` is returned as-is."""
    if isinstance(asset, Path):
        path = asset
    else:
        path = (CSS_DIR if kind == "css" else JS_DIR) / asset
    if not path.is_file():
        raise FileNotFoundError(f"{kind} asset not found: {asset} ({path})")
    return path


def read_assets(assets: Iterable[Asset], kind: str) -> str:
    parts = []
    for asset in assets:
        path = resolve(asset, kind)
        label = path.relative_to(STYLES_DIR) if path.is_relative_to(STYLES_DIR) else path.name
        parts.append(f"/* ---- {label} ---- */\n{path.read_text()}")
    return "\n\n".join(parts)


def shared_assets(kind: str) -> list[Path]:
    """Every shared CSS or JS file (used when publishing the site)."""
    root = CSS_DIR if kind == "css" else JS_DIR
    return sorted(p for p in root.rglob(f"*.{kind}") if p.is_file())


@dataclass(frozen=True)
class Bundle:
    """An ordered set of stylesheets and scripts that a page inlines."""

    css: tuple[Asset, ...] = ()
    js: tuple[Asset, ...] = ()

    def extend(self, *, css: Iterable[Asset] = (), js: Iterable[Asset] = ()) -> "Bundle":
        return Bundle(self.css + tuple(css), self.js + tuple(js))

    def css_text(self, theme: str | Theme | None = None) -> str:
        """Theme variables first, then every stylesheet in order."""
        return get_theme(theme).css() + "\n" + read_assets(self.css, "css")

    def js_text(self) -> str:
        return read_assets(self.js, "js")


BASE = Bundle(css=("base.css", "layout.css", "components/masthead.css", "components/code.css", "components/site-footer.css", "components/dark.css"), js=("mode.js", "frame.js"))

# Interactive widget: stage + control panel + results + derivation steps.
WIDGET = BASE.extend(
    css=("components/controls.css", "components/stage.css", "components/results.css", "components/steps.css"),
    js=("params.js", "manim_canvas.js"),
)

__all__ = ["BASE", "WIDGET", "Bundle", "CSS_DIR", "JS_DIR", "read_assets", "resolve", "shared_assets"]
