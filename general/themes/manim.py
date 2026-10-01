"""Classic dark Manim look (Manim Community default palette)."""

from .theme import SCALE_TOKENS, Theme

MANIM_COLORS = {
    "BLUE": "#58C4DD",
    "BLUE_D": "#29ABCA",
    "TEAL": "#5CD0B3",
    "GREEN": "#83C167",
    "YELLOW": "#FFFF00",
    "GOLD": "#F0AC5F",
    "RED": "#FC6255",
    "GREY": "#888888",
    "GREY_B": "#BBBBBB",
    "WHITE": "#FFFFFF",
}

MANIM = Theme(
    name="manim",
    label="Manim (dark)",
    color_scheme="dark",
    tokens={
        **SCALE_TOKENS,
        "bg": "#0E0E0E",
        "surface": "#181818",
        "text": "#FFFFFF",
        "text-soft": "#BBBBBB",
        "rule": "#2A2A2A",
        "primary": MANIM_COLORS["TEAL"],
        "primary-strong": "#3FAE93",
        "primary-soft": "#7FDCC4",
        "on-primary": "#0E0E0E",
        "on-gradient": "#FFFFFF",
        "accent": MANIM_COLORS["BLUE"],
        "accent-soft": "#9ADCEB",
        "accent-strong": MANIM_COLORS["BLUE_D"],
        "gradient-primary": "linear-gradient(135deg, #111 0%, #1B1B1B 60%, #232323 100%)",
        "shadow-paper": "none",
        "shadow-stage": "0 12px 30px rgba(0,0,0,0.5)",
        "focus": "0 0 0 2px #0E0E0E, 0 0 0 4px #5CD0B3",
    },
    stage={
        "background": "#0E0E0E",
        "grid": "rgba(41,171,202,0.28)",
        "axes": MANIM_COLORS["GREY_B"],
        "text": MANIM_COLORS["WHITE"],
        "muted": MANIM_COLORS["GREY_B"],
        "primary": MANIM_COLORS["BLUE"],
        "highlight": MANIM_COLORS["YELLOW"],
        "point": MANIM_COLORS["RED"],
        "secondary": MANIM_COLORS["GREEN"],
        "guide": MANIM_COLORS["GREY"],
        "warning": MANIM_COLORS["GOLD"],
        "plate": "rgba(14,14,14,0.8)",
    },
    fonts={
        "serif": '"Times New Roman", Georgia, serif',
        "sans": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
        "mono": "ui-monospace, SFMono-Regular, Menlo, monospace",
    },
)
