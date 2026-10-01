"""Colour parsing shared by the Manim and HTML layers."""

from __future__ import annotations

import re

_RGBA = re.compile(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)")


def split_alpha(color: str) -> tuple[str, float]:
    """CSS colour -> ('#RRGGBB', opacity). Accepts #RGB, #RRGGBB and rgb()/rgba().

    Manim takes colour and opacity separately, so rgba() theme values are
    split here rather than duplicated in the theme.
    """
    color = color.strip()
    if color.startswith("#"):
        hex_part = color[1:]
        if len(hex_part) == 3:
            hex_part = "".join(ch * 2 for ch in hex_part)
        if len(hex_part) != 6:
            raise ValueError(f"Unsupported hex colour {color!r}")
        return f"#{hex_part.upper()}", 1.0
    match = _RGBA.fullmatch(color)
    if not match:
        raise ValueError(f"Unsupported colour {color!r}; use #hex or rgb()/rgba()")
    r, g, b, a = match.groups()
    return "#" + "".join(f"{round(float(v)):02X}" for v in (r, g, b)), float(a) if a is not None else 1.0
