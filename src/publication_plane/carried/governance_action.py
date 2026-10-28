# Carried in-repo, verbatim from GCAT-BCAT-Engine/core-full@76227b0:src/stegverse_core_full/governance/action.py (sha256 3e87512d4847b6db9497e424135a6678de3846fa6347fe2538303d371c3b542e).
# Edit: from stegverse_core_lite.receipt.id import DeterministicReceiptID -> from publication_plane.core.deterministic import DeterministicReceiptID
# Edit: from stegverse_core_lite.hash.deterministic import DeterministicHash -> from publication_plane.core.deterministic import DeterministicHash
"""
Governed action evaluation.
Determines ALLOW / DENY / FAIL_CLOSED for any action in the StegVerse ecosystem.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class GovernedAction(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass
class ActionContext:
    """Context for action evaluation."""
    action_type: str
    source: str
    destination: str
    confidence: float
    evidence: Dict[str, Any]
    seed: str = "default"


class GovernedActionEvaluator:
    """
    Evaluates whether an action is permitted.
    Integrates with receipt verification for deterministic accountability.
    """

    CONFIDENCE_THRESHOLD = 0.85

    def __init__(self, receipt_provider=None):
        from publication_plane.core.deterministic import DeterministicReceiptID
        self.receipt_provider = receipt_provider or DeterministicReceiptID()

    def evaluate(self, context: ActionContext) -> Dict[str, Any]:
        """
        Evaluate action context and return deterministic result.
        """
        # Build canonical evaluation payload
        payload = {
            "action_type": context.action_type,
            "source": context.source,
            "destination": context.destination,
            "confidence": context.confidence,
            "evidence_hash": self._hash_evidence(context.evidence),
        }

        # Derive receipt ID for this evaluation (deterministic)
        evaluation_receipt = self.receipt_provider.derive(payload, context.seed)

        # Apply governance rules
        result = self._apply_rules(context)

        return {
            "result": result.value,
            "confidence": context.confidence,
            "threshold": self.CONFIDENCE_THRESHOLD,
            "evaluation_receipt": evaluation_receipt,
            "deterministic": True,
            "context": payload,
        }

    def _apply_rules(self, context: ActionContext) -> GovernedAction:
        """Apply governance rules to determine action result."""
        if context.confidence < 0.0 or context.confidence > 1.0:
            return GovernedAction.FAIL_CLOSED

        if context.confidence >= self.CONFIDENCE_THRESHOLD:
            return GovernedAction.ALLOW
        elif context.confidence >= 0.5:
            return GovernedAction.DENY
        else:
            return GovernedAction.FAIL_CLOSED

    def _hash_evidence(self, evidence: Dict[str, Any]) -> str:
        """Hash evidence for canonical inclusion."""
        import json
        from publication_plane.core.deterministic import DeterministicHash
        canonical = json.dumps(evidence, sort_keys=True, ensure_ascii=True)
        return DeterministicHash.hash(canonical, "")


def main():
    evaluator = GovernedActionEvaluator()

    test_cases = [
        ActionContext("publish", "sandbox", "publisher", 0.947, {"passes": 3}, "run-001"),
        ActionContext("publish", "sandbox", "publisher", 0.72, {"passes": 2}, "run-002"),
        ActionContext("publish", "sandbox", "publisher", 0.3, {"passes": 1}, "run-003"),
    ]

    for ctx in test_cases:
        result = evaluator.evaluate(ctx)
        print(f"Confidence {ctx.confidence} → {result['result']} (receipt: {result['evaluation_receipt'][:16]}...)")


if __name__ == "__main__":
    main()
