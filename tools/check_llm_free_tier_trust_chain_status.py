from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "LLM_FREE_TIER_TRUST_CHAIN_STATUS.md"

REQUIRED_TEXT = [
    "LLM Free Tier Trust Chain Status",
    "StegVerse-org/LLM-adapter: free_tier_trust metadata",
    "StegVerse-Labs/Site: ecosystem-chat.html display and checker",
    "StegVerse-org/StegVerse-SDK: validate_free_tier_metadata ingestion",
    "StegVerse-Labs/admissibility-wiki: docs/governance/llm-free-tier-trust-chain.md",
    "role: publication_awareness_only",
    "quota availability is not admissibility",
    "receipt export is not permanent retention",
    "replay is not commit-time standing",
    "reconstruction is not commit-time standing",
    "upgrade does not change admissibility requirements",
]


def main() -> int:
    errors = []
    if not STATUS.exists():
        errors.append("missing_status")
        text = ""
    else:
        text = STATUS.read_text(encoding="utf-8")

    for item in REQUIRED_TEXT:
        if item not in text:
            errors.append("status_missing:" + item)

    if errors:
        print("LLM FREE TIER TRUST CHAIN STATUS: FAIL - " + ", ".join(errors))
        return 1
    print("LLM FREE TIER TRUST CHAIN STATUS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
