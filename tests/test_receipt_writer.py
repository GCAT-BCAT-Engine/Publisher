"""Tests for publication receipt writer."""

import pytest
from publication_plane.core.receipt_writer import PublicationReceiptWriter
from stegverse_core_lite.receipt.id import DeterministicReceiptID


class TestPublicationReceiptWriter:
    def test_write_and_verify(self):
        writer = PublicationReceiptWriter(seed="test-seed")
        path = writer.write(
            gate_result="ALLOW",
            confidence=0.95,
            evidence={"passes": 3},
            module="test",
            destination="test",
        )
        assert path.exists()
        assert writer.verify(path) is True

    def test_determinism(self):
        writer = PublicationReceiptWriter(seed="test-seed")
        path1 = writer.write("ALLOW", 0.95, {}, "test", "test")
        path2 = writer.write("ALLOW", 0.95, {}, "test", "test")

        data1 = path1.read_text()
        data2 = path2.read_text()
        # Same content + same seed = same receipt ID, but different timestamps
        import json
        j1 = json.loads(data1)
        j2 = json.loads(data2)
        assert j1["receipt_id"] == j2["receipt_id"]
