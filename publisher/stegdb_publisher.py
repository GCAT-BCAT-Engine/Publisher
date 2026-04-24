"""Publisher StegDB Integration.

Tracks paper submissions, patent filings, and social media posts.
Emits publisher.* events and receives canonical publication policies.
Platform agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from publisher.stegdb_adapter import StegDBAdapter


@dataclass
class SubmissionRecord:
    """A paper or patent submission record."""

    submission_id: str
    title: str
    authors: list[str]
    venue: str
    status: str
    submitted_date: str
    decision_date: str | None = None
    decision: str | None = None
    notes: str = ""


@dataclass
class SocialMediaPost:
    """A planned or executed social media post."""

    post_id: str
    platform: str
    content: str
    scheduled_date: str
    posted_date: str | None = None
    engagement_metrics: dict[str, Any] | None = None


class PublisherStegDBEmitter:
    """Emit publisher events to StegDB."""

    def __init__(
        self,
        source_repo: str = "github.com/GCAT-BCAT-Engine/Publisher",
        platform: str = "github",
        backend: str = "git_commit",
    ) -> None:
        self.adapter = StegDBAdapter(
            source_repo=source_repo,
            platform=platform,
            backend=backend,
        )

    def emit_submission(
        self,
        record: SubmissionRecord,
        paper_type: str = "research",
    ) -> None:
        """Emit a publisher.submission event."""
        payload = {
            "domain": "publication",
            "paper_type": paper_type,
            "submission_id": record.submission_id,
            "title": record.title,
            "authors": record.authors,
            "venue": record.venue,
            "status": record.status,
            "submitted_date": record.submitted_date,
            "decision_date": record.decision_date,
            "decision": record.decision,
            "notes": record.notes,
        }
        self.adapter.emit(
            event_type="publisher.submission",
            payload=payload,
        )

    def emit_patent_filing(
        self,
        title: str,
        inventors: list[str],
        filing_date: str,
        patent_office: str,
        application_number: str = "",
        status: str = "provisional",
    ) -> None:
        """Emit a publisher.patent_filing event."""
        payload = {
            "domain": "patent",
            "title": title,
            "inventors": inventors,
            "filing_date": filing_date,
            "patent_office": patent_office,
            "application_number": application_number,
            "status": status,
        }
        self.adapter.emit(
            event_type="publisher.patent_filing",
            payload=payload,
        )

    def emit_paper_draft(
        self,
        title: str,
        authors: list[str],
        draft_date: str,
        word_count: int,
        sections: list[str],
        repo_path: str,
    ) -> None:
        """Emit a publisher.paper_draft event."""
        payload = {
            "domain": "publication",
            "title": title,
            "authors": authors,
            "draft_date": draft_date,
            "word_count": word_count,
            "sections": sections,
            "repo_path": repo_path,
        }
        self.adapter.emit(
            event_type="publisher.paper_draft",
            payload=payload,
        )

    def emit_social_media(
        self,
        post: SocialMediaPost,
        campaign: str = "",
    ) -> None:
        """Emit a social media post event."""
        payload = {
            "domain": "social_media",
            "post_id": post.post_id,
            "platform": post.platform,
            "content_preview": post.content[:200],
            "scheduled_date": post.scheduled_date,
            "posted_date": post.posted_date,
            "campaign": campaign,
            "engagement_metrics": post.engagement_metrics,
        }
        self.adapter.emit(
            event_type="publisher.social_media",
            payload=payload,
        )

    def receive_publication_policy(self, policy_path: str) -> dict[str, Any]:
        """Receive canonical publication policy from StegDB.

        Returns policy dict with keys:
        - target_venues: list of recommended venues
        - embargo_rules: dict of embargo periods by venue type
        - authorship_policy: requirements for author listing
        - social_media_schedule: recommended posting cadence
        """
        return self.adapter.receive_canonical_update(policy_path)
