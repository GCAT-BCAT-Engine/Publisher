# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-addons@29a74ef:stegverse_core_addons/cross_org/sync.py (sha256 d03db4f3929e16d2b0cc2f058ddb05a00ab0f2e421fef92c43bc0973621f0fb9).
# Edit: 1 upload-damaged line break(s) in 1 string literal(s) repaired: each literal line break restored to the \n
#   escape it replaced (the source file does not parse; GCAT-BCAT-Engine/core-addons 'Add files via upload'). No other change.
"""
Cross-organization registry synchronization.
Enables StegVerse components to publish across org boundaries.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class OrgRegistry:
    name: str
    github_org: str
    targets: List[str]  # Repo paths
    enabled: bool = True


class CrossOrgSync:
    """
    Manages publication targets across multiple GitHub organizations.
    All targets are validated before sync.
    """

    DEFAULT_ORGS = {
        "publisher": OrgRegistry("Publisher", "GCAT-BCAT-Engine", ["Publisher", "core-lite", "core-full"]),
        "stegverse_labs": OrgRegistry("StegVerse Labs", "StegVerse-Labs", ["StegBrain", "StegID", "StegOps-Orchestrator"]),
        "stegverse_org": OrgRegistry("StegVerse", "StegVerse-org", ["demo-suite-runner", "SDK"]),
        "stegghost": OrgRegistry("StegGhost", "StegGhost", ["entity-sandbox-runner"]),
    }

    def __init__(self, registry_file: str = "org_registry.json"):
        self.registry_file = Path(registry_file)
        self.orgs = self._load_registry()

    def _load_registry(self) -> Dict[str, OrgRegistry]:
        if self.registry_file.exists():
            data = json.loads(self.registry_file.read_text(encoding="utf-8"))
            return {k: OrgRegistry(**v) for k, v in data.items()}
        return self.DEFAULT_ORGS.copy()

    def save_registry(self):
        data = {k: {"name": v.name, "github_org": v.github_org, "targets": v.targets, "enabled": v.enabled}
                for k, v in self.orgs.items()}
        self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_targets(self, org_key: str) -> List[str]:
        """Get enabled publication targets for an org."""
        org = self.orgs.get(org_key)
        if not org or not org.enabled:
            return []
        return [f"{org.github_org}/{t}" for t in org.targets]

    def list_all_targets(self) -> List[str]:
        """List all enabled targets across all orgs."""
        targets = []
        for key in self.orgs:
            targets.extend(self.get_targets(key))
        return targets

    def validate_target(self, target: str) -> bool:
        """Validate that a target path exists in registry."""
        return any(target in self.list_all_targets() for _ in [1])


def main():
    sync = CrossOrgSync()

    print("All targets:")
    for t in sync.list_all_targets():
        print(f"  - {t}")

    print(f"\nPublisher targets: {sync.get_targets('publisher')}")
    print(f"Valid 'GCAT-BCAT-Engine/Publisher': {sync.validate_target('GCAT-BCAT-Engine/Publisher')}")


if __name__ == "__main__":
    main()
