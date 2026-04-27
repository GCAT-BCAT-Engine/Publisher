"""Tests for publication gate."""

import pytest
from publication_plane.core.publication_gate import PublicationGate, GateResult, PublicationAction


class TestPublicationGate:
    def test_allow_publishes(self):
        gate = PublicationGate()
        result = gate.evaluate("ALLOW", 0.95, {}, seed="test")
        assert result["action"] == "publish"

    def test_deny_quarantines(self):
        gate = PublicationGate()
        result = gate.evaluate("DENY", 0.6, {}, seed="test")
        assert result["action"] == "quarantine"

    def test_fail_closed_blocks(self):
        gate = PublicationGate()
        result = gate.evaluate("FAIL_CLOSED", 0.3, {}, seed="test")
        assert result["action"] == "block"

    def test_low_confidence_review(self):
        gate = PublicationGate(confidence_threshold=0.9)
        result = gate.evaluate("ALLOW", 0.85, {}, seed="test")
        assert result["action"] == "manual_review"
