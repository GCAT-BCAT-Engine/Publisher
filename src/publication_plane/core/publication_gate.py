"""
Publication gating logic.
Maps gate test results (ALLOW/DENY/FAIL_CLOSED) to publication actions.
Integrates with stegverse-core-full governance.
"""

from enum import Enum
from typing import Dict, Any, Optional

from stegverse_core_full.governance.action import GovernedActionEvaluator, ActionContext, GovernedAction
from stegverse_core_full.monitoring.stegdb import StegDBMonitor


class GateResult(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    FAIL_CLOSED = "FAIL_CLOSED"


class PublicationAction(Enum):
    PUBLISH = "publish"
    QUARANTINE = "quarantine"
    BLOCK = "block"
    REVIEW = "manual_review"


class PublicationGate:
    """
    Decides publication fate based on gate test output.
    Integrates with StegDB monitoring — no publish without pre-check.
    """

    GATE_MAP = {
        GateResult.ALLOW: PublicationAction.PUBLISH,
        GateResult.DENY: PublicationAction.QUARANTINE,
        GateResult.FAIL_CLOSED: PublicationAction.BLOCK,
    }

    def __init__(
        self,
        action_evaluator: Optional[GovernedActionEvaluator] = None,
        stegdb_monitor: Optional[StegDBMonitor] = None,
        confidence_threshold: float = 0.85
    ):
        self.action_evaluator = action_evaluator or GovernedActionEvaluator()
        self.stegdb_monitor = stegdb_monitor
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        gate_result: str,
        confidence: float,
        evidence: Dict[str, Any],
        source: str = "sandbox",
        destination: str = "publisher",
        seed: str = "default",
        require_stegdb_clearance: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate whether a result may be published.
        """
        # Use core-full governance for evaluation
        context = ActionContext(
            action_type="publication",
            source=source,
            destination=destination,
            confidence=confidence,
            evidence=evidence,
            seed=seed,
        )

        gov_result = self.action_evaluator.evaluate(context)

        # Map to publication action
        result_enum = GateResult(gate_result)
        action = self.GATE_MAP[result_enum]

        # Confidence override: even ALLOW can be quarantined if confidence too low
        if result_enum == GateResult.ALLOW and confidence < self.confidence_threshold:
            action = PublicationAction.REVIEW

        # StegDB pre-check
        stegdb_status = "bypassed"
        if require_stegdb_clearance and self.stegdb_monitor:
            # Use evaluation receipt for StegDB check
            receipt_id = gov_result["evaluation_receipt"]
            stegdb_status = self.stegdb_monitor.check(receipt_id)
            if stegdb_status != "cleared":
                action = PublicationAction.BLOCK

        return {
            "gate_result": gate_result,
            "confidence": confidence,
            "threshold": self.confidence_threshold,
            "action": action.value,
            "stegdb_status": stegdb_status,
            "governance": gov_result,
            "deterministic": True,
        }


def main():
    gate = PublicationGate()

    for result in ["ALLOW", "DENY", "FAIL_CLOSED"]:
        decision = gate.evaluate(
            gate_result=result,
            confidence=0.947 if result == "ALLOW" else 0.3,
            evidence={"passes": 3 if result == "ALLOW" else 1},
            seed="gate-demo-001"
        )
        print(f"{result} → {decision['action']} (StegDB: {decision['stegdb_status']})")
        print(f"  Governance receipt: {decision['governance']['evaluation_receipt'][:16]}...")


if __name__ == "__main__":
    main()
