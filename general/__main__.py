"""python -m general {build|serve|manifest}

    python -m general build              # → _site/  (what GitHub Pages serves)
    python -m general serve --port 8000  # build, then serve _site/ locally
    python -m general manifest           # print the API manifest

Run inside a project (a folder with pyproject.toml, e.g. a domain repo such as
algebra); its topics are built, and [tool.portfolio-site] names the site.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
from pathlib import Path

from .api import build_manifest, build_site, discover_topics
from .api.build import site_settings
from .api.registry import find_root


class _Handler(http.server.SimpleHTTPRequestHandler):
    """Static files plus the CORS header GitHub Pages sends, so other local sites can fetch the API."""

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m general", description="Build and serve the portfolio projects site/API.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "serve"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--out", type=Path, default=None, help="default: <project>/_site")
        if name == "serve":
            cmd.add_argument("--port", type=int, default=8000)
    sub.add_parser("manifest")
    args = parser.parse_args(argv)

    if args.command == "manifest":
        print(json.dumps(build_manifest(discover_topics(), site_settings(find_root())), indent=2))
        return

    out = build_site(args.out)
    print(f"Built {out}")
    if args.command == "serve":
        handler = functools.partial(_Handler, directory=str(out))
        print(f"Serving http://localhost:{args.port}/  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
