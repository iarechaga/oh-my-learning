#!/usr/bin/env python3
"""Serve the built Oh My Learning website locally.

Usage:
    python website/serve.py              # serve on http://localhost:8000
    python website/serve.py 3000         # serve on http://localhost:3000
    python website/serve.py --build      # build first, then serve
"""

from __future__ import annotations

import argparse
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "website" / "dist"


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Oh My Learning website locally.")
    parser.add_argument("port", nargs="?", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--build", action="store_true", help="Run the build script before serving")
    args = parser.parse_args()

    if args.build:
        import subprocess
        build_script = REPO_ROOT / "website" / "build.py"
        result = subprocess.run([sys.executable, str(build_script)], cwd=REPO_ROOT)
        if result.returncode != 0:
            return result.returncode

    if not DIST_DIR.is_dir():
        print(f"Error: {DIST_DIR} does not exist. Run 'python website/build.py' first.", file=sys.stderr)
        return 1

    handler = partial(SimpleHTTPRequestHandler, directory=str(DIST_DIR))
    server = ThreadingHTTPServer(("localhost", args.port), handler)

    print(f"Serving Oh My Learning at http://localhost:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
