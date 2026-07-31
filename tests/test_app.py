import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from monitor_core import ReloadingCountdownModel


class DummyWriter(io.BytesIO):
    def flush(self) -> None:
        return None


class DummyServer:
    def __init__(self, model: ReloadingCountdownModel) -> None:
        self.model = model


class DummyHandler(app.Handler):
    def __init__(self, model: ReloadingCountdownModel, path: str) -> None:
        self.server = DummyServer(model)
        self.path = path
        self.wfile = DummyWriter()
        self.responses = []
        self.headers = []
        self.status = None
        self.errors = []

    def send_response(self, status):  # noqa: ANN001
        self.status = status

    def send_header(self, key, value):  # noqa: ANN001
        self.headers.append((key, value))

    def end_headers(self) -> None:
        return None

    def send_error(self, status, message):  # noqa: ANN001
        self.errors.append((status, message))


class AppTests(unittest.TestCase):
    def write_env(self, text: str) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / ".env"
        path.write_text(text, encoding="utf-8")
        return path

    def test_events_endpoint_streams_one_payload(self) -> None:
        env_path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                ]
            )
        )
        model = ReloadingCountdownModel(env_path, 60)
        handler = DummyHandler(model, "/events")

        with patch.object(app.time, "sleep", side_effect=BrokenPipeError):
            handler.do_GET()

        body = handler.wfile.getvalue().decode("utf-8")
        self.assertEqual(200, handler.status)
        self.assertIn(("Content-Type", "text/event-stream; charset=utf-8"), handler.headers)
        self.assertTrue(body.startswith("data: "))
        self.assertIn("\n\n", body)

    def test_health_endpoint_reports_loaded_slots(self) -> None:
        env_path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                ]
            )
        )
        model = ReloadingCountdownModel(env_path, 60)
        handler = DummyHandler(model, "/healthz")

        handler.do_GET()

        body = handler.wfile.getvalue().decode("utf-8")
        self.assertEqual(200, handler.status)
        self.assertIn('"status":"ok"', body)
        self.assertIn('"slot_count":1', body)
        self.assertIn(("X-Content-Type-Options", "nosniff"), handler.headers)

    def test_dashboard_contains_status_controls(self) -> None:
        env_path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                ]
            )
        )
        model = ReloadingCountdownModel(env_path, 60)
        handler = DummyHandler(model, "/")

        handler.do_GET()

        body = handler.wfile.getvalue().decode("utf-8")
        self.assertEqual(200, handler.status)
        self.assertIn("connection-badge", body)
        self.assertIn("theme-toggle", body)
        self.assertIn("slot-filter", body)
        self.assertIn("/events", body)


if __name__ == "__main__":
    unittest.main()
