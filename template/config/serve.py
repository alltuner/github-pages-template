#!/usr/bin/env python

import argparse
import os
from pathlib import Path

from livereload import Server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the docs directory with livereload")
    parser.add_argument(
        "root",
        nargs="?",
        default=Path(__file__).resolve().parent.parent / "docs",
        help="Directory to serve (defaults to the docs directory)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Port to listen on (defaults to PORT env or 8000)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host interface to bind to (defaults to HOST env or 127.0.0.1)",
    )
    return parser.parse_args()


class NoCacheMiddleware:
    """WSGI middleware to add no-cache headers for bundle files"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            path = environ.get('PATH_INFO', '')
            if '/statics/js/bundle.' in path or '/statics/css/bundle.' in path:
                headers = list(headers)
                headers.append(('Cache-Control', 'no-cache, no-store, must-revalidate'))
                headers.append(('Pragma', 'no-cache'))
                headers.append(('Expires', '0'))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Serve root {root} is not a directory")

    server = Server()
    server.application = NoCacheMiddleware(server.application)

    server.watch(str(root / "*.html"))
    server.watch(str(root / "statics" / "**" / "*.*"), delay=0.1)
    server.watch(str(root / "**" / "*.xml"), delay=0.5)
    server.serve(host=args.host, port=args.port, root=str(root))


if __name__ == "__main__":
    main()