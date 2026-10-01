"""What a topic exposes, and discovery of topics across the repo.

A topic is any package folder with an ``api.py`` defining ``TOPIC``:

    TOPIC = Topic(
        title="Quadratic Formula",
        description="...",
        modules=(JSModule(name="quadratic", global_name="QuadMath",
                          scripts=(HERE / "html/static/quadratic_math.js",),
                          functions={"solve": core.solve, ...}),),
        pages=(Page(name="quadratic", title="...", build=build_page, params=("a", "b", "c")),),
    )

Its slug is its folder path from the project root (``a1`` in the algebra
repo), which is also where its files are published and how the frontend
addresses it: ``PP.use("a1/quadratic")``. The project root is the repo being
built (see ``find_root``), not the folder holding ``general/``, so domain repos
can install this package and keep their topics to themselves.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable


def find_root(start: Path | None = None) -> Path:
    """The project being built: ``$PP_ROOT``, else the nearest folder at or above
    the working directory that holds a ``pyproject.toml``."""
    if os.environ.get("PP_ROOT"):
        return Path(os.environ["PP_ROOT"]).resolve()
    here = (start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / "pyproject.toml").is_file():
            return folder
    return here

SKIP_DIRS = {".git", ".github", "_site", "general", "node_modules", "__pycache__", "output", ".pytest_cache", ".venv", "venv"}


@dataclass(frozen=True)
class JSModule:
    """A browser module: scripts that define ``window[global_name]`` with ``functions``.

    ``functions`` maps each exported name to its Python reference
    implementation, which documents it in the manifest and is what parity
    tests compare against.
    """

    name: str
    global_name: str
    scripts: tuple[Path, ...]
    functions: dict[str, Callable]
    title: str = ""


@dataclass(frozen=True)
class Page:
    """An interactive page. ``build(output_path, theme)`` writes it and returns the path."""

    name: str
    title: str
    build: Callable[..., Path]
    description: str = ""
    params: tuple[str, ...] = ()
    example: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Topic:
    """A published topic.

    ``cards`` lists the portfolio flashcard ids its pages walk through
    (``("A1.11",)``). Those neurons on the site's "Ethan's NN" tab are drawn
    filled and open this topic's first page.
    """

    title: str
    description: str = ""
    modules: tuple[JSModule, ...] = ()
    pages: tuple[Page, ...] = ()
    cards: tuple[str, ...] = ()
    slug: str = ""
    path: Path | None = None

    def module_id(self, module: JSModule) -> str:
        return f"{self.slug}/{module.name}"

    def page_id(self, page: Page) -> str:
        return f"{self.slug}/{page.name}"


def describe_function(fn: Callable) -> dict:
    doc = inspect.getdoc(fn) or ""
    signature = str(inspect.signature(fn)).replace("'", "")  # postponed annotations arrive as strings
    return {"signature": f"{fn.__name__}{signature}", "doc": doc.split("\n\n")[0].replace("\n", " ")}


def _alias(slug: str) -> str:
    return "pp_topic_" + re.sub(r"\W", "_", slug)


def load_topic(folder: Path, root: Path | None = None) -> Topic:
    """Import ``folder/api.py`` as part of its package, under a unique alias.

    The alias keeps same-named folders apart (``a1`` vs ``testing/a1``)
    while relative imports inside the topic keep working.
    """
    folder = folder.resolve()
    slug = folder.relative_to((root or find_root()).resolve()).as_posix()
    alias = _alias(slug)
    if alias not in sys.modules:
        spec = importlib.util.spec_from_file_location(alias, folder / "__init__.py", submodule_search_locations=[str(folder)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[alias] = package
        spec.loader.exec_module(package)
    topic = importlib.import_module(f"{alias}.api").TOPIC
    return replace(topic, slug=slug, path=folder)


def discover_topics(root: Path | None = None) -> list[Topic]:
    """Every folder under ``root`` containing both ``__init__.py`` and ``api.py``."""
    root = (root or find_root()).resolve()
    found = []
    for api in sorted(root.rglob("api.py")):
        rel = api.relative_to(root).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel[:-1]):
            continue
        if (api.parent / "__init__.py").exists():
            found.append(load_topic(api.parent, root))
    return found
