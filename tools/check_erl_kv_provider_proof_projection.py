#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
projection = json.loads((ROOT / "data/erl-kv-provider-proof-projection.json").read_text(encoding="utf-8"))
assert projection["schema"] == "stegverse.erl-kv-provider-proof-projection/v1"
assert projection["task_id"] == "SS-ERL-KV-PROPAGATION-VERIFICATION-001"
assert projection["consumer"]["repository"] == "GCAT-BCAT-Engine/Publisher"
assert projection["consumer"]["applicability"] == "UPDATE_REQUIRED"
assert projection["consumer"]["role"] == "GOVERNED_KV_DOCUMENT_RENDERER"
assert projection["upstream"]["erl_integration_commit"] == "722a11cf2ada6205a31e3678d489254fb736e8f7"
ORGANIZATION_RECORD_COMMIT = "master_records_organization_record_commit"
# Pre-migration field name, still accepted from already-published projections
# (Master Records boundary remediation, MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002).
LEGACY_ORGANIZATION_RECORD_COMMIT = "master_records_custody_commit"


def organization_record_commit(upstream):
    if ORGANIZATION_RECORD_COMMIT in upstream:
        return upstream[ORGANIZATION_RECORD_COMMIT]
    return upstream.get(LEGACY_ORGANIZATION_RECORD_COMMIT)


assert organization_record_commit(projection["upstream"]) == "3e1bc4f2f98bde1932261c2ce96ca42fa9952a19"
assert LEGACY_ORGANIZATION_RECORD_COMMIT not in projection["upstream"]
assert projection["upstream"]["provider_operation_receipt_sha256"] == "bb74904fcd8169829c78bdc1c0d64905b33243c2c22852565c13e614abcd1fa8"
assert all(projection["proof"].values())
assert not any(projection["nonclaims"].values())
assert projection["authority_effect"] == "NONE_REFERENCE_ONLY"
for rel in ("README.md", "docs/ERL_KV_PROVIDER_PROOF_PUBLISHER_PROJECTION_MIRROR_HANDOFF.md"):
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "SS-ERL-KV-PROPAGATION-VERIFICATION-001" in text
    assert "bb74904fcd8169829c78bdc1c0d64905b33243c2c22852565c13e614abcd1fa8" in text
print("ERL KV PROVIDER PROOF PUBLISHER PROJECTION: PASS")
