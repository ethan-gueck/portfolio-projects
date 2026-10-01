"""Render any Manim scene programmatically (no CLI needed)."""

from __future__ import annotations

from pathlib import Path

QUALITIES = ("low_quality", "medium_quality", "high_quality", "production_quality", "fourk_quality")


def require_manim() -> None:
    try:
        import manim  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SystemExit("Manim is not installed. See general/README.md -> 'Manim setup'.") from exc


def render_scene(
    scene_cls,
    *,
    media_dir: str | Path,
    quality: str = "low_quality",
    file_name: str | None = None,
    fmt: str = "mp4",
    preview: bool = False,
) -> Path:
    """Render a Scene class and return the path of the video (or gif) produced."""
    if quality not in QUALITIES:
        raise ValueError(f"quality must be one of {QUALITIES}")
    if fmt not in ("mp4", "gif"):
        raise ValueError("fmt must be 'mp4' or 'gif'")
    require_manim()
    from manim import tempconfig

    options = {"quality": quality, "media_dir": str(media_dir), "preview": preview, "format": fmt}
    if file_name:
        options["output_file"] = file_name
    with tempconfig(options):
        scene = scene_cls()
        scene.render()
        writer = scene.renderer.file_writer
        return Path(writer.gif_file_path if fmt == "gif" else writer.movie_file_path)
