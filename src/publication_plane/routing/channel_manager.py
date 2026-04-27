"""
Cross-org release channel management.
Coordinates publication across multiple GitHub organizations.
"""

from typing import Dict, Any, List

from stegverse_core_addons.cross_org.sync import CrossOrgSync


class ChannelManager:
    """
    Manages publication channels across the StegVerse ecosystem.
    Uses cross-org sync for target resolution.
    """

    def __init__(self, cross_org_sync: CrossOrgSync = None):
        self.sync = cross_org_sync or CrossOrgSync()

    def resolve_targets(self, org_keys: List[str]) -> List[str]:
        """Resolve org keys to full target paths."""
        targets = []
        for key in org_keys:
            targets.extend(self.sync.get_targets(key))
        return targets

    def validate_publication(
        self,
        target: str,
        receipt_id: str,
        governance_result: Dict[str, Any]
    ) -> bool:
        """
        Validate that a publication target is permitted.
        """
        # Target must be in registry
        if not self.sync.validate_target(target):
            return False

        # Governance must allow
        if governance_result.get("action") not in ["publish", "manual_review"]:
            return False

        return True


def main():
    manager = ChannelManager()

    targets = manager.resolve_targets(["publisher", "stegverse_labs"])
    print(f"Resolved targets: {targets}")

    valid = manager.validate_publication(
        "GCAT-BCAT-Engine/Publisher",
        "rcp-001",
        {"action": "publish"}
    )
    print(f"Valid: {valid}")


if __name__ == "__main__":
    main()
