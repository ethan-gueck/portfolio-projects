import pytest

from general.themes import MANIM, PORTFOLIO, SEMANTIC_TOKENS, STAGE_ROLES, THEMES, Theme, get_theme, register_theme, split_alpha


def test_default_is_portfolio():
    assert get_theme() is PORTFOLIO
    assert get_theme("manim") is MANIM
    assert get_theme(MANIM) is MANIM
    with pytest.raises(KeyError):
        get_theme("nope")


def test_portfolio_matches_site_tokens():
    # Values from ethan-gueck.github.io/assets/css/tokens.css
    assert PORTFOLIO.tokens["green-800"] == "#0B3D2E"
    assert PORTFOLIO.tokens["sand-300"] == "#D8C3A5"
    assert PORTFOLIO.tokens["canvas"] == "#EEF1EF"
    assert "Newsreader" in PORTFOLIO.fonts["serif"] and "IBM Plex Sans" in PORTFOLIO.fonts["sans"]


@pytest.mark.parametrize("theme", list(THEMES.values()), ids=list(THEMES))
def test_every_theme_is_complete_and_renders(theme):
    css = theme.css()
    for token in SEMANTIC_TOKENS:
        assert f"--{token}:" in css
    for role in STAGE_ROLES:
        assert f"--stage-{role}:" in css
        split_alpha(theme.stage[role])  # stage colours must be literal, Manim-parsable
    assert "--stage-gradient:" in css
    assert theme.to_dict()["stage"] == theme.stage


def test_incomplete_theme_rejected():
    with pytest.raises(ValueError, match="missing"):
        Theme(name="bad", label="bad", tokens={}, stage={}, fonts={})


def test_variant_merges_and_registers():
    gold = PORTFOLIO.variant("portfolio-gold", stage={"primary": "#F2C14E"})
    assert gold.stage["primary"] == "#F2C14E" and gold.stage["grid"] == PORTFOLIO.stage["grid"]
    assert PORTFOLIO.stage["primary"] == "#D8C3A5"  # original untouched
    register_theme(gold)
    try:
        assert get_theme("portfolio-gold") is gold
    finally:
        THEMES.pop("portfolio-gold")


@pytest.mark.parametrize(
    "css, expected",
    [("#fff", ("#FFFFFF", 1.0)), ("#0b3d2e", ("#0B3D2E", 1.0)), ("rgba(243,238,230,0.45)", ("#F3EEE6", 0.45)), ("rgb(0, 0, 0)", ("#000000", 1.0))],
)
def test_split_alpha(css, expected):
    assert split_alpha(css) == expected
