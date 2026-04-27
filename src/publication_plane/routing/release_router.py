"""
Research/demo/press release routing.
Determines the correct publication channel based on content type and governance.
"""

from typing import Dict, Any, List
from enum import Enum


class ReleaseType(Enum):
    RESEARCH = "research"
    DEMO = "demo"
    PRESS = "press"
    INTERNAL = "internal"


class ReleaseRouter:
    """
    Routes publications to the correct channel based on type and governance result.
    """

    CHANNELS = {
        ReleaseType.RESEARCH: ["arxiv", "github_releases", "academic_journals"],
        ReleaseType.DEMO: ["github_releases", "demo_surfaces", "social_media"],
        ReleaseType.PRESS: ["social_media", "press_releases", "blog"],
        ReleaseType.INTERNAL: ["internal_registry"],
    }

    def route(
        self,
        release_type: str,
        governance_result: Dict[str, Any],
        org_targets: List[str] = None
    ) -> Dict[str, Any]:
        """
        Determine publication channels for a release.
        """
        rt = ReleaseType(release_type)

        # Only ALLOW results go to external channels
        if governance_result["action"] not in ["publish", "manual_review"]:
            return {
                "release_type": release_type,
                "action": governance_result["action"],
                "channels": [],
                "reason": "governance_blocked",
            }

        channels = self.CHANNELS[rt].copy()

        # Manual review goes to review queue first
        if governance_result["action"] == "manual_review":
            channels = ["review_queue"] + channels

        return {
            "release_type": release_type,
            "action": governance_result["action"],
            "channels": channels,
            "org_targets": org_targets or [],
            "receipt_id": governance_result["governance"]["evaluation_receipt"],
        }


def main():
    router = ReleaseRouter()

    for rtype in ["research", "demo", "press"]:
        result = router.route(
            release_type=rtype,
            governance_result={
                "action": "publish",
                "governance": {"evaluation_receipt": "rcp-demo-001"}
            },
            org_targets=["GCAT-BCAT-Engine/Publisher"]
        )
        print(f"{rtype}: {result['channels']}")


if __name__ == "__main__":
    main()
