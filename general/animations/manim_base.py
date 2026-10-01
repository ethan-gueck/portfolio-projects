"""Topic-agnostic Manim helpers: themed scene, axes from a Viewport, LaTeX fallback.

Requires ``manim``. Import this only from scene modules, never from calculation
or HTML code, so those keep working without Manim installed.
"""

from __future__ import annotations

import shutil

from manim import DOWN, LEFT, Axes, NumberPlane, Scene, Text, VGroup, VMobject

from ..plotting import Viewport
from ..themes import Theme, get_theme

HAS_LATEX = shutil.which("latex") is not None


def _fmt(value: float) -> str:
    return f"{round(value, 10) + 0:.4g}"


def _font(theme: Theme) -> str:
    """First family of the theme's sans stack (Pango falls back if it isn't installed)."""
    return theme.fonts["sans"].split(",")[0].strip().strip('"')


class ThemedScene(Scene):
    """Scene that applies a theme's stage background and exposes styling helpers.

    Set the ``theme`` class attribute (name or Theme) to switch looks.
    """

    theme: str | Theme | None = None

    def setup(self):
        self.style = get_theme(self.theme)
        self.camera.background_color = self.style.manim_color("background")[0]

    def color(self, role: str) -> str:
        return self.style.manim_color(role)[0]

    def text(self, text: str, role: str = "text", font_size: float = 24) -> Text:
        color, opacity = self.style.manim_color(role)
        return Text(text, font=_font(self.style), font_size=font_size, color=color).set_opacity(opacity)

    def plate(self, mobject: VMobject) -> VMobject:
        """Add the theme's translucent label background (like the canvas engine's label plates)."""
        color, opacity = self.style.manim_color("plate")
        return mobject.add_background_rectangle(color=color, opacity=opacity, buff=0.06)

    def math(self, tex: str, plain: str, *, role: str = "text", font_size: float = 36) -> VMobject:
        """MathTex when LaTeX is installed, otherwise an equivalent plain ``Text``."""
        if HAS_LATEX:
            from manim import MathTex

            return MathTex(tex, font_size=font_size, color=self.color(role))
        return self.text(plain, role, font_size * 0.8)

    def axes(self, view: Viewport, *, x_length: float = 10, y_length: float = 5.4, grid: bool = True) -> VGroup:
        """Axes (and an aligned faint NumberPlane) sized to the viewport.

        Returns ``VGroup(plane?, axes, numbers?)``; use ``group.axes`` for coordinates.
        """
        common = dict(x_range=list(view.x_range), y_range=list(view.y_range), x_length=x_length, y_length=y_length)
        axes_color, axes_opacity = self.style.manim_color("axes")
        axes = Axes(
            **common,
            tips=False,
            axis_config={"color": axes_color, "stroke_opacity": axes_opacity, "include_numbers": HAS_LATEX, "font_size": 20},
        )
        group = VGroup()
        if grid:
            grid_color, grid_opacity = self.style.manim_color("grid")
            plane = NumberPlane(
                **common,
                background_line_style={"stroke_color": grid_color, "stroke_opacity": max(grid_opacity, 0.12), "stroke_width": 1},
            )
            plane.x_axis.set_opacity(0)
            plane.y_axis.set_opacity(0)
            group.add(plane)
        group.add(axes)
        if not HAS_LATEX:
            group.add(self._tick_numbers(axes, view))
        group.axes = axes
        return group

    def _tick_numbers(self, axes: Axes, view: Viewport) -> VGroup:
        numbers = VGroup()
        x = view.x_min
        while x <= view.x_max + 1e-9:
            if abs(x) > 1e-9:
                numbers.add(self.text(_fmt(x), "muted", 16).next_to(axes.c2p(x, 0), DOWN, buff=0.15))
            x += view.x_step
        y = view.y_min
        while y <= view.y_max + 1e-9:
            if abs(y) > 1e-9:
                numbers.add(self.text(_fmt(y), "muted", 16).next_to(axes.c2p(0, y), LEFT, buff=0.15))
            y += view.y_step
        return numbers
