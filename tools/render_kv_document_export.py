#!/usr/bin/env python3
"""Render an admitted KnowledgeVault document export through Publisher."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from publisher.document_pipeline import DocumentPipelineError, render_document_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        manifest, receipt = render_document_bundle(bundle, args.output_dir)
    except (OSError, json.JSONDecodeError, DocumentPipelineError) as exc:
        print(f"PUBLISHER_DOCUMENT_RENDER_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "result": receipt["result"],
        "generation_id": receipt["generation_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "formats": [item["format"] for item in manifest["artifacts"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
