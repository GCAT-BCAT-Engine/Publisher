"""
Publisher-specific press summary generation.
Wraps core-addons press module with Publisher configuration.
"""

from typing import Dict, Any, List

from stegverse_core_addons.press.social import PressSummaryGenerator


class PublisherPressSummary:
    """
    Generates press summaries configured for Publisher org targets.
    """

    def __init__(self, generator: PressSummaryGenerator = None):
        self.generator = generator or PressSummaryGenerator()

    def generate_for_release(
        self,
        title: str,
        findings: List[str],
        confidence: float,
        org: str = "GCAT-BCAT-Engine",
        seed: str = "publisher-press"
    ) -> Dict[str, Any]:
        """Generate press summary for a Publisher release."""
        summary = self.generator.generate(title, findings, confidence, org, seed)

        return {
            "headline": summary.headline,
            "body": summary.body,
            "hashtags": summary.hashtags,
            "platforms": summary.platforms,
            "receipt_id": summary.receipt_id,
            "org": org,
        }


def main():
    gen = PublisherPressSummary()

    result = gen.generate_for_release(
        title="Publisher v1.0 Release",
        findings=[
            "Deterministic receipts across all publications",
            "StegDB monitoring integrated",
            "Cross-org sync operational",
        ],
        confidence=0.95,
        org="GCAT-BCAT-Engine",
        seed="publisher-v1-announcement"
    )

    print(f"Headline: {result['headline']}")
    print(f"Receipt: {result['receipt_id']}")
    print(f"
Twitter preview:
{result['platforms']['twitter'][:150]}...")


if __name__ == "__main__":
    main()
