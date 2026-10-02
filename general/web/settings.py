"""The gear menu in the corner of an animation stage: the page's "show" toggles.

A page lists what its animation can show (grid, labels, intercepts, ...) and
puts ``{{stage_settings}}`` inside its ``.stage``; render_page(show=...) fills
it with a gear button that opens the toggles. Each toggle is an
``<input type="checkbox" data-show="key">``, so page controllers read and watch
them exactly as before. styles/js/stage_settings.js closes the menu on an
outside click or Escape; the look is in components/stage.css.
"""

from __future__ import annotations

import html

_GEAR_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/>'
    '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1'
    'a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1'
    'a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1'
    'a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1'
    'a1.7 1.7 0 0 0-1.5 1z"/></svg>'
)

ShowOption = tuple[str, str] | tuple[str, str, bool]


def stage_settings(show: list[ShowOption] | tuple[ShowOption, ...]) -> str:
    """The gear button and its menu: one checkbox per ``(key, label)`` or ``(key, label, checked)``."""
    boxes = []
    for option in show:
        key, label, checked = (*option, True) if len(option) == 2 else option
        boxes.append(
            f'<label class="check"><input type="checkbox" data-show="{html.escape(key)}"{" checked" if checked else ""}> {html.escape(label)}</label>'
        )
    return (
        '<details class="stage-settings">'
        f'<summary class="stage-settings__toggle" aria-label="Display options" title="Display options">{_GEAR_ICON}</summary>'
        '<div class="stage-settings__menu" role="group" aria-label="Show on the animation">'
        '<p class="stage-settings__title">Show</p>'
        f'<div class="stage-settings__checks">{"".join(boxes)}</div>'
        "</div></details>"
    )
