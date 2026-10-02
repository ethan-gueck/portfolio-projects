import json
import re
from pathlib import Path

import pytest

from general.styles import BASE, WIDGET, Bundle, resolve, shared_assets
from general.web import fill_template, render_page


def test_bundles_resolve_every_asset():
    for asset in WIDGET.css:
        resolve(asset, "css")
    for asset in WIDGET.js:
        resolve(asset, "js")


def test_css_only_uses_semantic_tokens():
    """Shared CSS must work under any theme, so it may not reach for brand tokens directly."""
    brand = re.compile(r"var\(--(green|sand)-\d+\)")
    for path in shared_assets("css"):
        assert not brand.search(path.read_text()), path


def test_bundle_extend_and_theme_first(tmp_path):
    extra = tmp_path / "x.css"
    extra.write_text(".x{}")
    bundle = BASE.extend(css=[extra])
    text = bundle.css_text("manim")
    assert text.index(":root") < text.index("base.css") < text.index(".x{}")
    assert isinstance(bundle, Bundle) and BASE.css[-1] != extra  # BASE unchanged


def test_missing_asset_raises():
    with pytest.raises(FileNotFoundError):
        resolve("nope.css", "css")


def test_render_page_embeds_theme_config(tmp_path):
    template = tmp_path / "t.html"
    template.write_text("<title>{{title}}</title>{{head}}<style>{{styles}}</style><script>{{scripts}}</script><script id='c'>{{config}}</script>")
    document = render_page(template, title="A & B", config={"x": "</script>"})
    assert "<title>A &amp; B</title>" in document
    assert "fonts.googleapis.com" in document  # portfolio web fonts
    config = json.loads(document.split("<script id='c'>")[1].rsplit("</script>", 1)[0])
    assert config["x"] == "</script>" and config["theme"]["name"] == "portfolio"


def test_every_page_gets_the_call_to_action_and_footer(tmp_path):
    template = tmp_path / "t.html"
    template.write_text("<html><head><style>{{styles}}</style></head><body><main>page</main></body></html>")
    document = render_page(template, title="Quadratic Formula")
    body = document.split("<body>")[1]
    assert body.index("</main>") < body.index('class="cta"') < body.index('class="site-footer"') < body.index("</body>")
    assert "Let’s work together" in document and "Quadratic Formula." in document
    assert "overscroll-behavior-y: none" in document  # no scrolling past the header or footer
    assert body.index('class="site-footer"') < body.index('class="contact-bar"')  # floating bar, hidden at the footer
    assert 'class="site-footer"' not in render_page(template, title="x", footer=False)


def test_footer_placeholder_places_it(tmp_path):
    template = tmp_path / "t.html"
    template.write_text("<body><main>page</main>{{footer}}<script>1</script></body>")
    document = render_page(template, title="x")
    assert document.count('class="site-footer"') == 1
    assert document.index('class="site-footer"') < document.index("<script>1</script>")


def test_unknown_placeholder_raises():
    with pytest.raises(KeyError):
        fill_template("{{nope}}", {})


def test_portfolio_pages_carry_a_dark_mode(tmp_path):
    template = tmp_path / "t.html"
    template.write_text("<head>{{head}}<style>{{styles}}</style></head><body><script id='c'>{{config}}</script></body>")
    document = render_page(template, title="x", footer=False)
    assert ':root[data-mode="dark"]' in document and "--accent: #e5a93c" in document
    assert "localStorage.getItem('pp-theme')" in document  # applied before first paint
    config = json.loads(document.split("<script id='c'>")[1].split("</script>")[0])
    assert config["theme_dark"]["stage"]["highlight"] == "#e5a93c" and config["theme"]["name"] == "portfolio"


def test_themes_without_a_dark_mode_are_left_alone(tmp_path):
    template = tmp_path / "t.html"
    template.write_text("<head>{{head}}<style>{{styles}}</style></head><body>{{config}}</body>")
    document = render_page(template, title="x", theme="manim", footer=False)
    assert ':root[data-mode="dark"]' not in document and "theme_dark" not in document
    assert "localStorage.getItem('pp-theme')" not in document
