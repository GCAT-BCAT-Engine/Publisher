"""Tests for result snapshot."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from publication_plane.core.result_snapshot import ResultSnapshot


class TestResultSnapshot(unittest.TestCase):
    def test_capture_and_verify(self):
        snap = ResultSnapshot()
        path = snap.capture({"key": "val"}, "source", "seed")
        assert path.exists()
        assert snap.verify(path) is True

    def test_tamper_detection(self):
        snap = ResultSnapshot()
        path = snap.capture({"key": "val"}, "source", "seed")

        # Tamper
        import json
        data = json.loads(path.read_text())
        data["data"]["key"] = "tampered"
        path.write_text(json.dumps(data))

        assert snap.verify(path) is False


if __name__ == "__main__":
    unittest.main()
