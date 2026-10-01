"""Default theme, taken from ethan-gueck.github.io (assets/css/tokens.css).

Page: cool paper background, white sheets, deep-green gradient mastheads,
sand accents, Newsreader serif body with IBM Plex Sans for UI.
Stage: the green gradient and sand/gold palette of the site's COBYLA demo.
"""

from .theme import SCALE_TOKENS, Theme

BRAND = {
    "green-900": "#072A20",
    "green-800": "#0B3D2E",
    "green-700": "#125A43",
    "green-600": "#1B6E53",
    "sand-300": "#D8C3A5",
    "sand-200": "#E6D7C2",
    "sand-500": "#9C8261",
    "paper": "#FFFFFF",
    "canvas": "#EEF1EF",
    "ink": "#17211D",
    "ink-soft": "#45524C",
    "rule-color": "#CFD6D2",
}

PORTFOLIO = Theme(
    name="portfolio",
    label="Portfolio (ethan-gueck.github.io)",
    tokens={
        **BRAND,
        **SCALE_TOKENS,
        "bg": "var(--canvas)",
        "surface": "var(--paper)",
        "text": "var(--ink)",
        "text-soft": "var(--ink-soft)",
        "rule": "var(--rule-color)",
        "primary": "var(--green-800)",
        "primary-strong": "var(--green-900)",
        "primary-soft": "var(--green-700)",
        "on-primary": "#F3EEE6",
        "on-gradient": "#F3EEE6",
        "accent": "var(--sand-300)",
        "accent-soft": "var(--sand-200)",
        "accent-strong": "var(--sand-500)",
        "gradient-primary": "linear-gradient(135deg, var(--green-900) 0%, var(--green-800) 45%, var(--green-700) 100%)",
        "shadow-paper": "0 1px 2px rgba(7, 42, 32, 0.06), 0 8px 24px rgba(7, 42, 32, 0.06)",
        "shadow-stage": "0 12px 30px rgba(7, 42, 32, 0.22)",
        "focus": "0 0 0 3px var(--sand-300), 0 0 0 5px var(--green-800)",
    },
    stage={
        "background": "#0B3D2E",
        "grid": "rgba(243,238,230,0.08)",
        "axes": "rgba(243,238,230,0.45)",
        "text": "#F3EEE6",
        "muted": "rgba(243,238,230,0.65)",
        "primary": "#D8C3A5",
        "highlight": "#F2C14E",
        "point": "#FFFFFF",
        "secondary": "#8FC7B1",
        "guide": "rgba(216,195,165,0.55)",
        "warning": "#E9A15B",
        "plate": "rgba(7,42,32,0.78)",
    },
    stage_gradient=(("#072A20", 0.0), ("#0B3D2E", 0.55), ("#125A43", 1.0)),
    fonts={
        "serif": '"Newsreader", "Iowan Old Style", "Palatino Linotype", Georgia, serif',
        "sans": '"IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif',
        "mono": '"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
    },
    font_links=(
        "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;"
        "0,6..72,600;1,6..72,400;1,6..72,500&family=IBM+Plex+Sans:wght@400;500;600&display=swap",
    ),
)
