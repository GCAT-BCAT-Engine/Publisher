"""Submission Tracker with StegDB persistence.

Tracks paper submissions, patent filings, and social media posts.
All state changes emit governance events.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from publisher.stegdb_publisher import PublisherStegDBEmitter, SubmissionRecord, SocialMediaPost


class SubmissionTracker:
    """Track submissions and sync to StegDB."""

    def __init__(
        self,
        data_dir: str = "publisher_data",
        emitter: PublisherStegDBEmitter | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.emitter = emitter or PublisherStegDBEmitter()
        self._submissions: list[SubmissionRecord] = []
        self._posts: list[SocialMediaPost] = []
        self._load()

    def add_submission(self, record: SubmissionRecord) -> None:
        """Add a submission and emit event."""
        self._submissions.append(record)
        self.emitter.emit_submission(record)
        self._save()

    def update_submission_status(
        self,
        submission_id: str,
        status: str,
        decision: str | None = None,
        decision_date: str | None = None,
    ) -> None:
        """Update submission status and emit event."""
        for sub in self._submissions:
            if sub.submission_id == submission_id:
                sub.status = status
                sub.decision = decision
                sub.decision_date = decision_date
                self.emitter.emit_submission(sub)
                self._save()
                return
        raise ValueError(f"Submission not found: {submission_id}")

    def add_social_media_post(self, post: SocialMediaPost, campaign: str = "") -> None:
        """Add a social media post and emit event."""
        self._posts.append(post)
        self.emitter.emit_social_media(post, campaign=campaign)
        self._save()

    def list_submissions(self, status: str | None = None) -> list[SubmissionRecord]:
        """List submissions, optionally filtered by status."""
        if status is None:
            return list(self._submissions)
        return [s for s in self._submissions if s.status == status]

    def list_posts(self, platform: str | None = None) -> list[SocialMediaPost]:
        """List social media posts, optionally filtered by platform."""
        if platform is None:
            return list(self._posts)
        return [p for p in self._posts if p.platform == platform]

    def export_for_stegdb(self, filepath: str | None = None) -> str:
        """Export all data as canonical JSON for StegDB ingestion."""
        data = {
            "submissions": [asdict(s) for s in self._submissions],
            "social_media_posts": [asdict(p) for p in self._posts],
        }
        path = filepath or str(self.data_dir / "stegdb_export.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return path

    def _save(self) -> None:
        data = {
            "submissions": [asdict(s) for s in self._submissions],
            "social_media_posts": [asdict(p) for p in self._posts],
        }
        with open(self.data_dir / "submissions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self) -> None:
        path = self.data_dir / "submissions.json"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._submissions = [SubmissionRecord(**s) for s in data.get("submissions", [])]
        self._posts = [SocialMediaPost(**p) for p in data.get("social_media_posts", [])]
