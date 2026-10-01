"""Themes shared by every project page and animation.

    from general.themes import get_theme
    theme = get_theme()              # default: "portfolio"
    theme = get_theme("manim")
    custom = get_theme().variant("portfolio-gold", stage={"primary": "#F2C14E"})
    register_theme(custom)
"""

from __future__ import annotations

from .color import split_alpha
from .manim import MANIM
from .portfolio import PORTFOLIO
from .theme import SEMANTIC_TOKENS, STAGE_ROLES, Theme

DEFAULT_THEME = "portfolio"
THEMES: dict[str, Theme] = {}


def register_theme(theme: Theme) -> Theme:
    THEMES[theme.name] = theme
    return theme


def get_theme(theme: str | Theme | None = None) -> Theme:
    """Look up a theme by name (``None`` = default); Theme instances pass through."""
    if isinstance(theme, Theme):
        return theme
    name = theme or DEFAULT_THEME
    try:
        return THEMES[name]
    except KeyError:
        raise KeyError(f"Unknown theme {name!r}; available: {sorted(THEMES)}") from None


register_theme(PORTFOLIO)
register_theme(MANIM)

__all__ = [
    "DEFAULT_THEME",
    "MANIM",
    "PORTFOLIO",
    "SEMANTIC_TOKENS",
    "STAGE_ROLES",
    "THEMES",
    "Theme",
    "get_theme",
    "register_theme",
    "split_alpha",
]
