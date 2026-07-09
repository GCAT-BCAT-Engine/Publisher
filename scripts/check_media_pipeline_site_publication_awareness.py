#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AWARENESS = ROOT / "docs" / "media-pipeline-site-publication-awareness.md"
REQUIRED_MARKERS = [
    "awareness_id: media_pipeline_site_publication_awareness_001",
    "manual_actions_required: false",
    "source_repo: StegVerse-Labs/Site",
    "source_manifest: data/publication-manifest/media-pipeline.json",
    "source_page: docs/media/media-pipeline-overview.md",
    "state: SITE_MIRROR_AWARENESS_RECORDED",
    "planning-and-replay only",
    "does not claim live camera use",
    "does not claim live microphone use",
    "public broadcast",
    "external platform streaming",
    "provider execution",
    "broadcast-engine",
    "publication-awareness metadata only",
]


def main():
    if not AWARENESS.exists():
        print(f"FAIL missing {AWARENESS.relative_to(ROOT)}")
        return 1
    print(f"PASS {AWARENESS.relative_to(ROOT)}")
    text = AWARENESS.read_text(encoding="utf-8")
    failed = False
    for marker in REQUIRED_MARKERS:
        if marker in text:
            print(f"PASS awareness contains {marker}")
        else:
            failed = True
            print(f"FAIL awareness missing {marker}")
    if failed:
        return 1
    print("PASS media pipeline Site publication awareness")
    return 0


if __name__ == "__main__":
    sys.exit(main())
