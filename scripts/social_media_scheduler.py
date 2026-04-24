#!/usr/bin/env python3
"""
social_media_scheduler.py — Publisher social media automation

Evaluates AaCT-E status reports against milestone rules and generates
post content for X, LinkedIn, and Blog.

Usage:
    python social_media_scheduler.py --status-file last_status.json --platform x
"""

import argparse
import json
from pathlib import Path
from typing import Optional


MILESTONE_RULES = {
    "first_verification": {
        "condition": lambda data: data.get("status") == "success" and len(data.get("traces", [])) > 0,
        "message": "🛡️ AaCT-E demo achieves zero-dependency verification. Commit-time safety enforcement is now executable.",
        "platforms": ["x", "linkedin", "blog"]
    },
    "deny_scenario": {
        "condition": lambda data: any(t.get("decision") == "DENY" for t in data.get("traces", [])),
        "message": "✅ AaCT-E correctly denies unsafe actions at the commit point. Recovery alternatives identified and preserved.",
        "platforms": ["x", "linkedin"]
    },
    "recovery_reachable": {
        "condition": lambda data: all(t.get("recovery_reachable") for t in data.get("traces", [])),
        "message": "🔄 All scenarios preserve recovery reachability. BCAT invariant holds across the demo suite.",
        "platforms": ["linkedin", "blog"]
    }
}


def evaluate_milestones(data: dict) -> list[dict]:
    """Evaluate status against all milestone rules."""
    triggered = []
    for name, rule in MILESTONE_RULES.items():
        if rule["condition"](data):
            triggered.append({
                "name": name,
                "message": rule["message"],
                "platforms": rule["platforms"]
            })
    return triggered


def format_post(milestone: dict, platform: str, data: dict) -> str:
    """Format post for specific platform."""
    base = milestone["message"]

    if platform == "x":
        # 280 char limit
        lines = [
            base[:200],
            f"→ {len(data.get('traces', []))} scenarios verified",
            "#AviationSafety #AI #GCAT #BCAT"
        ]
        return "\n".join(lines)

    elif platform == "linkedin":
        lines = [
            base,
            "",
            "This is part of the GCAT/BCAT formalism for commit-time safety enforcement in AI-assisted aviation decisions.",
            "",
            "The demo is zero-dependency, deterministic, and fully verifiable:",
            "→ git clone https://github.com/AaCT-E/demo",
            "→ python verify_demo.py",
            "",
            "#Aviation #AI #Safety #SBIR #Research"
        ]
        return "\n".join(lines)

    elif platform == "blog":
        lines = [
            f"## {milestone['name'].replace('_', ' ').title()}",
            "",
            base,
            "",
            "### Technical Details",
            "",
            f"- Repository: {data.get('repo')}",
            f"- Commit: {data.get('commit_sha')}",
            f"- Timestamp: {data.get('timestamp_utc')}",
            f"- Scenarios: {len(data.get('traces', []))}",
            "",
            "### Trace Summary",
            ""
        ]
        for trace in data.get("traces", []):
            lines.append(f"- **{trace['scenario']}**: {trace['decision']} (min sep: {trace['proposal_min_separation_nm']:.3f} nm)")
        return "\n".join(lines)

    return base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("--platform", choices=["x", "linkedin", "blog", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print posts without publishing")
    args = parser.parse_args()

    data = json.loads(args.status_file.read_text(encoding="utf-8"))
    milestones = evaluate_milestones(data)

    if not milestones:
        print("No milestones triggered.")
        return

    platforms = ["x", "linkedin", "blog"] if args.platform == "all" else [args.platform]

    for milestone in milestones:
        print(f"\n=== Milestone: {milestone['name']} ===")
        for platform in platforms:
            if platform in milestone["platforms"]:
                post = format_post(milestone, platform, data)
                print(f"\n--- {platform.upper()} ---")
                print(post)
                if not args.dry_run:
                    # TODO: Integrate with platform APIs
                    print(f"[Would publish to {platform}]")


if __name__ == "__main__":
    main()
