"""Manim helpers shared by every topic.

Importing this package does not import Manim; import ``manim_base`` (which
does) from scene modules only. ``render_scene`` imports Manim lazily.
"""

from .render import QUALITIES, render_scene, require_manim

__all__ = ["QUALITIES", "render_scene", "require_manim"]
