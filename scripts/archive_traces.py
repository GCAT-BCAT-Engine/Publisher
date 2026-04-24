#!/usr/bin/env python3
"""
archive_traces.py — Publisher trace archival

Copies milestone traces from AaCT-E CI artifacts into long-term storage
with full provenance metadata.

Usage:
    python archive_traces.py --traces-dir outputs/ --tag v0.1.0 --paper-version 1.0.0
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone


def archive_traces(traces_dir: Path, archive_root: Path, tag: str, paper_version: str) -> Path:
    """Archive traces with full provenance."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_dir = archive_root / f"{timestamp}_aacte-{tag}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "archive_date": timestamp,
        "aacte_version": tag,
        "paper_version": paper_version,
        "traces": []
    }

    for trace_file in sorted(traces_dir.glob("*_trace.json")):
        dest = archive_dir / trace_file.name
        shutil.copy2(trace_file, dest)

        data = json.loads(trace_file.read_text(encoding="utf-8"))
        manifest["traces"].append({
            "file": trace_file.name,
            "scenario": data.get("scenario"),
            "decision": data.get("decision"),
            "proposal_min_separation_nm": data.get("proposal_min_separation_nm"),
            "sha256": "placeholder"  # TODO: compute actual hash
        })

    manifest_path = archive_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Archived {len(manifest['traces'])} traces to {archive_dir}")
    return archive_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces-dir", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, default=Path("archives/traces"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--paper-version", default="unknown")
    args = parser.parse_args()

    archive_traces(args.traces_dir, args.archive_root, args.tag, args.paper_version)


if __name__ == "__main__":
    main()
