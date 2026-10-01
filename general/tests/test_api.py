import json
from pathlib import Path

import pytest

from general.api import build_manifest, build_site, discover_topics
from general.api.build import API_DIR, site_settings
from general.api.registry import find_root
from general.jsrun import AVAILABLE, run_js
from general.styles import JS_DIR
from general.themes import THEMES

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo_site"
EXAMPLE_ID = "demo/demo"


@pytest.fixture(scope="module")
def topics():
    return discover_topics(FIXTURE)


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("site") / "_site", root=FIXTURE)


def test_discovers_topics_under_the_project_root(topics):
    assert [t.slug for t in topics] == ["demo"]


def test_find_root_is_the_nearest_pyproject(monkeypatch):
    monkeypatch.delenv("PP_ROOT", raising=False)
    assert find_root(FIXTURE / "demo") == FIXTURE
    monkeypatch.setenv("PP_ROOT", str(FIXTURE / "demo"))
    assert find_root() == FIXTURE / "demo"


def test_manifest_describes_modules_pages_and_themes(topics):
    manifest = build_manifest(topics, site_settings(FIXTURE))
    assert manifest["site"]["title"] == "Demo"
    module = manifest["modules"][EXAMPLE_ID]
    assert module["global"] == "DemoMath"
    assert module["functions"]["double"]["signature"].startswith("double(x: float)")
    page = manifest["pages"][EXAMPLE_ID]
    assert page["params"] == ["x"]
    assert set(page["themes"]) == set(THEMES)
    assert set(manifest["themes"]) == set(THEMES)


def test_manifest_lists_topic_cards_for_the_nn_tab(topics):
    topic = build_manifest(topics)["topics"]["demo"]
    assert topic["cards"] == ["A1.1"]
    assert topic["pages"] == [EXAMPLE_ID]


def test_build_site_writes_every_manifest_path(site):
    manifest = json.loads((site / "api/v1/manifest.json").read_text())
    paths = [*manifest["themes"].values(), *manifest["styles"], *manifest["scripts"]]
    for module in manifest["modules"].values():
        paths += module["scripts"]
    for page in manifest["pages"].values():
        paths += [page["path"], *page["themes"].values()]
    missing = [p for p in paths if not (site / p).is_file()]
    assert not missing
    assert (site / "index.html").is_file() and (site / "api/v1/pp.js").is_file() and (site / ".nojekyll").exists()
    assert "Demo" in (site / "index.html").read_text()


def test_built_pages_use_their_theme(site):
    assert 'data-theme="portfolio"' in (site / "demo/demo.html").read_text()
    assert 'data-theme="manim"' in (site / "demo/demo.manim.html").read_text()


@pytest.mark.skipif(not AVAILABLE, reason="no JavaScript runtime (node or osascript)")
@pytest.mark.parametrize("script", [API_DIR / "pp.js", *sorted(JS_DIR.glob("*.js"))], ids=lambda p: Path(p).name)
def test_client_scripts_parse(script):
    assert run_js([], f"(new Function({json.dumps(Path(script).read_text())}), true)") is True


def test_repo_is_derived_from_a_github_pages_url(tmp_path, monkeypatch):
    monkeypatch.delenv("PP_PUBLIC_URL", raising=False)
    (tmp_path / "pyproject.toml").write_text('[tool.portfolio-site]\nurl = "https://ethan-gueck.github.io/algebra/"\n')
    assert site_settings(tmp_path)["repo"] == "https://github.com/ethan-gueck/algebra"
    assert site_settings(FIXTURE)["repo"] == ""  # not a Pages URL
