#!/usr/bin/env python3
"""Generate safe demo traffic using only the Python standard library."""

from __future__ import annotations

import argparse
import concurrent.futures
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def request(url: str) -> int:
    try:
        with urlopen(url, timeout=5) as response:
            response.read()
            return response.status
    except HTTPError as exc:
        return exc.code
    except URLError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8080/")
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        statuses = list(pool.map(request, [args.url] * args.requests))
    duration = time.monotonic() - started
    successful = sum(200 <= status < 400 for status in statuses)
    print(f"requests={args.requests} successful={successful} duration={duration:.2f}s rate={args.requests / duration:.1f}rps")


if __name__ == "__main__":
    main()

