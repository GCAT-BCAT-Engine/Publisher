#!/usr/bin/env python3
"""Render a generic evidence-backed report package through Publisher."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from publisher.evidence_report import EvidenceReportError, render_evidence_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
        manifest, receipt = render_evidence_report(package, args.output_dir)
    except (OSError, json.JSONDecodeError, EvidenceReportError) as exc:
        print(f"PUBLISHER_EVIDENCE_REPORT_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "result": receipt["result"],
        "report_id": receipt["report_id"],
        "package_sha256": receipt["package_sha256"],
        "manifest_sha256": receipt["manifest_sha256"],
        "formats": [item["format"] for item in manifest["artifacts"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
