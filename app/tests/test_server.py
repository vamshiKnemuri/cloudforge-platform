import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))

import server  # noqa: E402


class PayloadTests(unittest.TestCase):
    def test_json_payload_is_deterministic(self) -> None:
        payload = json.loads(server.json_payload("ok", service="test"))
        self.assertEqual(payload, {"service": "test", "status": "ok"})

    def test_metrics_contain_required_series(self) -> None:
        text = server.prometheus_metrics().decode()
        self.assertIn("cloudforge_up 1", text)
        self.assertIn("cloudforge_uptime_seconds", text)


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = 18080
        env = os.environ | {"PORT": str(cls.port), "APP_VERSION": "test"}
        cls.process = subprocess.Popen(
            [sys.executable, str(ROOT / "app" / "server.py")],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        for _ in range(50):
            try:
                with urlopen(f"http://127.0.0.1:{cls.port}/healthz", timeout=0.2) as response:
                    if response.status == 200:
                        return
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("test service did not become ready")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.process.terminate()
        cls.process.wait(timeout=5)

    def get(self, path: str):
        return urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=2)

    def test_root_returns_version(self) -> None:
        with self.get("/") as response:
            data = json.load(response)
        self.assertEqual(data["service"], "cloudforge-demo")
        self.assertEqual(data["version"], "test")

    def test_simulated_failure(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.get("/simulate?fail=true")
        self.assertEqual(context.exception.code, 503)

    def test_metrics_record_requests(self) -> None:
        with self.get("/metrics") as response:
            body = response.read().decode()
        self.assertIn("cloudforge_http_requests_total", body)


if __name__ == "__main__":
    unittest.main()

