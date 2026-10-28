"""Tests for routing modules."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from publication_plane.routing.release_router import ReleaseRouter
from publication_plane.routing.channel_manager import ChannelManager
from publication_plane.routing.notary import PublicationNotary


class TestReleaseRouter(unittest.TestCase):
    def test_research_routing(self):
        router = ReleaseRouter()
        result = router.route("research", {"action": "publish", "governance": {"evaluation_receipt": "rcp-1"}})
        assert "arxiv" in result["channels"]

    def test_blocked_no_channels(self):
        router = ReleaseRouter()
        result = router.route("research", {"action": "block", "governance": {"evaluation_receipt": "rcp-1"}})
        assert result["channels"] == []


class TestChannelManager(unittest.TestCase):
    def test_resolve_targets(self):
        manager = ChannelManager()
        targets = manager.resolve_targets(["publisher"])
        assert any("GCAT-BCAT-Engine" in t for t in targets)


class TestPublicationNotary(unittest.TestCase):
    def test_notarize_artifact(self):
        notary = PublicationNotary()
        result = notary.notarize_artifact({"test": "data"}, "dest", "demo")
        assert "notarization_id" in result
        assert result["transition_permitted"] is False


if __name__ == "__main__":
    unittest.main()
