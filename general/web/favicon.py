"""The tab icon: the portfolio's "EG" mark, green in light mode and blue-grey in dark.

Inlined as data URIs so pages stay self-contained. The <link> carries both; the dark-mode
snippet in <head> (web/page.py) switches to ``data-dark`` before first paint, and the theme
button (styles/js/mode.js) reloads the page into the other mode.
"""

from __future__ import annotations

from urllib.parse import quote

_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient></defs>'
    '<rect width="64" height="64" rx="12" fill="url(#g)"/>'
    '<text x="32" y="43" font-family="Georgia,serif" font-size="30" text-anchor="middle" fill="{text}">EG</text></svg>'
)

LIGHT = _MARK.format(start="#072A20", end="#125A43", text="#D8C3A5")
DARK = _MARK.format(start="#0C2236", end="#334E68", text="#E5A93C")


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml," + quote(svg, safe="=:/,")


def favicon_link() -> str:
    """The <link rel="icon"> tag, light icon by default with the dark one in ``data-dark``."""
    light, dark = _data_uri(LIGHT), _data_uri(DARK)
    return f'\n  <link rel="icon" type="image/svg+xml" href="{light}" data-light="{light}" data-dark="{dark}">'
