"""Tests for surface modules."""

import pytest
from publication_plane.surfaces.demo_sync import DemoSurfaceSync
from publication_plane.surfaces.evidence_builder import EvidenceBuilder


class TestDemoSurfaceSync:
    def test_publish_demo(self):
        sync = DemoSurfaceSync()
        result = sync.publish_demo("rcp-1", "seed", {"passes": 3, "confidence": 0.95, "deterministic": True})
        assert result["status"] == "published"
        assert "badge_id" in result


class TestEvidenceBuilder:
    def test_build_and_verify(self):
        builder = EvidenceBuilder()
        claims = [{"id": "c1", "text": "claim", "figure_refs": ["f1"], "confidence": 0.9}]
        figures = [{"id": "f1", "caption": "fig", "path": "p"}]

        path = builder.build_appendix(claims, figures, "rcp-1", "seed")
        assert path.exists()
        assert builder.verify_appendix(path) is True
