"""Static API: topics declare modules/pages in ``api.py``; ``build_site`` publishes them.

GitHub Pages can't run Python, so the API is client-side: each module is a JS
mirror of a Python core (kept equal by parity tests), described in
``api/v1/manifest.json`` and loaded on demand by ``api/v1/pp.js``.
"""

from .build import API_VERSION, build_manifest, build_site
from .registry import JSModule, Page, Topic, discover_topics, load_topic

__all__ = ["API_VERSION", "JSModule", "Page", "Topic", "build_manifest", "build_site", "discover_topics", "load_topic"]
