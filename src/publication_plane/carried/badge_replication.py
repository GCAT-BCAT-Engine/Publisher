# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-addons@29a74ef:stegverse_core_addons/badge/replication.py (sha256 bb43563f36512620ac40bc4f2c4caf810b834e566250bf54399a9d9ebc5dc19d).
# Edit: from stegverse_core_lite.hash.deterministic import DeterministicHash -> from publication_plane.core.deterministic import DeterministicHash
"""
Reproducibility badge generation.
Creates verifiable badges for sandbox runs and research releases.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ReplicationBadge:
    badge_id: str
    receipt_id: str
    seed: str
    passes: int
    confidence: float
    deterministic: bool
    generated_at: str
    svg_markup: str


class ReplicationBadgeGenerator:
    """
    Generates reproducibility badges for StegVerse artifacts.
    Badges are deterministic: same receipt + same seed = same badge.
    """

    def __init__(self, output_dir: str = "badges"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        receipt_id: str,
        seed: str,
        passes: int,
        confidence: float,
        deterministic: bool = True
    ) -> ReplicationBadge:
        """Generate a reproducibility badge."""
        from publication_plane.core.deterministic import DeterministicHash

        badge_id = DeterministicHash.hash(f"{receipt_id}:{seed}", "badge")[:16]
        timestamp = datetime.now(timezone.utc).isoformat()

        # Generate SVG badge
        color = self._color_for_confidence(confidence)
        label = "reproducible" if deterministic else "unverified"

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="20">
  <rect width="90" height="20" fill="#555"/>
  <rect x="90" width="90" height="20" fill="{color}"/>
  <text x="45" y="14" fill="#fff" font-size="11" text-anchor="middle">StegVerse</text>
  <text x="135" y="14" fill="#fff" font-size="11" text-anchor="middle">{label}</text>
</svg>'''

        badge = ReplicationBadge(
            badge_id=badge_id,
            receipt_id=receipt_id,
            seed=seed,
            passes=passes,
            confidence=confidence,
            deterministic=deterministic,
            generated_at=timestamp,
            svg_markup=svg,
        )

        # Save
        path = self.output_dir / f"{badge_id}.json"
        path.write_text(json.dumps(asdict(badge), indent=2), encoding="utf-8")

        svg_path = self.output_dir / f"{badge_id}.svg"
        svg_path.write_text(svg, encoding="utf-8")

        return badge

    def _color_for_confidence(self, confidence: float) -> str:
        if confidence >= 0.95:
            return "#4c1"  # Green
        elif confidence >= 0.85:
            return "#97ca00"  # Yellow-green
        elif confidence >= 0.7:
            return "#dfb317"  # Yellow
        else:
            return "#e05d44"  # Red


def main():
    generator = ReplicationBadgeGenerator()

    badge = generator.generate(
        receipt_id="rcp-demo-001",
        seed="run-001",
        passes=3,
        confidence=0.947,
        deterministic=True
    )

    print(f"Badge ID: {badge.badge_id}")
    print(f"SVG saved to: badges/{badge.badge_id}.svg")
    print(f"Confidence color: {generator._color_for_confidence(badge.confidence)}")


if __name__ == "__main__":
    main()
