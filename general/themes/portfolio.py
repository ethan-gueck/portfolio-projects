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


# Dark mode for the portfolio theme: the blue-grey scale with a complementary yellow.
#   blue-grey  050 #f0f4f8  100 #d9e2ec  200 #bcccdc  300 #9fb3c8  400 #829ab1  500 #627d98
#              600 #486581  700 #334e68  800 #243b53  900 #102a43
#   yellow (from #E5A93C at the blue scale's lightness steps)
#              050 #fcf8ef  100 #f9efdc  200 #f3d7a5  300 #edc378  400 #e5a93c  500 #d8961d  600 #b17b18
# Pages carry it as a [data-mode="dark"] block and switch when the reader picked dark mode on
# ethan-gueck.github.io (localStorage "pp-theme"; see web/page.py and styles/js/mode.js).
PORTFOLIO_DARK = PORTFOLIO.variant(
    "portfolio-dark",
    label="Portfolio dark (blue-grey and yellow)",
    color_scheme="dark",
    tokens={
        "green-900": "#102a43", "green-800": "#243b53", "green-700": "#334e68", "green-600": "#486581",
        "sand-300": "#e5a93c", "sand-200": "#f3d7a5", "sand-500": "#edc378",
        "paper": "#1b334c", "canvas": "#102a43", "ink": "#f0f4f8", "ink-soft": "#bcccdc", "rule-color": "#334e68",
        "bg": "#102a43",
        "surface": "#1b334c",
        "text": "#f0f4f8",
        "text-soft": "#bcccdc",
        "primary": "#bcccdc",
        "primary-strong": "#0c2236",
        "primary-soft": "#9fb3c8",
        "on-primary": "#102a43",
        "on-gradient": "#f0f4f8",
        "accent": "#e5a93c",
        "accent-soft": "#f3d7a5",
        "accent-strong": "#edc378",
        "gradient-primary": "linear-gradient(135deg, #0c2236 0%, #1b334c 45%, #334e68 100%)",
        "shadow-paper": "0 1px 2px rgba(4, 14, 26, 0.4), 0 8px 24px rgba(4, 14, 26, 0.35)",
        "shadow-stage": "0 12px 30px rgba(4, 14, 26, 0.5)",
        "focus": "0 0 0 3px #e5a93c, 0 0 0 5px #102a43",
    },
    stage={
        "background": "#102a43",
        "grid": "rgba(240,244,248,0.08)",
        "axes": "rgba(240,244,248,0.45)",
        "text": "#f0f4f8",
        "muted": "rgba(240,244,248,0.65)",
        "primary": "#f3d7a5",
        "highlight": "#e5a93c",
        "point": "#FFFFFF",
        "secondary": "#9fb3c8",
        "guide": "rgba(229,169,60,0.55)",
        "warning": "#d8961d",
        "plate": "rgba(12,34,54,0.82)",
    },
    stage_gradient=(("#0c2236", 0.0), ("#1b334c", 0.55), ("#334e68", 1.0)),
)
