"""Topic-agnostic plotting helpers: picking a window and tick spacing.

Nothing here knows about any one topic, so every project (trig, calculus, ...)
can reuse it as-is. Mirrored in JS by each topic that needs live updates.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Callable, Iterable


def nice_step(span: float, target_ticks: int = 8) -> float:
    """A 1/2/5 × 10ⁿ tick spacing that gives roughly ``target_ticks`` ticks."""
    if span <= 0:
        return 1.0
    raw = span / target_ticks
    magnitude = 10 ** math.floor(math.log10(raw))
    for multiple in (1, 2, 5, 10):
        if raw <= multiple * magnitude:
            return multiple * magnitude
    return 10 * magnitude


@dataclass(frozen=True)
class Viewport:
    """Visible region of the plane plus tick spacing for each axis."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    x_step: float
    y_step: float

    @property
    def x_range(self) -> tuple[float, float, float]:
        """Manim-style [min, max, step]."""
        return self.x_min, self.x_max, self.x_step

    @property
    def y_range(self) -> tuple[float, float, float]:
        return self.y_min, self.y_max, self.y_step

    def to_dict(self) -> dict:
        return asdict(self)


def _snap_outward(lo: float, hi: float, step: float) -> tuple[float, float]:
    return math.floor(lo / step) * step, math.ceil(hi / step) * step


def fit_viewport(
    xs: Iterable[float],
    f: Callable[[float], float],
    *,
    always_include_y: Iterable[float] = (),
    padding: float = 0.25,
    min_span: float = 4.0,
    samples: int = 101,
) -> Viewport:
    """Frame the given x-values, then size y so the whole curve on that x-range fits.

    The x-range covers ``xs`` plus ``padding`` of the span on each side; the
    y-range covers ``f`` sampled over it and every value in ``always_include_y``.
    Both ranges are snapped outward to their tick spacing.
    """
    xs = list(xs)
    lo, hi = min(xs), max(xs)
    span = max(hi - lo, min_span)
    mid = (lo + hi) / 2
    x_lo, x_hi = mid - span * (0.5 + padding), mid + span * (0.5 + padding)
    x_step = nice_step(x_hi - x_lo)
    x_lo, x_hi = _snap_outward(x_lo, x_hi, x_step)

    ys = [f(x_lo + (x_hi - x_lo) * i / (samples - 1)) for i in range(samples)]
    ys += list(always_include_y)
    y_lo, y_hi = min(ys), max(ys)
    if y_hi - y_lo < min_span:
        centre = (y_lo + y_hi) / 2
        y_lo, y_hi = centre - min_span / 2, centre + min_span / 2
    y_pad = (y_hi - y_lo) * 0.08
    y_step = nice_step(y_hi - y_lo + 2 * y_pad)
    y_lo, y_hi = _snap_outward(y_lo - y_pad, y_hi + y_pad, y_step)

    return Viewport(x_lo, x_hi, y_lo, y_hi, x_step, y_step)
