"""
Central configuration for publication_plane.
All paths, thresholds, and org targets defined here.
"""

from pathlib import Path
from typing import Dict, List


class PublicationConfig:
    """
    iOS-compatible: pure Python, file-based, no env var dependencies.
    """

    SEED: str = "publisher-default-seed"
    CONFIDENCE_THRESHOLD: float = 0.85
    REQUIRE_STEGDB_CLEARANCE: bool = True

    # Cross-org publication targets
    ORG_TARGETS: Dict[str, str] = {
        "publisher": "GCAT-BCAT-Engine/Publisher",
        "core_lite": "GCAT-BCAT-Engine/core-lite",
        "core_full": "GCAT-BCAT-Engine/core-full",
        "core_addons": "GCAT-BCAT-Engine/core-addons",
        "stegverse_labs": "StegVerse-Labs",
        "stegverse_org": "StegVerse-org",
        "stegghost": "StegGhost",
    }

    # Output directories (relative to Publisher repo root)
    RECEIPT_DIR: Path = Path("receipts")
    NOTARY_STORE: Path = Path("notary_store")
    EVIDENCE_DIR: Path = Path("evidence")
    BADGE_DIR: Path = Path("badges")
    AUDIT_DIR: Path = Path("audit")

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.RECEIPT_DIR, cls.NOTARY_STORE, cls.EVIDENCE_DIR, cls.BADGE_DIR, cls.AUDIT_DIR]:
            d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    PublicationConfig.ensure_dirs()
    print("Publication directories ready.")
