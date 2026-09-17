"""Small dependency-free service used to demonstrate the delivery platform."""

from __future__ import annotations

import json
import os
import signal
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

STARTED_AT = time.monotonic()
LOCK = threading.Lock()
REQUESTS: dict[tuple[str, int], int] = {}
LATENCY_SUM = 0.0


def record_request(path: str, status: int, duration: float) -> None:
    global LATENCY_SUM
    with LOCK:
        key = (path, status)
        REQUESTS[key] = REQUESTS.get(key, 0) + 1
        LATENCY_SUM += duration


def json_payload(status: str, **extra: object) -> bytes:
    return json.dumps({"status": status, **extra}, sort_keys=True).encode("utf-8")


def prometheus_metrics() -> bytes:
    with LOCK:
        request_lines = [
            f'cloudforge_http_requests_total{{path="{path}",status="{status}"}} {count}'
            for (path, status), count in sorted(REQUESTS.items())
        ]
        total = sum(REQUESTS.values())
        latency = LATENCY_SUM

    lines = [
        "# HELP cloudforge_up Whether the service is running.",
        "# TYPE cloudforge_up gauge",
        "cloudforge_up 1",
        "# HELP cloudforge_uptime_seconds Process uptime in seconds.",
        "# TYPE cloudforge_uptime_seconds gauge",
        f"cloudforge_uptime_seconds {time.monotonic() - STARTED_AT:.3f}",
        "# HELP cloudforge_http_requests_total Requests processed by path and status.",
        "# TYPE cloudforge_http_requests_total counter",
        *request_lines,
        "# HELP cloudforge_http_request_duration_seconds_sum Total request duration.",
        "# TYPE cloudforge_http_request_duration_seconds summary",
        f"cloudforge_http_request_duration_seconds_sum {latency:.6f}",
        f"cloudforge_http_request_duration_seconds_count {total}",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


class CloudForgeHandler(BaseHTTPRequestHandler):
    server_version = "CloudForge/1.0"

    def do_GET(self) -> None:  # noqa: N802 - stdlib API name
        started = time.monotonic()
        parsed = urlparse(self.path)
        status = HTTPStatus.OK

        if parsed.path == "/":
            body = json_payload(
                "ok",
                service="cloudforge-demo",
                version=os.getenv("APP_VERSION", "dev"),
                environment=os.getenv("APP_ENV", "local"),
            )
            content_type = "application/json"
        elif parsed.path in {"/healthz", "/readyz"}:
            body = json_payload("ok")
            content_type = "application/json"
        elif parsed.path == "/metrics":
            body = prometheus_metrics()
            content_type = "text/plain; version=0.0.4"
        elif parsed.path == "/simulate":
            query = parse_qs(parsed.query)
            delay_ms = min(max(int(query.get("delay_ms", ["0"])[0]), 0), 5000)
            if delay_ms:
                time.sleep(delay_ms / 1000)
            if query.get("fail", ["false"])[0].lower() == "true":
                status = HTTPStatus.SERVICE_UNAVAILABLE
                body = json_payload("error", reason="simulated failure")
            else:
                body = json_payload("ok", delay_ms=delay_ms)
            content_type = "application/json"
        else:
            status = HTTPStatus.NOT_FOUND
            body = json_payload("error", reason="not found")
            content_type = "application/json"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
        record_request(parsed.path, int(status), time.monotonic() - started)

    def log_message(self, format_string: str, *args: object) -> None:
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "client": self.client_address[0],
            "message": format_string % args,
        }
        print(json.dumps(event), flush=True)


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), CloudForgeHandler)

    def stop(_signum: int, _frame: object) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    print(json.dumps({"event": "server_started", "host": host, "port": port}), flush=True)
    server.serve_forever()
    server.server_close()


if __name__ == "__main__":
    main()

