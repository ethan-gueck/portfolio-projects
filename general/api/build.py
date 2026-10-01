"""Build the static site + API that GitHub Pages serves.

    _site/
    ├── index.html                        catalog of every topic, themed
    ├── api/v1/pp.js                      browser client
    ├── api/v1/manifest.json              modules, functions, pages, themes, styles
    ├── general/styles/css/**             shared CSS (+ themes/<name>.css, generated)
    ├── general/styles/js/**              shared JS
    └── <topic slug>/                     e.g. a1/
        ├── <module scripts>.js
        ├── <page>.html                   default theme
        └── <page>.<theme>.html           other themes
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import tomllib
from pathlib import Path

from ..styles import BASE, CSS_DIR, JS_DIR, STYLES_DIR, shared_assets
from ..themes import DEFAULT_THEME, THEMES
from ..web import render_page
from .registry import Topic, describe_function, discover_topics, find_root

API_VERSION = 1
API_DIR = Path(__file__).resolve().parent
INDEX_TEMPLATE = Path(__file__).resolve().parents[1] / "web" / "templates" / "index.html"


def site_settings(root: Path) -> dict:
    """``[tool.portfolio-site]`` from the project's pyproject.toml: title, url, description."""
    pyproject = root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text()) if pyproject.is_file() else {}
    site = data.get("tool", {}).get("portfolio-site", {})
    url = os.environ.get("PP_PUBLIC_URL", site.get("url", ""))
    pages = re.match(r"https://([\w-]+)\.github\.io/([\w.-]+)/?$", url)
    return {
        "title": site.get("title", data.get("project", {}).get("name", root.name)),
        "url": url,
        # The repo behind the site: [tool.portfolio-site] repo, else derived from a GitHub Pages project URL.
        "repo": site.get("repo") or (f"https://github.com/{pages[1]}/{pages[2]}" if pages else ""),
        "description": site.get("description", "Interactive calculations and Manim-style animations, callable from any page."),
    }


def _shared_path(path: Path) -> str:
    return "general/styles/" + path.relative_to(STYLES_DIR).as_posix()


def build_manifest(topics: list[Topic], site: dict | None = None) -> dict:
    manifest = {
        "version": API_VERSION,
        "site": site or {},
        "commit": os.environ.get("GITHUB_SHA"),
        "defaultTheme": DEFAULT_THEME,
        "themes": {name: f"general/styles/css/themes/{name}.css" for name in THEMES},
        "styles": [_shared_path(p) for p in shared_assets("css")],
        "scripts": [_shared_path(p) for p in shared_assets("js")],
        "topics": {},
        "modules": {},
        "pages": {},
    }
    for topic in topics:
        manifest["topics"][topic.slug] = {
            "title": topic.title,
            "description": topic.description,
            "cards": list(topic.cards),
            "pages": [topic.page_id(page) for page in topic.pages],
        }
        for module in topic.modules:
            manifest["modules"][topic.module_id(module)] = {
                "title": module.title or topic.title,
                "topic": topic.slug,
                "global": module.global_name,
                "scripts": [f"{topic.slug}/{Path(s).name}" for s in module.scripts],
                "functions": {name: describe_function(fn) for name, fn in module.functions.items()},
            }
        for page in topic.pages:
            manifest["pages"][topic.page_id(page)] = {
                "title": page.title,
                "description": page.description,
                "topic": topic.slug,
                "path": f"{topic.slug}/{page.name}.html",
                "themes": {name: f"{topic.slug}/{page.name}{'' if name == DEFAULT_THEME else '.' + name}.html" for name in THEMES},
                "params": list(page.params),
                "example": page.example,
            }
    return manifest


def _link(href: str, text: str) -> str:
    return f'<a href="{html.escape(href)}">{html.escape(text)}</a>'


def _page_item(page: dict) -> str:
    hash_ = "&".join(f"{k}={v}" for k, v in page["example"].items())
    alternates = [_link(path, name) for name, path in page["themes"].items() if path != page["path"]]
    tail = f' <span class="card__alt">also: {", ".join(alternates)}</span>' if alternates else ""
    return f"<li>{_link(page['path'] + ('#' + hash_ if hash_ else ''), page['title'])}{tail}</li>"


def _module_item(module_id: str, module: dict) -> str:
    functions = ", ".join(f"<code>{html.escape(fn)}</code>" for fn in module["functions"])
    return f"<li><code>{html.escape(module_id)}</code>: {functions}</li>"


def _topic_card(topic: Topic, manifest: dict) -> str:
    pages = "".join(_page_item(p) for p in manifest["pages"].values() if p["topic"] == topic.slug)
    modules = "".join(_module_item(mid, m) for mid, m in manifest["modules"].items() if m["topic"] == topic.slug)
    return (
        f'<article class="card"><p class="card__kicker">{html.escape(topic.slug)}</p>'
        f'<h3 class="card__title">{html.escape(topic.title)}</h3>'
        f"<p>{html.escape(topic.description)}</p>"
        f"<h4>Pages</h4><ul>{pages}</ul><h4>API modules</h4><ul>{modules}</ul></article>"
    )


def _index_html(manifest: dict, topics: list[Topic], site: dict) -> str:
    module_id = next(iter(manifest["modules"]), "topic/module")
    page_id, page = next(iter(manifest["pages"].items()), ("topic/page", {"example": {}}))
    return render_page(
        INDEX_TEMPLATE,
        title=site["title"],
        bundle=BASE.extend(css=("components/controls.css", "components/catalog.css")),
        extra={
            "cards": "\n".join(_topic_card(t, manifest) for t in topics) or "<p>No topics yet.</p>",
            "public_url": html.escape(site["url"]),
            "description": html.escape(site["description"]),
            "module_id": html.escape(module_id),
            "page_id": html.escape(page_id),
            "example": html.escape(json.dumps(page["example"])),
            "version": str(API_VERSION),
        },
    )


def build_site(out: str | Path | None = None, root: Path | None = None) -> Path:
    """Build the project at ``root`` (default: ``find_root()``) into ``out``
    (default: ``<root>/_site``, wiped first) and return its path."""
    root = Path(root or find_root()).resolve()
    site = site_settings(root)
    out = Path(out or root / "_site").resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "api" / f"v{API_VERSION}").mkdir(parents=True)

    for src_dir in (CSS_DIR, JS_DIR):
        shutil.copytree(src_dir, out / "general" / "styles" / src_dir.name)
    themes_dir = out / "general" / "styles" / "css" / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        (themes_dir / f"{name}.css").write_text(theme.css())

    topics = discover_topics(root)
    for topic in topics:
        target = out / topic.slug
        target.mkdir(parents=True, exist_ok=True)
        for module in topic.modules:
            for script in module.scripts:
                shutil.copy2(script, target / Path(script).name)
        for page in topic.pages:
            for name in THEMES:
                suffix = "" if name == DEFAULT_THEME else f".{name}"
                page.build(target / f"{page.name}{suffix}.html", theme=name)

    manifest = build_manifest(topics, site)
    api_dir = out / "api" / f"v{API_VERSION}"
    (api_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    shutil.copy2(API_DIR / "pp.js", api_dir / "pp.js")
    (out / "index.html").write_text(_index_html(manifest, topics, site))
    (out / ".nojekyll").write_text("")
    return out


__all__ = ["build_manifest", "build_site"]
