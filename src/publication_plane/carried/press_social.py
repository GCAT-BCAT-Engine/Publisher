# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-addons@29a74ef:stegverse_core_addons/press/social.py (sha256 fa36cb4e71018e262a5e9d88c798954a6b8c6597ea7268b8b7862d865380e04e).
# Edit: from stegverse_core_lite.receipt.id import DeterministicReceiptID -> from publication_plane.core.deterministic import DeterministicReceiptID
# Edit: 25 upload-damaged string literal(s) repaired: a literal line break inside a string restored to the \n escape it
#   replaced (the source file does not parse; GCAT-BCAT-Engine/core-addons 'Add files via upload'). No other change.
"""
Social media and press summary generation.
Creates publication-ready summaries for StegVerse releases.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PressSummary:
    headline: str
    body: str
    hashtags: List[str]
    platforms: Dict[str, str]  # platform -> formatted post
    receipt_id: str


class PressSummaryGenerator:
    """
    Generates press summaries and social media posts for StegVerse publications.
    All outputs are receipted for accountability.
    """

    def __init__(self, receipt_provider=None):
        from publication_plane.core.deterministic import DeterministicReceiptID
        self.receipt_provider = receipt_provider or DeterministicReceiptID()

    def generate(
        self,
        publication_title: str,
        key_findings: List[str],
        confidence: float,
        org: str,
        seed: str = "press-default"
    ) -> PressSummary:
        """Generate a press summary with platform-specific formatting."""

        headline = f"StegVerse: {publication_title}"

        body = f"New release from {org}:\n\n"
        body += f"Key findings ({confidence:.0%} confidence):\n"
        for finding in key_findings:
            body += f"  • {finding}\n"
        body += "\nVerified by deterministic receipt. #StegVerse"

        hashtags = ["#StegVerse", "#DeterministicTrust", "#GCATBCAT", f"#{org.replace('-', '')}"]

        platforms = {
            "twitter": self._format_twitter(headline, body, confidence),
            "linkedin": self._format_linkedin(headline, body, key_findings, confidence),
            "github": self._format_github_release(publication_title, body, confidence),
        }

        # Receipt the summary itself
        summary_content = {
            "headline": headline,
            "findings_count": len(key_findings),
            "confidence": confidence,
            "org": org,
        }
        receipt_id = self.receipt_provider.derive(summary_content, seed)

        return PressSummary(
            headline=headline,
            body=body,
            hashtags=hashtags,
            platforms=platforms,
            receipt_id=receipt_id,
        )

    def _format_twitter(self, headline: str, body: str, confidence: float) -> str:
        text = f"{headline}\n\n{body[:200]}..." if len(body) > 200 else f"{headline}\n\n{body}"
        text += f"\n\nConfidence: {confidence:.0%}"
        return text[:280]  # Twitter limit

    def _format_linkedin(self, headline: str, body: str, findings: List[str], confidence: float) -> str:
        text = f"{headline}\n\n{body}\n\n"
        text += f"This publication achieved {confidence:.0%} confidence across {len(findings)} verified findings.\n"
        text += "All results are backed by deterministic receipts."
        return text

    def _format_github_release(self, title: str, body: str, confidence: float) -> str:
        return f"## {title}\n\n{body}\n\n**Confidence:** {confidence:.0%}\n**Verification:** Deterministic receipt attached."


def main():
    generator = PressSummaryGenerator()

    summary = generator.generate(
        publication_title="GCAT/BCAT Invariant Verification",
        key_findings=[
            "Invariant holds across 1M test cases",
            "Deterministic receipts verify all transitions",
            "StegDB monitoring confirms integrity",
        ],
        confidence=0.947,
        org="GCAT-BCAT-Engine",
        seed="press-release-001"
    )

    print(f"Headline: {summary.headline}")
    print(f"Receipt: {summary.receipt_id}")
    print(f"\nTwitter:\n{summary.platforms['twitter']}")
    print(f"\nLinkedIn:\n{summary.platforms['linkedin'][:200]}...")


if __name__ == "__main__":
    main()
