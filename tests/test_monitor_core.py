import tempfile
import os
import time
import unittest
from unittest.mock import patch
from pathlib import Path

import monitor_core
from monitor_core import CountdownModel, ReloadingCountdownModel, mask_email, parse_env_pairs


class MonitorCoreTests(unittest.TestCase):
    def write_env(self, text: str) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / ".env"
        path.write_text(text, encoding="utf-8")
        return path

    def test_parse_env_pairs_preserves_repeated_key_names(self) -> None:
        path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                    "GOOGLE_ID_02=two@example.com",
                    "GOOGLE_API_KEY=key-two",
                ]
            )
        )

        slots = parse_env_pairs(path)

        self.assertEqual(2, len(slots))
        self.assertEqual("one@example.com", slots[0].google_id)
        self.assertEqual("key-one", slots[0].api_key)
        self.assertEqual("two@example.com", slots[1].google_id)
        self.assertEqual("key-two", slots[1].api_key)

    def test_mask_email_hides_local_part(self) -> None:
        self.assertEqual("ar…@gmail.com", mask_email("arinfamily.th@gmail.com"))

    def test_countdown_snapshot_contains_expected_fields(self) -> None:
        path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                    "GOOGLE_ID_02=two@example.com",
                    "GOOGLE_API_KEY=key-two",
                ]
            )
        )
        slots = parse_env_pairs(path)
        model = CountdownModel(slots, 60)

        snapshot = model.snapshot()

        self.assertEqual(1, snapshot["active_slot"])
        self.assertEqual(2, snapshot["next_slot"])
        self.assertEqual(2, snapshot["slot_count"])
        self.assertIn("remaining_text", snapshot)
        self.assertIn("next_switch_label", snapshot)
        self.assertGreaterEqual(snapshot["progress"], 0.0)
        self.assertLessEqual(snapshot["progress"], 1.0)

    def test_reloading_model_refreshes_when_env_changes(self) -> None:
        path = self.write_env(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                ]
            )
        )
        model = ReloadingCountdownModel(path, 60)
        first = model.snapshot()
        self.assertEqual(1, first["slot_count"])

        path.write_text(
            "\n".join(
                [
                    "GOOGLE_ID_01=one@example.com",
                    "GOOGLE_API_KEY=key-one",
                    "GOOGLE_ID_02=two@example.com",
                    "GOOGLE_API_KEY=key-two",
                ]
            ),
            encoding="utf-8",
        )
        future = time.time() + 5
        os.utime(path, (future, future))

        second = model.snapshot()
        self.assertEqual(2, second["slot_count"])

    def test_default_env_path_uses_exe_dir_when_frozen(self) -> None:
        with patch.object(monitor_core.sys, "frozen", True, create=True), patch.object(
            monitor_core.sys, "executable", "/opt/ggtmoni/ggtmoni.exe"
        ):
            self.assertEqual(Path("/opt/ggtmoni/.env"), monitor_core.default_env_path())

    def test_default_env_path_uses_cwd_when_not_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            current = Path.cwd()
            try:
                os.chdir(tmpdir)
                self.assertEqual(Path(tmpdir) / ".env", monitor_core.default_env_path())
            finally:
                os.chdir(current)


if __name__ == "__main__":
    unittest.main()
